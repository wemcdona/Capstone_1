import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import pdb

from forms import UserAddForm, LoginForm
from models import db, connect_db, User, Anime, Episode 

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/crunchylist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

DebugToolbarExtension(app)

# Define routes

@app.route('/')
def index():
    """Homepage."""

    return render_template('index.html')


# Add error handling for database operations
@app.errorhandler(IntegrityError)
def handle_integerity_error(e):
    """Handle IntegrityError exceptions."""

    db.session.rollback()
    flash('An error occurred. Please try again.', 'danger')
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)