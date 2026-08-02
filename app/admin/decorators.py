from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user


def admin_required(f):
    """
    Decorator to restrict route access to users with role='admin'.
    Redirects unauthenticated users to admin login page and non-admin users to home.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access the admin panel.", "warning")
            return redirect(url_for("admin.admin_login", next=request.url))
        if getattr(current_user, "role", "user") != "admin":
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("auth.home"))
        return f(*args, **kwargs)
    return decorated_function
