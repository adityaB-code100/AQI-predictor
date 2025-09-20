import threading
import time
from datetime import datetime, timedelta

from add_raw_data_server import index
from get_from_db import get_aqi_by_village
from get_map_mapgenerator import mapgenerator
from processing_data import index2
from data_function_seven import next_seven_days
from send_alert_user import send_message_to_users
# from send_Email_institution import send_message_to_all

def auto_app():
    start_date = datetime.now().strftime("%Y-%m-%d")
    
    # index(start_date)
    # index2(start_date)

    # datelist = next_seven_days(start_date)
    # for date in datelist:
    #     village_aqi_data = get_aqi_by_village(date)
    #     mapgenerator(date, village_aqi_data)

    #send_message_to_all()
    send_message_to_users()

# def schedule_auto_app():
#     while True:
#         now = datetime.now()
#         # Run only between 12:00 AM and 12:05 AM
#         if now.hour == 0 and 0 <= now.minute < 5:
#             print(f"Running auto_app at {now}")
#             auto_app()
#             # Sleep for 5 minutes to avoid running multiple times in the same window
#             time.sleep(300)
#         else:
#             # Check every 30 seconds until the window
#             time.sleep(30)

# # Start the scheduler in a background thread
# threading.Thread(target=schedule_auto_app, daemon=True).start()

auto_app()