from pymongo import MongoClient
from atlas import get_mongo_uri
# Connect to MongoDB
client = MongoClient(get_mongo_uri())
db = client["AQI_Project"]

def get_health_alert_institution(aqi_value, category="general"):
    collection = db["institution_alerts"]

    if category == 'None':
        category = "general"

    # Map AQI value → AQI class
    if aqi_value <= 50:
        aqi_class = "Good"
    elif aqi_value <= 100:
        aqi_class = "Moderate"
    elif aqi_value <= 150:
        aqi_class = "Unhealthy for Sensitive Groups"
    elif aqi_value <= 200:
        aqi_class = "Unhealthy"
    elif aqi_value <= 300:
        aqi_class = "Very Unhealthy"
    else:
        aqi_class = "Hazardous"

    # Fetch record
    record = collection.find_one({}, {"_id": 0})
    if not record:
        return "No health alerts found in database."

    data = record  # 👈 FIX: use top-level fields directly

    # Look inside chosen category (general, hospital, school, etc.)
    category_data = data.get(category.lower(), {})
    if category_data:
        return category_data.get(aqi_class, "No alert available for this AQI range.")

    # fallback
    return data.get("general", {}).get(aqi_class, "No alert available.")
