from math import cos, radians
from pathlib import Path
import osmnx as ox
import geopandas as gpd
import pandas as pd

from osm_constants import (
    US_REGIONS,
    PLACE_VALUE_TAGS,
    ALL_US_CITIES_BY_PLACE_RAW_PARQUET,
    US_STATE_CITIES_BY_PLACE_RAW_PARQUET_TEMPLATE,
    ALL_US_CITIES_CENTRIODS_PROJECTED_PARQUET,
)
from geofabrik_constants import OSM_PBF_US_PATH
from config import (
    OSM_RAW_DATA_FOLDER,
    OSM_CITIES_DATA_FOLDER,
    GEOFABRIK_DERIVED_FOLDER,
    OSM_DERIVED_FOLDER,
)

# ---------------------------------------------
# Local constants
# ---------------------------------------------
PYTHON_FILENAME = Path(__file__).name


# ---------------------------------------------
# OSM config for large states
# ---------------------------------------------
ox.settings.max_query_area_size = 1_000_000_000_000  # 1e12

if __name__ == "__main__":
    print(f"🚫🐛[{PYTHON_FILENAME}.__main__] started")
    all_us_cities_raw_parquet = (
        Path(OSM_RAW_DATA_FOLDER) / ALL_US_CITIES_BY_PLACE_RAW_PARQUET
    )
    cache_exists = all_us_cities_raw_parquet.exists()

    if not cache_exists:
        print(
            f"🚫🐛[{PYTHON_FILENAME}.__main__] WARNING: must run `osm_us_cities.py` before to work with 'all_us_cities_raw_parquet'"
        )
        print(f"🚫🐛[{PYTHON_FILENAME}.__main__] finished")
        exit(1)

    all_US_cities_raw_gdf = gpd.read_parquet(all_us_cities_raw_parquet)

    na_counts = all_US_cities_raw_gdf.isna().sum()
    na_percent = (na_counts / len(all_US_cities_raw_gdf)) * 100
    all_dtypes = all_US_cities_raw_gdf.dtypes
    summary_df = pd.DataFrame(
        {"dtype": all_dtypes, "na_count": na_counts, "na_percent": na_percent.round(2)}
    )

    usless_columns = set()
    for inx, row in summary_df.iterrows():
        if row["na_percent"] >= 50:
            usless_columns.add(row.name)
            continue
        print(
            f"{str(row.name):40s} {str(row["dtype"]):16s}, NA pct= {row["na_percent"]:6.2f}%, NA count {row["na_count"]:18,}"
        )

    print("*" * 40)
    name_na_df = all_US_cities_raw_gdf[all_US_cities_raw_gdf["name"].isna()]
    name_na_df = name_na_df.dropna(axis=1, how="all")
    name_na_no_geom_df = name_na_df.drop(columns=["geometry"])
    name_na_no_geom_df.to_csv("foo.csv", index=False)
    exit()
    print(all_US_cities_raw_gdf.head())
    print(all_US_cities_raw_gdf.active_geometry_name)
    print(all_US_cities_raw_gdf.attrs)
    print(all_US_cities_raw_gdf.crs)
    print(all_US_cities_raw_gdf.index)

    for column_name in sorted(all_US_cities_raw_gdf.columns):
        if (
            column_name.startswith("name:")
            or column_name.startswith("name_")
            or column_name.startswith("alt")
            or column_name.startswith("old_name")
            or column_name.startswith("contact")
            or column_name.startswith("app:")
            or column_name.startswith("email")
            or column_name.startswith("facebook")
            or column_name.startswith("fax")
        ):
            continue
        if column_name.startswith("alt"):
            print(column_name)
            continue
        print(column_name)
