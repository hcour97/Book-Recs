"""SQLAlchemy models for Book Recommendations."""

from datetime import datetime

# from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

# bcrypt = Bcrypt()
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
    # author_id = db.ForeignKey("authors.id", ondelete='cascade')
    
# class Author(db.Model):
#     """Model for authors."""
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.column(db.Text, nullable=False)
#     last_name = db.column(db.Text, nullable=False)

#     book = db.relationship('Book')