from __future__ import annotations
import os
from flask import Flask, render_template, url_for, redirect
from flask import request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required
from flask_login import login_user, logout_user, current_user

from hashing_examples import UpdatedHasher
from loginforms import RegisterForm, LoginForm
import requests
import json

from functools import wraps

# Identify necessary files
scriptdir = os.path.dirname(os.path.abspath(__file__))
dbfile = os.path.join(scriptdir, "users.sqlite3")
pepfile = os.path.join(scriptdir, "pepper.bin")

# open and read the contents of the pepper file into your pepper key
# NOTE: you should really generate your own and not use the one from the starter
with open(pepfile, 'rb') as fin:
  pepper_key = fin.read()

# create a new instance of UpdatedHasher using that pepper key
pwd_hasher = UpdatedHasher(pepper_key)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = 'correcthorsebatterystaple'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbfile}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Getting the database object handle from the app
db = SQLAlchemy(app)

# Prepare and connect the LoginManager to this app
login_manager = LoginManager()
login_manager.init_app(app)
# function name of the route that has the login form (so it can redirect users)
login_manager.login_view = 'get_login' # type: ignore
login_manager.session_protection = "strong"
# function that takes a user id and
@login_manager.user_loader
def load_user(uid: int) -> User|None:
    return User.query.get(int(uid))

# Create a database model for Movies
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.Unicode, nullable=False)
    Year = db.Column(db.Integer, nullable=False)
    Rated = db.Column(db.Unicode)
    Released = db.Column(db.Unicode)
    Runtime = db.Column(db.Unicode, nullable=False)
    Genre = db.Column(db.Unicode)
    Director = db.Column(db.Unicode)
    Writer = db.Column(db.Unicode)
    Actors = db.Column(db.Unicode)
    Plot = db.Column(db.Unicode)
    Language = db.Column(db.Unicode)
    Country = db.Column(db.Unicode)    
    Awards = db.Column(db.Unicode)
    Poster = db.Column(db.Unicode)
    Type = db.Column(db.Unicode)
    BoxOffice = db.Column(db.Unicode)

# Create a database model for Users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode, nullable=False)
    password_hash = db.Column(db.LargeBinary) # hash is a binary attribute
    role = db.Column(db.String, default="user")

    # make a write-only password property that just updates the stored hash
    @property
    def password(self):
        raise AttributeError("password is a write-only attribute")
    @password.setter
    def password(self, pwd: str) -> None:
        self.password_hash = pwd_hasher.hash(pwd)
    
    # add a verify_password convenience method
    def verify_password(self, pwd: str) -> bool:
        return pwd_hasher.check(pwd, self.password_hash)

def create_admin():
    if not User.query.filter_by(email="admin@gmail.com").first():
        admin = User(email="admin@gmail.com", role="admin")
        admin.password = "SupremeRuler"  # set a strong password
        db.session.add(admin)
        db.session.commit()

# remember that all database operations must occur within an app context
with app.app_context():
    db.create_all() # this is only needed if the database doesn't already exist
    create_admin()
    # comedies = [
    #     Movie(Title="Step Brothers", Year=2008, runtime = "1h 38m"),
    #     Movie(Title="White Chicks", Year=2004, runtime = "1h 49m"),
    #     Movie(Title="The Hangover", Year=2009, runtime = "1h 40m"),
    #     Movie(Title="Horrible Bosses", Year=2011, runtime = "1h 38m"),
    #     Movie(Title="Drillbit Taylor", Year=2008, runtime = "1h 50m"),
    #     Movie(Title="Wedding Crashers", Year=2005, runtime = "1h 59m"),
    #     Movie(Title="Bad Teacher", Year=2011, runtime = "1h 32m"),
    #     Movie(Title="The Other Guys", Year=2010, runtime = "1h 47m"),
    #     Movie(Title="Due Date", Year=2010, runtime = "1h 35m"),
    #     Movie(Title="Taxi", Year=2004, runtime = "1h 37m"),
    # ]

@app.get('/register/')
def get_register():
    form = RegisterForm()
    return render_template('register.html', form=form)

@app.post('/register/')
def post_register():
    form = RegisterForm()
    if form.validate():
        # check if there is already a user with this email address
        user = User.query.filter_by(email=form.email.data).first()
        # if the email address is free, create a new user and send to login
        if user is None:
            user = User(email=form.email.data, password=form.password.data) # type:ignore
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('get_login'))
        else: # if the user already exists
            # flash a warning message and redirect to get registration form
            flash('There is already an account with that email address')
            return redirect(url_for('get_register'))
    else: # if the form was invalid
        # flash error messages and redirect to get registration form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('get_register'))

@app.get('/login/')
def get_login():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.post('/login/')
def post_login():
    form = LoginForm()
    if form.validate():
        # try to get the user associated with this email address
        user = User.query.filter_by(email=form.email.data).first()
        # if this user exists and the password matches
        if user is not None and user.verify_password(form.password.data):
            # log this user in through the login_manager
            login_user(user)
            # redirect the user to the page they wanted or the home page
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            return redirect(next)
        else: # if the user does not exist or the password is incorrect
            # flash an error message and redirect to login form
            flash('Invalid email address or password')
            return redirect(url_for('get_login'))
    else: # if the form was invalid
        # flash error messages and redirect to get login form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('get_login'))

@app.get('/')
def index():
    comedyMovies = makeRequest("Comedy")
    return render_template('home.html', current_user=current_user)

@app.get('/movie/<string:id>')
def getMovie(id: str):
    movie_info = makeRequestID(id)
    print(f"In request header: {id}")
    return render_template('movie.html', movie_info=movie_info)

def makeRequestID(id: str):
    base_url = f"https://api.themoviedb.org/3/movie/{id}?api_key=d136d005b47c87f94a7f7245dbede8dd"
    print(f"In makeRequest {id}")

    response = requests.get(base_url)

    if response.status_code == 200:
        data = response.json()
        print(data)  # This will print the movie data
        #id = data['results'][0]['id']
        #response2 = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key=d136d005b47c87f94a7f7245dbede8dd")
        #data2 = response2.json()
        #print(data2)
        return data
    else:
        print(f"Error: {response.status_code}")

def makeRequest(genre: str):
    api_key = 'fafe5690'
    base_url = 'http://www.omdbapi.com/'
    title = "The"
    params = {
        'apikey': api_key,
        's': title,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        Movie.query.delete()
        db.create_all()

        data = response.json()
        print(data)  # This will print the movie data
    else:
        print(f"Error: {response.status_code}")

@app.get('/logout/')
@login_required
def get_logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('get_login'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous or current_user.role != "admin":
            flash('You do not have access to this page')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.get('/admin/')
@login_required
@admin_required
def adminPage():
    return render_template('admin.html')
