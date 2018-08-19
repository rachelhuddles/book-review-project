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

# Connect to database
engine = create_engine("postgres://lijguuuketxvgt:41b5b754c093cc173bad3e5b5ac739efe2531630ea7b1a501a6dfb3a8bd3fed9@ec2-54-83-13-119.compute-1.amazonaws.com:5432/deo34sags8udmk")
db = scoped_session(sessionmaker(bind=engine))

# Registration form class
class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

# Index - the register/ login home page
@app.route("/")
def index():
    return render_template("index.html")

# Login - GET method allows the user to retrieve data from database // POST method allows them to submit data
@app.route('/login/', methods=["GET","POST"])
def login():
    error = ''
    try:
        if request.method == "POST":

            data = db.execute("SELECT * FROM users WHERE username = :username")
            
            data = db.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in")
                return redirect(url_for('search'))

            else:
                error = "Invalid credentials, try again."

        return render_template("login.html", error=error)

    except Exception as e:
        #flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error = error)  

# Register
@app.route('/register/', methods=["GET","POST"])
def register():
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.hash((str(form.password.data)))

            # See if username already exists
            if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount >= 1:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                db.execute("INSERT INTO users (username, password, email) VALUES (:username, :password, :email)")

                db.commit()
                flash("Welcome!")

                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('search'))

        return render_template('register.html', form=form)

# Search - redirected here after registering or logging in. Allows the user to search for a book Title, Author, or ISBN
@app.route('/search/')
def search():
    return render_template("search.html")

# Book - Detail page on each book. Allows users to read and leave reviews
@app.route("/book/")
def book():
    return render_template("book.html")

# Logout
@app.route('/dashboard/')
def logout():
    return render_template("logout.html")

# 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")
	
if __name__ == "__main__":
    app.run()
