from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required, logout_user
from models import NewsPost, Comment, PostVote
from application.forms import CreatePostForm, UserComment
from datetime import date, datetime
from . import db


# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@main_bp.route('/', methods=['GET'])
def get_all_posts():
    posts = NewsPost.query.order_by(NewsPost.upvotes.desc()).all()
    return render_template('index.html', all_posts=posts)


@main_bp.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for('auth_bp.login'))


@main_bp.context_processor
def time_processor():
    def format_time_year():
        return datetime.now().strftime("%Y")

    return dict(format_time_year=format_time_year)


@main_bp.route('/new-post', methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        new_post = NewsPost(
            title=form.title.data,
            body=form.body.data,
            url=form.post_url.data,
            poster=current_user,
            date=date.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template('make-post.html', form=form, current_user=current_user)


@main_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = NewsPost.query.get(post_id)
    comment_form = UserComment()
    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(text=comment_form.comment.data, post_id=post_id, author_id=current_user.id)
            db.session.add(new_comment)
            db.session.commit()
            return render_template("post.html", post=requested_post, comment_form=comment_form)
        else:
            flash("Only users who are logged in can comment, please log in")
            return redirect(url_for('login'))

    return render_template("post.html", post=requested_post, comment_form=comment_form, current_user=current_user)


@main_bp.route('/delete/<int:post_id>', methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    post_to_delete = NewsPost.query.get(post_id)
    db.session.query(PostVote).filter_by(post_id=post_id).delete()
    db.session.delete(post_to_delete)

    db.session.commit()
    return redirect(url_for("get_all_posts"))


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/post-upvote/<int:post_id>", methods=["GET", "POST"])
def upvote(post_id):
    if not current_user.is_authenticated:
        flash("Only registered users can vote. Please login or register.")
        return redirect(url_for("login"))
    vote = PostVote.query.filter_by(post_id=post_id, author_id=current_user.id).first()
    post = NewsPost.query.get(post_id)
    if not vote:
        new_vote = PostVote(vote_author=current_user,
                            parent_post=post,
                            upvote=1,
                            downvote=0)
        db.session.add(new_vote)
        post.upvotes += 1

    elif vote.upvote == 1:
        vote.upvote = 0
        post.upvotes -= 1

    elif vote.upvote == 0:
        vote.upvote = 1
        vote.downvote = 0
        post.upvotes += 1
        if post.downvotes > 0:
            post.downvotes -= 1

    db.session.commit()

    return redirect(url_for("get_all_posts"))


@main_bp.route("/post-downvote/<int:post_id>", methods=["GET", "POST"])
def downvote(post_id):
    if not current_user.is_authenticated:
        flash("Only registered users can vote. Please login or register")
        return redirect(url_for("login"))
    vote = PostVote.query.filter_by(post_id=post_id, author_id=current_user.id).first()
    post = NewsPost.query.get(post_id)

    if not vote:
        new_vote = PostVote(vote_author=current_user,
                            parent_post=post,
                            upvote=0,
                            downvote=1)
        db.session.add(new_vote)
        post.downvotes += 1

    elif vote.downvote == 1:
        vote.downvote = 0
        post.downvotes -= 1

    elif vote.downvote == 0:
        vote.downvote = 1
        vote.upvote = 0
        post.downvotes += 1
        if post.upvotes > 0:
            post.upvotes -= 1

    db.session.commit()
    return redirect(url_for("get_all_posts"))


@main_bp.route("/comment-upvote/<int:comment_id>", methods=["GET", "POST"])
def comment_upvote(comment_id):
    if not current_user.is_authenticated:
        flash("Only registered users can vote. Please login or register.")
        return redirect(url_for("login"))
    vote = CommentVote.query.filter_by(comment_id=comment_id, author_id=current_user.id).first()
    comment = Comment.query.get(comment_id)
    if not vote:
        new_vote = CommentVote(vote_author=current_user,
                               parent_comment=comment,
                               upvote=1,
                               downvote=0)
        db.session.add(new_vote)
        comment.upvotes += 1

    elif vote.upvote == 1:
        vote.upvote = 0
        comment.upvotes -= 1

    elif vote.upvote == 0:
        vote.upvote = 1
        vote.downvote = 0
        comment.upvotes += 1
        if comment.downvotes > 0:
            comment.downvotes -= 1

    db.session.commit()

    return redirect(url_for("show_post", post_id=comment.post_id))


@main_bp.route("/comment-downvote/<int:comment_id>", methods=["GET", "POST"])
def comment_downvote(comment_id):
    if not current_user.is_authenticated:
        flash("Only registered users can vote. Please login or register")
        return redirect(url_for("login"))
    vote = CommentVote.query.filter_by(comment_id=comment_id, author_id=current_user.id).first()
    comment = Comment.query.get(comment_id)

    if not vote:
        new_vote = CommentVote(vote_author=current_user,
                               parent_comment=comment,
                               upvote=0,
                               downvote=1)
        db.session.add(new_vote)
        comment.downvotes += 1

    elif vote.downvote == 1:
        vote.downvote = 0
        comment.downvotes -= 1

    elif vote.downvote == 0:
        vote.downvote = 1
        vote.upvote = 0
        comment.downvotes += 1
        if comment.upvotes > 0:
            comment.upvotes -= 1

    db.session.commit()

    return redirect(url_for("show_post", post_id=comment.post_id))

