"""
app.py — Vault application factory and entry point.

Run with:
    python app.py

Or with Gunicorn (production):
    gunicorn -w 4 "app:create_app()"
"""

import os
from flask import Flask
from flask_login import LoginManager
from models import db, User


def create_app() -> Flask:
    app = Flask(__name__)

    # ── Config ────────────────────────────────────────────────────────────
    app.config["SECRET_KEY"]         = os.environ.get("SECRET_KEY", os.urandom(32))
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///vault.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"]      = os.path.join(app.root_path, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB hard Flask limit

    # Security headers
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    # Set SESSION_COOKIE_SECURE = True in production (HTTPS only)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Extensions ────────────────────────────────────────────────────────
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view     = "auth.login"
    login_manager.login_message  = "Please log in to access your Vault."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # ── CSRF protection via custom token ─────────────────────────────────
    # Flask-WTF CSRFProtect works globally; we handle it via meta tag + JS
    try:
        from flask_wtf.csrf import CSRFProtect
        CSRFProtect(app)
    except ImportError:
        pass  # Flask-WTF optional — remove if not installed

    # ── Blueprints ────────────────────────────────────────────────────────
    from routes.auth       import auth_bp
    from routes.dashboard  import dashboard_bp
    from routes.files      import files_bp
    from routes.notes      import notes_bp
    from routes.links      import links_bp
    from routes.passwords  import passwords_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(links_bp)
    app.register_blueprint(passwords_bp)

    # ── DB Init ───────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    # ── Security headers on every response ───────────────────────────────
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"]         = "DENY"
        response.headers["X-XSS-Protection"]        = "1; mode=block"
        response.headers["Referrer-Policy"]          = "strict-origin-when-cross-origin"
        return response

    return app


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True, host="0.0.0.0", port=5000)
