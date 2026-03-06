from pathlib import Path
import pickle

from config import OSM_DATA_FOLDER, CENSUS_DATA_FOLDER, RUNNING_STATE_FOLDER
from osm_constants import US_REGIONS, COUNTY_TAGS, CITY_TAGS

import osmnx as ox
import geopandas as gpd
import pandas as pd

if __name__ == "__main__":
    extended_regions = [
        "Jefferson, Alabama, USA",
        "Mobile, Alabama, USA",
        "Madison, Alabama, USA",
        "Tuscaloosa,Alabama, USA",
    ]

    for region in extended_regions:
        county_name, state_name, country = region.split(", ")
        print(region)
        try:
            county = ox.features_from_place(
                region, tags={"admin_level": "6", "boundary": "administrative"}
            )
            print(county)

            county = county[["name", "geometry"]].rename(columns={"name": "county"})
            try:
                gdf = ox.features_from_polygon(geometry, tags=CITY_TAGS)
            except Exception as e:
                print(f"    Failed for county {county_name}: {e}")
                continue

        except Exception as e:
            print(f"Failed to fetch cities for for {region}: {e}")
            continue
