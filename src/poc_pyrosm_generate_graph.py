from datetime import datetime
from pathlib import Path
import pickle
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
)
from config import OSM_CITIES_DATA_FOLDER, RUNNING_STATE_FOLDER

from geofabrik_constants import OSM_PBF_US_PATH

# ---------------------------------------------
# Local constants
# ---------------------------------------------
PYTHON_FILENAME = Path(__file__).name


def get_driving_graph_north_america():
    print(
        f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_north_america] started"
    )

    # --------------------------------------------------------------------------
    # check G in cache
    # --------------------------------------------------------------------------
    #
    G_pickle_path = Path(RUNNING_STATE_FOLDER) / "get_driving_graph_north_america.G.pkl"

    if G_pickle_path.exists():
        with open(G_pickle_path, "rb") as G_pickle:
            G = pickle.load(G_pickle)
        print(
            f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_north_america] 'G' loaded from cache"
        )
        return G

    # --------------------------------------------------------------------------
    # osm = OSM(str(OSM_PBF_US_PATH))
    # --------------------------------------------------------------------------
    #
    osm_pickle_path = (
        Path(RUNNING_STATE_FOLDER) / "get_driving_graph_north_america.osm.pkl"
    )

    if osm_pickle_path.exists():
        with open(osm_pickle_path, "rb") as osm_pickle:
            osm = pickle.load(osm_pickle)
        print(
            f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_north_america] 'osm' loaded from cache"
        )
    else:
        print(
            f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_north_america] 'osm' load from PBF started"
        )
        osm = OSM(str(OSM_PBF_US_PATH))
        print(
            f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_north_america] 'osm' load from PBF finished"
        )
        with open(osm_pickle_path, "wb") as osm_pickle:
            pickle.dump(osm, osm_pickle)

    # --------------------------------------------------------------------------
    # nodes, edges = osm.get_network(network_type="driving", nodes=True)
    # --------------------------------------------------------------------------
    #
    nodes_edges_pickle_path = (
        Path(RUNNING_STATE_FOLDER) / "get_driving_graph_north_america.nodes_edges.pkl"
    )
    if nodes_edges_pickle_path.exists():
        with open(nodes_edges_pickle_path, "rb") as node_edges_pickle:
            nodes, edges = pickle.load(node_edges_pickle)
        print(
            f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_north_america] 'nodes, edges' loaded from cache"
        )
    else:
        print(
            f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_north_america] generating 'nodes, edges' from osm"
        )
        nodes, edges = osm.get_network(network_type="driving", nodes=True)
        print(
            f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_north_america] 'nodes, edges' generated from osm"
        )
        with open(nodes_edges_pickle_path, "wb") as node_edges_pickle:
            pickle.dump((nodes, edges), node_edges_pickle)

    # --------------------------------------------------------------------------
    # nodes, edges = osm.get_network(network_type="driving", nodes=True)
    # --------------------------------------------------------------------------
    #
    print(
        f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_north_america] generating 'G' from osm"
    )
    G = osm.to_graph(nodes, edges, graph_type="networkx")
    print(
        f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_north_america] 'G' generated from osm"
    )
    with open(G_pickle_path, "wb") as G_pickle:
        pickle.dump(G, G_pickle)

    return G


if __name__ == "__main__":
    driving_graph_north_america = get_driving_graph_north_america()

    all_us_city_centroids_projected_parquet = (
        Path(OSM_CITIES_DATA_FOLDER) / ALL_US_CITIES_CENTRIODS_PROJECTED_PARQUET
    )
    all_us_city_centroids_projected_gdf = gpd.read_parquet(
        all_us_city_centroids_projected_parquet
    )
