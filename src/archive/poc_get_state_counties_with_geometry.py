from math import isnan
from pathlib import Path
import osmnx as ox
import geopandas as gpd
import pandas as pd

from osm_constants import (
    US_REGIONS,
    COUNTY_TAGS,
    US_ALL_COUNTY_NAMES_GEOM_PARQUET,
    US_STATE_COUNTIES_PARQUET_GEOM_TEMPLATE,
)
from wikidata_constants import US_COUNTY_CLASSES
from config import OSM_COUNTIES_DATA_FOLDER

# ---------------------------------------------
# Local constants
# ---------------------------------------------
PYTHON_FILENAME = Path(__file__).name

# ---------------------------------------------
# OSM config for large states
# ---------------------------------------------
ox.settings.max_query_area_size = 1_000_000_000_000  # 1e12


def is_us_county(gdf_row) -> bool:
    wikidata_raw_id = gdf_row["wikidata"]
    if isinstance(wikidata_raw_id, str):
        wikidata_ids = wikidata_raw_id.split(";")
        return any(id_ in US_COUNTY_CLASSES for id_ in wikidata_ids)

    if isinstance(wikidata_raw_id, list) and all(
        isinstance(item, str) for item in wikidata_raw_id
    ):
        return any(item in US_COUNTY_CLASSES for item in wikidata_raw_id)
    return False


def get_us_counties(refresh: bool = False):
    print(f"🚫🐛[{PYTHON_FILENAME}.get_us_counties] started")
    us_all_counties_parquet = (
        Path(OSM_COUNTIES_DATA_FOLDER) / US_ALL_COUNTY_NAMES_GEOM_PARQUET
    )
    cache_exists = us_all_counties_parquet.exists()

    if not refresh and cache_exists:
        us_counties_gdf = gpd.read_parquet(us_all_counties_parquet)
        print(f"🚫🐛[{PYTHON_FILENAME}.get_us_counties] results from cache")
        print(f"🚫🐛[{PYTHON_FILENAME}.get_us_counties] finished")
        return us_counties_gdf

    frames = []
    # Counties by State
    for state_query in US_REGIONS:
        state_name = state_query.split(",")[0].strip().lower().replace(" ", "_")
        print(
            f"🚫🐛[{PYTHON_FILENAME}.get_us_counties] processing counties for {state_name}"
        )

        state_counties_parquet = Path(OSM_COUNTIES_DATA_FOLDER) / str.format(
            US_STATE_COUNTIES_PARQUET_GEOM_TEMPLATE, state_name
        )

        # check is state cache exists and not refresh
        cache_exists = state_counties_parquet.exists()

        if not refresh and cache_exists:
            state_counties_gdf = gpd.read_parquet(state_counties_parquet)
            print(
                f"🚫🐛[{PYTHON_FILENAME}.get_us_counties] {state_name} State: county results from cache"
            )
        else:
            state_counties_gdf = ox.features_from_place(state_query, tags=COUNTY_TAGS)
            geom = state_counties_gdf.geometry.name
            keep = ["name", "name:en", "wikidata", "osmid", geom]
            state_counties_gdf = state_counties_gdf[
                [c for c in keep if c in state_counties_gdf.columns]
            ]

            state_counties_gdf["county_name"] = state_counties_gdf["name"]
            state_counties_gdf["state_name"] = state_name

            state_counties_gdf = state_counties_gdf[
                state_counties_gdf.apply(is_us_county, axis=1)
            ]

            # Fixing error:
            # On retrieving counties using OSMnx, while trying to save a gdf to
            # parquet, I got his error:

            # pyarrow.lib.ArrowInvalid: ("Could not convert 'Bazetta Township'
            # with type str: tried to convert to int64", 'Conversion failed for
            # column id with type object')
            state_counties_gdf = state_counties_gdf.reset_index(drop=True)

            state_counties_gdf.to_parquet(state_counties_parquet)
            print(
                f"🚫🐛[{PYTHON_FILENAME}.get_us_counties] {state_name} State: county results from OSM"
            )

        frames.append(state_counties_gdf)

    us_counties_gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True))
    us_counties_gdf.to_parquet(us_all_counties_parquet)

    print(f"🚫🐛[{PYTHON_FILENAME}.get_us_counties] results from OSM data")
    print(f"🚫🐛[{PYTHON_FILENAME}.get_us_counties] finished")
    return us_counties_gdf


if __name__ == "__main__":
    us_all_counties_gdf = get_us_counties(refresh=True)

    gdf_state_county_count = us_all_counties_gdf.groupby("state_name").count()
    print(gdf_state_county_count)
    # for row in us_all_counties_gdf.itertuples():
    #     print(f"{row.state_name:40} {row.county_name}")
