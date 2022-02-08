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

class NewsPost(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    #Create Foreign Key, "users.id" the users refers to the tablename of User.

    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    poster = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="news_posts")

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("NewsPost", back_populates="poster")
    comments = relationship("Comment", back_populates="comment_author")

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    comment_author = relationship("User", back_populates="comments")
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    text = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    news_posts = relationship("NewsPost", back_populates="comments")

#db.create_all()

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
    posts = NewsPost.query.all()
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
            date=date.today().strftime("%B %d, %Y")
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

    db.session.delete(post_to_delete)
    db.session.commit()
    return render_template(url_for("get_all_posts"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

if __name__ == "__main__":
    app.run(debug=True)


