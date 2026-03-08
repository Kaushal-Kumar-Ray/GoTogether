import os
import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")


def send_email(receiver_email, otp):

    try:
        msg = MIMEText(f"""
GoTogether Verification Code

Your OTP is: {otp}

This code expires in 5 minutes.
""")

        msg["Subject"] = "GoTogether OTP Verification"
        msg["From"] = SMTP_USER
        msg["To"] = receiver_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        return True

    except Exception as e:
        print("Email error:", e)
        return False