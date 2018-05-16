#imports
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from billshare.auth import login_required
from billshare.db import get_db

bp = Blueprint('user', __name__, url_prefix = '/user')
# user home page
@bp.route('/home', methods=('GET', 'POST'))
@login_required
def home():
    if(method == 'POST'):
        topic = request.form['topic']
        db = get_db()
        error = None
        if not topic:
            error = 'Please enter a name for a new topic'
        elif # check to make sure topic does not already exists

        # insert new entry into topic db
    return render_template('user/home.html')
# add item
@bp.route('/addbill', methods=('GET', 'POST'))
@login_required
def addbill():
    return render_template('user/addbill.html')

# view item
