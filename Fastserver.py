from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["AQI_Project"]
collection = db["processed_data"]

def save_or_update_data(date: str, village: str, extra_data: dict):
    """
    Saves or updates data in the processed_data collection.
    If the date exists, it updates/replaces the specific village data.
    If not, it inserts a new document.
    """
    result = collection.update_one(
        {"date": date},  # find by date
            {
                "$set": {f"data.{village}": extra_data}
            },
            upsert=True
    
    )
    print("saved",date,village)
