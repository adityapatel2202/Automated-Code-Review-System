from flask import Blueprint

prediction_bp = Blueprint('prediction', __name__, url_prefix='/prediction')

from . import routes
