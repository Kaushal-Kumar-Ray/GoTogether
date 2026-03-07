from flask import Blueprint, render_template

support_bp = Blueprint("support", __name__)


# -------- SUPPORT PAGE -------- #

@support_bp.route("/support")
def support():
    return render_template("support.html")