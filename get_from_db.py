from pymongo import MongoClient
from datetime import datetime

def get_aqi_data(date: str, village: str = None, mongo_uri="mongodb://localhost:27017/",
                 db_name="AQI_Project", collection_name="aqi_records"):
    """
    Fetch AQI data for a given date and optionally for a specific village.
    Handles date in "YYYY-MM-DD" or "DD-MM-YYYY" formats.

    Args:
        date (str): Date string (e.g., "2025-09-12" or "12-09-2025").
        village (str, optional): Village/City name. If None, returns all villages.
        mongo_uri (str): MongoDB connection URI.
        db_name (str): MongoDB database name.
        collection_name (str): MongoDB collection name.

    Returns:
        dict: AQI data for the date. If village is specified, returns only that village's data.
              If village is None, returns all villages' data. Returns None if date not found.
    """
    # Convert date to DB format: "DD-MM-YYYY"
    try:
        if "-" in date:
            parts = date.split("-")
            if len(parts[0]) == 4:
                # Format YYYY-MM-DD → convert to DD-MM-YYYY
                dt = datetime.strptime(date, "%Y-%m-%d")
                db_date = dt.strftime("%d-%m-%Y")
            else:
                # Assume already DD-MM-YYYY
                db_date = date
        else:
            raise ValueError("Invalid date format")
    except Exception as e:
        print(f"❌ Date parsing error: {e}")
        return None

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    if village:
        # Query for specific village
        doc = collection.find_one(
            {"date": db_date},
            {f"data.{village}": 1, "_id": 0}
        )
        if doc and "data" in doc and village in doc["data"]:
            return doc["data"][village]
        else:
            return None
    else:
        # Query for all villages
        doc = collection.find_one({"date": db_date}, {"data": 1, "_id": 0})
        if doc and "data" in doc:
            return doc["data"]
        else:
            return None
        


        
# Using YYYY-MM-DD format
# village_data = get_aqi_data("2025-09-12", "VillageB")
# print(village_data)

# # Using DD-MM-YYYY format
# all_data = get_aqi_data("12-09-2025")
# print(all_data)


# def get_aqi_by_village(date: str, db_name="AQI_Project", collection_name="aqi_records"):
#     """
#     Fetch only Predicted_AQI_mean for all villages on a given date.
    
#     Args:
#         date (str): Date in 'DD-MM-YYYY' or 'YYYY-MM-DD' format.
#         db_name (str): MongoDB database name.
#         collection_name (str): MongoDB collection name.
    
#     Returns:
#         dict: { "VillageA": 56, "VillageB": 267, ... } or None if date not found.
#     """
#     # Convert date to both formats
#     try:
#         dt_obj = datetime.strptime(date, "%d-%m-%Y")
#         date_dmy = dt_obj.strftime("%d-%m-%Y")
#         date_ymd = dt_obj.strftime("%Y-%m-%d")
#     except ValueError:
#         raise ValueError("Date must be in DD-MM-YYYY or YYYY-MM-DD format")

#     client = MongoClient("mongodb://localhost:27017/")
#     db = client[db_name]
#     collection = db[collection_name]

#     # Try both date formats
#     result = collection.find_one({"date": date_dmy})
#     if not result:
#         result = collection.find_one({"date": date_ymd})

#     if result and "data" in result:
#         village_aqi = {}
#         for village, pollutants in result["data"].items():
#             aqi = pollutants.get("Predicted_AQI_mean")
#             if aqi is not None:
#                 village_aqi[village] = aqi
#         return village_aqi
#     else:
#         print(f"No AQI data found for date {date}")
#         return None

# # Example usage:
# # date_input = "12-09-2025"
# # village_aqi_data = get_aqi_by_village(date_input)
# # print(village_aqi_data)
# # # Output: {'VillageA': 56, 'VillageB': 267}
from pymongo import MongoClient
from datetime import datetime

def get_aqi_by_village(date: str, db_name="AQI_Project", collection_name="aqi_records"):
    """
    Fetch Predicted_AQI_mean for all villages on a given date.
    
    Accepts date in multiple formats: DD-MM-YYYY or YYYY-MM-DD.

    Returns:
        dict: { "VillageA": 56, "VillageB": 267 } or None if date not found.
    """
    date_formats = ["%d-%m-%Y", "%Y-%m-%d"]  # Add more if needed
    dt_obj = None

    # Try parsing date with known formats
    for fmt in date_formats:
        try:
            dt_obj = datetime.strptime(date, fmt)
            break
        except ValueError:
            continue

    if not dt_obj:
        print(f"⚠️ Date format not recognized: {date}")
        return None

    # Convert to both formats for MongoDB search
    date_dmy = dt_obj.strftime("%d-%m-%Y")
    date_ymd = dt_obj.strftime("%Y-%m-%d")

    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db[collection_name]

    # Try both formats in the DB
    result = collection.find_one({"date": date_dmy})
    if not result:
        result = collection.find_one({"date": date_ymd})

    if result and "data" in result:
        village_aqi = {}
        for village, pollutants in result["data"].items():
            aqi = pollutants.get("Predicted_AQI_mean")
            if aqi is not None:
                village_aqi[village] = aqi
        return village_aqi
    else:
        print(f"No AQI data found for date {date}")
        return None

# # Example usage:
# village_aqi_data = get_aqi_by_village("2025-09-12")
# print(village_aqi_data)
