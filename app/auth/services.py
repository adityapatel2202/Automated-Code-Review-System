from flask_login import login_user

from app import db
from app.models.user import User


def register_user(username, email, password):
    user = User(
        username=username,
        email=email
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return user


def login_user_service(email, password):
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user)
        return True

    return False