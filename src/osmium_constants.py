OSMIUM_EXTRACT_COMPLETE_WAYS_COMMAND_TEMPLATE = "osmium extract --strategy=complete_ways --bbox {min_lon},{min_lat},{max_lon},{max_lat} -o {bbx_extract_pbf} {source_pbf}"
OSMIUM_EXTRACT_SIMPLE_COMMAND_TEMPLATE = "osmium extract --strategy=complete_ways --bbox {min_lon},{min_lat},{max_lon},{max_lat} -o {bbx_extract_pbf} {source_pbf}"
OSMIUM_FILTER_COMMAND_TEMPLATE = "osmium tags-filter w/highway=motorway,motorway_link,primary,primary_link,secondary,secondary_link,tertiary,tertiary_link,trunk,trunk_link,residential,unclassified,service -o {final_drivable_pbf} {source_pbf}"
