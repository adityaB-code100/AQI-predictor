

from get_from_db import get_aqi_data

from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from atlas import get_mongo_uri

# MongoDB connection
client = MongoClient(get_mongo_uri())
db = client["AQI_Project"]

aqi_collection = db["processed_data"]

notes_collection = db["notes"]

def get_current_date():
    return datetime.now().date()  # ✅ date object



def get_notes_for_matching_aqi(user_id, village):
    matched_notes = []
    today = get_current_date()  # already a datetime.date object

    # Fetch all user notes once
    user_notes = list(notes_collection.find({"user_id": user_id}))
    print(f"User notes fetched: {user_notes}")
    aqi_test = get_aqi_data( str(today), village, mongo_uri=get_mongo_uri(),db_name="AQI_Project", collection_name="processed_data")

    # Check past 28 days
    for note in user_notes:
        # Compare AQI with user's notes
            # Optional: convert note created_at string to date
            note_date_str = note.get("created_at", "").strip('"')
            try:
                note_date = datetime.strptime(note_date_str, "%d-%m-%Y").date()
            except:
                continue

            if note.get("live_aqi") == aqi_test.get('live_AQI'):
                matched_notes.append({
                     "Title": note.get("Title", "No title found"),
                    "note": note.get("content", "No note text found")
                })

    return matched_notes if matched_notes else [{"note": "No matching notes found"}]

# # Example usage
# if __name__ == "__main__":
#     result = get_notes_for_matching_aqi("68cc09f65b0dba0eebe96bca", "Pune")
#     print(result)
