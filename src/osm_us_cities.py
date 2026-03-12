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


def bbox_from_point(lat, lon, radius_km):
    delta_lat = radius_km / 111.32
    delta_lon = radius_km / (111.32 * cos(radians(lat)))

    min_lat = lat - delta_lat
    max_lat = lat + delta_lat
    min_lon = lon - delta_lon
    max_lon = lon + delta_lon

    return min_lon, min_lat, max_lon, max_lat


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
            state_cities_gdf = ox.features_from_place(ox_query, tags=PLACE_VALUE_TAGS)
            state_cities_gdf["state_name"] = state_name
            state_cities_gdf["state_name_normalized"] = state_name_normalized
            state_cities_gdf["city_name"] = state_cities_gdf["name"]
            state_cities_gdf["city_name_normalized"] = state_cities_gdf[
                "city_name"
            ].apply(
                lambda x: (
                    x.strip().lower().replace(" ", "_") if isinstance(x, str) else pd.NA
                )
            )
            state_cities_gdf["geometry:original"] = state_cities_gdf.geometry
            state_cities_gdf["geometry:original_type"] = state_cities_gdf.geom_type

            # Fixing error:
            # On retrieving counties using OSMnx, while trying to save a gdf to
            # parquet, I got his error:

            # pyarrow.lib.ArrowInvalid: ("Could not convert 'Bazetta Township'
            # with type str: tried to convert to int64", 'Conversion failed for
            # column id with type object')
            # state_cities_gdf = state_cities_gdf.reset_index(drop=True)

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
    print(f"🚫🐛[{PYTHON_FILENAME}.get_all_us_city_centroids_projected] started")
    interesting_columns = [
        "geometry",
        "geometry:original",
        "geometry:original_type",
        "gnis:feature_id",
        "state_name",
        "state_name_normalized",
        "city_name",
        "city_name_normalized",
        "place_type",
        "population:normalized",
        "wikidata",
    ]

    print(
        f"🚫🐛[{PYTHON_FILENAME}.get_all_us_city_centroids_projected] remove rows with no name"
    )
    all_us_city_centroids_projected_gdf = all_us_cities_raw_gdf[
        all_us_cities_raw_gdf["city_name_normalized"].notna()
    ]

    print(
        f"🚫🐛[{PYTHON_FILENAME}.get_all_us_city_centroids_projected] generate population as number"
    )
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

    print(
        f"🚫🐛[{PYTHON_FILENAME}.get_all_us_city_centroids_projected] remove rows where there's no population"
    )
    all_us_city_centroids_projected_gdf = all_us_city_centroids_projected_gdf[
        all_us_city_centroids_projected_gdf["population:normalized"].notna()
    ]

    print(
        f"🚫🐛[{PYTHON_FILENAME}.get_all_us_city_centroids_projected] generate place type"
    )
    all_us_city_centroids_projected_gdf[
        "place_type"
    ] = all_us_city_centroids_projected_gdf["population:normalized"].apply(
        lambda x: (
            "city"
            if x >= 50_000
            else "town" if x >= 10_000 else "village" if x >= 1_000 else "hamlet"
        )
    )

    print(
        f"🚫🐛[{PYTHON_FILENAME}.get_all_us_city_centroids_projected] drop unnecessary columns"
    )
    all_us_city_centroids_projected_gdf = all_us_city_centroids_projected_gdf[
        interesting_columns
    ]

    print(f"🚫🐛[{PYTHON_FILENAME}.get_all_us_city_centroids_projected] reset index")
    all_us_city_centroids_projected_gdf.reset_index(drop=True)

    print(
        f"🚫🐛[{PYTHON_FILENAME}.get_all_us_city_centroids_projected] reset coordinates to 4326"
    )
    all_us_city_centroids_projected_gdf = all_us_city_centroids_projected_gdf.to_crs(
        "EPSG:4326"
    )

    all_us_city_centroids_projected_gdf["centroid"] = (
        all_us_city_centroids_projected_gdf.geometry.centroid
    )
    all_us_city_centroids_projected_gdf["centroid:latitude"] = (
        all_us_city_centroids_projected_gdf.geometry.centroid.y
    )
    all_us_city_centroids_projected_gdf["centroid:longitude"] = (
        all_us_city_centroids_projected_gdf.geometry.centroid.x
    )

    print(
        f"🚫🐛[{PYTHON_FILENAME}.get_all_us_city_centroids_projected] save parquet file"
    )
    all_us_city_centroids_projected_parquet = (
        Path(OSM_CITIES_DATA_FOLDER) / ALL_US_CITIES_CENTRIODS_PROJECTED_PARQUET
    )

    all_us_city_centroids_projected_gdf.to_parquet(
        all_us_city_centroids_projected_parquet
    )

    print(f"🚫🐛[{PYTHON_FILENAME}.get_all_us_city_centroids_projected] finished")
    return all_us_city_centroids_projected_gdf


def generate_osmium_extract_commands_by_state_city(
    all_us_normalized_cities_and_towns,
    radius_km: int = 320,
    source_pbf_path=OSM_PBF_US_PATH,
):
    def generate_box_coordinates(row):
        min_lon, min_lat, max_lon, max_lat = bbox_from_point(
            row["centroid:latitude"], row["centroid:longitude"], radius_km
        )
        destination_pbf_path = (
            Path(GEOFABRIK_DERIVED_FOLDER)
            / f"us-260304.{row["state_name_normalized"]}-{row["city_name_normalized"]}.pbf"
        )
        return OSMIUM_COMMAND_TEMPLATE.format(
            min_lon=min_lon,
            min_lat=min_lat,
            max_lon=max_lon,
            max_lat=max_lat,
            destination_pbf=str(destination_pbf_path),
            source_pbf=str(source_pbf_path),
        )

    commands_df = pd.DataFrame(
        {
            "command": all_us_normalized_cities_and_towns.apply(
                generate_box_coordinates, axis=1
            ).astype(str)
        }
    )

    return commands_df


if __name__ == "__main__":
    all_us_places_raw_gdf = get_us_cities_raw(refresh=False)

    all_us_places_with_centroids_projected_gdf = get_all_us_city_centroids_projected(
        all_us_places_raw_gdf
    )

    all_us_normalized_cities_and_towns = all_us_places_with_centroids_projected_gdf[
        all_us_places_with_centroids_projected_gdf["place_type"].isin(["city", "town"])
    ]

    print(f"Total interesting data rows: {len(all_us_normalized_cities_and_towns)}")

    print(all_us_normalized_cities_and_towns.head())
    print(all_us_normalized_cities_and_towns.centroid.head())

    all_us_normalized_cities_and_towns.to_parquet(
        Path(OSM_CITIES_DATA_FOLDER) / "all_us_normalized_cities_and_towns.parquet"
    )

    osmium_commands_df = generate_osmium_extract_commands_by_state_city(
        all_us_normalized_cities_and_towns, radius_km=300
    )

    osmium_commands_df.to_parquet(Path(OSM_DERIVED_FOLDER) / "osmium_commands.parquet")

    print(osmium_commands_df["command"].to_list()[:10])
