from flask import Flask, render_template, redirect
import re
from datetime import datetime

app = Flask(__name__)

registration_info = {}

@app.route("/")
def home():
    if(len(registration_info) == 0):
        return redirect("/register")
    else:
        return redirect("/login")

@app.route("/api/data")
def get_data():
    return app.send_static_file("data.json")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

