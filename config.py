import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = "change_this_to_a_secret_key"

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" +
        os.path.join(BASE_DIR, "code_review.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "uploads"