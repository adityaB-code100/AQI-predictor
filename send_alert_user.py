
# from flask import app
# from twilio.rest import Client
# import json
# from datetime import datetime
# from pymongo import MongoClient
# from get_from_db import get_aqi_data
# from get_health_alert import get_health_alert_personal
# from atlas import get_mongo_uri
# from flask_mail import Mail, Message

# # ✅ Load configuration from config.json
# from transalator import translator_gemini
# with open("config.json") as f:
#     config = json.load(f)

# twilio_config = config["twilio1"]

# # ✅ Twilio setup
# account_sid = twilio_config["account_sid"]
# auth_token = twilio_config["auth_token"]
# twilio_number = twilio_config["from_number"]

# client = Client(account_sid, auth_token)

# # ✅ MongoDB setup
# mongo_client =MongoClient(get_mongo_uri())

# db = mongo_client["AQI_Project"]
# users_collection = db["users"]
# with open("config.json") as f:
#     params = json.load(f)['params']
# app.config['MAIL_SERVER'] = params['mail_server']
# app.config['MAIL_PORT'] = params['mail_port']
# app.config['MAIL_USE_TLS'] = params['mail_use_tls']
# app.config['MAIL_USE_SSL'] = params['mail_use_ssl']
# app.config['MAIL_USERNAME'] = params['gmail_user']
# app.config['MAIL_PASSWORD'] = params['gmail_password']

# def get_current_date():
#     return datetime.now().strftime("%Y-%m-%d")


# def format_phone_number(number: str) -> str | None:
#     """
#     Ensure phone number is in +91XXXXXXXXXX format (India E.164).
#     Returns None if invalid.
#     """
#     if not number:
#         return None
#     number = str(number).strip().replace(" ", "").replace("-", "")

#     if number.startswith("+91") and len(number) == 13 and number[1:].isdigit():
#         return number
#     if number.startswith("91") and len(number) == 12 and number.isdigit():
#         return "+" + number
#     if number.startswith("0") and len(number) == 11 and number.isdigit():
#         return "+91" + number[1:]
#     if len(number) == 10 and number.isdigit():
#         return "+91" + number
#     return None


# def send_message_to_users():
#     try:
#         users = users_collection.find()
#     except Exception as db_error:
#         print(f"❌ Error fetching users from DB: {db_error}")
#         return

#     sent_sms, failed_sms, invalid_numbers = [], [], []

#     for user in users:
#         try:
#             village = user.get("village")
#             raw_number = user.get("mobile")
#             name = user.get("name", "User")
#             language = user.get("language", "en")

#             # ✅ Validate phone number
#             phone_number = format_phone_number(raw_number)
#             if not phone_number:
#                 print(f"⚠️ Skipping {name}: invalid number {raw_number}")
#                 invalid_numbers.append(raw_number)
#                 continue

#             date = get_current_date()

#             # ✅ Get AQI data
#             try:
#                 data = get_aqi_data(date, village)
#                 print(data)
#                 aqi_all = data.get("village_aqi_data", {})
#                 aqi = data['Predicted_AQI']
#             except Exception as aqi_error:
#                 print(f"⚠️ Failed to fetch AQI for {village}: {aqi_error}")
#                 aqi = -1

#             # ✅ Get alerts safely
#             try:
#                 health_alert = (
#                     get_health_alert_personal(aqi, "general")
#                     if aqi != -1 else "AQI data not available"
#                 )
#                 personalise_alert = (
#                     get_health_alert_personal(aqi, user.get("disease"))
#                     if user.get("disease") and aqi != -1
#                     else "AQI data not available"
#                 )
#             except Exception as alert_error:
#                 print(f"⚠️ Alert generation failed for {name}: {alert_error}")
#                 health_alert = "Error generating advice"
#                 personalise_alert = "Error generating advice"

#             # ✅ Create SMS text
#             text_message = (
#                 f"AQI Alert - {village} ({date})\n\n"
#                 f"Dear,\n{name},\n"
#                 f"Current AQI for Your Village : {aqi if aqi != -1 else 'N/A'}\n\n"
#                 f"General Advice: {health_alert}\n"
#                 f"Personal Advice : {personalise_alert}\n\n"
#                 f"Please take precautions.\n"
#                 f"- Hyperlocal AQI System"
#             )

#             # ✅ Send SMS
#             print(text_message)
#             try:
#                 # message = client.messages.create(
#                 #     body=translator_gemini(text_message, language),
#                 #     from_=twilio_number,
#                 #     to=phone_number
#                 # )
#                 print(f"✅ SMS sent to {phone_number} (SID: {message.sid})")
#                 sent_sms.append(phone_number)


                
#                 # ✅ Draft email body
#                 message_body = (
#                   f"AQI Alert - {village} ({date})\n\n"
#                 f"Dear,\n{name},\n"
#                 f"Current AQI for Your Village : {aqi if aqi != -1 else 'N/A'}\n\n"
#                 f"General Advice: {health_alert}\n"
#                 f"Personal Advice : {personalise_alert}\n\n"
#                 f"Please take precautions.\n"
#                 f"- Hyperlocal AQI System"
#                 )

#                 # ✅ Send Email with PDF
#                 msg = Message(
#                     subject=f"🌍 AQI Health Report - {village} ({date})",
#                     sender=app.config['MAIL_USERNAME'],
#                     recipients=[user.get("email")],
#                     body=translator_gemini(text_message, language)
#                 )


#             except Exception as sms_error:
#                 print(f"❌ Could not send SMS to {phone_number}: {sms_error}")
#                 failed_sms.append(phone_number)

#         except Exception as user_error:
#             print(f"❌ Unexpected error with user {user.get('name', 'Unknown')}: {user_error}")
#             failed_sms.append(user.get("mobile"))


#     # ✅ Final summary
#     print("\n📌 SMS Summary:")
#     print(f"✅ Sent SMS ({len(sent_sms)}): {sent_sms}")
#     print(f"❌ Failed SMS ({len(failed_sms)}): {failed_sms}")
#     print(f"⚠️ Invalid Numbers ({len(invalid_numbers)}): {invalid_numbers}")


# if __name__ == "__main__":
#     send_message_to_users()
from flask import Flask
from twilio.rest import Client
import json
from datetime import datetime
from pymongo import MongoClient
from get_from_db import get_aqi_data
from get_health_alert import get_health_alert_personal
from atlas import get_mongo_uri
from flask_mail import Mail, Message
from transalator import transaltor

# ✅ Load configuration from config.json
with open("config.json") as f:
    config = json.load(f)

twilio_config = config["twilio1"]
params = config["params"]

# ✅ Twilio setup
account_sid = twilio_config["account_sid"]
auth_token = twilio_config["auth_token"]
twilio_number = twilio_config["from_number"]
client = Client(account_sid, auth_token)

# ✅ Flask + Mail setup
app = Flask(__name__)
app.config['MAIL_SERVER'] = params['mail_server']
app.config['MAIL_PORT'] = params['mail_port']
app.config['MAIL_USE_TLS'] = params['mail_use_tls']
app.config['MAIL_USE_SSL'] = params['mail_use_ssl']
app.config['MAIL_USERNAME'] = params['gmail_user']
app.config['MAIL_PASSWORD'] = params['gmail_password']

mail = Mail(app)

# ✅ MongoDB setup
mongo_client = MongoClient(get_mongo_uri())
db = mongo_client["AQI_Project"]
users_collection = db["users"]

# ----------------------------------------------------------
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def format_phone_number(number: str) -> str | None:
    """Ensure phone number is in +91XXXXXXXXXX format (India E.164)."""
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

# ----------------------------------------------------------
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
            language = user.get("language", "en")

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

            # ✅ Create message body
            text_message = (
                f"AQI Alert - {village} ({date})\n\n"
                f"Dear {name},\n"
                f"Current AQI for Your Village : {aqi if aqi != -1 else 'N/A'}\n\n"
                f"General Advice: {health_alert}\n"
                f"Personal Advice: {personalise_alert}\n\n"
                f"Please take precautions.\n"
                f"- Hyperlocal AQI System"
            )

            # ✅ Send SMS
            try:
                # message = client.messages.create(
                #     body=transaltor(text_message, language),
                #     from_=twilio_number,
                #     to=phone_number
                # )
                # print(f"✅ SMS sent to {phone_number} (SID: {message.sid})")
                # print(f"✅ SMS (mock) prepared for {phone_number}")
                # sent_sms.append(phone_number)

                # ✅ Send Email inside Flask app context
                with app.app_context():
                    msg = Message(
                        subject=f"🌍 AQI Health Report - {village} ({date})",
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[user.get("email")],
                        body=transaltor(text_message, language)
                    )
                    mail.send(msg)
                    print(f"📧 Email sent to {user.get('email')}")

            except Exception as sms_error:
                print(f"❌ Could not send message to {phone_number}: {sms_error}")
                failed_sms.append(phone_number)

        except Exception as user_error:
            print(f"❌ Unexpected error with user {user.get('name', 'Unknown')}: {user_error}")
            failed_sms.append(user.get("mobile"))

    # ✅ Final summary
    print("\n📌 Message Summary:")
    print(f"✅ Sent SMS ({len(sent_sms)}): {sent_sms}")
    print(f"❌ Failed SMS ({len(failed_sms)}): {failed_sms}")
    print(f"⚠️ Invalid Numbers ({len(invalid_numbers)}): {invalid_numbers}")

# ----------------------------------------------------------
if __name__ == "__main__":
    send_message_to_users()
