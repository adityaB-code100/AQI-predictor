from pymongo import MongoClient
from datetime import datetime
import statistics
from atlas import get_mongo_uri
def calculate_and_store_monthly_mean_aqi():
    # Connect to MongoDB
    client = MongoClient(get_mongo_uri())
    db = client["AQI_Project"]
    source = db["aqi_records"]
    target = db["monthly_aqi"]

    # Dictionary: {month: {city: [aqi_values]}}
    monthly_citywise_aqi = {}

    # Fetch all documents from source
    for doc in source.find():
        date_str = doc.get("date")
        if not date_str:
            continue

        # Parse date "dd-mm-yyyy"
        try:
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            continue

        month_key = date_obj.strftime("%Y-%m")  # e.g., "2025-08"

        # Get city-wise AQI
        city_data = doc.get("data", {})
        for city, values in city_data.items():
            aqi = values.get("Predicted_AQI")
            if aqi is not None:
                monthly_citywise_aqi.setdefault(month_key, {}).setdefault(city, []).append(aqi)

    # Calculate mean AQI per city per month and update DB
    for month, cities in monthly_citywise_aqi.items():
        # Check if month already exists in target collection
        existing_doc = target.find_one({"month": month})

        month_doc = {"month": month}

        for city, aqis in cities.items():
            # If already exists, merge old value with new
            if existing_doc and city in existing_doc:
                old_value = existing_doc[city]
                # Recompute mean from old mean and new values
                combined = aqis + [old_value]
                month_doc[city] = round(statistics.mean(combined), 2)
            else:
                # Just compute mean from current batch
                month_doc[city] = round(statistics.mean(aqis), 2)

        # Upsert into DB
        target.update_one(
            {"month": month},   # filter
            {"$set": month_doc}, # update
            upsert=True          # insert if not exists
        )

    print("✅ Monthly mean AQI stored/updated successfully!")

