from flask import Blueprint, render_template, session, redirect

from backend.app.services.json_storage import load_users, load_rides

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
def profile():

    users = load_users()
    rides = load_rides()

    user = next((u for u in users if u["email"] == session["email"]), None)

    if not user:
        session.clear()
        return redirect("/login")

    created = sum(1 for r in rides if r["creator_email"] == user["email"])

    joined = sum(1 for r in rides if user["email"] in r["joined_users"])

    return render_template(

        "profile.html",

        first_name=user["first_name"],
        last_name=user["last_name"],
        dob=user["dob"],
        contact=user["contact"],
        email=user["email"],

        rides_created=created,
        rides_joined=joined

    )