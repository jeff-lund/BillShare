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
    cat = db.execute('SELECT topic FROM topics WHERE id = ?', (g.user['id'],)).fetchall()
    bills = db.execute('SELECT total, posted_date, due_date, topic, bill_id FROM bills WHERE id = ? AND paid = 0', (g.user['id'],)).fetchall()
    
    if(request.method == 'POST'):
        del_id = request.form['paid']
        db.execute('UPDATE bills SET paid = 1 WHERE bill_id = ?', (del_id))
        db.commit()
        return render_template('user/home.html', cat=cat, bills=bills)
    
    return render_template('user/home.html', cat=cat, bills=bills)

#add topic
@bp.route('/addtopic', methods=('GET', 'POST'))
@login_required
def addtopic():
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
            return redirect(url_for('.home'))

        flash(error)

    return render_template('user/addtopic.html')


# add item
@bp.route('/addbill/<top>', methods=('GET', 'POST'))
@login_required
def addbill(top):
    if(request.method == 'POST'):
        db = get_db()
        error = None
        total = float(request.form['total'])
        due = request.form['due']
        posted = request.form['posted']

        db.execute('INSERT INTO bills (id, topic, total, posted_date, due_date, paid) VALUES ( ?, ?, ?, ?, ?, 0)', (g.user['id'], top, total, posted, due,))
        db.commit()
        return redirect(url_for('.home'))

    return render_template('user/addbill.html')

# view item
