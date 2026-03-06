from pathlib import Path
import pickle

from config import OSM_DATA_FOLDER, CENSUS_DATA_FOLDER, RUNNING_STATE_FOLDER
from osm_constants import US_REGIONS, COUNTY_TAGS, CITY_TAGS

import osmnx as ox
import geopandas as gpd
import pandas as pd


# ---------------------------------------------
# 2.2 OSM config for large states
# ---------------------------------------------
ox.settings.max_query_area_size = 1_000_000_000_000  # 1e12


def get_OSM_US_cities(
    region: str,
    osm_data_folder: str = OSM_DATA_FOLDER,
    census_data_folder: str = CENSUS_DATA_FOLDER,
) -> bool:
    # ---------------------------------------------
    # 3. Loop: state → counties → cities
    # ---------------------------------------------
    all_city_rows = []

    state_name = region.split(",")[0]

    print(f"\n=== Processing {state_name} ===")

    # Fetch counties for this state/territory
    try:
        counties = ox.features_from_place(region, tags=COUNTY_TAGS)
    except Exception as e:
        print(f"Failed to fetch counties for {state_name}: {e}")
        return False

    # Keep only name + geometry
    counties = counties[["name", "geometry"]].rename(columns={"name": "county"})

    # Loop through counties
    for idx, row in counties.iterrows():
        county_name = row["county"]
        geom = row["geometry"]

        # print(f"  → County: {county_name}")

        try:
            gdf = ox.features_from_polygon(geom, tags=CITY_TAGS)
        except Exception as e:
            # print(f"    Failed for county {county_name}: {e}")
            continue

        if len(gdf) == 0:
            print(f"{state_name:36}, {county_name:36} : no cities in county")
            continue

        gdf["county"] = county_name
        gdf["state"] = state_name

        all_city_rows.append(gdf)
        print(
            f"{state_name:36}, {county_name:36} : {len(gdf)} {'cities' if len(gdf)>1 else 'city'} in county"
        )

    # ---------------------------------------------
    # 4. Combine all results
    # ---------------------------------------------
    if all_city_rows:
        cities = gpd.GeoDataFrame(pd.concat(all_city_rows, ignore_index=True))
    else:
        cities = gpd.GeoDataFrame(
            columns=["name", "place", "county", "state", "geometry"]
        )

    # ---------------------------------------------
    # 5. Clean up columns
    # ---------------------------------------------
    keep_cols = ["name", "place", "county", "state", "geometry"]
    cities = cities[keep_cols]

    print("\n====================================")
    print("Completed extraction.")
    print(f"Total cities/towns collected: {len(cities)}")
    print("====================================")

    # save to parquet
    parquet_filename = str(Path(osm_data_folder) / f"osm_{state_name}_cities.parquet")
    cities.to_parquet(parquet_filename)

    # save to GeoJSON
    geojson_filename = str(Path(osm_data_folder) / f"osm_{state_name}_cities.geojson")
    cities.to_file(geojson_filename, driver="GeoJSON")
    return True


if __name__ == "__main__":
    processed_states = set()
    processed_states_filename = Path(RUNNING_STATE_FOLDER) / "processed_states.pkl"
    if processed_states_filename.exists():
        with open(processed_states_filename, "rb") as processed_states_pickle:
            processed_states = pickle.load(processed_states_pickle)

    for region in US_REGIONS:
        if region in processed_states:
            continue
        state_processed_successfully = get_OSM_US_cities(region)
        if state_processed_successfully:
            processed_states.add(region)
            with open(processed_states_filename, "wb") as processed_states_pickle:
                # processed_states = pickle.load(processed_states_pickle)
                pickle.dump(processed_states, processed_states_pickle)
