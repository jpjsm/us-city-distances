# Source: https://copilot.microsoft.com/shares/2pcnoSSik3Eek2G4wK7Pr

from pathlib import Path
import osmnx as ox
import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from shapely.prepared import prep
from sklearn.neighbors import BallTree
from pyrosm import OSM

from osm_constants import (
    ALL_US_CITIES_CENTRIODS_PROJECTED_PARQUET,
    ALL_US_CITIES_ADJACENCY_PAIRS_PARQUET,
    ALL_US_CITIES_ADJACENCY_PAIRS_CSV,
)
from config import OSM_CITIES_DATA_FOLDER
from geofabrik_constants import OSM_PBF_PATHS

# ---------------------------------------------
# Local constants
# ---------------------------------------------
PYTHON_FILENAME = Path(__file__).name

# ---------------------------------------------
# OSM config for large states
# ---------------------------------------------
ox.settings.max_query_area_size = 1_000_000_000_000  # 1e12


def get_graph_from_pbfs(
    north, south, east, west, network_type="driving", pbfs=OSM_PBF_PATHS
):
    print(
        f"🚫🐛[{PYTHON_FILENAME}.get_graph_from_pbfs] get_graph_from_pbfs{(north, south, east, west, f"network_type={network_type}", f"pbfs={pbfs}")}"
    )

    for pbf in pbfs:
        osm = OSM(str(pbf), bounding_box=[west, south, east, north])
        nodes, edges = osm.get_network(network_type=network_type, nodes=True)
        G = osm.to_graph(nodes, edges, graph_type="networkx")

        if len(G.nodes):
            print(
                f"🚫🐛[{PYTHON_FILENAME}.get_graph_from_pbfs] get_graph_from_pbfs(): successful"
            )
            return G

    print(
        f"🚫🐛[{PYTHON_FILENAME}.get_graph_from_pbfs] get_graph_from_pbfs(): No graph for coordinates {(north, south, east, west)}"
    )
    return nx.MultiDiGraph()


def get_all_city_undirected_adjacency(
    cities_gdf,
    k_neighbors=12,
    crs_projected="EPSG:5070",
    min_radius_km=50,
    max_radius_km=500,
    neighbor_k_for_radius=8,
):
    """
    Build a national adjacency graph for U.S. cities where two cities A and B
    are adjacent if there exists a drivable path between their centroids
    that does NOT cross any other city polygon.

    This version uses an adaptive per-city radius:
        radius = clip( 2 × distance_to_kth_neighbor , min_radius_km , max_radius_km )

    Parameters
    ----------
    cities_gdf : GeoDataFrame
        Must contain:
            - geometry (city polygons)
            - centroid (Point)
            - name (string)
    k_neighbors : int
        Number of nearest neighbors to test per city.
    crs_projected : str
        Projected CRS for graph operations.
    min_radius_km : float
        Minimum allowed radius for any city.
    max_radius_km : float
        Maximum allowed radius for any city.
    neighbor_k_for_radius : int
        k-th nearest neighbor used to compute adaptive radius.

    Returns
    -------
    adjacency_df : DataFrame
        Columns: ["city_a", "city_b"]
    """

    # --- 1. Prepare centroids and polygons ---
    cities = cities_gdf.copy()

    # Ensure centroids exist
    cities = cities.to_crs("EPSG:4326")
    cities["centroid"] = cities.geometry.centroid

    # Prepared polygons for fast intersection
    cities["prepared"] = cities.geometry.apply(prep)

    # --- 2. Compute adaptive radius per city ---
    coords = np.radians(np.column_stack([cities.centroid.y, cities.centroid.x]))
    tree = BallTree(coords, metric="haversine")
    distances, _ = tree.query(coords, k=neighbor_k_for_radius)

    # Convert to km
    km = distances * 6371.0
    kth = km[:, -1]  # distance to k-th nearest neighbor

    # Adaptive radius
    cities["radius_km"] = np.clip(kth * 2.0, min_radius_km, max_radius_km)

    # --- 3. Build BallTree for adjacency candidates ---
    distances_knn, indices_knn = tree.query(coords, k=k_neighbors)

    # --- 4. Helper: bounding box around a city ---
    def city_bbox(lat, lon, km):
        d = km / 111  # approx degrees per km
        return lat + d, lat - d, lon + d, lon - d

    # --- 5. Helper: block all other cities from a graph ---
    def block_other_cities(G, cities, keep_city_name):
        G2 = G.copy()
        for _, row in cities.iterrows():
            if row["name"] == keep_city_name:
                continue
            poly = row["prepared"]
            for u, v, k, data in list(G2.edges(keys=True, data=True)):
                geom = data.get("geometry")
                if geom is not None and poly.intersects(geom):
                    G2.remove_edge(u, v, k)
        return G2

    # --- 6. Main loop: compute adjacency ---
    edges_out = []

    total_cities = len(cities)
    progress_count = 1
    for i, row in cities.iterrows():
        print(
            f"🚫🐛[{PYTHON_FILENAME}.get_all_city_undirected_adjacency] Progress: {progress_count:7,}/{total_cities:7,} ({(progress_count*100)//total_cities:3}%) | {row['state_name']:30}, {row['name']}"
        )
        progress_count += 1
        A_name = row["name"]
        A_lat = row.centroid.y
        A_lon = row.centroid.x
        radius = row["radius_km"]

        # Local bounding box
        north, south, east, west = city_bbox(A_lat, A_lon, radius)

        # Load local road graph
        print(
            f"🚫🐛[{PYTHON_FILENAME}.get_all_city_undirected_adjacency] get_graph_from_pbfs({(north, south, east, west)}, network_type='drive)', with radius: {radius} km"
        )
        try:
            G = get_graph_from_pbfs(north, south, east, west)
            if len(G.nodes) == 0:
                raise ValueError(
                    f"No PBF file ({OSM_PBF_PATHS}) to cover bbox: {(north, south, east, west)}"
                )
        except Exception as ex:
            print(
                f"\t🚫🐛[{PYTHON_FILENAME}.get_all_city_undirected_adjacency] [ERROR: {ex}] {row['state_name']}.{row['name']}: cant get graph from bbox for {(north, south, east, west)}"
            )
            continue

        # Project graph
        print(
            f"🚫🐛[{PYTHON_FILENAME}.get_all_city_undirected_adjacency] ox.project_graph(G, to_crs=crs_projected)"
        )
        G = ox.project_graph(G, to_crs=crs_projected)

        # Block other cities
        print(
            f"🚫🐛[{PYTHON_FILENAME}.get_all_city_undirected_adjacency] block_other_cities(G, cities, keep_city_name={A_name})"
        )
        G2 = block_other_cities(G, cities, keep_city_name=A_name)

        # Snap A
        try:
            print(
                f"🚫🐛[{PYTHON_FILENAME}.get_all_city_undirected_adjacency] ox.nearest_nodes(G2, {A_lon}, {A_lat})"
            )
            A_node = ox.nearest_nodes(G2, A_lon, A_lat)
        except Exception as ex:
            print(
                f"🚫🐛[{PYTHON_FILENAME}.get_all_city_undirected_adjacency] Ooops... ox.nearest_nodes(G2, {A_lon}, {A_lat}) Exception: {ex}"
            )
            continue

        # Candidate neighbors
        for j in indices_knn[i][1:]:  # skip itself
            B = cities.iloc[j]
            B_name = B["name"]
            B_lat = B.centroid.y
            B_lon = B.centroid.x

            # Skip if B is outside the local box
            if not (south < B_lat < north and west < B_lon < east):
                continue

            # Snap B
            try:
                B_node = ox.nearest_nodes(G2, B_lon, B_lat)
            except Exception:
                continue

            # Shortest path test
            try:
                nx.shortest_path_length(G2, A_node, B_node, weight="length")
                edges_out.append((A_name, B_name))
            except nx.NetworkXNoPath:
                pass

    # --- 7. Build adjacency DataFrame ---
    adj = pd.DataFrame(edges_out, columns=["city_a", "city_b"])
    adj = adj.drop_duplicates()

    # --- 8. Add state information to adj
    # left side: city_a
    adj = (
        adj.merge(
            cities[["name", "state_name"]],
            left_on="city_a",
            right_on="name",
            how="left",
        )
        .rename(columns={"state_name": "state_a"})
        .drop(columns=["name"])
    )

    # right side: city_b
    adj = (
        adj.merge(
            cities[["name", "state_name"]],
            left_on="city_b",
            right_on="name",
            how="left",
        )
        .rename(columns={"state_name": "state_b"})
        .drop(columns=["name"])
    )

    # --- 9. Enforce canonical ordering
    adj["city_min"] = adj[["city_a", "city_b"]].min(axis=1)
    adj["city_max"] = adj[["city_a", "city_b"]].max(axis=1)
    adj = adj[["city_min", "city_max"]].drop_duplicates()
    adj = adj.rename(columns={"city_min": "city_a", "city_max": "city_b"})

    # --- 10. Save generated adjacency dataset
    all_us_cities_adjacency_pairs_parquet = (
        Path(OSM_CITIES_DATA_FOLDER) / ALL_US_CITIES_ADJACENCY_PAIRS_PARQUET
    )

    adj.to_parquet(all_us_cities_adjacency_pairs_parquet)

    all_us_cities_adjacency_pairs_csv = (
        Path(OSM_CITIES_DATA_FOLDER) / ALL_US_CITIES_ADJACENCY_PAIRS_CSV
    )

    adj.to_csv(all_us_cities_adjacency_pairs_csv)

    return adj


if __name__ == "__main__":
    all_us_city_centroids_projected_parquet = (
        Path(OSM_CITIES_DATA_FOLDER) / ALL_US_CITIES_CENTRIODS_PROJECTED_PARQUET
    )
    all_us_city_centroids_projected_gdf = gpd.read_parquet(
        all_us_city_centroids_projected_parquet
    )

    all_us_cities_adjacency_pairs_df = get_all_city_undirected_adjacency(
        all_us_city_centroids_projected_gdf
    )

    all_us_cities_adjacency_pairs_parquet = (
        Path(OSM_CITIES_DATA_FOLDER) / ALL_US_CITIES_ADJACENCY_PAIRS_PARQUET
    )

    all_us_cities_adjacency_pairs_df.to_parquet(all_us_cities_adjacency_pairs_parquet)
