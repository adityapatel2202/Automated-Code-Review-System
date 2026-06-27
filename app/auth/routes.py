from . import auth_bp
from flask import render_template

@auth_bp.route("/")
def home():
    return render_template("home.html")
