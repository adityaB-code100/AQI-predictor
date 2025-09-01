from pymongo import MongoClient

# connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["AQI_Project"]
collection = db["health_alerts"]

# JSON data (from above)
data = {
    "data": {
        "general": {
            "good": "Air quality is satisfactory, no risk.",
            "moderate": "Acceptable; some pollutants may affect sensitive individuals.",
            "usg": "Sensitive groups may feel effects; general public usually unaffected.",
            "unhealthy": "Everyone may begin to experience health effects; sensitive groups more serious.",
            "very_unhealthy": "Emergency conditions possible; health warning for everyone.",
            "hazardous": "Serious health risks; emergency situation for all."
        },
        "asthma": {
            "good": "No risk; enjoy outdoor activities.",
            "moderate": "Keep inhaler ready; avoid known triggers.",
            "usg": "Use controller medication; avoid outdoor exercise.",
            "unhealthy": "Stay indoors; use inhaler early if symptoms start; consult doctor if needed.",
            "very_unhealthy": "Strictly avoid outdoor exposure; follow asthma action plan.",
            "hazardous": "High risk; seek immediate medical attention for breathing issues."
        },
        "bronchitis": {
            "good": "No extra precautions needed.",
            "moderate": "Avoid long outdoor exposure if coughing increases.",
            "usg": "Rest, stay hydrated, reduce outdoor activity.",
            "unhealthy": "Stay indoors; avoid smoke and irritants.",
            "very_unhealthy": "Stay indoors; consider humidifier; seek help if breathing worsens.",
            "hazardous": "Severe risk; medical attention may be necessary."
        },
        "copd": {
            "good": "No risk; normal activity allowed.",
            "moderate": "Keep rescue medication ready; avoid exertion.",
            "usg": "Limit outdoor time; follow COPD plan.",
            "unhealthy": "Stay indoors; use prescribed medicines.",
            "very_unhealthy": "Strictly remain indoors; urgent care if breathlessness increases.",
            "hazardous": "Emergency condition; immediate medical help may be required."
        },
        "allergic_rhinitis": {
            "good": "No risk; enjoy outdoor activities.",
            "moderate": "Keep antihistamines ready; close windows.",
            "usg": "Limit outdoor exposure; use sprays/antihistamines.",
            "unhealthy": "Stay indoors; clean nasal passages; avoid dust.",
            "very_unhealthy": "Remain indoors; use purifier; follow medication plan.",
            "hazardous": "Avoid outdoor exposure; seek medical advice if symptoms worsen."
        }
    }
}

# insert into MongoDB
collection.insert_one(data)
print("Data inserted successfully!")
