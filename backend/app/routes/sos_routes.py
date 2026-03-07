from flask import Blueprint, render_template, request, jsonify, session
from email.mime.text import MIMEText
import smtplib

from backend.app.services.email_service import SENDER_EMAIL, SENDER_PASSWORD

sos_bp = Blueprint("sos", __name__)


# -------- SOS PAGE -------- #

@sos_bp.route("/sos")
def sos():
    return render_template("sos.html")


# -------- SEND SOS LOCATION -------- #

@sos_bp.route("/sos/send_location", methods=["POST"])
def send_sos_location():

    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not latitude or not longitude:
        return jsonify({"error": "Location not provided"}), 400

    user_email = session["email"]

    maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

    message_body = f"""
🚨 EMERGENCY ALERT 🚨

Latitude: {latitude}
Longitude: {longitude}

View on Google Maps:
{maps_link}
"""

    msg = MIMEText(message_body)

    msg["Subject"] = "Emergency SOS Location Alert"
    msg["From"] = SENDER_EMAIL
    msg["To"] = user_email

    try:

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        server.send_message(msg)

        server.quit()

        return jsonify({"success": True})

    except Exception as e:

        return jsonify({"error": str(e)}), 500