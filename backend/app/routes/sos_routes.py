from flask import Blueprint, render_template, request, jsonify, session
import os
import requests

sos_bp = Blueprint("sos", __name__)

BREVO_API_KEY = os.environ.get("BREVO_API_KEY")


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

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "name": "GoTogether",
            "email": "raykaushal456@gmail.com"
        },
        "to": [
            {"email": user_email}
        ],
        "subject": "🚨 Emergency SOS Location Alert",
        "htmlContent": f"""
        <h2>🚨 Emergency Alert</h2>

        <p>Your SOS button was triggered in <strong>GoTogether</strong>.</p>

        <p><strong>Latitude:</strong> {latitude}</p>
        <p><strong>Longitude:</strong> {longitude}</p>

        <p>
        <a href="{maps_link}"
        style="background:#e63946;color:white;padding:10px 18px;text-decoration:none;border-radius:6px;">
        View Location on Google Maps
        </a>
        </p>

        <p>If this was accidental you can ignore this message.</p>
        """
    }

    try:

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            return jsonify({"success": True})
        else:
            print("Brevo error:", response.text)
            return jsonify({"error": "Failed to send SOS email"}), 500

    except Exception as e:
        print("SOS email error:", e)
        return jsonify({"error": "Failed to send SOS email"}), 500