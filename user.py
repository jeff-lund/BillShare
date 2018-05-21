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
    db = get_db()
    bills = {}
    categories = db.execute('SELECT topic FROM bills WHERE id = ?', (g.user['id'],)).fetchall()
    for c in categories:
        bills[c] = db.execute('SELECT name, total, posted_date, due_date FROM bills WHERE id = ?, topic = ?', (g.user['id'], c,)).fetchall()

    return render_template('user/home.html')
# add item
@bp.route('/addbill', methods=('GET', 'POST'))
@login_required
def addbill():
    if(request.method == 'POST'):
        topic = request.form['topic']
        name = 

    return render_template('user/addbill.html')

# view item
