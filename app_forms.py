from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[validators.Length(min=4, max=25), validators.DataRequired()], id='uname')
    password = PasswordField('Password', validators=[validators.Length(min=8, max=25), validators.DataRequired()], id='pword')
    phone2fa = StringField('Two factor phone number', id='2fa')



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.Length(min=4, max=25), validators.DataRequired()], id='uname')
    password = PasswordField('Password', validators=[validators.Length(min=8, max=25), validators.DataRequired()], id='pword')
    phone2fa = StringField('Two factor phone number', id='2fa')


    