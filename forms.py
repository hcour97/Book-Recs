from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, TextAreaField, BooleanField
from wtforms.validators import InputRequired, Length, NumberRange, Optional, URL

class AddBookForm(FlaskForm):
    """Form for user to add a book.
        Only having user enter a title atm.
        """
    title = StringField("Book Title", validators = [InputRequired()],)
    # author_first_name = StringField("Author's First name", validators = [InputRequired()])
    # author_last_name = StringField("Author's Last name", validators = [InputRequired()])

class CommonSubjectsForm(FlaskForm):
    """Form for user to find common subjects between 2 books."""
    title1 = StringField("First Book Title", validators = [InputRequired()],)
    title2 = StringField("Second Book Title", validators = [InputRequired()],)

class BookRecommendationForm(FlaskForm):
    """Form for user to find common subjects between 2 books."""
    title1 = StringField("First Book Title", validators = [InputRequired()],)
    title2 = StringField("Second Book Title", validators = [InputRequired()],)