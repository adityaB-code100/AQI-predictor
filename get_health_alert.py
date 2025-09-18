from pymongo import MongoClient
from atlas import get_mongo_uri
# Connect to MongoDB
client = MongoClient(get_mongo_uri())
db = client["AQI_Project"]

def get_health_alert_personal(aqi_value, category="general"):

    """
    Fetch health alert message based on AQI value and category (general or disease).
    """
    collection = db["health_alerts"]

    if category == 'None':
         category="general"
    # Determine AQI category
    if aqi_value <= 50:
        aqi_class = "good"
    elif aqi_value <= 100:
        aqi_class = "moderate"
    elif aqi_value <= 150:
        aqi_class = "usg"   # renamed to match DB key
    elif aqi_value <= 200:
        aqi_class = "unhealthy"
    elif aqi_value <= 300:
        aqi_class = "very_unhealthy"
    else:
        aqi_class = "hazardous"

    # Fetch document

    record = collection.find_one({}, {"_id": 0})
    if not record:
        return "No health alerts found in database."

    data = record.get("data", {})   # 👈 now safely get nested 'data'

    # Look inside chosen category
    category_data = data.get(category.lower(), {})
    if category_data:
        return category_data.get(aqi_class, "No alert available for this AQI range.")

    # fallback
    return data.get("general", {}).get(aqi_class, "No alert available.")
