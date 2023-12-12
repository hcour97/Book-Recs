import os, requests

from flask import Flask, render_template, request, flash, redirect, session, g, abort
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import pdb

from forms import AddBookForm, BookRecommendationForm, UserLoginForm, UserAddForm
from models import db, connect_db, Book, User

CURR_USER_KEY = "curr_user"

BASE_URL = "https://openlibrary.org/search.json?"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = ('postgresql:///book_recommendations')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.drop_all()
db.create_all()

########################################
############## FUNCTIONS ###############
########################################
def get_subject(book_name):
    query_book = book_name.lower()
    query_book = query_book.replace(' ', '+')
    resp = requests.get(f"https://openlibrary.org/search.json?title={query_book}")
    info = resp.json()
    try:
        subjects = info['docs'][0]['subject']
        return subjects
    except:
        return "sorry. no common subjects available."

def get_common_subjects(subj1, subj2):
    set1 = set(subj1)
    set2 = set(subj2)
    common_subject = set1 & set2 ### finds the intersection... should be a list?
    common_subject =list(common_subject)
    common_subject.sort() 
    return common_subject

def get_books(subject_name):
    query_subject = subject_name.lower()
    query_subject = query_subject.replace(' ', '+')
    resp = requests.get(f"https://openlibrary.org/search.json?subject={query_subject}")
    info = resp.json()
    books = []
    i = 0
    while i <=5:
        book = info['docs'][i]['title']
        books.append(book)
    return books

################## USE Flask's g object to store data during running web app #########

@app.before_request
def add_user_to_g():
    """If logged in, add current user to Flask Global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """login user."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

########################################
################# USER #################
################ ROUTES ################
########################################

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle new user signup. Create a new User and add to db. 
        Redirect to their reading list."""
    form = UserAddForm()
    if form.validate_on_submit():
        try: 
            user = User.signup(
                username = form.username.data,
                password = form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template('users/signup.html', form=form)
        
        do_login(user)
        return redirect(f"/users/{user.id}")
    else:
        return render_template('users/signup.html', form=form)
 
@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle existing user login."""
    form = UserLoginForm()
    if form.validate_on_submit():
        user=User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(f"/users/{ user.id }")
        
        else:
            flash("Invalid credentials. Please try again.", "danger")
    
    return render_template("users/login.html", form=form)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Handle existing user logout."""
    do_logout()
    flash("User successfully logged out.")
    return redirect("/login")

########################################
################ ROUTES ################
########################################

@app.route("/books/add", methods=["GET", "POST"])
def manually_add_book():
    """Allows logged-in user to manually add a book to their list."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = AddBookForm()
    if form.validate_on_submit():
        book = Book(title=form.title.data) # create with Book model
        g.user.books.append(book) # add book to g.user session

        db.session.commit() # add to db
        
        return redirect(f"/users/{g.user.id}")
    return render_template("add_book_form.html", form=form)

@app.route("/book-recs/new", methods = ["GET", "POST"])
def add_book_recs():
    """Get a new list of books recs.
    Show form if GET. If valid, update message and redirect to results page."""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/") ### figure out what this new "/" page will look like...
    
    form = BookRecommendationForm()

    if form.validate_on_submit():
        book1 = form.title1.data
        book2 = form.title2.data
        subj1 = get_subject(book1)
        subj2 = get_subject(book2)
    
        try:
            common_subjects = get_common_subjects(subj1, subj2)
            subject = common_subjects[0]
            query_subject = common_subjects[0].lower().replace(' ', '+')

            resp = requests.get(f"https://openlibrary.org/search.json?subject={query_subject}")
            info = resp.json()
        
            books = []
            i = 0
            while i <=5:
                book_title = info['docs'][i]['title']
                # book = Book(title=book_title.data) ## not actually saving to the db.
                books.append(book_title)
                i+=1
            return render_template("recommendation_results.html", form=form, books=books, subject=subject)
        except:
            return render_template("error_recommendations.html")
    return render_template("recommendation_form.html", form=form)

@app.route("/users/<int:user_id>", methods=["GET"])
def show_books(user_id):
    """Display the logged-in users to-read list."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)
    books = user.books
    return render_template("users/books.html", user=user, books=books)

@app.route('/books/<int:book_id>/delete', methods=["GET","POST"])
def delete_book(book_id):
    """Deletes a book. """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    book_to_delete = Book.query.get(book_id)
    db.session.delete(book_to_delete)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")

@app.route("/")
def homepage():
    """Show homepage
    anon users: no books
    logged in users: book list."""

    if g.user: 
        books = Book.query.all()
        return render_template("homepage.html")
    
    else:
        return render_template("home-anon.html")





##### PREVIOUS ROUTES #####

# @app.route("/", methods=["GET"])
# def homepage():
#     """Homepage that displays books the user would like to read."""
#     books = Book.query.all()
#     return render_template("users_books.html", books=books)

# @app.route("/form", methods=["GET", "POST"])
# def view_books():
#     """Form for user to manually add books to their read-list."""
#     form = AddBookForm()
#     if form.validate_on_submit():
#         book = Book(title=form.title.data) # create with Book model

#         db.session.add(book) # add book to session
#         db.session.commit() # add to db
        
#         ## not working
#         flash(f"Success, ${book.title} was added to your list.", 'success') 
#         return redirect('/')
#     return render_template("add_book_form.html", form=form)

# @app.route('/delete/<int:book_id>', methods=["GET","POST"])
# def delete_book(book_id):
#     book_to_delete = Book.query.get_or_404(book_id)
#     try:
#         db.session.delete(book_to_delete)
#         db.session.commit()
#         return redirect("/")
#     except:
#         return "Sorry. Cannot delete that book."

@app.route("/book-recs", methods=["GET", "POST"])
def book_recommender():
    """Form and results for user to receive book recommendations based off of two books they've read."""
    form = BookRecommendationForm()
    if form.validate_on_submit():
        book1 = form.title1.data
        book2 = form.title2.data
        subj1 = get_subject(book1)
        subj2 = get_subject(book2)
    
        try:
            common_subjects = get_common_subjects(subj1, subj2)
            subject = common_subjects[0]
            query_subject = common_subjects[0].lower().replace(' ', '+')

            resp = requests.get(f"https://openlibrary.org/search.json?subject={query_subject}")
            info = resp.json()
        
            books = []
            i = 0
            while i <=5:
                book_title = info['docs'][i]['title']
                # book = Book(title=book_title.data) ## not actually saving to the db.
                books.append(book_title)
                i+=1
            # return redirect("/book-recs/add")
            return render_template("recommendation_results.html", form=form, books=books, subject=subject)
        except:
            return render_template("error_recommendations.html")
    return render_template("recommendation_form.html", form=form)

@app.route("/book-recs/add", methods=["GET", "POST"])
def add_rec_book():
    # how do I grab the text that is associated with that button???
    book_title = request.form.get("book") # get the value of the radio button selected, returning "on" as book_title rn
    print(book_title) # prints "on" as each book_title
    book_to_add = Book(title=book_title) # create a book model

    try: # add to db
        db.session.add(book_to_add)
        db.session.commit()
        return redirect("/")
    except:
        return "Sorry. Cannot add that book."




    

