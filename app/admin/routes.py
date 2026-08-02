from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_user, logout_user

from app import db
from . import admin_bp
from .decorators import admin_required
from app.models.user import User
from app.models.review import Review
from .dashboard import get_dashboard_metrics, get_recent_dashboard_activity, parse_dash_date_range
from .analytics import get_analytics_data


@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    """
    Dedicated Admin Login Route.
    """
    if current_user.is_authenticated:
        if getattr(current_user, "role", "user") == "admin":
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Current account does not have admin privileges.", "danger")
            return redirect(url_for("auth.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if getattr(user, "role", "user") != "admin":
                flash("Access denied. Admin credentials required.", "danger")
                return redirect(url_for("admin.admin_login"))
            if getattr(user, "status", "active") != "active":
                flash("Account is disabled.", "danger")
                return redirect(url_for("admin.admin_login"))

            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user)
            flash("Admin login successful!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin.dashboard"))

        flash("Invalid admin email or password.", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/")
@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """
    Admin Dashboard view displaying 13 metrics, date filtering, and registered users modal inspection.
    """
    date_filter = request.args.get("date_filter", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    if date_filter == "today":
        display_range = "Today"
    elif date_filter == "yesterday":
        display_range = "Yesterday"
    elif date_filter == "last_7_days":
        display_range = "Last 7 Days"
    elif date_filter == "this_month":
        display_range = "This Month"
    elif date_filter == "last_30_days":
        display_range = "Last 30 Days"
    elif date_filter == "custom" and start_date and end_date:
        display_range = f"{start_date} to {end_date}"
    else:
        display_range = "All Time"

    metrics = get_dashboard_metrics(date_filter, start_date, end_date)
    recent_users, recent_reviews = get_recent_dashboard_activity(10, date_filter, start_date, end_date)

    return render_template(
        "admin/dashboard.html",
        metrics=metrics,
        recent_users=recent_users,
        recent_reviews=recent_reviews,
        date_filter=date_filter,
        start_date=start_date,
        end_date=end_date,
        display_range=display_range
    )


@admin_bp.route("/dashboard/registered-users")
@admin_required
def get_registered_users_json():
    """
    API endpoint returning JSON list of users registered within a timeframe for modal inspection.
    """
    date_filter = request.args.get("date_filter", "today").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    start_dt, end_dt = parse_dash_date_range(date_filter, start_date, end_date)

    query = User.query
    if start_dt and end_dt:
        query = query.filter(User.created_at >= start_dt, User.created_at <= end_dt)

    users_list = query.order_by(User.created_at.desc()).all()

    users_data = []
    for u in users_list:
        users_data.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "status": u.status,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else "N/A",
            "total_uploads": u.reviews.count()
        })

    return jsonify({
        "success": True,
        "date_filter": date_filter,
        "count": len(users_data),
        "users": users_data
    })


# ==========================================
# USER MANAGEMENT SUBSYSTEM
# ==========================================

@admin_bp.route("/users")
@admin_required
def users():
    page = request.args.get("page", 1, type=int)
    search_q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    date_filter = request.args.get("date_filter", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    query = User.query

    if search_q:
        query = query.filter(
            (User.username.ilike(f"%{search_q}%")) |
            (User.email.ilike(f"%{search_q}%"))
        )

    if status_filter in ["active", "disabled"]:
        query = query.filter(User.status == status_filter)

    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)

    if date_filter == "today":
        query = query.filter(User.created_at >= today_start)
    elif date_filter == "yesterday":
        y_start = today_start - timedelta(days=1)
        y_end = today_start - timedelta(seconds=1)
        query = query.filter(User.created_at >= y_start, User.created_at <= y_end)
    elif date_filter == "last_7_days":
        query = query.filter(User.created_at >= (today_start - timedelta(days=7)))
    elif date_filter == "last_30_days":
        query = query.filter(User.created_at >= (today_start - timedelta(days=30)))
    elif date_filter == "custom" and start_date and end_date:
        try:
            s_dt = datetime.strptime(start_date, "%Y-%m-%d")
            e_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(User.created_at >= s_dt, User.created_at <= e_dt)
        except ValueError:
            pass

    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template(
        "admin/users.html",
        users=pagination.items,
        pagination=pagination,
        search_q=search_q,
        status_filter=status_filter,
        date_filter=date_filter,
        start_date=start_date,
        end_date=end_date
    )


@admin_bp.route("/users/<int:user_id>/json")
@admin_required
def get_user_json(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "status": user.status,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "N/A",
        "last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else "Never",
        "total_uploads": user.reviews.count()
    })


@admin_bp.route("/users/<int:user_id>/disable", methods=["POST"])
@admin_required
def disable_user(user_id):
    if user_id == current_user.id:
        return jsonify({"success": False, "error": "You cannot disable your own admin account."}), 400

    user = User.query.get_or_404(user_id)
    user.status = "disabled"
    db.session.commit()
    return jsonify({"success": True, "message": f"User '{user.username}' has been disabled."})


@admin_bp.route("/users/<int:user_id>/enable", methods=["POST"])
@admin_required
def enable_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = "active"
    db.session.commit()
    return jsonify({"success": True, "message": f"User '{user.username}' has been activated."})


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        return jsonify({"success": False, "error": "You cannot delete your own admin account."}), 400

    user = User.query.get_or_404(user_id)
    username = user.username

    Review.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()

    return jsonify({"success": True, "message": f"User '{username}' and associated data deleted."})


# ==========================================
# UPLOAD MANAGEMENT SUBSYSTEM
# ==========================================

@admin_bp.route("/uploads")
@admin_required
def uploads():
    page = request.args.get("page", 1, type=int)
    search_q = request.args.get("q", "").strip()
    date_filter = request.args.get("date_filter", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    query = Review.query.join(User, Review.user_id == User.id)

    if search_q:
        query = query.filter(
            (Review.filename.ilike(f"%{search_q}%")) |
            (User.username.ilike(f"%{search_q}%"))
        )

    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)

    if date_filter == "today":
        query = query.filter(Review.created_at >= today_start)
    elif date_filter == "yesterday":
        y_start = today_start - timedelta(days=1)
        y_end = today_start - timedelta(seconds=1)
        query = query.filter(Review.created_at >= y_start, Review.created_at <= y_end)
    elif date_filter == "last_7_days":
        query = query.filter(Review.created_at >= (today_start - timedelta(days=7)))
    elif date_filter == "last_30_days":
        query = query.filter(Review.created_at >= (today_start - timedelta(days=30)))
    elif date_filter == "custom" and start_date and end_date:
        try:
            s_dt = datetime.strptime(start_date, "%Y-%m-%d")
            e_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(Review.created_at >= s_dt, Review.created_at <= e_dt)
        except ValueError:
            pass

    pagination = query.order_by(Review.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template(
        "admin/uploads.html",
        uploads=pagination.items,
        pagination=pagination,
        search_q=search_q,
        date_filter=date_filter,
        start_date=start_date,
        end_date=end_date
    )


@admin_bp.route("/uploads/<int:review_id>/delete", methods=["POST"])
@admin_required
def delete_upload(review_id):
    review = Review.query.get_or_404(review_id)
    filename = review.filename
    db.session.delete(review)
    db.session.commit()
    return jsonify({"success": True, "message": f"File '{filename}' and review record deleted."})


# ==========================================
# REPORT MANAGEMENT SUBSYSTEM
# ==========================================

@admin_bp.route("/reports")
@admin_required
def reports():
    page = request.args.get("page", 1, type=int)
    search_q = request.args.get("q", "").strip()
    date_filter = request.args.get("date_filter", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    query = Review.query.join(User, Review.user_id == User.id)

    if search_q:
        query = query.filter(
            (Review.filename.ilike(f"%{search_q}%")) |
            (User.username.ilike(f"%{search_q}%")) |
            (Review.ml_prediction.ilike(f"%{search_q}%"))
        )

    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)

    if date_filter == "today":
        query = query.filter(Review.created_at >= today_start)
    elif date_filter == "yesterday":
        y_start = today_start - timedelta(days=1)
        y_end = today_start - timedelta(seconds=1)
        query = query.filter(Review.created_at >= y_start, Review.created_at <= y_end)
    elif date_filter == "last_7_days":
        query = query.filter(Review.created_at >= (today_start - timedelta(days=7)))
    elif date_filter == "last_30_days":
        query = query.filter(Review.created_at >= (today_start - timedelta(days=30)))
    elif date_filter == "custom" and start_date and end_date:
        try:
            s_dt = datetime.strptime(start_date, "%Y-%m-%d")
            e_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(Review.created_at >= s_dt, Review.created_at <= e_dt)
        except ValueError:
            pass

    pagination = query.order_by(Review.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template(
        "admin/reports.html",
        reports=pagination.items,
        pagination=pagination,
        search_q=search_q,
        date_filter=date_filter,
        start_date=start_date,
        end_date=end_date
    )


@admin_bp.route("/reports/<int:review_id>/json")
@admin_required
def get_report_json(review_id):
    review = Review.query.get_or_404(review_id)
    return jsonify({
        "id": review.id,
        "filename": review.filename,
        "quality_score": review.quality_score,
        "ml_prediction": review.ml_prediction,
        "ml_confidence": review.ml_confidence,
        "issue_count": review.issue_count,
        "semantic_score": review.semantic_score,
        "user_username": review.user.username if review.user else "Unknown",
        "user_email": review.user.email if review.user else "",
        "created_at": review.created_at.strftime("%Y-%m-%d %H:%M:%S") if review.created_at else "N/A"
    })


@admin_bp.route("/reports/<int:review_id>/delete", methods=["POST"])
@admin_required
def delete_report(review_id):
    review = Review.query.get_or_404(review_id)
    filename = review.filename
    db.session.delete(review)
    db.session.commit()
    return jsonify({"success": True, "message": f"Report for '{filename}' deleted."})


# ==========================================
# ANALYTICS SUBSYSTEM
# ==========================================

@admin_bp.route("/analytics")
@admin_required
def analytics():
    date_filter = request.args.get("date_filter", "last_30_days").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    if date_filter == "today":
        display_range = "Today"
    elif date_filter == "yesterday":
        display_range = "Yesterday"
    elif date_filter == "last_7_days":
        display_range = "Last 7 Days"
    elif date_filter == "this_month":
        display_range = "This Month"
    elif date_filter == "custom" and start_date and end_date:
        display_range = f"{start_date} to {end_date}"
    else:
        date_filter = "last_30_days"
        display_range = "Last 30 Days"

    return render_template(
        "admin/analytics.html",
        date_filter=date_filter,
        start_date=start_date,
        end_date=end_date,
        display_range=display_range
    )


@admin_bp.route("/analytics/data")
@admin_required
def analytics_data():
    date_filter = request.args.get("date_filter", "last_30_days").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    data = get_analytics_data(
        date_filter=date_filter,
        start_date_str=start_date,
        end_date_str=end_date
    )
    return jsonify(data)
