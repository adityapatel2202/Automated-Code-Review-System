from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField


class UploadForm(FlaskForm):

    python_file = FileField(
        "Python File",
        validators=[
            FileRequired()
        ]
    )

    submit = SubmitField("Upload")