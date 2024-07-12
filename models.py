from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to the database."""
    db.app = app
    db.init_app(app)


class Anime (db.Model):
    """List of anime."""

    __tablename__ = 'anime'

    id = db.Column(db.Integer, primary_key=True,)
    title = db.Column(db.Text, nullable=False,)
    genre = db.Column(db.Text,)
    episode_count = db.Column(db.Integer, nullable=False,)
    rating = db.Column(db.Float, nullable=False)

class Episode(db.Model):
    """List of episodes for an anime."""

    __tablename__ = 'episodes'

    id = db.Column(db.Integer, primary_key=True,)
    title = db.Column(db.Text, nullable=True,)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'))
    userlist_id = db.Column(db.Integer, db.ForeignKey('userlist.id'))

class Userlist(db.Model):
    """List of User shows."""

    __tablename__= 'userlist'

    id = db.Column(db.Integer, primary_key=True,)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id', ondelete='cascade'))

class User(db.Model):
    """User in the system."""

    __tablename__= 'users'

    id = db.Column(db.Integer, primary_key=True,)
    email = db.Column(db.Text, nullable=False, unique=True,)
    username = db.Column(db.Text, nullable=False, unique=True,)
    password = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"
    
    @classmethod
    def signup(cls, username, email, password):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        
        user = User(username=username, email=email, password=hashed_pwd)

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password. This is a class method (call it on the class, not an individual user.) It searches for a user whose password hash matches this password and, if it finds such a user, returns that user object. If can't find matching user (or if password is wrong), returns False."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
            
            return False