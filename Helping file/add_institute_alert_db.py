from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["AQI_Project"]  # replace with your DB name

# ================== ALERT DATA ==================

general_alerts = {
    "general": {
        "Good": "Air quality is good. Safe for all individuals.",
        "Moderate": "Acceptable air quality. Sensitive individuals may notice mild effects.",
        "Unhealthy for Sensitive Groups": "Sensitive groups may experience respiratory symptoms.",
        "Unhealthy": "Health effects may be experienced by everyone. Sensitive groups at higher risk.",
        "Very Unhealthy": "Increased health risk for everyone. Minimize outdoor activities.",
        "Hazardous": "Serious health risks for all. Stay indoors and use air purifiers if available."
    },


    "hospital": {
        "Good": "Air quality is safe. No special precautions needed for patients.",
        "Moderate": "Monitor respiratory patients. Provide masks if needed.",
        "Unhealthy for Sensitive Groups": "Patients with asthma, COPD, or heart disease may need extra care.",
        "Unhealthy": "Increase hospital ventilation. High-risk patients should avoid outdoor exposure.",
        "Very Unhealthy": "Prepare for more respiratory-related admissions. Provide oxygen support readiness.",
        "Hazardous": "Critical risk. Ensure hospitals have emergency respiratory care available."
    },


    "school": {
        "Good": "Safe air quality. Outdoor activities allowed.",
        "Moderate": "Mild risk. Encourage students with asthma to carry inhalers.",
        "Unhealthy for Sensitive Groups": "Limit outdoor sports. Monitor children with asthma or allergies.",
        "Unhealthy": "Suspend outdoor activities. Move PE classes indoors.",
        "Very Unhealthy": "All children should stay indoors. Provide N95 masks if possible.",
        "Hazardous": "Severe risk. Schools should remain closed. Move learning online if possible."
    }
}

# ================== STORE IN MONGODB ==================

def store_alerts(collection_name, alert_data):
    collection = db[collection_name]
    # Clear old data
    collection.delete_many({})
    # Insert new
    collection.insert_one(alert_data)
    print(f"✅ Alerts stored in '{collection_name}' collection.")

# Store all three
store_alerts("institution_alerts", general_alerts)
