import pandas as pd
from pymongo import MongoClient

# ✅ Example DataFrame
def mango_data(data):
    # data = {
    #     "date": ["01-01-2025 01:00", "01-01-2025 02:00"],
    #     "PM2.5": [59.13, 60.25],
    #     "PM10": [115.28, 118.3],
    #     "NO2": [12.37, 13.4]
    # }
    df = pd.DataFrame(data)

    # ✅ Connect to MongoDB (replace with your connection string if using Atlas)
    client = MongoClient("mongodb://localhost:27017/")

    # ✅ Select Database and Collection
    db = client["aditya_mumbai"]
    collection = db["AQI_Data"]

    # ✅ Convert DataFrame to dictionary and insert
    data_dict = df.to_dict("records")  # convert to list of dictionaries
    collection.insert_many(data_dict)

    print("✅ DataFrame inserted successfully into MongoDB!")
    return data