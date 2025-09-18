from flask import Flask, jsonify
from pymongo import MongoClient
from atlas import get_mongo_uri
# Connect to MongoDB
client = MongoClient(get_mongo_uri())
app = Flask(__name__)

# connect to MongoDB (change URI for your DB)
db = client["AQI_Project"]        # replace with your DB name
collection = db["institutions"]          # replace with your collection name

#@app.route("/get_institutions")
def get_institutions():
    try:
        institutions = []
        for record in collection.find():
            record["_id"] = str(record["_id"])
            institutions.append(record)
        return institutions  # ✅ return list, NOT jsonify
    except Exception as e:
        print(f"Error fetching institutions: {e}")
        return []  # return empty list on error


if __name__ == "__main__":
    app.run(debug=True)
    # get_institutions()