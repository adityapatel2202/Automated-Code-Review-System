import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_to_a_secret_key")

    db_url = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "code_review.db"))
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = UPLOAD_FOLDER
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)