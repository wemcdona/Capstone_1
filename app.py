import os

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import pdb

from forms import UserAddForm, LoginForm, UserEditForm
from models import db, connect_db, User, Userlist, Anime, Episode

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/crunchylist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = 'neededForPythonDebugToolbar'

connect_db(app)

DebugToolbarExtension(app)

# Define routes

# @app.before_request
def get_current_user():
    return User.query.get(session[CURR_USER_KEY])

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
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)
        
        do_login(user)
        
        return redirect("/")
    
    else:
        # TODO: Fix this by fixing path to the template html file
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
            return redirect("/")
        
        flash("Invalid username or password.", 'danger')
# TODO: Fix this by fixing path to the template html file
    return render_template('/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")

@app.route('/users')
def list_users():
    """Page with listing of users."""

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)

@app.route('/users/<int:user_id>/anime', methods=['POST'])
def add_anime(user_id):
    """Add anime to user's list."""
    user = User.query.get_or_404(user_id)
    anime_id = request.form.get('anime_id')
    anime = Anime.query.get(anime_id)
    userlist = Userlist(user=user, anime=anime)
    db.session.add(userlist)
    db.session.commit()
    return redirect(f'/users/{user_id}')

@app.route('/users/<int:user_id>/anime/<int:anime_id>', methods=['DELETE'])
def delete_anime(user_id, anime_id):
    """Delete anime from user's list."""
    user = User.query.get_or_404(user_id)
    anime = Anime.query.get_or_404(anime_id)
    userlist = Userlist.query.filter(Userlist.user == user.id, Userlist.anime == anime.id)
    db.session.delete(userlist)
    db.session.commit()
    return redirect(f'/users/{user_id}')


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile. Display user list."""

    user = User.query.get_or_404(user_id)

    return render_template('users/show.html', user=user)

@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    if not get_current_user:
        flash("Access unauthorized", "danger")

    user = get_current_user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or "/static/images/default-pic.png"

            db.session.commit()
            return redirect(f"/users/{user.id}")
        
        flash("Wrong password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not get_current_user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    do_logout()

    db.session.delete(get_current_user)
    db.session.commit()

    return redirect("/signup")

@app.route('/')
def homepage():
    """Homepage:
    
    anon users: show home page with options to log in.
    logged in: display user's personal anime list."""

    all_anime = Anime.query.all()
    return render_template('home.html', all_anime=all_anime)


# Add error handling for database operations
@app.errorhandler(IntegrityError)
def handle_integerity_error(e):
    """Handle IntegrityError exceptions."""

    db.session.rollback()
    flash('An error occurred. Please try again.', 'danger')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)