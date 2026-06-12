from flask import Flask, session, redirect, request

def create_app():

    app = Flask(
        __name__,
        template_folder="../../templates",
        static_folder="../../static"
    )

    app.secret_key = "GoTogether_secure_key"

    from backend.app.routes.auth_routes import auth_bp
    from backend.app.routes.ride_routes import ride_bp
    from backend.app.routes.chat_routes import chat_bp
    from backend.app.routes.sos_routes import sos_bp
    from backend.app.routes.support_routes import support_bp
    from backend.app.routes.profile_routes import profile_bp
    from backend.app.routes.ai_routes import ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(ride_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(sos_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(ai_bp)

    @app.before_request
    def require_login():

        allowed = [
            "auth.login",
            "auth.login_user",
            "auth.register",
            "auth.register_send_otp",
            "auth.register_verify",
            "auth.verify_security",
            "auth.reset_password",
            "static"
        ]

        if request.endpoint not in allowed and "email" not in session:
            return redirect("/login")

    return app

