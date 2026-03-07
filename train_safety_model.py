"""
GoTogether - Safety Risk Scorer Model Trainer
Run once: python train_safety_model.py
Saves model to: data/safety_model.pkl
"""

import os
import random
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# SYNTHETIC DATA GENERATION
# Rules that mirror real-world safety logic:
#   - Late night (22:00–05:00)  → higher risk
#   - Very early morning        → higher risk
#   - Solo / 1 passenger        → higher risk
#   - Long unknown routes       → moderate
#   - Peak hours + many seats   → low risk
# ─────────────────────────────────────────────

def generate_dataset(n=2000):
    rows = []
    for _ in range(n):
        hour = random.randint(0, 23)
        minute = random.choice([0, 15, 30, 45])
        seats_total = random.randint(2, 10)
        seats_filled = random.randint(1, seats_total)
        route_length = random.randint(1, 20)      # km proxy (1–20)
        is_campus_route = random.randint(0, 1)    # 1 = known campus route

        # ── feature engineering ──
        is_night    = 1 if (hour >= 22 or hour <= 5) else 0
        is_early    = 1 if (6 <= hour <= 7) else 0
        is_peak     = 1 if (hour in [8, 9, 17, 18, 19]) else 0
        fill_ratio  = seats_filled / seats_total
        lone_rider  = 1 if seats_filled == 1 else 0

        # ── label logic ──
        risk_score = 0
        risk_score += 3 if is_night else 0
        risk_score += 1 if is_early else 0
        risk_score -= 1 if is_peak else 0
        risk_score += 2 if lone_rider else 0
        risk_score -= 1 if fill_ratio > 0.6 else 0
        risk_score += 1 if route_length > 15 else 0
        risk_score -= 1 if is_campus_route else 0
        risk_score += random.randint(-1, 1)   # noise

        if risk_score >= 4:
            label = "high"
        elif risk_score >= 2:
            label = "moderate"
        else:
            label = "low"

        rows.append({
            "hour": hour,
            "minute": minute,
            "seats_total": seats_total,
            "seats_filled": seats_filled,
            "fill_ratio": round(fill_ratio, 2),
            "route_length": route_length,
            "is_campus_route": is_campus_route,
            "is_night": is_night,
            "is_early": is_early,
            "is_peak": is_peak,
            "lone_rider": lone_rider,
            "label": label
        })

    return pd.DataFrame(rows)


df = generate_dataset(2000)
print("Dataset distribution:")
print(df["label"].value_counts())

FEATURES = [
    "hour", "minute", "seats_total", "seats_filled",
    "fill_ratio", "route_length", "is_campus_route",
    "is_night", "is_early", "is_peak", "lone_rider"
]

X = df[FEATURES]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=150,
    max_depth=8,
    random_state=42,
    class_weight="balanced"
)
model.fit(X_train, y_train)

print("\nClassification Report:")
print(classification_report(y_test, model.predict(X_test)))

model_path = os.path.join(DATA_DIR, "safety_model.pkl")
joblib.dump(model, model_path)
print(f"\nModel saved to: {model_path}")
