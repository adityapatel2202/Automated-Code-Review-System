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