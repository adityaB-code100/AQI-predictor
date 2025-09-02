from flask import Flask, request, render_template, jsonify
from twilio.rest import Client
import random
app = Flask(__name__)

# Replace these with your actual Twilio credentials
account_sid = 'AC652c5769a2b125b15650d26c38109ce6'
auth_token = '5b4d318883c82c5c9e0c9f9b21bf4091'
twilio_number = '+18483541225'

client = Client(account_sid, auth_token)

def generate_otp():
    return str(random.randint(100000, 999999))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone_number = data.get('phone')

    if not phone_number:
        return jsonify({'error': 'Phone number is required'}), 400

    otp = generate_otp()

    try:
        message = client.messages.create(
            body=f'Nikhil Dont take tension ',
            from_=twilio_number,
            to=phone_number
        )
        return jsonify({'message': 'OTP sent successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
