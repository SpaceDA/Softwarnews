from . import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    """ USER TABLE """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("NewsPost", back_populates="poster")
    comments = relationship("Comment", back_populates="comment_author")
    post_votes = relationship("PostVote", back_populates="vote_author")
    comment_votes = relationship("CommentVote", back_populates="vote_author")


class NewsPost(db.Model):
    """ POSTS TABLE """
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    poster = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(250), nullable=False, unique=True)
    comments = relationship("Comment", back_populates="parent_post")
    post_votes = relationship("PostVote", back_populates="parent_post")
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)


class Comment(db.Model):
    """ COMMENTS TABLE FOR POSTS"""
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship("NewsPost", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")
    text = db.Column(db.Text, nullable=False)
    comment_votes = relationship("CommentVote", back_populates="parent_comment")
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)


class PostVote(db.Model):
    """ TABLE TO TRACK UPVOTES AND DOWNVOTES ON POSTS"""
    __tablename__ = "post-votes"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship("NewsPost", back_populates="post_votes")
    vote_author = relationship("User", back_populates="post_votes")
    upvote = db.Column(db.Integer, default=0)
    downvote = db.Column(db.Integer, default=0)


class CommentVote(db.Model):
    """TABLE TO TRACK UPVOTES AND DOWNVOTES ON INDIVIDUAL COMMENTS ON POSTS"""
    __tablename__ = "comment-votes"
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_comment = relationship("Comment", back_populates="comment_votes")
    vote_author = relationship("User", back_populates="comment_votes")
    upvote = db.Column(db.Integer, default=0)
    downvote = db.Column(db.Integer, default=0)