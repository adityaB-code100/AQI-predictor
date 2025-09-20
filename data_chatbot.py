from pymongo import MongoClient
from atlas import get_mongo_uri

# MongoDB connection
client = MongoClient(get_mongo_uri())
db = client["AQI_Project"]
collection = db["aqi_records"]

# Specify the date to match
def data_chat(target_date)  :

# Fetch all documents matching the date
    matching_docs = list(collection.find({"date": target_date}))

    # Optional: convert ObjectId to string for easier handling
    for doc in matching_docs:
        doc["_id"] = str(doc["_id"])

    # Print or pass to template
    return matching_docs