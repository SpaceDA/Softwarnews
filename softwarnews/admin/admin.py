from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from softwarnews.api import fetch_articles
from softwarnews.application.forms import AdminArticleSearch

admin_bp = Blueprint(
    "admin_bp", __name__, template_folder="templates", static_folder="static"
)


@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin():
    if current_user.id != 1:
        return redirect(url_for('main_bp.get_all_posts'))
    search = AdminArticleSearch()
    if search.validate_on_submit():
        articles = fetch_articles(search.keyword)
    return render_template('admin.html', articles=articles, search=search)