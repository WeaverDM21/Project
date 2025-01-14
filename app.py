from __future__ import annotations
import os
from flask import Flask, render_template, url_for, redirect
from flask import request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required
from flask_login import login_user, logout_user, current_user

from hashing_examples import UpdatedHasher
from loginforms import RegisterForm, LoginForm
from reviewForm import ReviewForm
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

#Create a database model for Reviews
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, nullable=False)
    movieID = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Unicode)

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
    return render_template('home.html', current_user=current_user)

@app.get('/movie/<int:id>/')
def getMovie(id: int):
    movie_info = makeRequestID(id)
    cast_info = makeRequestIDCast(id)
    print(f"In request header: {id}")
    form = ReviewForm()
    reviews = db.session.query(Review, User).join(User, Review.userID == User.id).filter(Review.movieID == id).all()
    total = 0
    num = 0
    for review, user in reviews:
        total += 1
        num += review.rating
    if (total >= 1):
        average_rating = num/total
    else:
        average_rating = 0
    return render_template('movie.html', movie_info=movie_info, cast_info=cast_info, form=form, reviews=reviews, average_rating=average_rating)

@app.post('/movie/<int:id>/')
@login_required
def post_Movie(id: int):
    form = ReviewForm()
    if form.validate():
        review = Review(userID=current_user.id, movieID=id, rating=form.rating.data, text=form.text.data)
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('getMovie', id=id))
    else: # if the form was invalid
        # flash error messages and redirect to get login form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('getMovie', id=id))

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

def makeRequestIDCast(id: str):
    base_url = f"https://api.themoviedb.org/3/movie/{id}/credits?api_key=d136d005b47c87f94a7f7245dbede8dd"
    print(f"In makeRequestCast {id}")

    response = requests.get(base_url)

    if response.status_code == 200:
        data = response.json()
        print(data)  # This will print the movie cast data
        return data
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
    # Example inappropriate words list (can be more comprehensive)
    inappropriate_words = ['fuck', 'shit', 'crap']

    # Create a filter condition for reviews containing inappropriate words
    filter_condition = None
    for word in inappropriate_words:
        condition = Review.text.ilike(f'%{word}%')
        filter_condition = condition if filter_condition is None else filter_condition | condition

    # Query reviews that contain inappropriate words
    inappropriate_reviews = db.session.query(Review, User).join(User, Review.userID == User.id).filter(filter_condition).all()
    # Fetch movie names for each inappropriate review
    reviews_with_movies = []
    for review, user in inappropriate_reviews:
        movie_info = makeRequestID(review.movieID)  # Assumes makeRequestID fetches movie details
        movie_name = movie_info.get("title", "Unknown Movie") if movie_info else "Unknown Movie"
        reviews_with_movies.append((review, user, movie_name))

    return render_template('admin.html', reviews_with_movies=reviews_with_movies, current_user=current_user)
    
@app.post('/admin/delete_review/<int:review_id>/')
@login_required
@admin_required
def delete_review(review_id: int):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash("Review deleted successfully.", "success")
    return redirect(url_for('adminPage'))
