"""
Admin Dashboard Data Aggregator Module
Calculates system-wide metrics, registration trends, and date-filtered user breakdowns.
"""
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.user import User
from app.models.review import Review


def parse_dash_date_range(date_filter, start_date_str=None, end_date_str=None):
    """
    Parse date filter parameters into start_dt and end_dt.
    """
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)

    if date_filter == "today":
        start_dt = today_start
        end_dt = now
    elif date_filter == "yesterday":
        start_dt = today_start - timedelta(days=1)
        end_dt = today_start - timedelta(seconds=1)
    elif date_filter == "last_7_days":
        start_dt = today_start - timedelta(days=7)
        end_dt = now
    elif date_filter == "this_month":
        start_dt = datetime(now.year, now.month, 1, 0, 0, 0)
        end_dt = now
    elif date_filter == "last_30_days":
        start_dt = today_start - timedelta(days=30)
        end_dt = now
    elif date_filter == "custom" and start_date_str and end_date_str:
        try:
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
        except ValueError:
            start_dt = None
            end_dt = None
    else:
        start_dt = None
        end_dt = None

    return start_dt, end_dt


def get_dashboard_metrics(date_filter=None, start_date_str=None, end_date_str=None):
    """
    Calculate and return the dashboard metrics along with date-filtered user data.
    """
    now = datetime.utcnow()

    # Default time boundaries (UTC)
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    yesterday_start = today_start - timedelta(days=1)
    yesterday_end = today_start - timedelta(seconds=1)
    start_of_week = today_start - timedelta(days=today_start.weekday())
    start_of_month = datetime(now.year, now.month, 1, 0, 0, 0)

    # 1. Total Registered Users
    total_users = User.query.count()

    # 2. Total Uploaded Files / Reviews
    total_uploads = Review.query.count()

    # 3. Total Analysis Reports
    total_reports = total_uploads

    # 4. Total Successful Reviews
    total_successful_reviews = Review.query.filter(Review.quality_score > 0).count()

    # 5. Average Quality Score
    avg_score_result = db.session.query(func.avg(Review.quality_score)).scalar()
    avg_quality_score = round(avg_score_result, 2) if avg_score_result is not None else 0.0

    # Registration Breakdowns
    users_today = User.query.filter(User.created_at >= today_start).count()
    users_yesterday = User.query.filter(User.created_at >= yesterday_start, User.created_at <= yesterday_end).count()
    users_this_week = User.query.filter(User.created_at >= start_of_week).count()
    users_this_month = User.query.filter(User.created_at >= start_of_month).count()

    # Upload Breakdowns
    uploads_today = Review.query.filter(Review.created_at >= today_start).count()
    uploads_yesterday = Review.query.filter(Review.created_at >= yesterday_start, Review.created_at <= yesterday_end).count()
    uploads_this_week = Review.query.filter(Review.created_at >= start_of_week).count()
    uploads_this_month = Review.query.filter(Review.created_at >= start_of_month).count()

    # Filtered Date Range calculations
    start_dt, end_dt = parse_dash_date_range(date_filter, start_date_str, end_date_str)
    
    if start_dt and end_dt:
        filtered_users_count = User.query.filter(User.created_at >= start_dt, User.created_at <= end_dt).count()
        filtered_uploads_count = Review.query.filter(Review.created_at >= start_dt, Review.created_at <= end_dt).count()
    else:
        filtered_users_count = total_users
        filtered_uploads_count = total_uploads

    return {
        "total_users": total_users,
        "total_uploads": total_uploads,
        "total_reports": total_reports,
        "total_successful_reviews": total_successful_reviews,
        "avg_quality_score": avg_quality_score,
        "users_today": users_today,
        "users_yesterday": users_yesterday,
        "users_this_week": users_this_week,
        "users_this_month": users_this_month,
        "uploads_today": uploads_today,
        "uploads_yesterday": uploads_yesterday,
        "uploads_this_week": uploads_this_week,
        "uploads_this_month": uploads_this_month,
        "filtered_users_count": filtered_users_count,
        "filtered_uploads_count": filtered_uploads_count,
    }


def get_recent_dashboard_activity(limit=5, date_filter=None, start_date_str=None, end_date_str=None):
    """
    Fetch recent users and reviews, optionally filtered by selected date range.
    """
    start_dt, end_dt = parse_dash_date_range(date_filter, start_date_str, end_date_str)

    user_query = User.query
    review_query = Review.query

    if start_dt and end_dt:
        user_query = user_query.filter(User.created_at >= start_dt, User.created_at <= end_dt)
        review_query = review_query.filter(Review.created_at >= start_dt, Review.created_at <= end_dt)

    recent_users = user_query.order_by(User.created_at.desc()).limit(limit).all()
    recent_reviews = review_query.order_by(Review.created_at.desc()).limit(limit).all()

    return recent_users, recent_reviews
