from flask import Blueprint, render_template, request, jsonify, session
import requests

from backend.app.services.json_storage import load_rides
from ai_engine.services.safety_scoring import extract_safety_features, safety_model

ai_bp = Blueprint("ai", __name__)

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjVhNzNhMjRkYzMzMTRkYzk5M2JkMDg2YzY0ZDcwOTZlIiwiaCI6Im11cm11cjY0In0="


# -------- AI PAGE -------- #

@ai_bp.route("/ai")
def ai_page():

    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    return render_template("ai.html")


# -------- GEOCODE -------- #

def geocode_location(place):

    url = "https://api.openrouteservice.org/geocode/search"

    headers = {"Authorization": ORS_API_KEY}

    params = {"text": place}

    res = requests.get(url, headers=headers, params=params)

    data = res.json()

    if data.get("features"):

        coords = data["features"][0]["geometry"]["coordinates"]

        return coords

    return None


# -------- ROUTE OPTIMIZER -------- #

@ai_bp.route("/ai/ask", methods=["POST"])
def ai_ask():

    data = request.get_json()

    question = data.get("question", "")

    stops = [s.strip() for s in question.split("-") if s.strip()]

    if len(stops) < 2:
        return jsonify({"error": "Provide at least 2 locations"}), 400

    coordinates = []

    for stop in stops:

        coords = geocode_location(stop)

        if not coords:
            return jsonify({"error": f"Location not found {stop}"}), 400

        coordinates.append(coords)

    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"

    headers = {

        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"

    }

    response = requests.post(url, json={"coordinates": coordinates}, headers=headers)

    result = response.json()

    summary = result["features"][0]["properties"]["summary"]

    duration = summary["duration"] / 60
    distance = summary["distance"] / 1000

    ai_response = f"""

Optimized Route:
{' → '.join(stops)}

Distance: {distance:.2f} km
Time: {duration:.1f} minutes
"""

    return jsonify({"answer": ai_response})


# -------- SAFETY SCORE -------- #

@ai_bp.route("/ai/safety_score/<ride_id>")
def ai_safety_score(ride_id):

    rides = load_rides()

    ride = next((r for r in rides if r["ride_id"] == ride_id), None)

    if not ride:
        return jsonify({"error": "Ride not found"}), 404

    features = extract_safety_features(ride)

    prediction = safety_model.predict(features)[0]

    proba = safety_model.predict_proba(features)[0]

    confidence = round(float(max(proba)) * 100)

    return jsonify({

        "level": prediction,
        "confidence": confidence

    })