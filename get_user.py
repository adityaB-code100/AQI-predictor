from pymongo import MongoClient
from atlas import get_mongo_uri
# Connect to MongoDB
client = MongoClient(get_mongo_uri())
db = client["AQI_Project"]
collection = db["processed_data"]

def get_data(date, village):
    query = {
        "date": date,
        "village": village
    }

    result = collection.find_one(query, {"_id": 0})
    if result:
        return result
    else:
        return None



# date1=get_data("30-08-2025", "Mumbai")
# print("printing",date1)
