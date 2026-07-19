import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_to_a_secret_key")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "code_review.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = UPLOAD_FOLDER
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024