import os

class Config:
    SECRET_KEY = "automated_code_review_secret_key"

    SQLALCHEMY_DATABASE_URI = "sqlite:///code_review.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "uploads"