from flask import render_template
from flask_login import login_required

from . import upload_bp


@upload_bp.route("/")
@login_required
def upload():

    return render_template("upload/upload.html")