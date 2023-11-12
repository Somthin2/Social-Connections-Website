import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps
import firebase_admin
from firebase_admin import credentials, db, firestore



def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def reg_required(f):
    """ similar to the login """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db = firestore.client()

        likings = db.collection('likes').document(session.get("user_id")).get()
        user = db.collection('usrProfile').document(session.get("user_id")).get()

        if not user.to_dict():
            return redirect("/")
        elif not likings.to_dict():
            return redirect("/")

        return f(*args, **kwargs)
    return decorated_function


