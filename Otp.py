
from twilio.rest import Client
import json
from datetime import datetime
from pymongo import MongoClient
from get_from_db import get_aqi_data
from get_health_alert import get_health_alert_personal

# ✅ Load configuration from config.json
with open("config.json") as f:
    config = json.load(f)

twilio_config = config["twilio1"]

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

    if number.startswith("+91") and len(number) == 13 and number[1:].isdigit():
        return number
    if number.startswith("91") and len(number) == 12 and number.isdigit():
        return "+" + number
    if number.startswith("0") and len(number) == 11 and number.isdigit():
        return "+91" + number[1:]
    if len(number) == 10 and number.isdigit():
        return "+91" + number
    return None


def send_message_to_users():
    try:
        users = users_collection.find()
    except Exception as db_error:
        print(f"❌ Error fetching users from DB: {db_error}")
        return

    sent_sms, failed_sms, invalid_numbers = [], [], []

    for user in users:
        try:
            village = user.get("village")
            raw_number = user.get("mobile")
            name = user.get("name", "User")

            # ✅ Validate phone number
            phone_number = format_phone_number(raw_number)
            if not phone_number:
                print(f"⚠️ Skipping {name}: invalid number {raw_number}")
                invalid_numbers.append(raw_number)
                continue

            date = get_current_date()

            # ✅ Get AQI data
            try:
                data = get_aqi_data(date, village)
                print(data)
                aqi_all = data.get("village_aqi_data", {})
                aqi = data['Predicted_AQI']
            except Exception as aqi_error:
                print(f"⚠️ Failed to fetch AQI for {village}: {aqi_error}")
                aqi = -1

            # ✅ Get alerts safely
            try:
                health_alert = (
                    get_health_alert_personal(aqi, "general")
                    if aqi != -1 else "AQI data not available"
                )
                personalise_alert = (
                    get_health_alert_personal(aqi, user.get("disease"))
                    if user.get("disease") and aqi != -1
                    else "AQI data not available"
                )
            except Exception as alert_error:
                print(f"⚠️ Alert generation failed for {name}: {alert_error}")
                health_alert = "Error generating advice"
                personalise_alert = "Error generating advice"

            # ✅ Create SMS text
            text_message = (
                f"AQI Alert - {village} ({date})\n\n"
                f"Dear,\n{name},\n"
                f"Current AQI for Your Village : {aqi if aqi != -1 else 'N/A'}\n\n"
                f"General Advice: {health_alert}\n"
                f"Personal Advice : {personalise_alert}\n\n"
                f"Please take precautions.\n"
                f"- Hyperlocal AQI System"
            )

            # ✅ Send SMS
            print(text_message)
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
            print(f"❌ Unexpected error with user {user.get('name', 'Unknown')}: {user_error}")
            failed_sms.append(user.get("mobile"))

    # ✅ Final summary
    print("\n📌 SMS Summary:")
    print(f"✅ Sent SMS ({len(sent_sms)}): {sent_sms}")
    print(f"❌ Failed SMS ({len(failed_sms)}): {failed_sms}")
    print(f"⚠️ Invalid Numbers ({len(invalid_numbers)}): {invalid_numbers}")


# if __name__ == "__main__":
#     send_message_to_users()
