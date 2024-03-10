from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Email, Length

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[InputRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email(message='Please enter a valid email address')])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')

class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[InputRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email(message='Please enter a vallid email address')])
    image_url = StringField('(Optional) Image URL')
    password = PasswordField('Password', validators=[Length(min=6)])
    submit = SubmitField('Update Profile')

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])