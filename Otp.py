from twilio.rest import Client
import json
from datetime import datetime
from pymongo import MongoClient
from get_from_db import get_aqi_data
from get_health_alert import get_health_alert_personal

# ✅ Load configuration from config.json
with open("config.json") as f:
    config = json.load(f)

twilio_config = config["twilio"]

# ✅ Twilio setup
account_sid = twilio_config["account_sid"]
auth_token = twilio_config["auth_token"]
twilio_number = twilio_config["from_number"]

client = Client(account_sid, auth_token)

# ✅ MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["AQI_Project"]
users_collection = db["users"]


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


def format_phone_number(number: str) -> str | None:
    """
    Ensure phone number is in +91XXXXXXXXXX format (India E.164).
    Returns None if invalid.
    """
    if not number:
        return None

    number = str(number).strip().replace(" ", "").replace("-", "")

    # Already in correct format
    if number.startswith("+91") and len(number) == 13 and number[1:].isdigit():
        return number

    # Starts with 91 but missing +
    if number.startswith("91") and len(number) == 12 and number.isdigit():
        return "+" + number

    # Starts with 0 and has 11 digits (like 0987654321)
    if number.startswith("0") and len(number) == 11 and number.isdigit():
        return "+91" + number[1:]

    # Plain 10-digit number
    if len(number) == 10 and number.isdigit():
        return "+91" + number

    # Otherwise invalid
    return None


def send_message_to_users():
    users = users_collection.find()
    sent_sms, failed_sms, invalid_numbers = [], [], []

    for user in users:
        try:
            village = user.get("village")
            raw_number = user.get("mobile")
            name = user.get("name", "User")

            if not village or not raw_number:
                print(f"⚠️ Skipping {name}: missing village/mobile")
                continue

            # ✅ Format phone number
            phone_number = format_phone_number(raw_number)
            if not phone_number:
                print(f"⚠️ Skipping {name}: invalid phone number {raw_number}")
                invalid_numbers.append(raw_number)
                continue

            date = get_current_date()

            # ✅ Get AQI data
            data = get_aqi_data(date, village)
            aqi_all = data.get("village_aqi_data", {})
            aqi = aqi_all.get(village, "N/A")

            # ✅ Get health alerts
            health_alert = get_health_alert_personal(aqi, "general")
            personalise_alert = (
                get_health_alert_personal(aqi, user.get("disease"))
                if user.get("disease")
                else "N/A"
            )

            # ✅ Create SMS text
            text_message = (
                f"🌍 AQI Alert - {village} ({date})\n\n"
                f"👤 {name}, Age: {user.get('age', 'N/A')}\n"
                f"📊 Current AQI: {aqi}\n\n"
                f"⚠️ General Advice: {health_alert}\n"
                f"🩺 Personal Advice ({user.get('disease', 'N/A')}): {personalise_alert}\n\n"
                f"Please take precautions.\n"
                f"- AQI Monitoring System"
            )

            try:
                message = client.messages.create(
                    body=text_message,
                    from_=twilio_number,
                    to=phone_number
                )
                print(f"✅ SMS sent to {phone_number} (SID: {message.sid})")
                sent_sms.append(phone_number)

            except Exception as sms_error:
                print(f"❌ Could not send SMS to {phone_number}: {sms_error}")
                failed_sms.append(phone_number)

        except Exception as user_error:
            print(f"⚠️ Error processing user {user.get('name', 'Unknown')}: {user_error}")
            failed_sms.append(user.get("mobile"))

    # ✅ Final summary
    print("\n📌 SMS Summary:")
    print(f"✅ Sent SMS ({len(sent_sms)}): {sent_sms}")
    print(f"❌ Failed SMS ({len(failed_sms)}): {failed_sms}")
    print(f"⚠️ Invalid Numbers ({len(invalid_numbers)}): {invalid_numbers}")


if __name__ == "__main__":
    send_message_to_users()
