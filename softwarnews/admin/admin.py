from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from softwarnews.api import fetch_articles
from flask import current_app as app

admin_bp = Blueprint(
    "admin_bp", __name__, template_folder="templates", static_folder="static"
)


@admin_bp.route('/admin', methods=['GET'])
def admin():
    if current_user.id != 1:
        return redirect(url_for('main_bp.get_all_posts'))
    articles = fetch_articles()
    return render_template('admin.html', articles=articles)