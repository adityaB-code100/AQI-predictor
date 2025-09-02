import json
from flask import Flask
from flask_mail import Mail, Message
from get_institution_data import get_institutions  # your DB function

# Load configuration
with open("config.json") as f:
    params = json.load(f)['params']

app = Flask(__name__)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = params['mail_server']
app.config['MAIL_PORT'] = params['mail_port']
app.config['MAIL_USE_TLS'] = params['mail_use_tls']
app.config['MAIL_USE_SSL'] = params['mail_use_ssl']
app.config['MAIL_USERNAME'] = params['gmail_user']
app.config['MAIL_PASSWORD'] = params['gmail_password']

mail = Mail(app)

def send_message_to_all():
    # Use application context
    with app.app_context():
        # Fetch all institutions
        record_insti = get_institutions()

        sent_emails = []
        failed_emails = []

        for inst in record_insti:
            recipient_email = inst.get("email")
            if recipient_email:
                try:
                    msg = Message(
                        subject='Message from User',
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[recipient_email],
                        body=f'You are selected for our internship. Please check your email for more details.'
                    )
                    mail.send(msg)
                    print(f"Email sent to {recipient_email}")
                    sent_emails.append(recipient_email)
                except Exception as e:
                    print(f"Failed to send to {recipient_email}: {e}")
                    failed_emails.append(recipient_email)

        print("\nSummary:")
        print(f"Sent emails ({len(sent_emails)}): {sent_emails}")
        print(f"Failed emails ({len(failed_emails)}): {failed_emails}")

if __name__ == "__main__":
    send_message_to_all()
