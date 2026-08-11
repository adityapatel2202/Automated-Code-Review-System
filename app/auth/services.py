from datetime import datetime
from flask_login import login_user
from sqlalchemy import func

from app import db
from app.models.user import User


def register_user(username, email, password, role="user"):
    user = User(
        username=username,
        email=email,
        role=role
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return user


def login_user_service(identifier, password):
    identifier = (identifier or "").strip().lower()

    user = User.query.filter(
        (func.lower(User.email) == identifier) | 
        (func.lower(User.username) == identifier)
    ).first()

    if user and user.check_password(password):
        if getattr(user, "status", "active") != "active":
            return False
        user.last_login = datetime.utcnow()
        db.session.commit()
        login_user(user)
        return True

    return False