"""
Admin Analytics & Chart Data Aggregation Module
Computes datasets for 7 Chart.js analytics graphs with flexible date range filtering.
Fully compatible with SQLite locally and PostgreSQL RDS in production.
"""
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.user import User
from app.models.review import Review


def parse_date_range(date_filter, start_date_str=None, end_date_str=None):
    """
    Helper function to parse date filter parameter and return start_dt and end_dt.
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
    elif date_filter == "last_30_days" or not date_filter:
        start_dt = today_start - timedelta(days=30)
        end_dt = now
    elif date_filter == "custom" and start_date_str and end_date_str:
        try:
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
        except ValueError:
            start_dt = today_start - timedelta(days=30)
            end_dt = now
    else:
        start_dt = today_start - timedelta(days=30)
        end_dt = now

    return start_dt, end_dt


def get_analytics_data(date_filter="last_30_days", start_date_str=None, end_date_str=None):
    """
    Generate datasets for all 7 Chart.js graphs based on date filter.
    """
    start_dt, end_dt = parse_date_range(date_filter, start_date_str, end_date_str)

    # 1. New Users Per Day
    users_query = db.session.query(
        func.date(User.created_at).label("date"),
        func.count(User.id).label("count")
    ).filter(User.created_at >= start_dt, User.created_at <= end_dt)\
     .group_by(func.date(User.created_at))\
     .order_by(func.date(User.created_at)).all()

    users_by_day_labels = [str(r.date) for r in users_query]
    users_by_day_data = [int(r.count) for r in users_query]

    # 2. Uploads Per Day
    uploads_query = db.session.query(
        func.date(Review.created_at).label("date"),
        func.count(Review.id).label("count")
    ).filter(Review.created_at >= start_dt, Review.created_at <= end_dt)\
     .group_by(func.date(Review.created_at))\
     .order_by(func.date(Review.created_at)).all()

    uploads_by_day_labels = [str(r.date) for r in uploads_query]
    uploads_by_day_data = [int(r.count) for r in uploads_query]

    # 3. Reports Per Day
    reports_by_day_labels = uploads_by_day_labels
    reports_by_day_data = uploads_by_day_data

    # 4. Average Quality Score Over Time
    avg_score_query = db.session.query(
        func.date(Review.created_at).label("date"),
        func.avg(Review.quality_score).label("avg_score")
    ).filter(Review.created_at >= start_dt, Review.created_at <= end_dt)\
     .group_by(func.date(Review.created_at))\
     .order_by(func.date(Review.created_at)).all()

    score_by_day_labels = [str(r.date) for r in avg_score_query]
    score_by_day_data = [round(float(r.avg_score), 2) for r in avg_score_query]

    # 5. Top 10 Active Users
    top_users_query = db.session.query(
        User.username,
        func.count(Review.id).label("upload_count")
    ).join(Review, User.id == Review.user_id)\
     .filter(Review.created_at >= start_dt, Review.created_at <= end_dt)\
     .group_by(User.id, User.username)\
     .order_by(func.count(Review.id).desc())\
     .limit(10).all()

    top_users_labels = [r.username for r in top_users_query]
    top_users_data = [int(r.upload_count) for r in top_users_query]

    # 6. Programming Language Distribution
    lang_query = db.session.query(
        Review.language,
        func.count(Review.id).label("count")
    ).filter(Review.created_at >= start_dt, Review.created_at <= end_dt)\
     .group_by(Review.language).all()

    lang_labels = [r.language or "Python" for r in lang_query]
    lang_data = [int(r.count) for r in lang_query]

    if not lang_labels:
        lang_labels = ["Python"]
        lang_data = [total_uploads_count(start_dt, end_dt)]

    # 7. Analysis Per Month (Last 12 Months) - Portable across SQLite and Postgres
    now = datetime.utcnow()
    twelve_months_ago = datetime(now.year - 1 if now.month == 12 else now.year, (now.month % 12) + 1, 1)

    try:
        month_query = db.session.query(
            func.strftime('%Y-%m', Review.created_at).label("month_year"),
            func.count(Review.id).label("count")
        ).filter(Review.created_at >= twelve_months_ago)\
         .group_by("month_year")\
         .order_by("month_year").all()
    except Exception:
        db.session.rollback()
        month_query = db.session.query(
            func.to_char(Review.created_at, 'YYYY-MM').label("month_year"),
            func.count(Review.id).label("count")
        ).filter(Review.created_at >= twelve_months_ago)\
         .group_by("month_year")\
         .order_by("month_year").all()

    month_labels = [r.month_year for r in month_query if r.month_year]
    month_data = [int(r.count) for r in month_query if r.month_year]

    return {
        "users_by_day": {"labels": users_by_day_labels, "data": users_by_day_data},
        "uploads_by_day": {"labels": uploads_by_day_labels, "data": uploads_by_day_data},
        "reports_by_day": {"labels": reports_by_day_labels, "data": reports_by_day_data},
        "score_by_day": {"labels": score_by_day_labels, "data": score_by_day_data},
        "top_users": {"labels": top_users_labels, "data": top_users_data},
        "language_distribution": {"labels": lang_labels, "data": lang_data},
        "analysis_per_month": {"labels": month_labels, "data": month_data},
    }


def total_uploads_count(start_dt, end_dt):
    return Review.query.filter(Review.created_at >= start_dt, Review.created_at <= end_dt).count()
