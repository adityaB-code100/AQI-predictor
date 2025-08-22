
from pymongo import MongoClient

def save_aqi_to_mongo(records, city, mongo_uri="mongodb://localhost:27017/", db_name="AQI_Project", collection_name="aqi_records"):
    """
    Save AQI records into MongoDB in nested {city: pollutants} format grouped by date.
    
    Args:
        records (list of dict): Each dict must contain 'date' and pollutant fields.
        city (str): City/village name for the document.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    for rec in records:
        rec_copy = rec.copy()
        date = rec_copy.pop("date")

        # Upsert: one document per date, with multiple villages inside
        collection.update_one(
            {"date": date},  # find by date
            {
                "$set": {f"data.{city}": rec_copy}
            },
            upsert=True
        )

    print(f"✅ Inserted/Updated data for {city}")
