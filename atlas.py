import json

def get_mongo_uri():
    """Reads MongoDB URI from config.json and returns it"""
    with open("config.json") as f:
        config = json.load(f)
    return config["MONGO_URI"]
