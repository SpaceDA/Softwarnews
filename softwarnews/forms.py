from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, email
from flask_ckeditor import CKEditorField


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    #subtitle = StringField("Subtitle", validators=[DataRequired()])
    post_url = StringField("Post URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class UserComment(FlaskForm):
    comment = CKEditorField('Comment', validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


class NewUserForm(FlaskForm):
    user_name = StringField("Create Username", validators=[DataRequired()])
    user_email = StringField("Email Address", validators=[DataRequired(), email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class UserLogin(FlaskForm):
    user_email = StringField("Email Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class AdminArticleSearch(FlaskForm):
    keyword = StringField("keyword", validators=[DataRequired()])
    submit = SubmitField("Submit")
