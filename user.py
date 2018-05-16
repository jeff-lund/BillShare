#imports
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from billshare.auth import login_required
from billshare.db import get_db

bp = Blueprint('user', __name__, url_prefix = '/user')
# user home page
@bp.route('/home')
@login_required
def home():
    return render_template('user/home.html')

# add item
@bp.route('/addbill', methods=('GET', 'POST'))
@login_required
def addbill():
    return render_template('user/addbill.html')

# view item
