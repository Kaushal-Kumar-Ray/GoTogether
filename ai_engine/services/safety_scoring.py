import os
import joblib

# get project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

MODEL_PATH = os.path.join(BASE_DIR, "data", "safety_model.pkl")

safety_model = None

if os.path.exists(MODEL_PATH):
    safety_model = joblib.load(MODEL_PATH)
    print("✅ Safety model loaded")
else:
    print("❌ Safety model not found:", MODEL_PATH)

def extract_safety_features(ride):

    time_str = ride.get("time", "12:00")

    try:
        hour, minute = [int(x) for x in time_str.split(":")]
    except:
        hour, minute = 12, 0

    seats_total = ride.get("seats_total", 4)

    seats_filled = seats_total - ride.get("seats_available", seats_total)

    fill_ratio = seats_filled / seats_total if seats_total > 0 else 0

    # route length proxy
    route_length = min(
        20,
        (len(ride.get("from", "")) + len(ride.get("to", ""))) // 4
    )

    campus_keywords = [
        "campus",
        "hostel",
        "college",
        "library",
        "lab",
        "gate",
        "block",
        "admin"
    ]

    combined = (ride.get("from", "") + ride.get("to", "")).lower()

    is_campus_route = 1 if any(k in combined for k in campus_keywords) else 0

    is_night = 1 if (hour >= 22 or hour <= 5) else 0

    is_early = 1 if (6 <= hour <= 7) else 0

    is_peak = 1 if hour in [8, 9, 17, 18, 19] else 0

    lone_rider = 1 if seats_filled <= 1 else 0

    return [[
        hour,
        minute,
        seats_total,
        seats_filled,
        round(fill_ratio, 2),
        route_length,
        is_campus_route,
        is_night,
        is_early,
        is_peak,
        lone_rider
    ]]