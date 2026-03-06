from math import isnan
from pathlib import Path
import osmnx as ox
import geopandas as gpd
import pandas as pd

from osm_constants import (
    US_REGIONS,
    CITY_EQUIVALENT_TAGS,
    ALL_US_CITIES_BY_PLACE_RAW_PARQUET,
    US_STATE_CITIES_BY_PLACE_RAW_PARQUET_TEMPLATE,
    ALL_US_CITIES_CENTRIODS_PROJECTED_PARQUET,
)
from config import OSM_RAW_DATA_FOLDER, OSM_CITIES_DATA_FOLDER

# ---------------------------------------------
# Local constants
# ---------------------------------------------
PYTHON_FILENAME = Path(__file__).name

# ---------------------------------------------
# OSM config for large states
# ---------------------------------------------
ox.settings.max_query_area_size = 1_000_000_000_000  # 1e12


def get_us_cities_raw(refresh: bool = False):
    print(f"🚫🐛[{PYTHON_FILENAME}.get_us_cities_raw] started")
    all_us_cities_raw_parquet = (
        Path(OSM_RAW_DATA_FOLDER) / ALL_US_CITIES_BY_PLACE_RAW_PARQUET
    )
    cache_exists = all_us_cities_raw_parquet.exists()

    if not refresh and cache_exists:
        us_all_cities_gdf = gpd.read_parquet(all_us_cities_raw_parquet)
        print(f"🚫🐛[{PYTHON_FILENAME}.get_us_cities_raw] results from cache")
        print(f"🚫🐛[{PYTHON_FILENAME}.get_us_cities_raw] finished")
        return us_all_cities_gdf

    frames = []
    # Cities by State
    for state_query in US_REGIONS:
        state_name = state_query.split(",")[0].strip()
        country_name = state_query.split(",")[1].strip()
        state_name_normalized = state_name.lower().replace(" ", "_")
        print(
            f"🚫🐛[{PYTHON_FILENAME}.get_us_cities_raw] processing cities for {state_name_normalized}"
        )

        state_cities_parquet = Path(OSM_RAW_DATA_FOLDER) / str.format(
            US_STATE_CITIES_BY_PLACE_RAW_PARQUET_TEMPLATE, state_name_normalized
        )

        # check is state cache exists and not refresh
        cache_exists = state_cities_parquet.exists()

        if not refresh and cache_exists:
            state_cities_gdf = gpd.read_parquet(state_cities_parquet)
            print(
                f"🚫🐛[{PYTHON_FILENAME}.get_us_cities_raw] {state_name_normalized} State: cities results from cache"
            )
        else:
            ox_query = {"country": country_name, "state": state_name}
            state_cities_gdf = ox.features_from_place(
                ox_query, tags=CITY_EQUIVALENT_TAGS
            )
            state_cities_gdf["state_name"] = state_name
            state_cities_gdf["state_name_normalized"] = state_name_normalized
            # Fixing error:
            # On retrieving counties using OSMnx, while trying to save a gdf to
            # parquet, I got his error:

            # pyarrow.lib.ArrowInvalid: ("Could not convert 'Bazetta Township'
            # with type str: tried to convert to int64", 'Conversion failed for
            # column id with type object')
            state_cities_gdf = state_cities_gdf.reset_index(drop=True)

            state_cities_gdf.to_parquet(state_cities_parquet)
            print(
                f"🚫🐛[{PYTHON_FILENAME}.get_us_cities_raw] {state_name_normalized} State: {len(state_cities_gdf)} cities results from OSM"
            )

        frames.append(state_cities_gdf)

    us_all_cities_gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True))
    us_all_cities_gdf.to_parquet(all_us_cities_raw_parquet)

    print(f"🚫🐛[{PYTHON_FILENAME}.get_us_cities_raw] results from OSM data")
    print(f"🚫🐛[{PYTHON_FILENAME}.get_us_cities_raw] finished")
    return us_all_cities_gdf


def get_all_us_city_centroids_projected(all_us_cities_raw_gdf):
    interesting_columns = [
        "geometry",
        "state_name",
        "name",
        "place",
        "population:normalized",
        "wikidata",
    ]

    all_us_city_centroids_projected_gdf = all_us_cities_raw_gdf[
        all_us_cities_raw_gdf["name"].notna()
    ]
    all_us_city_centroids_projected_gdf["population:normalized"] = (
        all_us_city_centroids_projected_gdf["population"]
        .apply(
            lambda value: (
                pd.NA
                if pd.isna(value) or not str(value).replace(".", "", 1).isdigit()
                else int(float(value))
            )
        )
        .astype("Int64")
    )

    all_us_city_centroids_projected_gdf = all_us_city_centroids_projected_gdf[
        all_us_city_centroids_projected_gdf["population:normalized"].notna()
    ]
    all_us_city_centroids_projected_gdf = all_us_city_centroids_projected_gdf[
        interesting_columns
    ]
    all_us_city_centroids_projected_gdf.reset_index(drop=True)
    all_us_city_centroids_projected_gdf = all_us_city_centroids_projected_gdf.to_crs(
        5070
    )
    all_us_city_centroids_projected_gdf = all_us_city_centroids_projected_gdf.to_crs(
        4326
    )

    all_us_city_centroids_projected_parquet = (
        Path(OSM_CITIES_DATA_FOLDER) / ALL_US_CITIES_CENTRIODS_PROJECTED_PARQUET
    )

    all_us_city_centroids_projected_gdf.to_parquet(
        all_us_city_centroids_projected_parquet
    )

    return all_us_city_centroids_projected_gdf


if __name__ == "__main__":
    all_us_cities_raw_gdf = get_us_cities_raw(refresh=False)
    all_us_city_centroids_projected_gdf = get_all_us_city_centroids_projected(
        all_us_cities_raw_gdf
    )

    print(f"Total interesting data rows: {len(all_us_city_centroids_projected_gdf)}")
    print(all_us_city_centroids_projected_gdf.head())
    print(all_us_city_centroids_projected_gdf.centroid.head())
