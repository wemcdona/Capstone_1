from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_debugtoolbar import DebugToolbarExtension
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, InputRequired, Length, Email
from sqlalchemy.exc import IntegrityError
import requests
from forms import UserAddForm, LoginForm, UserEditForm
from models import db, User, Anime, Userlist

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:password@localhost/crunchylist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = 'neededForPythonDebugToolbar'

db.init_app(app)
app.app_context().push()
toolbar = DebugToolbarExtension(app)

CURR_USER_KEY = "curr_user"

def get_current_user():
    """Return the current user from the session."""
    user_id = session.get(CURR_USER_KEY)
    if user_id:
        return User.query.get(user_id)
    return None

@app.context_processor
def inject_user():
    return dict(get_current_user=get_current_user())

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup. Create new user and add to DB. Redirect to home page. If form not valid, present form. If there already is a user with that username: flash message and re-present form."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)
        return redirect("/users/home/{user.id}")

    return render_template('signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(f"/users/home/{user.id}")

        flash("Invalid username or password.", 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have successfully logged out.", 'success')
    return redirect("/login")

@app.route('/users/home/<int:user_id>')
def users_home(user_id):
    """Display user home page with anime to choose from."""
    user = User.query.get_or_404(user_id)

    response = requests.get("https://kitsu.io/api/edge/anime", timeout=10)

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            flash("Error: Unable to parse JSON response from API.", 'danger')
            return redirect(f"/users/home/{user.id}")

        anime_list = [
            dict(
                id=anime["id"],
                title=anime["attributes"]["titles"],
                genre=", ".join(anime["relationships"]["genres"]),
                episode_count=anime["attributes"]["episodeCount"],
                rating=anime["attributes"]["averageRating"],
            )
            for anime in data["data"]
        ]

        return render_template('users/home.html', user=user, anime_list=anime_list)
    else:
        flash("Error: Unable to retrieve anime list from API.", 'danger')
        return redirect(f'/users/home/{user.id}')

@app.route('/users/<int:user_id>/anime', methods=['POST'])
def add_anime(user_id):
    """Add anime to user's list."""
    user = User.query.get_or_404(user_id)
    anime_id = request.form.get('anime_id')
    anime = Anime.query.get(anime_id)
    userlist = Userlist(user=user, anime=anime)
    db.session.add(userlist)
    db.session.commit()
    return redirect(f'/users/home/{user.id}')

@app.route('/users/<int:user_id>/anime/<int:anime_id>', methods=['DELETE'])
def delete_anime(user_id, anime_id):
    """Delete anime from user's list."""
    user = User.query.get_or_404(user_id)
    anime = Anime.query.get_or_404(anime_id)
    userlist = Userlist.query.filter(Userlist.user == user.id, Userlist.anime == anime.id).first()
    db.session.delete(userlist)
    db.session.commit()
    return redirect(url_for('users_show', user_id=user_id))

@app.route('/users/<int:user_id>/anime', methods=['GET'])
def users_show(user_id):
    """Display user anime list."""
    user = User.query.get_or_404(user_id)

    userlists = Userlist.query.filter_by(user_id=user_id).all()
    anime_ids = [ul.anime_id for ul in userlists]

    api_url = "https://kitsu.io/api/edge/anime"
    response = requests.get(api_url)

    if response.status_code == 200:
        api_data = response.json()
        anime_data = [a for a in api_data["data"] if a["id"] in anime_ids]
        return render_template('users/show.html', user=user, anime=anime_data)

@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""
    if not get_current_user():
        flash("Access unauthorized", "danger")

    user = get_current_user()
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            return redirect(f"/users/{user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""
    if not get_current_user():
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()
    db.session.delete(get_current_user())
    db.session.commit()

    return redirect("/signup")

@app.route('/')
def homepage():
    """Homepage:
    anon users: show home page with options to log in.
    logged in: display user's personal anime list."""
    all_anime = Anime.query.all()
    return render_template('home-anon.html', all_anime=all_anime)

# Add error handling for database operations
@app.errorhandler(IntegrityError)
def handle_integrity_error(e):
    """Handle IntegrityError exceptions."""
    db.session.rollback()
    flash('An error occurred. Please try again.', 'danger')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
