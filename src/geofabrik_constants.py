from pathlib import Path
from config import GEOFABRIK_FOLDER

OSM_PBF_NORTH_AMERICA_FILENAME = "north-america-260304.osm.pbf"
OSM_PBF_AUSTRALIA_OCEANIA_FILENAME = "australia-oceania-260304.osm.pbf"
OSM_PBF_CENTRAL_AMERICA_FILENAME = "central-america-260304.osm.pbf"
OSM_PBF_AMERICAN_OCEANIA_FILENAME = "american-oceania-260304.osm.pbf"
OSM_PBF_US_FILENAME = "us-260304.osm.pbf"

OSM_PBF_NORTH_AMERICA_PATH = Path(GEOFABRIK_FOLDER) / OSM_PBF_NORTH_AMERICA_FILENAME
OSM_PBF_AUSTRALIA_OCEANIA_PATH = (
    Path(GEOFABRIK_FOLDER) / OSM_PBF_AUSTRALIA_OCEANIA_FILENAME
)
OSM_PBF_CENTRAL_AMERICA_PATH = Path(GEOFABRIK_FOLDER) / OSM_PBF_CENTRAL_AMERICA_FILENAME
OSM_PBF_AMERICAN_OCEANIA_PATH = (
    Path(GEOFABRIK_FOLDER) / OSM_PBF_AMERICAN_OCEANIA_FILENAME
)
OSM_PBF_US_PATH = Path(GEOFABRIK_FOLDER) / OSM_PBF_US_FILENAME

OSM_PBF_US_STATES_TERRITORIES_URLS = [
    "https://download.geofabrik.de/north-america/us/alabama-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/alaska-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/arizona-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/arkansas-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/california-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/colorado-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/connecticut-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/delaware-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/district-of-columbia-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/florida-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/georgia-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/hawaii-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/idaho-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/illinois-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/indiana-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/iowa-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/kansas-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/kentucky-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/louisiana-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/maine-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/maryland-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/massachusetts-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/michigan-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/minnesota-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/mississippi-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/missouri-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/montana-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/nebraska-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/nevada-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/new-hampshire-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/new-jersey-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/new-mexico-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/north-carolina-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/north-dakota-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/ohio-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/oklahoma-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/oregon-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/pennsylvania-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/puerto-rico-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/rhode-island-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/south-carolina-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/south-dakota-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/tennessee-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/texas-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/us-virgin-islands-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/utah-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/vermont-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/virginia-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/washington-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/west-virginia-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/wisconsin-latest.osm.pbf",
    "https://download.geofabrik.de/north-america/us/wyoming-latest.osm.pbf",
    "https://download.geofabrik.de/australia-oceania/american-oceania-latest.osm.pbf",
]
