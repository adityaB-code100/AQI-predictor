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
