from pathlib import Path
import osmnx as ox
import geopandas as gpd
import pandas as pd

from archive.poc_get_state_counties_with_geometry import get_us_counties

from osm_constants import (
    CITY_FILTER,
    US_ALL_CITY_NAMES_GEOM_PARQUET,
    US_STATE_COUNTY_CITIES_GEOM_PARQUET_TEMPLATE,
)
from config import OSM_COUNTIES_DATA_FOLDER

# ---------------------------------------------
# Local constants
# ---------------------------------------------
PYTHON_FILENAME = Path(__file__).name

# ---------------------------------------------
# OSM config for large states
# ---------------------------------------------
ox.settings.max_query_area_size = 1_000_000_000_000  # 1e12


def get_us_cities(refresh: bool = False):
    print(f"🚫🐛[{PYTHON_FILENAME}.get_us_cities] started")
    us_all_cities_parquet = (
        Path(OSM_COUNTIES_DATA_FOLDER) / US_ALL_CITY_NAMES_GEOM_PARQUET
    )
    cache_exists = us_all_cities_parquet.exists()

    if not refresh and cache_exists:
        us_counties_gdf = gpd.read_parquet(us_all_cities_parquet)
        print(f"🚫🐛[{PYTHON_FILENAME}.get_us_cities] results from cache")
        print(f"🚫🐛[{PYTHON_FILENAME}.get_us_cities] finished")
        return us_counties_gdf

    us_all_counties_gdf = get_us_counties()
    cols_to_keep = [
        "name",
        "name:en",
        "wikidata",
        "osmid",
        "state_fips",
        "county_fips",
        "geometry",
    ]
    frames = []
    # cities by county
    for _, county_row in us_all_counties_gdf.iterrows():
        county_geom = county_row.geometry
        cities_gdf = gpd.GeoDataFrame(
            columns=["state_name", "county_name"] + cols_to_keep, geometry="geometry"
        )
        try:
            cities_gdf = ox.features_from_polygon(county_geom, CITY_FILTER)
            cities_gdf = cities_gdf[
                [
                    col_name
                    for col_name in cols_to_keep
                    if col_name in cities_gdf.columns
                ]
            ]
            cities_gdf["state_name"] = county_row["state_name"]
            cities_gdf["county_name"] = county_row["county_name"]
            cities_gdf = cities_gdf.reset_index(drop=True)
        except Exception:
            cities_gdf["state_name"] = county_row["state_name"]
            cities_gdf["county_name"] = county_row["county_name"]

        frames.append(cities_gdf)

    for state_query in US_REGIONS:
        state_name = state_query.split(",")[0].strip().lower().replace(" ", "_")
        print(
            f"🚫🐛[{PYTHON_FILENAME}.get_us_cities] processing counties for {state_name}"
        )

        state_counties_parquet = Path(OSM_COUNTIES_DATA_FOLDER) / str.format(
            US_STATE_COUNTIES_PARQUET_GEOM_TEMPLATE, state_name
        )

        # check is state cache exists and not refresh
        cache_exists = state_counties_parquet.exists()

        if not refresh and cache_exists:
            state_counties_gdf = gpd.read_parquet(state_counties_parquet)
            print(
                f"🚫🐛[{PYTHON_FILENAME}.get_us_cities] {state_name} State: county results from cache"
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

            # Fixing error:
            # On retrieving counties using OSMnx, while trying to save a gdf to
            # parquet, I got his error:

            # pyarrow.lib.ArrowInvalid: ("Could not convert 'Bazetta Township'
            # with type str: tried to convert to int64", 'Conversion failed for
            # column id with type object')
            state_counties_gdf = state_counties_gdf.reset_index(drop=True)

            state_counties_gdf.to_parquet(state_counties_parquet)
            print(
                f"🚫🐛[{PYTHON_FILENAME}.get_us_cities] {state_name} State: county results from OSM"
            )

        frames.append(state_counties_gdf)

    us_counties_gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True))
    us_counties_gdf.to_parquet(us_all_cities_parquet)

    print(f"🚫🐛[{PYTHON_FILENAME}.get_us_cities] results from OSM data")
    print(f"🚫🐛[{PYTHON_FILENAME}.get_us_cities] finished")
    return us_counties_gdf


if __name__ == "__main__":
    us_all_counties_gdf = get_us_cities(refresh=True)

    gdf_state_county_count = us_all_counties_gdf.groupby("state_name").count()
    print(gdf_state_county_count)
    # for row in us_all_counties_gdf.itertuples():
    #     print(f"{row.state_name:40} {row.county_name}")
