import os, requests

from flask import Flask, render_template, request, flash, redirect, session, g, abort
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import pdb

from forms import AddBookForm, CommonSubjectsForm
from models import db, connect_db, Book

CURR_USER_KEY = "curr_user"
# https://openlibrary.org/search.json?q=the+lord+of+the+rings
BASE_URL = "https://openlibrary.org/search.json?"

app = Flask(__name__)
# app.app_context().push()

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = ('postgresql:///book_recommendations')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

###### FUNCTIONS
def get_subject(book_name):
    query_book = book_name.lower()
    query_book = query_book.replace(' ', '+')
    resp = requests.get(f"https://openlibrary.org/search.json?title={query_book}")
    info = resp.json()
    subjects = info['docs'][0]['subject']
    return subjects

@app.route("/", methods=["GET"])
def homepage():
    """Homepage that displays books the user has read."""
    books = Book.query.all()
    return render_template("users_books.html", books=books)

@app.route("/form", methods=["GET", "POST"])
def view_books():

    form = AddBookForm()
    if form.validate_on_submit():
        book = Book(title=form.title.data) # create with Book model

        db.session.add(book) # add book to session
        db.session.commit() # add to db
        

        ## not working
        flash(f"Success, ${book.title} was added to your list.", 'success') 
        return redirect('/')
    return render_template("add_book_form.html", form=form)

@app.route("/subjects", methods=["GET", "POST"])
def common_subjects():
    form = CommonSubjectsForm()
    if form.validate_on_submit():
        book1 = form.title1.data
        book2 = form.title2.data
        subj1 = get_subject(book1)
        subj2 = get_subject(book2)
        set1 = set(subj1)
        set2 = set(subj2)
        common_subject = set1 & set2 ### finds the intersection... should be a list?
        common_subject =list(common_subject)
        common_subject.sort() ## should order alphabetically
        return render_template("common_subject_results.html", form=form, common_subject=common_subject)
    return render_template("common_subjects_form.html", form=form)

# @app.route("/results", methods=["GET"])
# @app.route subject_results():
#     return render_template("common_subject_results.html", form=form, common_subject=common_subject)

