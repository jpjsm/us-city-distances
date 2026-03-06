# ---------------------------------------------
# List of all U.S. states and territories
# ---------------------------------------------
US_REGIONS = [
    # States
    "Alabama, USA",
    "Alaska, USA",
    "Arizona, USA",
    "Arkansas, USA",
    "California, USA",
    "Colorado, USA",
    "Connecticut, USA",
    "Delaware, USA",
    "Florida, USA",
    "Georgia, USA",
    "Hawaii, USA",
    "Idaho, USA",
    "Illinois, USA",
    "Indiana, USA",
    "Iowa, USA",
    "Kansas, USA",
    "Kentucky, USA",
    "Louisiana, USA",
    "Maine, USA",
    "Maryland, USA",
    "Massachusetts, USA",
    "Michigan, USA",
    "Minnesota, USA",
    "Mississippi, USA",
    "Missouri, USA",
    "Montana, USA",
    "Nebraska, USA",
    "Nevada, USA",
    "New Hampshire, USA",
    "New Jersey, USA",
    "New Mexico, USA",
    "New York, USA",
    "North Carolina, USA",
    "North Dakota, USA",
    "Ohio, USA",
    "Oklahoma, USA",
    "Oregon, USA",
    "Pennsylvania, USA",
    "Rhode Island, USA",
    "South Carolina, USA",
    "South Dakota, USA",
    "Tennessee, USA",
    "Texas, USA",
    "Utah, USA",
    "Vermont, USA",
    "Virginia, USA",
    "Washington, USA",
    "West Virginia, USA",
    "Wisconsin, USA",
    "Wyoming, USA",
    # Territories
    "District of Columbia, USA",
    "Puerto Rico, USA",
    "Guam, USA",
    "American Samoa, USA",
    "U.S. Virgin Islands, USA",
    "Northern Mariana Islands, USA",
]

# ---------------------------------------------
# OSM tags
# ---------------------------------------------

CITY_EQUIVALENT_TAGS = {
    "place": [
        "city",
        "town",
        "village",
        # "borough",
        # "suburb",
        # "county",
        # "district",
        # "subdistrict",
        # "municipality",
    ]
}

# ---------------------------------------------
# OSM cache files
# ---------------------------------------------

# Raw data
ALL_US_CITIES_BY_PLACE_RAW_PARQUET = "all_us_cities_by_place_raw.parquet"
US_STATE_CITIES_BY_PLACE_RAW_PARQUET_TEMPLATE = "us_{0}_cities_by_place_raw.parquet"

# Processed

ALL_US_CITIES_CENTRIODS_PROJECTED_PARQUET = "all_us_city_centroids_projected.parquet"
ALL_US_CITIES_ADJACENCY_PAIRS_PARQUET = "all_us_city_adjacency_pairs.parquet"
ALL_US_CITIES_ADJACENCY_PAIRS_CSV = "all_us_city_adjacency_pairs.csv"
