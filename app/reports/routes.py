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


def _build_fast_review_result(review):
    """
    Build result dictionary from saved Review database record instantly
    without re-running heavy AI model inference.
    """
    file_path = f"uploads/{review.filename}"
    source_code = ""
    try:
        from app.analysis.code_reader import CodeReader
        source_code = CodeReader().read(file_path)
    except Exception:
        source_code = review.refactored_code or review.clean_code or "# Source code file no longer available on server disk."

    ast_analysis = {}
    issues_found = []
    suggestions = []
    try:
        from app.analysis.ast_analyzer import ASTAnalyzer
        from app.analysis.pylint_analyzer import PylintAnalyzer
        from app.analysis.suggestion_engine import SuggestionEngine

        ast_analysis = ASTAnalyzer().analyze(file_path)
        pylint_res = PylintAnalyzer().analyze(file_path)
        issues_found = pylint_res.get("issues", [])
        suggestions = SuggestionEngine().generate(issues_found)
    except Exception:
        ast_analysis = {
            "functions": 0, "classes": 0, "variables": 0, "imports": 0,
            "loops": 0, "if_statements": 0, "try_blocks": 0, "returns": 0,
            "function_calls": 0, "comments": 0
        }

    chg_list = review.changes.split("\n") if review.changes else []

    return {
        "quality_score": review.quality_score,
        "issue_count": review.issue_count,
        "issues_found": issues_found,
        "suggestions": suggestions,
        "ast_analysis": ast_analysis,
        "source_code": source_code,
        "ai_result": {
            "clean_code": review.clean_code or source_code,
            "best_practice": review.best_practice_code or source_code,
            "optimized_code": review.optimized_code or source_code,
            "changes": chg_list if chg_list else ["PEP 8 formatting and code structure refactored."]
        },
        "semantic_analysis": {
            "embedding_dimension": 768,
            "token_count": len(source_code.split()) if source_code else 0,
            "semantic_score": review.semantic_score or review.quality_score,
            "confidence": review.ml_confidence or 85.0
        },
        "ml_prediction": {
            "quality_label": review.ml_prediction or "Good",
            "prediction": review.ml_prediction or "Good",
            "confidence": review.ml_confidence or 85.0
        } if review.ml_prediction else None,
    }


@reports_bp.route("/review/<int:review_id>")
@login_required
def view_review(review_id):
    review = Review.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    result = _build_fast_review_result(review)

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

    result = _build_fast_review_result(review)

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
        code = review.refactored_code or "# Refactored code not available."

    response = make_response(code)
    response.headers["Content-Disposition"] = f"attachment; filename={version}_{review.filename}"
    response.headers["Content-Type"] = "text/x-python"
    return response