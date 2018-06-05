# !usr/bin/python3
# Copyright (c) 2018 Jeff Lund

import functools
from flask import Blueprint, g, request, session, render_template, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from billshare.db import get_db

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username or not password:
            error = "Missing required field"
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'Username not available.'

        # sucessful generation of new user
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            id = db.execute(
                'SELECT id FROM user WHERE username =?',
                (username,)).fetchone()
            db.execute(
                'INSERT INTO groups (owner_id, name) VALUES (?, ?)',
                (id['id'], 'Default',)
            )
            gid = db.execute(
                'SELECT group_id FROM groups \
                WHERE owner_id = ? AND name = ?', \
                (id['id'], 'Default',)).fetchone()
            db.execute('INSERT INTO group_members (group_id, member_id, permission) \
                VALUES (?, ?, 2)',  (gid['group_id'], id['id'],))
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        if user is None:
            error = 'Username not found.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('user.home', username=username))

        flash(error)

    return render_template('login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped_view
