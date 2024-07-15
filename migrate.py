import os
from dotenv import load_dotenv
import psycopg2
from models import connect_db, db, User, Book
from flask import Flask

# load environmental variables from .env
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SUPABASE_DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
connect_db(app)

LOCAL_DB_URI = 'postgresql://localhost:6543/book_recommendations'

def fetch_local_data():
    conn = psycopg2.connect(LOCAL_DB_URI)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, email, username, password FROM users")
    users = cursor.fetchall()
    
    cursor.execute("SELECT id, title, user_id FROM books")
    books = cursor.fetchall()
    
    conn.close()
    return users, books

def seed_supabase_data(users, books):
    with app.app_context():
        for user in users:
            id, email, username, password = user
            new_user = User(id=id, email=email, username=username, password=password)
            db.session.add(new_user)
        
        for book in books:
            id, title, user_id = book
            new_book = Book(id=id, title=title, user_id=user_id)
            db.session.add(new_book)
        
        db.session.commit()

if __name__ == "__main__":
    users, books = fetch_local_data()
    seed_supabase_data(users, books)
    print("Data migration complete.")
