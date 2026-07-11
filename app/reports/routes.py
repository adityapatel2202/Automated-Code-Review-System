from flask import render_template, request
from flask_login import login_required

from . import reports_bp
from app.analysis.analysis_manager import AnalysisManager


@reports_bp.route("/result")
@login_required
def result():

    filename = request.args.get("filename")

    manager = AnalysisManager()

    file_path = f"uploads/{filename}"

    result = manager.analyze(file_path)

    return render_template(
        "reports/result.html",
        result=result,
        filename=filename
    )