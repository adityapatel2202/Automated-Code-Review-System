from flask import Flask

def create_app():

    app = Flask(__name__)

    app.config.from_object("config.Config")

    from .auth import auth_bp

    app.register_blueprint(auth_bp)

    return app