import smtplib
import os
from email.message import EmailMessage

SENDER_EMAIL = os.environ.get("raykaushal456@gmail.com")
SENDER_PASSWORD = os.environ.get("opeqtylcxpjensjf")


def send_email(receiver_email, otp):

    msg = EmailMessage()
    msg.set_content(f"Your GoTogether Verification Code is: {otp}")
    msg["Subject"] = "GoTogether OTP"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        print("Email error:", e)    