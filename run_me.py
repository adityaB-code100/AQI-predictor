from add_raw_data_server import index
from get_from_db import get_aqi_by_village
from get_map_mapgenerator import mapgenerator
from processing_data import index2
from data_function_seven import next_seven_days


start_date = '2025-09-18'
index(start_date)
index2(start_date)


datelist=next_seven_days(start_date)
for date in datelist:
    # Call the map generator for each date
    village_aqi_data = get_aqi_by_village(date)
    mapgenerator(date, village_aqi_data)
