from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_session import Session
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, validators
import re
import os
import subprocess
from datetime import datetime
import app_forms

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
csrf = CSRFProtect(app)
SESSION_TYPE = 'filesystem'
app.config['SESSION_TYPE'] = SESSION_TYPE
Session(app)

registration_info = []
logged_in_user = []

validate_success = 1
validate_login = 0
validate_2fa = -1

@app.route('/')
def home():
    if len(registration_info) == 0:
        return redirect('/register')
    elif len(logged_in_user) == 0:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('spell_check'))

@app.route('/set/')
def set():
    session['key'] = 'value'
    return 'ok'

@app.route('/get/')
def get():
    return session.get('key', 'not set')

@app.route('/api/data')
def get_data():
    return app.send_static_file('data.json')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET','POST'])
def register():
    try:
        form=app_forms.RegistrationForm(request.form)

        if request.method == 'POST':
            if form.validate_on_submit():
                user = {}
                user['username'] = form.username.data
                user['password'] = form.password.data
                user['twofactor'] = form.phone2fa.data
                registration_info.append(user)
                flash('Registration was a success', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration was a faulure', 'success')
            
        return render_template('register.html', form=form)
    except Exception as e:
        return(str(e))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        form = app_forms.LoginForm(request.form)

        if request.method == 'POST' and form.validate_on_submit():
            logged_in_user.clear()
            user = {}
            user['username'] = form.username.data
            user['password'] = form.password.data
            user['twofactor'] = form.phone2fa.data
            validation = validate_user(user)
            if validation == validate_success:
                logged_in_user.append(user)
                flash('Login was a success', 'result')
            elif validation == validate_login:
                flash('Incorrect', 'result')
            else:
                flash('Two-factor failure', 'result')

            return redirect(url_for('spell_check')) 
    except Exception as e:
        return(str(e))
    return render_template('login.html', form=form)

def validate_user(user):
    validation_result = validate_success
    for registered_user in registration_info:
        if user['username'] == registered_user['username']:
            if user['password'] == registered_user['password']:
                if user['twofactor'] == registered_user['twofactor']:
                    validation_result = validate_success
                    return validation_result
                else:
                    validation_result = validate_2fa
            else:
                validation_result = validate_login
        else:
            validation_result = validate_login
    
    return validation_result

@app.route('/spell_check', methods=['GET', 'POST'])
def spell_check():
    if len(registration_info) == 0:
        return redirect('/register')
    elif len(logged_in_user) == 0:
        return redirect(url_for('login'))

    try:
        form = app_forms.SpellCheckForm(request.form)

        if request.method == 'POST' and form.validate_on_submit():
            lines = form.inputtext.data.split('\n')
            f = open('check_words.txt', 'w')
            f.writelines(lines)
            f.close()

            p = subprocess.run(['./a.out', './check_words.txt', './wordlist.txt'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            msg = '\n'.join(lines)
            sc_form = app_forms.SpellCheckResultsForm()
            sc_form.inputtext.data = msg
            msg = p.stdout.decode('utf-8')
            msg = msg.replace('\n', ', ')
            msg = msg.rstrip(', ')
            
            sc_form.misspelled.data = msg
            return render_template('sc_results.html', form=sc_form) 

    except Exception as e:
        return(str(e))
    return render_template('spell_check.html', form=form)

@app.route('/sc_results', methods=['GET'])
def sc_results():
    if len(registration_info) == 0:
        return redirect('/register')
    elif len(logged_in_user) == 0:
        return redirect(url_for('login'))

    try:
        form = app_forms.SpellCheckResultsForm(request.form)

        if request.method == 'POST' and form.validate_on_submit():
            return redirect(url_for('spell_check'))

    except Exception as e:
        return(str(e))
    return render_template('sc_results.html', form=form)