from flask import Flask, render_template, request, flash, redirect, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
import pdb

from forms import UserAddForm, LoginForm, UserEditForm
from models import db, connect_db, User, Userlist, Anime, Episode

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:password@localhost/crunchylist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = 'neededForPythonDebugToolbar'

connect_db(app)

DebugToolbarExtension(app)

# Define routes

# @app.before_request
def get_current_user():
    """Return the current user from the session."""
    user_id = session.get(CURR_USER_KEY)
    if user_id:
        return User.query.get(user_id)
    return None

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
        
        return redirect("/")
    
    else:

        return render_template('/signup.html', form=form)

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
    return render_template('/login.html', form=form)

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

    # Make a request to the API to get the list of anime
    response = requests.get("https://kitsu.io/api/edge/anime", timeout=10)

    # Check if the request was successful
    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            flash("Error: Unable to parse JSON response from API.", 'danger')
            return redirect(f"/users/home/{user.id}")

        # Extract the list of anime
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

        # Render the template with the user and anime list
        # TODO:  HINT:  Any variables and functions provided here will be usable by the templates.
        #  Anything not specified here will not work in the template.
        return render_template('users/home.html', user=user, anime_list=anime_list)
    # If the request was not successful, display an error message
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

    return redirect(url_for('users.show', user_id=user_id))


@app.route('/users/<int:user_id>/anime', methods=['GET'])
def users_show(user_id):
    """Display user anime list."""
    # get the current user
    user = User.query.get_or_404(user_id)

    # retrieve the user's anime list from the database
    userlists = Userlist.query.filter_by(user_id=user_id).all()

    # extract the anime IDs from the userlists
    anime_ids = [ul.anime_id for ul in userlists]

    # make a request to the API to get the anime data
    api_url = "https://kitsu.io/api/edge/anime"
    response = requests.get(api_url)

    if response.status_code == 200:
        #parse the JSON data
        api_data = response.json()

        # filter the data to only include anime with matching ID
        anime_data = [a for a in api_data["data"] if a["id"] in anime_ids]

        # TODO:  HINT:  Any variables and functions provided here will be usable by the templates.
        #  Anything not specified here will not work in the template.
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
def handle_integerity_error(e):
    """Handle IntegrityError exceptions."""

    db.session.rollback()
    flash('An error occurred. Please try again.', 'danger')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)


