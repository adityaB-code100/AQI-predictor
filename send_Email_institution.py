import os
import json
from flask import Flask
from flask_mail import Mail, Message
from get_institution_data import get_institutions  # your DB function
from get_health_alerts_institution import get_health_alert_institution
from get_from_db import get_aqi_data
from datetime import datetime
from get_report_generator import get_report
from xhtml2pdf import pisa
import tempfile

# ✅ Flask app setup
with open("config.json") as f:
    params = json.load(f)['params']

app = Flask(__name__)
app.config['MAIL_SERVER'] = params['mail_server']
app.config['MAIL_PORT'] = params['mail_port']
app.config['MAIL_USE_TLS'] = params['mail_use_tls']
app.config['MAIL_USE_SSL'] = params['mail_use_ssl']
app.config['MAIL_USERNAME'] = params['gmail_user']
app.config['MAIL_PASSWORD'] = params['gmail_password']

mail = Mail(app)

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

# ✅ Function to convert HTML → PDF
def html_to_pdf(html_content, output_path):
    with open(output_path, "w+b") as f:
        pisa_status = pisa.CreatePDF(html_content, dest=f)
    return not pisa_status.err

def send_message_to_all():
    with app.app_context():
        record_insti = get_institutions()
        sent_emails, failed_emails = [], []

        for inst in record_insti:
            try:
                village = inst.get("village")
                recipient_email = inst.get("email")
                inst_type = inst.get("institution_type", "general")
                inst_name = inst.get("name", "Institution")

                if not village or not recipient_email:
                    print(f"Skipping institution {inst_name}: missing village/email")
                    continue

                date = get_current_date()
                # ✅ Generate HTML Report
                html_report = get_report(village, date)

                # ✅ Convert HTML to PDF
                pdf_path = f"AQI_Report_{village}_{date}.pdf"
                success = html_to_pdf(html_report, pdf_path)

                if not success:
                    print(f"❌ Failed to generate PDF for {inst_name}")
                    continue

                # ✅ Draft email body
                message_body = (
                    f"Hello {inst_name},\n\n"
                    f"Please find attached the detailed Air Quality & Health Report "
                    f"for {village} on {date}.\n\n"
                    f"- AQI Monitoring System"
                )

                # ✅ Send Email with PDF
                msg = Message(
                    subject=f"🌍 AQI Health Report - {village} ({date})",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[recipient_email],
                    body=message_body
                )

                with open(pdf_path, "rb") as pdf:
                    msg.attach(
                        os.path.basename(pdf_path),
                        "application/pdf",
                        pdf.read()
                    )

                mail.send(msg)
                print(f"✅ Email with PDF sent to {recipient_email}")
                sent_emails.append(recipient_email)

                # cleanup
                os.remove(pdf_path)

            except Exception as e:
                print(f"❌ Failed to send to {inst.get('email')}: {e}")
                failed_emails.append(inst.get("email"))

        print("\n📌 Summary:")
        print(f"Sent emails ({len(sent_emails)}): {sent_emails}")
        print(f"Failed emails ({len(failed_emails)}): {failed_emails}")



send_message_to_all()
