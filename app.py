from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from flask_ckeditor import CKEditor
from forms import CreatePostForm, UserComment, NewUserForm, UserLogin
from datetime import date
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'softwar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///softwareNews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ckeditor = CKEditor(app)
Bootstrap(app)
db = SQLAlchemy(app)

##FLASK LOGIN##
login_manager = LoginManager()
login_manager.init_app(app)

##CONFIGURE TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("NewsPost", back_populates="poster")
    comments = relationship("Comment", back_populates="comment_author")
    votes = relationship("Vote", back_populates="vote_author")



class NewsPost(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    poster = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")
    votes = relationship("Vote", back_populates="parent_post")
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship("NewsPost", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")
    text = db.Column(db.Text, nullable=False)

class Vote(db.Model):
    __tablename__ = "votes"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship("NewsPost", back_populates="votes")
    vote_author = relationship("User", back_populates="votes")
    upvote = db.Column(db.Integer, default=0)
    downvote = db.Column(db.Integer, default=0)


db.create_all()


@app.context_processor
def time_processor():
    def format_time_year():
        return datetime.now().strftime("%Y")
    return dict(format_time_year=format_time_year)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=["GET", "POST"])
def register_user():
    new_user_form = NewUserForm()
    if new_user_form.validate_on_submit():
        if User.query.filter_by(email=new_user_form.user_email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        new_user = User(
            name = new_user_form.user_name.data,
            email = new_user_form.user_email.data,
            password =generate_password_hash(new_user_form.password.data,
                                             method='pbkdf2:sha256', salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()
        #login & auth user
        login_user(new_user)
        return redirect(url_for('get_all_posts'))

    return render_template("register.html", form=new_user_form)


@app.route('/login', methods=["GET", "POST"])
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


@app.route('/')
def get_all_posts():
    posts = NewsPost.query.order_by(NewsPost.upvotes.desc()).all()

    return render_template('index.html', all_posts=posts)


@app.route('/new-post', methods=["GET", "POST"])
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


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
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


@app.route('/delete/<int:post_id>', methods=["GET", "POST"])
def delete_post(post_id):
    post_to_delete = NewsPost.query.get(post_id)
    db.session.query(Vote).filter_by(post_id=post_id).delete()
    db.session.delete(post_to_delete)

    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/upvote/<int:post_id>", methods=["GET", "POST"])
def upvote(post_id):
    if not current_user.is_authenticated:
        flash("Only registered users can vote. Please login or register.")
        return redirect(url_for("login"))
    vote = Vote.query.filter_by(post_id=post_id, author_id=current_user.id).first()
    post = NewsPost.query.get(post_id)
    if not vote:
        new_vote = Vote(vote_author=current_user,
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


@app.route("/downvote/<int:post_id>", methods=["GET", "POST"])
def downvote(post_id):
    if not current_user.is_authenticated:
        flash("Only registered users can vote. Please login or register")
        return redirect(url_for("login"))
    vote = Vote.query.filter_by(post_id=post_id, author_id=current_user.id).first()
    post = NewsPost.query.get(post_id)

    if not vote:
        new_vote = Vote(vote_author=current_user,
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
            post.upvotes -=1



    db.session.commit()
    return redirect(url_for("get_all_posts"))


if __name__ == "__main__":
    app.run(debug=True)


