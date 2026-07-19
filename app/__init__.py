from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))


def create_app():

    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from .auth import auth_bp
    
    app.register_blueprint(auth_bp)

    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from .upload import upload_bp
    app.register_blueprint(upload_bp)
    
    from .reports import reports_bp
    app.register_blueprint(reports_bp)

    from .prediction import prediction_bp
    app.register_blueprint(prediction_bp)

    return app