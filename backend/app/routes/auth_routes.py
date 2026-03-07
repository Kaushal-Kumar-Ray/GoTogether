from flask import Blueprint, render_template, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random

from backend.app.services.json_storage import load_users, save_users
from backend.app.services.email_service import send_email
import re

auth_bp = Blueprint("auth", __name__)

otp_data = {}


# ---------------- PASSWORD VALIDATION ---------------- #

def is_strong_password(password):

    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    return True


# ---------------- REGISTER PAGE ---------------- #

@auth_bp.route("/register")
def register():
    return render_template("register.html")


# ---------------- SEND OTP ---------------- #

@auth_bp.route("/register/send_otp", methods=["POST"])
def register_send_otp():

    email = request.json.get("email")

    otp = str(random.randint(100000, 999999))

    expiry = datetime.now().timestamp() + 180

    otp_data[email] = {
        "otp": otp,
        "expiry": expiry
    }

    send_email(email, otp)

    return jsonify({"message": "OTP sent"}), 200


# ---------------- VERIFY REGISTER ---------------- #

@auth_bp.route("/register/verify", methods=["POST"])
def register_verify():

    data = request.json

    email = data.get("email")
    otp = data.get("otp")
    password = data.get("password")

    if email not in otp_data:
        return jsonify({"error": "OTP expired"}), 400

    stored = otp_data[email]

    if datetime.now().timestamp() > stored["expiry"]:
        del otp_data[email]
        return jsonify({"error": "OTP expired"}), 400

    if stored["otp"] != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    users = load_users()

    if any(u["email"] == email for u in users):
        return jsonify({"error": "User already exists"}), 400

    if not is_strong_password(password):
        return jsonify({
            "error": "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
        }), 400

    new_user = {

        "email": email,
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "dob": data.get("dob"),
        "contact": data.get("contact"),
        "password": generate_password_hash(password),

        "security_q1": data.get("security_q1"),
        "security_a1": data.get("security_a1"),

        "security_q2": data.get("security_q2"),
        "security_a2": data.get("security_a2"),

        "active_ride_id": None
    }

    users.append(new_user)

    save_users(users)

    session["email"] = email
    session["name"] = data.get("first_name") + " " + data.get("last_name")

    del otp_data[email]

    return jsonify({"redirect": "/"}), 200


# ---------------- LOGIN PAGE ---------------- #

@auth_bp.route("/login")
def login():
    return render_template("login.html")


# ---------------- LOGIN USER ---------------- #

@auth_bp.route("/login_user", methods=["POST"])
def login_user():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    users = load_users()

    user = next((u for u in users if u["email"] == email), None)

    if not user:
        return jsonify({"error": "User not found"}), 400

    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Incorrect password"}), 400

    session["email"] = user["email"]
    session["name"] = user["first_name"] + " " + user["last_name"]

    return jsonify({"redirect": "/"}), 200


# ---------------- SECURITY QUESTIONS ---------------- #

@auth_bp.route("/forgot_password/verify_security", methods=["POST"])
def verify_security():

    data = request.json

    email = data.get("email")
    answer1 = data.get("answer1")
    answer2 = data.get("answer2")

    users = load_users()

    user = next((u for u in users if u["email"] == email), None)

    if not user:
        return jsonify({"error": "User not found"}), 400

    if user.get("security_a1") != answer1 or user.get("security_a2") != answer2:
        return jsonify({"error": "Security answers incorrect"}), 400

    otp = str(random.randint(100000, 999999))

    expiry = datetime.now().timestamp() + 180

    otp_data[email] = {
        "otp": otp,
        "expiry": expiry
    }

    send_email(email, otp)

    return jsonify({"success": True}), 200


# ---------------- RESET PASSWORD ---------------- #

@auth_bp.route("/reset_password", methods=["POST"])
def reset_password():

    data = request.json

    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("new_password")

    if email not in otp_data:
        return jsonify({"error": "OTP expired"}), 400

    stored = otp_data[email]

    if datetime.now().timestamp() > stored["expiry"]:
        del otp_data[email]
        return jsonify({"error": "OTP expired"}), 400

    if stored["otp"] != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    if not is_strong_password(new_password):
        return jsonify({
            "error": "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
        }), 400

    users = load_users()

    user = next((u for u in users if u["email"] == email), None)

    if not user:
        return jsonify({"error": "User not found"}), 400

    user["password"] = generate_password_hash(new_password)

    save_users(users)

    del otp_data[email]

    return jsonify({"success": True}), 200


# ---------------- LOGOUT ---------------- #

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/login")