from flask import render_template, request
from flask_login import login_required, current_user

from . import reports_bp
from app import db
from app.analysis.analysis_manager import AnalysisManager
from app.models.review import Review


@reports_bp.route("/result")
@login_required
def result():

    filename = request.args.get("filename")

    manager = AnalysisManager()

    file_path = f"uploads/{filename}"

    result = manager.analyze(file_path)

    # Extract ML prediction data for saving
    ml_pred = result.get("ml_prediction")
    ml_label = None
    ml_conf = None
    if ml_pred and isinstance(ml_pred, dict):
        ml_label = ml_pred.get("prediction")
        ml_conf = ml_pred.get("confidence")

    # Extract semantic score
    semantic = result.get("semantic_analysis", {})
    semantic_score = None
    if semantic and isinstance(semantic, dict):
        semantic_score = semantic.get("semantic_score")

    # Extract AI refactored code and explanation
    ai_res = result.get("ai_result", {})
    clean_code = ai_res.get("clean_code")
    best_practice_code = ai_res.get("best_practice")
    optimized_code = ai_res.get("optimized_code")
    changes_list = ai_res.get("changes", [])
    changes_str = "\n".join(changes_list) if isinstance(changes_list, list) else str(changes_list)

    # Save review to database
    review = Review(
        user_id=current_user.id,
        filename=filename,
        quality_score=result.get("quality_score", 0),
        ml_prediction=ml_label,
        ml_confidence=ml_conf,
        issue_count=result.get("issue_count", 0),
        semantic_score=semantic_score,
        clean_code=clean_code,
        best_practice_code=best_practice_code,
        optimized_code=optimized_code,
        changes=changes_str,
    )
    db.session.add(review)
    db.session.commit()

    return render_template(
        "reports/result.html",
        result=result,
        filename=filename,
        review_id=review.id
    )


@reports_bp.route("/review/<int:review_id>")
@login_required
def view_review(review_id):

    review = Review.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    # Re-run analysis to get full results
    file_path = f"uploads/{review.filename}"
    try:
        manager = AnalysisManager()
        result = manager.analyze(file_path)
    except Exception:
        chg_list = review.changes.split("\n") if review.changes else []
        result = {
            "quality_score": review.quality_score,
            "issue_count": review.issue_count,
            "issues_found": [],
            "suggestions": [],
            "ast_analysis": {},
            "source_code": "File no longer available.",
            "ai_result": {
                "clean_code": review.clean_code or "",
                "best_practice": review.best_practice_code or "",
                "optimized_code": review.optimized_code or "",
                "changes": chg_list
            },
            "semantic_analysis": {},
            "ml_prediction": {
                "quality_label": review.ml_prediction or "Unknown",
                "prediction": review.ml_prediction or "Unknown",
                "confidence": review.ml_confidence or 0.0
            } if review.ml_prediction else None,
        }

    return render_template(
        "reports/result.html",
        result=result,
        filename=review.filename,
        review_id=review.id
    )


@reports_bp.route("/download/<int:review_id>")
@login_required
def download_report(review_id):
    from flask import make_response
    from app.analysis.report_builder import ReportBuilder

    review = Review.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    file_path = f"uploads/{review.filename}"
    try:
        manager = AnalysisManager()
        result = manager.analyze(file_path)
    except Exception:
        chg_list = review.changes.split("\n") if review.changes else []
        result = {
            "quality_score": review.quality_score,
            "issue_count": review.issue_count,
            "issues_found": [],
            "suggestions": [],
            "ast_analysis": {},
            "source_code": "File no longer available.",
            "ai_result": {
                "clean_code": review.clean_code or "",
                "best_practice": review.best_practice_code or "",
                "optimized_code": review.optimized_code or "",
                "changes": chg_list
            },
            "semantic_analysis": {},
            "ml_prediction": {
                "quality_label": review.ml_prediction or "Unknown",
                "prediction": review.ml_prediction or "Unknown",
                "confidence": review.ml_confidence or 0.0
            } if review.ml_prediction else None,
        }

    builder = ReportBuilder()
    html_content = builder.build_html_report(result, review.filename)

    response = make_response(html_content)
    response.headers["Content-Disposition"] = f"attachment; filename=report_{review.filename}.html"
    response.headers["Content-Type"] = "text/html"
    return response


@reports_bp.route("/download_refactored/<int:review_id>")
@login_required
def download_refactored(review_id):
    from flask import make_response, request

    review = Review.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    version = request.args.get("version", "best_practice")
    
    if version == "clean":
        code = review.clean_code
    elif version == "optimized":
        code = review.optimized_code
    else:
        code = review.best_practice_code

    if not code:
        return "Refactored code version not available.", 404

    response = make_response(code)
    response.headers["Content-Disposition"] = f"attachment; filename={version}_{review.filename}"
    response.headers["Content-Type"] = "text/x-python"
    return response