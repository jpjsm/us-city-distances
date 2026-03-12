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
from config import GEOFABRIK_DERIVED_FOLDER, RUNNING_STATE_FOLDER

from geofabrik_constants import OSM_PBF_US_PATH

# ---------------------------------------------
# Local constants
# ---------------------------------------------
PYTHON_FILENAME = Path(__file__).name


def get_driving_graph_from_pbf(pbf_path, label="<state>-<city>"):
    print(
        f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_from_pbf({pbf_path}, {label})] started"
    )

    # --------------------------------------------------------------------------
    # check G in cache
    # --------------------------------------------------------------------------
    #
    G_pickle_path = (
        Path(RUNNING_STATE_FOLDER) / f"get_driving_graph_from_pbf.{label}.pkl"
    )

    if G_pickle_path.exists():
        with open(G_pickle_path, "rb") as G_pickle:
            G = pickle.load(G_pickle)
        print(
            f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_from_pbf({pbf_path}, {label})] 'G' loaded from cache"
        )
        return G

    # --------------------------------------------------------------------------
    # osm = OSM(str(pbf_path))
    # --------------------------------------------------------------------------
    #
    osm = OSM(str(pbf_path))

    # --------------------------------------------------------------------------
    # nodes, edges = osm.get_network(network_type="driving", nodes=True)
    # --------------------------------------------------------------------------
    #
    nodes_edges_pickle_path = (
        Path(RUNNING_STATE_FOLDER)
        / "get_driving_graph_from_pbf.nodes_edges.{label}.pkl"
    )
    if nodes_edges_pickle_path.exists():
        with open(nodes_edges_pickle_path, "rb") as node_edges_pickle:
            nodes, edges = pickle.load(node_edges_pickle)
        print(
            f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_from_pbf({pbf_path}, {label})] 'nodes, edges' loaded from cache"
        )
    else:
        print(
            f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_from_pbf({pbf_path}, {label})] generating 'nodes, edges' from pbf: {pbf_path}"
        )
        nodes, edges = osm.get_network(network_type="driving", nodes=True)
        print(
            f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_from_pbf({pbf_path}, {label})] 'nodes, edges' generated from pbf: {pbf_path}"
        )
        with open(nodes_edges_pickle_path, "wb") as node_edges_pickle:
            pickle.dump((nodes, edges), node_edges_pickle)

    # --------------------------------------------------------------------------
    # nodes, edges = osm.get_network(network_type="driving", nodes=True)
    # --------------------------------------------------------------------------
    #
    print(
        f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_from_pbf({pbf_path}, {label})] generating 'G' from osm"
    )
    G = osm.to_graph(nodes, edges, graph_type="networkx")
    print(
        f"«{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}» 🚫🐛 [{PYTHON_FILENAME}.get_driving_graph_from_pbf({pbf_path}, {label})] 'G' generated from osm"
    )
    with open(G_pickle_path, "wb") as G_pickle:
        pickle.dump(G, G_pickle)

    return (nodes, edges, G)


if __name__ == "__main__":
    osm_pbf_files = [
        f
        for f in Path(GEOFABRIK_DERIVED_FOLDER).iterdir()
        if f.is_file() and f.suffix == ".pbf"
    ]
    for osm_pbf in osm_pbf_files:
        source, state_place, _ = osm_pbf.name.split(".")
        suffixes = osm_pbf.suffixes
        nodes, edges, G = get_driving_graph_from_pbf(osm_pbf, state_place)
        print(nodes)
        print(edges)
        print(G)
