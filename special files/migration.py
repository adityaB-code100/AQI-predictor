from pymongo import MongoClient

# 1️⃣ Connect to local MongoDB
local_client = MongoClient("mongodb://localhost:27017/")
local_db = local_client["AQI_Project"]

# 2️⃣ Connect to MongoDB Atlas
atlas_client = MongoClient(
    "mongodb+srv://hyperlocalaqi_db_user:Test1234@aqiproject.7r8nvxf.mongodb.net/AQI_Project?retryWrites=true&w=majority&appName=AQIProject"
)
atlas_db = atlas_client["AQI_Project"]

# 3️⃣ Loop through all collections in local DB and copy them
for collection_name in local_db.list_collection_names():
    local_collection = local_db[collection_name]
    atlas_collection = atlas_db[collection_name]

    # Fetch all documents from local
    documents = list(local_collection.find())

    if documents:
        # Remove _id to avoid duplicate key issues
        for doc in documents:
            doc.pop("_id", None)

        # Insert into Atlas
        atlas_collection.insert_many(documents)
        print(f"✅ Copied {len(documents)} documents from {collection_name}")
    else:
        print(f"⚠️ Collection {collection_name} is empty, skipped.")

print("🎉 Migration completed successfully!")
