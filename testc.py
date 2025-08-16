# from pymongo import MongoClient

# def save_aqi_to_mongo(records, city, mongo_uri="mongodb://localhost:27017/", db_name="Aditya_B", collection_name="aqi_records"):
#     """
#     Save AQI records into MongoDB in nested {date: pollutants} format.
    
#     Args:
#         records (list of dict): Each dict must contain 'date' and pollutant fields.
#         city (str): City name for the document.
#         mongo_uri (str): MongoDB connection URI.
#         db_name (str): Database name.
#         collection_name (str): Collection name.
#     """
#     # Connect to MongoDB
#     client = MongoClient(mongo_uri)
#     db = client[db_name]
#     collection = db[collection_name]
    
#     # Transform list of dicts into {date: pollutants}
#     nested_data = {}
#     for rec in records:
#         rec_copy = rec.copy()
#         date = rec_copy.pop("date")
#         nested_data[date] = rec_copy
    
#     # Final document
#     doc = {
#         "city": city,
#         "data": nested_data
#     }
    
#     # Insert into collection
#     result = collection.insert_one(doc)
#     print(f"✅ Inserted data for {city} with _id: {result.inserted_id}")
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
