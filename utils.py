from pymongo import MongoClient
from gridfs import GridFS
from datetime import datetime, timedelta
from atlas import get_mongo_uri

client = MongoClient(get_mongo_uri())
db = client["AQI_Project"]
fs = GridFS(db)

def save_html_page(html_content: str, date_str: str):
    page_date = datetime.strptime(date_str, "%d-%m-%Y").replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Delete old files beyond 7 days
    cutoff_date = page_date - timedelta(days=1)
    for f in fs.find({"date": {"$lt": cutoff_date}}):
        fs.delete(f._id)
    
    # Save new HTML
    fs.put(html_content.encode("utf-8"), filename=f"map_{date_str}.html", date=page_date)
    print(f"Map HTML saved to GridFS for {date_str}")


def get_html_page(date_str: str) -> str | None:
    page_date = datetime.strptime(date_str, "%d-%m-%Y").replace(hour=0, minute=0, second=0, microsecond=0)
    file_doc = fs.find_one({"date": page_date})
    if file_doc:
        return file_doc.read().decode("utf-8")
    return None
