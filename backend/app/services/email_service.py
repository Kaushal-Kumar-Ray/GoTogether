import os
import requests

BREVO_API_KEY = os.environ.get("BREVO_API_KEY")


def send_email(receiver_email, otp):

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    data = {
        "sender": {
            "name": "GoTogether",
            "email": "raykaushal456@gmail.com"
        },
        "to": [
            {"email": receiver_email}
        ],
        "subject": "GoTogether OTP Verification",
        "htmlContent": f"""
        <h2>GoTogether Verification Code</h2>
        <p>Your OTP is:</p>
        <h1>{otp}</h1>
        <p>This code expires in 5 minutes.</p>
        """
    }

    try:
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            return True
        else:
            print("Email error:", response.text)
            return False

    except Exception as e:
        print("Email error:", e)
        return False