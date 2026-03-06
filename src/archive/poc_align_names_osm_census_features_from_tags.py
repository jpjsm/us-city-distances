from pathlib import Path
import osmnx as ox
import geopandas as gpd
import pandas as pd

from osm_constants import (
    STATE_TAGS,
    COUNTY_TAGS,
    CITY_FILTER,
    US_COUNTY_NAME_PARQUET,
    US_STATE_NAME_PARQUET,
    US_ALL_COUNTY_NAME_PARQUET,
)
from config import OSM_DATA_FOLDER

# ---------------------------------------------
# Local constants
# ---------------------------------------------
PYTHON_FILENAME = Path(__file__).name

# ---------------------------------------------
# OSM config for large states
# ---------------------------------------------
ox.settings.max_query_area_size = 1_000_000_000_000  # 1e12


def get_us_counties_gdf(refresh: bool = False):
    print(f"🚫🐛[{PYTHON_FILENAME}.get_us_counties_gdf] started")
    us_counties_parquet = Path(OSM_DATA_FOLDER) / US_COUNTY_NAME_PARQUET
    cache_exists = us_counties_parquet.exists()

    if not refresh and cache_exists:
        us_counties_gdf = gpd.read_parquet(us_counties_parquet)
        print(f"🚫🐛[{PYTHON_FILENAME}.get_us_counties_gdf] results from cache")
        print(f"🚫🐛[{PYTHON_FILENAME}.get_us_counties_gdf] finished")
        return us_counties_gdf

    # Counties
    query = """
    [out:json][timeout:3600];
    relation
    ["boundary"="administrative"]
    ["admin_level"="6"];
    out geom;
    """

    all_counties = ox.features_from_place(query, COUNTY_TAGS)

    us_counties = all_counties[
        (all_counties["ISO3166-1"] == "US")
        | (all_counties["ISO3166-2"].str.startswith("US-"))
    ]

    # us_counties = us_counties[["name", "wikidata", "ISO3166-2", "geometry"]]
    us_counties.to_parquet(us_counties_parquet)


if __name__ == "__main__":
    us_counties_gdf = get_us_counties_gdf()
    print(us_counties_gdf.describe())
