from bson.objectid import ObjectId
from datetime import datetime
def get_current_date():
    return datetime.now().strftime("%d-%m-%Y")

def add_note(collection, user_id, title, content, village, live_aqi):
    """Insert a new note with village, AQI, and timestamp"""
    note = {
        "user_id": user_id,
        "title": title,
        "content": content,
        "village": village,
        "live_aqi": live_aqi,
    }
    return collection.insert_one(note)

def get_notes_by_user(collection, user_id):
    return collection.find({"user_id": user_id})

def update_note(collection, note_id, title, content):
    return collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {"title": title, "content": content}}
    )

def delete_note(collection, note_id):
    return collection.delete_one({"_id": ObjectId(note_id)})
