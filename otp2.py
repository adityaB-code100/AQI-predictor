from twilio.rest import Client
import json
with open("config.json") as f:
    config = json.load(f)
twilio_config = config["twilio1"]

# ✅ Twilio setup
account_sid = twilio_config["account_sid"]
auth_token = twilio_config["auth_token"]

client = Client(account_sid, auth_token)

numbers = ['+919168225507', '+919890945506']  # List of phone numbers to send the message to

for number in numbers:
    message = client.messages.create(
        body="Alert: Check your AQI updates!",
        from_=twilio_config["from_number"],  # Your Twilio SMS number
        to=number
    )
    print(f"Sent to {number}: {message.sid}")
