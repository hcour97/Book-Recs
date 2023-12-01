"""SQLAlchemy models for Book Recommendations."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """
    db.app = app
    db.init_app(app)

class Book(db.Model):
    """Model for a books."""
    __tablename__ = "books"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey("users.id"), ondelete="cascade")
    
# class User(db.Model):
#     """User info"""
#     __tablename__ = "users"

#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.Text, nullable=False, unique=True)
#     username = db.Column(db.Text, nullable=False, unique=True)

#     books = db.relationship("Book")

#     def __repr__(self):
#         return f"<User #{self.id}: {self.username}, {self.email}"
    
#     @classmethod
#     def signup(cls, username, email, password):
#         """Hashes password and signs up user to add to system."""

#         hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

#         user = User(
#             username = username,
#             email = email,
#             password = hashed_pwd
#         )

#         db.session.add(user)
#         return user
    
#     @classmethod
#     def authenticate(cls,username,password):
#         """Searches for a user whose hashed password matches. 
#         If it does, it returns the user, otherwise returns False."""

#         user = cls.query.filter_by(username=username).first()

#         if user:
#             is_auth = bcrypt.check_password_hash(user.password, password)
#             if is_auth:
#                 return user
            
#         else:
#             return False