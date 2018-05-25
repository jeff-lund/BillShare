#imports
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from billshare.auth import login_required
from billshare.db import get_db
import datetime

bp = Blueprint('user', __name__)

# user home page
@bp.route('/<username>/home', methods=('GET', 'POST'))
@login_required
def home(username):
    db = get_db()
    date = str(datetime.date.today())
    cat = db.execute('SELECT topic FROM topics WHERE id = ?', (g.user['id'],)).fetchall()
    bills = db.execute('SELECT total, posted_date, due_date, topic, bill_id, past_due FROM bills WHERE id = ? AND paid = 0', (g.user['id'],)).fetchall()

    for b in bills:
        if b.past_due < date:
            db.execute('UPDATE bills SET past_due = 1 WHERE bill_id =?' (bill_id))
            db.commit()

    if(request.method == 'POST'):
        del_id = request.form['paid']
        db.execute('UPDATE bills SET paid = 1 WHERE bill_id = ?', (del_id))
        db.commit()
        return redirect('user/home.html', cat=cat, bills=bills, username = g.user['username'])

    return render_template('user/home.html', cat=cat, bills=bills, username = g.user['username'])

#add topic
@bp.route('/<username>/addtopic', methods=('GET', 'POST'))
@login_required
def addtopic(username):
    if(request.method == 'POST'):
        db = get_db()
        error = None
        category = request.form['topic']

        if not category:
            error = "Please enter a new category"

        if db.execute('SELECT topic FROM topics WHERE id = ? AND topic = ?', (g.user['id'], category,)).fetchone() is not None:
            error = "Category already exists"

        if error is None:
            db.execute( 'INSERT INTO topics (id, topic) VALUES (?, ?)', (g.user['id'], category))
            db.commit()
            return redirect(url_for('.home', username = g.user['username']))

        flash(error)

    return render_template('user/addtopic.html', username=g.user['username'])


# add item
@bp.route('/<username>/addbill/<top>', methods=('GET', 'POST'))
@login_required
def addbill(username,top):
    if(request.method == 'POST'):
        db = get_db()
        error = None
        total = float(request.form['total'])
        due = request.form['due']
        posted = request.form['posted']

        db.execute('INSERT INTO bills (id, topic, total, posted_date, due_date, paid, past_due) VALUES ( ?, ?, ?, ?, ?, 0, 0)', (g.user['id'], top, total, posted, due,))
        db.commit()
        return redirect(url_for('.home', username=g.user['username']))

    return render_template('user/addbill.html', username=g.user['username'])

# view item
