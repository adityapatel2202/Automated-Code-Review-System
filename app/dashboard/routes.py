from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from . import dashboard_bp
from app import db
from app.models.review import Review


@dashboard_bp.route("/")
@login_required
def dashboard():

    # Query current user's reviews ordered by most recent first
    reviews = Review.query.filter_by(
        user_id=current_user.id
    ).order_by(Review.created_at.desc()).all()

    # Compute stats
    total_reviews = len(reviews)

    if total_reviews > 0:
        scores = [r.quality_score for r in reviews]
        avg_score = round(sum(scores) / len(scores), 1)
        best_score = round(max(scores), 1)
        worst_score = round(min(scores), 1)
    else:
        avg_score = 0
        best_score = 0
        worst_score = 0

    stats = {
        "total_reviews": total_reviews,
        "avg_score": avg_score,
        "best_score": best_score,
        "worst_score": worst_score,
    }

    return render_template(
        "dashboard/dashboard.html",
        reviews=reviews,
        stats=stats
    )