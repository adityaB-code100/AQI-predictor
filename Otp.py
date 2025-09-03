from twilio.rest import Client
import json

# ✅ Load configuration from config.json
with open('config.json', 'r') as c:
    config = json.load(c)

twilio_config = config["twilio"]

# ✅ Twilio setup
account_sid = twilio_config["account_sid"]
auth_token = twilio_config["auth_token"]
twilio_number = twilio_config["from_number"]
profile_no = twilio_config["profile_no"]


