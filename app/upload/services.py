import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"py"}


def allowed_file(filename):

    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_python_file(file, upload_folder):

    if not allowed_file(file.filename):

        return None

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        upload_folder,
        filename
    )

    file.save(filepath)

    return filename