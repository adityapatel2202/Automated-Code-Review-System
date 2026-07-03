
from flask import render_template, redirect, url_for, flash
from . import auth_bp
from .forms import RegisterForm
from .services import register_user
from .forms import LoginForm
from .services import login_user_service
from flask_login import logout_user, current_user
from flask_login import login_required


@auth_bp.route("/")
def home():
    return render_template("home.html")



@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        register_user(
            form.username.data,
            form.email.data,
            form.password.data
        )

        flash("Registration successful! Please login.", "success")

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/register.html",
        form=form
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # If user is already logged in, go to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        success = login_user_service(
            form.email.data,
            form.password.data
        )

        if success:
            flash("Login successful!", "success")
            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid email or password", "danger")

    return render_template(
        "auth/login.html",
        form=form
    )

@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "info")

    return redirect(url_for("auth.login"))