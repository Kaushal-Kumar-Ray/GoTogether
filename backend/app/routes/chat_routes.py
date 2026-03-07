from flask import Blueprint, request, session, jsonify
from datetime import datetime

from backend.app.services.json_storage import load_rides, save_rides

chat_bp = Blueprint("chat", __name__)


# -------- GET CHAT -------- #

@chat_bp.route("/chat/<ride_id>")
def get_chat(ride_id):

    rides = load_rides()
    user_email = session["email"]

    for ride in rides:

        if ride["ride_id"] == ride_id:

            if user_email in ride["joined_users"]:
                return jsonify(ride.get("messages", []))

            else:
                return jsonify({"error": "Access denied"}), 403

    return jsonify([])


# -------- SEND CHAT -------- #

@chat_bp.route("/chat/send/<ride_id>", methods=["POST"])
def send_chat(ride_id):

    rides = load_rides()
    user_email = session["email"]

    message_text = request.form.get("message")

    for ride in rides:

        if ride["ride_id"] == ride_id:

            if user_email not in ride["joined_users"]:
                return ("Access denied", 403)

            ride["messages"].append({

                "user": session["name"],
                "text": message_text,
                "time": datetime.now().strftime("%H:%M")

            })

            break

    save_rides(rides)

    return ("", 204)