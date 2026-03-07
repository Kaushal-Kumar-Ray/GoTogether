import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "raykaushal456@gmail.com"
SENDER_PASSWORD = "opeqtylcxpjensjf"


def send_email(receiver_email, otp):

    msg = EmailMessage()
    msg.set_content(f"Your GoTogether Verification Code is: {otp}")
    msg["Subject"] = "GoTogether OTP"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)