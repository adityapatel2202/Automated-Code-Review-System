from flask import (
    render_template,
    current_app,
    flash,
    redirect,
    url_for
)

from flask_login import login_required

from . import upload_bp
from .forms import UploadForm
from .services import save_python_file


@upload_bp.route("/", methods=["GET", "POST"])
@login_required
def upload():

    form = UploadForm()

    if form.validate_on_submit():

        filename = save_python_file(
            form.python_file.data,
            current_app.config["UPLOAD_FOLDER"]
        )

        if filename:

            flash(
                f"{filename} uploaded successfully!",
                "success"
            )

            return redirect(
                url_for(
                    "reports.result",
                    filename=filename
                )
            )

        else:

            flash(
                "Only Python (.py) files are allowed.",
                "danger"
            )

    return render_template(
        "upload/upload.html",
        form=form
    )