from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime, timezone
from pathlib import Path

import osmnx as ox
import geopandas as gpd
import pandas as pd

from config import OSM_COUNTIES_DATA_FOLDER, LOG_FOLDER


# ---------------------------------------------
# OSM config for large states
# ---------------------------------------------
ox.settings.max_query_area_size = 1_000_000_000_000  # 1e12


def get_county_queries(
    csv_filename: str = "data/census/Counties_by_State_Code.csv",
) -> list:
    with open(csv_filename, "r", encoding="utf-8") as csv_file:
        county_by_state_code = pd.read_csv(csv_file)

    county_by_state_code["query"] = (
        county_by_state_code.County_Name.map(str)
        + ", "
        + county_by_state_code.State_Name
        + ", USA"
    )

    return county_by_state_code["query"].to_list()


def cities_in_county(county_query):
    """
    Given a county query like 'King, Washington, USA',
    return all OSM cities/towns inside that county with
    county and state labels attached.
    """

    # Split out county and state names
    county_name = county_query.split(",")[0].strip()
    state_name = county_query.split(",")[1].strip()

    # 1. Fetch the county polygon
    county_tags = {"admin_level": "6", "boundary": "administrative"}
    county_gdf = ox.features_from_place(county_query, tags=county_tags)

    if county_gdf.empty:
        raise ValueError(f"No county boundary found for: {county_query}")

    county_poly = county_gdf.geometry.iloc[0]

    # 2. Fetch cities/towns inside the county polygon
    city_tags = {"place": ["city", "town"]}
    cities = ox.features_from_polygon(county_poly, tags=city_tags)

    if cities.empty:
        # Return empty GeoDataFrame with expected columns
        return gpd.GeoDataFrame(
            columns=["name", "place", "county", "state", "geometry"],
            geometry="geometry",
            crs="EPSG:4326",
        )

    # 3. Attach county + state labels
    cities["county"] = county_name
    cities["state"] = state_name

    # Keep only the useful columns
    keep = ["name", "place", "county", "state", "geometry"]
    cities = cities[keep]

    return cities


def save_county_cities(county_query, osm_folder: str = OSM_COUNTIES_DATA_FOLDER):
    """
    Runs your cities_in_county() function and writes the result to disk.
    Always returns None.
    """
    gdf = cities_in_county(county_query)

    # Split out county and state names
    county_name = county_query.split(",")[0].strip().replace(" ", "_")
    state_name = county_query.split(",")[1].strip().replace(" ", "_")

    # Unique filename per county
    parquet_filename = str(
        Path(osm_folder) / f"{state_name}-{county_name}-cities.parquet"
    )

    gdf.to_parquet(parquet_filename)

    return None


def run_all_counties(
    county_queries,
    max_workers=75,
    osm_counties_folder_name: str = OSM_COUNTIES_DATA_FOLDER,
    log_folder_name: str = LOG_FOLDER,
):
    osm_counties_folder = Path(osm_counties_folder_name)
    osm_counties_folder.mkdir(exist_ok=True, parents=True)

    log_folder = Path(log_folder_name)
    log_folder.mkdir(parents=True, exist_ok=True)
    log_file_name = (
        f"run_all_counties.{datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")}.log"
    )
    log_file = log_folder / log_file_name
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(save_county_cities, q): q for q in county_queries}

        for future in as_completed(futures):
            q = futures[future]
            try:
                future.result()
            except Exception as e:
                err_msg = f"Error processing {q}: {e}"
                print(err_msg)
                with open(log_file, "a+", encoding="utf-8") as log_outfile:
                    log_outfile.write(err_msg + "\n")


if __name__ == "__main__":
    county_queries = get_county_queries()
    run_all_counties(county_queries, max_workers=100)
