from dotenv import load_dotenv
import os

# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()

from flask import Flask
from flask_cors import CORS

# =====================================================
# IMPORT BLUEPRINTS
# =====================================================

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.public import public_bp

# =====================================================
# CREATE APP
# =====================================================

app = Flask(__name__)

# =====================================================
# BASIC CONFIG
# =====================================================

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "change-me"
)

app.config["UPLOAD_FOLDER"] = os.getenv(
    "UPLOAD_FOLDER",
    "static/uploads"
)

app.config["MAX_CONTENT_LENGTH"] = int(
    os.getenv(
        "MAX_CONTENT_LENGTH",
        "5242880"
    )
)

# =====================================================
# SESSION SECURITY
# =====================================================

app.config["SESSION_COOKIE_HTTPONLY"] = (
    os.getenv(
        "SESSION_COOKIE_HTTPONLY",
        "True"
    ).lower() == "true"
)

app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv(
        "SESSION_COOKIE_SECURE",
        "False"
    ).lower() == "true"
)

app.config["SESSION_COOKIE_SAMESITE"] = os.getenv(
    "SESSION_COOKIE_SAMESITE",
    "Lax"
)

# =====================================================
# CORS
# =====================================================

frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5000"
)

if frontend_url:
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [frontend_url]
            }
        }
    )
else:
    CORS(app)

# =====================================================
# UPLOAD FOLDER
# =====================================================

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)

# =====================================================
# REGISTER BLUEPRINTS
# =====================================================

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(public_bp)

# =====================================================
# STARTUP INFO
# =====================================================

print("\n" + "=" * 60)
print("Website HIMATKN")
print("=" * 60)

print(
    "FLASK_ENV:",
    os.getenv("FLASK_ENV")
)

print(
    "FLASK_DEBUG:",
    os.getenv("FLASK_DEBUG")
)

print(
    "FRONTEND_URL:",
    frontend_url
)

print(
    "DB_HOST:",
    os.getenv("DB_HOST")
)

print(
    "DB_NAME:",
    os.getenv("DB_NAME")
)

print(
    "DB_USER:",
    os.getenv("DB_USER")
)

print("=" * 60 + "\n")

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv(
            "FLASK_DEBUG",
            "False"
        ).lower() == "true"
    )