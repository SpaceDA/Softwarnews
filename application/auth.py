from flask import Blueprint, render_template, flash, redirect, url_for
from application.forms import UserLogin, NewUserForm
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from . import login_manager

# Blueprint configuration
auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates',
    static_folder='static',
)

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    new_login = UserLogin()
    if new_login.validate_on_submit():
        email = new_login.user_email.data
        password = new_login.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("User Not Validated. Please Try Again")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Incorrect password. Please Try Again")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template('login.html', form=new_login)


@auth_bp.route('/register', methods=["GET", "POST"])
def register_user():
    """
        User sign-up page.

        GET requests serve sign-up page.
        POST requests validate form & user creation.
        """
    new_user_form = NewUserForm()
    if new_user_form.validate_on_submit():
        if User.query.filter_by(email=new_user_form.user_email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        new_user = User(
            name=new_user_form.user_name.data,
            email=new_user_form.user_email.data,
            password=generate_password_hash(new_user_form.password.data,
                                            method='pbkdf2:sha256', salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()
        # login & auth user
        login_user(new_user)
        return redirect(url_for('get_all_posts'))

    return render_template("register.html", form=new_user_form)


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))

