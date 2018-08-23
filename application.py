import os

from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from wtforms import Form, PasswordField, StringField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

# In original project // Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# In original project // Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Setting up a SQLalchemy engine and session
engine = create_engine("postgres://lijguuuketxvgt:41b5b754c093cc173bad3e5b5ac739efe2531630ea7b1a501a6dfb3a8bd3fed9@ec2-54-83-13-119.compute-1.amazonaws.com:5432/deo34sags8udmk")
db = scoped_session(sessionmaker(bind=engine))

# Index - the register/ login home page
@app.route("/")
def index():
    return render_template("index.html")

# Register - Landing page to register a new user
@app.route('/register/')
def register():
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("register.html", users=users)

# Register a new user
@app.route("/newuser", methods=["POST"])
def newuser():

    # Get form information.
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm = request.form.get("confirm")

    # Validate user input - Make sure the passwords match
    if password != confirm:
        return render_template("error.html", message="Passwords must match.")

    # Validate user input - Make sure the username does not already exist
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount > 0:
        return render_template("error.html", message="That username is not available.")

    # Register the new user and send them to search.html
    db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
            {"username": username, "email": email, "password": password})
    db.commit()
    return render_template("search.html", username=username)

# Login - Landing page for existing users to log in
@app.route('/login/')
def login():
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("login.html", users=users)

# Returning user - 
@app.route("/returninguser", methods=["POST"])
def returninguser():

    # Get form information.
    username = request.form.get("username")
    password = request.form.get("password")

    # Verify user input
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 0:
        return render_template("error.html", message="Invalid username or password. Please try again.")
    return render_template("search.html", username=username)

# Search - redirected here after registering or logging in. Allows the user to search for a book Title, Author, or ISBN
@app.route("/search/")
def search():
    return render_template("search.html")

# List all search results
@app.route("/results/", methods=["POST"])
def results():

    # Get form information.
    isbn = request.form.get("isbn")
    author = request.form.get("author")
    title = request.form.get("title")
    
    # Find matching books in book table
    try:
        results = db.execute("SELECT isbn, title, author FROM books WHERE isbn = :isbn OR author = :author OR title = :title ", {"isbn":isbn, "author":author, "title":title}).fetchall()
        return render_template("results.html", results=results)
    except ValueError:
        return render_template("error.html", message="No match. Please try a different author, ISBN, or book title.")

# Book - Detail page on each book
@app.route("/book/<title>")
def book(title):

    author = db.execute("SELECT author FROM books WHERE title = :title ", {"title":title}).fetchall()
    ISBN = db.execute("SELECT isbn FROM books WHERE title = :title ", {"title":title}).fetchall()
    return render_template("book.html", title=title, author=author, ISBN=ISBN)
    
# Logout
@app.route('/logout/')
def logout():
    return render_template("logout.html")

if __name__ == "__main__":
    app.run()
