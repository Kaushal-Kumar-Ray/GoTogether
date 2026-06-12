from flask import Blueprint, render_template, request, redirect, session, jsonify
from datetime import datetime
import uuid

from backend.app.services.json_storage import load_rides, save_rides, load_users, save_users

ride_bp = Blueprint("ride", __name__)


# ---------------- DASHBOARD ---------------- #

@ride_bp.route("/")
def dashboard():

    rides = load_rides()

    user_email = session["email"]

    created_rides = [r for r in rides if r["creator_email"] == user_email]

    return render_template(
        "dashboard.html",
        created_rides=created_rides
    )


# ---------------- RIDES PAGE ---------------- #

@ride_bp.route("/rides")
def rides_page():
    return render_template("rides.html")


# ---------------- CREATE RIDE ---------------- #

@ride_bp.route("/create_ride", methods=["POST"])
def create_ride():

    rides = load_rides()
    users = load_users()

    user = next((u for u in users if u["email"] == session["email"]), None)

    if not user:
        session.clear()
        return redirect("/login")

    if user["active_ride_id"]:

        current_ride = next(
            (r for r in rides if r["ride_id"] == user["active_ride_id"] and session["email"] in r["joined_users"]),
            None
        )

        if not current_ride:
            user["active_ride_id"] = None
            save_users(users)

    if user["active_ride_id"]:

        current_ride = next(
            (r for r in rides if r["ride_id"] == user["active_ride_id"]),
            None
        )

        if current_ride:
            return redirect("/")

    seats = int(request.form["seats"])

    new_ride = {

        "ride_id": str(uuid.uuid4()),
        "creator_email": session["email"],

        "from": request.form["from"],
        "to": request.form["to"],
        "time": request.form["time"],

        "seats_total": seats,
        "seats_available": seats - 1,

        "joined_users": [session["email"]],
        "pending_requests": [],
        "messages": [],

        "created_at": datetime.now().isoformat()
    }

    rides.append(new_ride)

    user["active_ride_id"] = new_ride["ride_id"]

    save_rides(rides)
    save_users(users)

    return redirect("/rides")


# ---------------- REQUEST JOIN ---------------- #

@ride_bp.route("/request_join/<ride_id>", methods=["POST"])
def request_join(ride_id):

    rides = load_rides()
    users = load_users()

    user = next((u for u in users if u["email"] == session["email"]), None)

    if not user:
        session.clear()
        return jsonify({"error": "Session expired"}), 401

    if user["active_ride_id"]:

        current_ride = next(
            (r for r in rides if r["ride_id"] == user["active_ride_id"] and session["email"] in r["joined_users"]),
            None
        )

        if not current_ride:
            user["active_ride_id"] = None
            save_users(users)

    ride = next((r for r in rides if r["ride_id"] == ride_id), None)

    if not ride:
        return jsonify({"error": "Ride not found"}), 404

    if session["email"] in ride["joined_users"]:
        return jsonify({"error": "You already joined"}), 400

    pending = ride.get("pending_requests", [])

    if any(p["email"] == session["email"] for p in pending):
        return jsonify({"error": "Request already pending"}), 400

    if user["active_ride_id"] and user["active_ride_id"] != ride_id:

        current_ride = next(
            (r for r in rides if r["ride_id"] == user["active_ride_id"]),
            None
        )

        if current_ride:
            return jsonify({
                "error": f"You already joined ride {current_ride['from']} → {current_ride['to']}"
            }), 400

    if ride["seats_available"] <= 0:
        return jsonify({"error": "Ride full"}), 400

    ride["pending_requests"].append({

        "email": session["email"],
        "name": session["name"],
        "requested_at": datetime.now().isoformat()

    })

    save_rides(rides)

    return jsonify({"message": "Join request sent"}), 200


# ---------------- APPROVE REQUEST ---------------- #

@ride_bp.route("/approve_request/<ride_id>/<requester_email>", methods=["POST"])
def approve_request(ride_id, requester_email):

    rides = load_rides()
    users = load_users()

    ride = next((r for r in rides if r["ride_id"] == ride_id), None)

    if not ride:
        return jsonify({"error": "Ride not found"}), 404

    if ride["creator_email"] != session["email"]:
        return jsonify({"error": "Only creator can approve"}), 403

    pending = ride.get("pending_requests", [])

    req = next((p for p in pending if p["email"] == requester_email), None)

    if not req:
        return jsonify({"error": "Request not found"}), 404

    if ride["seats_available"] <= 0:

        ride["pending_requests"] = [
            p for p in pending if p["email"] != requester_email
        ]

        save_rides(rides)

        return jsonify({"error": "Ride full"}), 400

    ride["pending_requests"] = [
        p for p in pending if p["email"] != requester_email
    ]

    ride["joined_users"].append(requester_email)

    ride["seats_available"] -= 1

    requester_user = next((u for u in users if u["email"] == requester_email), None)

    if requester_user:
        requester_user["active_ride_id"] = ride_id

    save_rides(rides)
    save_users(users)

    return jsonify({"message": "User approved"}), 200


# ---------------- REJECT REQUEST ---------------- #

@ride_bp.route("/reject_request/<ride_id>/<requester_email>", methods=["POST"])
def reject_request(ride_id, requester_email):

    rides = load_rides()

    ride = next((r for r in rides if r["ride_id"] == ride_id), None)

    if not ride:
        return jsonify({"error": "Ride not found"}), 404

    if ride["creator_email"] != session["email"]:
        return jsonify({"error": "Only creator can reject"}), 403

    pending = ride.get("pending_requests", [])

    ride["pending_requests"] = [
        p for p in pending if p["email"] != requester_email
    ]

    save_rides(rides)

    return jsonify({"message": "Request rejected"}), 200


# ---------------- CANCEL REQUEST ---------------- #

@ride_bp.route("/cancel_request/<ride_id>", methods=["POST"])
def cancel_request(ride_id):

    rides = load_rides()

    ride = next((r for r in rides if r["ride_id"] == ride_id), None)

    if not ride:
        return jsonify({"error": "Ride not found"}), 404

    pending = ride.get("pending_requests", [])

    ride["pending_requests"] = [
        p for p in pending if p["email"] != session["email"]
    ]

    save_rides(rides)

    return jsonify({"message": "Request cancelled"}), 200


# ---------------- DELETE RIDE ---------------- #

@ride_bp.route("/delete/<ride_id>")
def delete_ride(ride_id):

    rides = load_rides()
    users = load_users()

    ride = next((r for r in rides if r["ride_id"] == ride_id), None)

    if not ride:
        return redirect("/")

    if ride["creator_email"] != session["email"]:
        return redirect("/")

    for joined_email in ride["joined_users"]:

        joined_user = next((u for u in users if u["email"] == joined_email), None)

        if joined_user and joined_user["active_ride_id"] == ride_id:
            joined_user["active_ride_id"] = None

    rides = [r for r in rides if r["ride_id"] != ride_id]

    save_rides(rides)
    save_users(users)

    return redirect("/")

# ---------------- RIDES DATA API ---------------- #

@ride_bp.route("/rides/data")
def rides_data():

    rides = load_rides()
    user_email = session["email"]

    search_from = request.args.get("from", "").lower()
    search_to = request.args.get("to", "").lower()

    filtered = []

    for ride in rides:

        if search_from and search_from not in ride["from"].lower():
            continue

        if search_to and search_to not in ride["to"].lower():
            continue

        ride["is_joined"] = user_email in ride["joined_users"]
        ride["is_full"] = ride["seats_available"] <= 0
        ride["is_creator"] = ride["creator_email"] == user_email

        pending = ride.get("pending_requests", [])

        ride["is_pending"] = any(p["email"] == user_email for p in pending)

        if ride["is_creator"]:
            ride["pending_requests_data"] = pending
        else:
            ride["pending_requests_data"] = []

        filtered.append(ride)

    return jsonify(filtered)