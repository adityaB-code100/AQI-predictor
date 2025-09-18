from pymongo import MongoClient
import certifi

# Use your connection string
uri = "mongodb+srv://hyperlocalaqi_db_user:Test1234@aqiproject.7r8nvxf.mongodb.net/?retryWrites=true&w=majority&appName=AQIProject"

# Connect to MongoDB Atlas
client = MongoClient(uri, tlsCAFile=certifi.where())

try:
    # Test connection
    client.admin.command("ping")
    print("✅ Connected to MongoDB Atlas!")

    # Select database and collection
    db = client["AQIProject"]
    collection = db["health_alerts"]

    # Insert sample data
    alert = {"city": "Delhi", "aqi": 350, "alert": "Severe"}
    result = collection.insert_one(alert)
    print("Inserted document ID:", result.inserted_id)

except Exception as e:
    print("❌ Connection failed:", e)
