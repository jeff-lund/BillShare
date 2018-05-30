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
    error = None
    date = datetime.date.today()
    groups = db.execute(
        'SELECT * FROM groups \
        JOIN group_members on groups.group_id = group_members.group_id  \
        WHERE group_members.member_id = ? AND group_members.permission != 0', (g.user['id'],)).fetchall()
    cat = db.execute('SELECT * FROM topics \
        JOIN group_members on topics.group_id=group_members.group_id \
        WHERE group_members.member_id = ?', (g.user['id'],)).fetchall()
    bills = db.execute(
        'SELECT * FROM bills \
        JOIN group_members on bills.group_id=group_members.group_id \
        WHERE group_members.member_id = ? AND bills.paid = 0', (g.user['id'],)).fetchall()

    if request.method == 'POST':
        if 'paid' in request.form:
            db.execute('UPDATE bills SET paid = 1 WHERE bill_id = ?', (request.form['paid'],))
            db.commit()

            return redirect(url_for('.home', username = g.user['username']))
        if 'delete' in request.form:
            db.execute('DELETE FROM bills WHERE bill_id = ?', (request.form['delete'],))
            db.commit()

            return redirect(url_for('.home', username = g.user['username']))

    if error is not None:
        flash(error)

    return render_template('user/home.html', cat=cat, bills=bills, groups=groups, username=g.user['username'])

#add topic
@bp.route('/addtopic/<group_id>', methods=['POST'])
@login_required
def addtopic(group_id):
    db = get_db()
    error = None
    category = request.form['category']
    if not category:
        error = "Please enter a new category"
    if db.execute(
        'SELECT topic FROM topics WHERE user_id = ? \
        AND group_id = ? AND topic = ?', \
        (g.user['id'], group_id, category,)).fetchone() is not None:
        error = "Category already exists"
    if error is None:
        db.execute(
            'INSERT INTO topics (user_id, topic, group_id) \
            VALUES (?, ?, ?)', (g.user['id'], category, group_id))
        db.commit()
    if error is not None:
        flash(error)
    return redirect(url_for('.home', username = g.user['username']))

# add item
@bp.route('/addbill/<group_id>/<topic_id>', methods=['POST'])
@login_required
def addbill(group_id, topic_id):
    db = get_db()
    error = None
    total = float(request.form['total'])
    due = request.form['due']
    posted = request.form['posted']

    db.execute('INSERT INTO bills \
        (owner_id, group_id, topic_id, total, posted_date, due_date, paid, past_due) \
        VALUES (?, ?, ?, ?, ?, ?, 0, 0)', \
        (g.user['id'], group_id, topic_id, total, posted, due,))
    db.commit()
    return redirect(url_for('.home', username=g.user['username']))

# add new group
@bp.route('/<username>/addgroup', methods=('GET', 'POST'))
@login_required
def addgroup(username):
    if request.method == 'POST':
        db = get_db()
        error = None
        name = request.form['name']
        if (db.execute('SELECT name FROM groups WHERE name = ?', (name,)).fetchone()) is not None:
            error = "Group Already Exists"

        if error is None:
            db.execute('INSERT INTO groups (owner_id, name) VALUES (?, ?)', (g.user['id'], name,))
            db.commit()
            gid = db.execute('SELECT group_id FROM groups WHERE  name = ?', (name,)).fetchone()
            db.execute('INSERT INTO group_members (group_id, member_id, permission) VALUES (?, ?, 2)', (gid['group_id'], g.user['id'],))
            db.commit()
            return redirect(url_for('.home', username=g.user['username']))

        flash(error)

    return render_template('user/addgroup.html', username=g.user['username'])

# Group Management
@bp.route('/<username>/groupmanagement', methods=('GET', 'POST'))
@login_required
def groupmanagement(username):
    db = get_db()

    invites = db.execute(
        'SELECT * FROM groups \
        INNER JOIN group_members on groups.group_id = group_members.group_id \
        WHERE group_members.member_id = ? AND group_members.permission = 0', (g.user['id'],)).fetchall()

    group = db.execute(
        'SELECT * FROM groups \
        INNER JOIN group_members on groups.group_id = group_members.group_id \
        WHERE group_members.member_id = ? AND group_members.permission != 0 \
        AND groups.name != ?', \
        (g.user['id'], 'Default',)).fetchall()

    topics = db.execute('SELECT * FROM topics \
        INNER JOIN group_members on topics.group_id = group_members.group_id \
        WHERE group_members.member_id = ?', \
        (g.user['id'], )).fetchall()

    if request.method == 'POST':
        error = None
        # Accept invite request
        if 'accept' in request.form:
            db.execute('UPDATE group_members SET permission = 1 \
                WHERE member_id = ? AND group_id = ?', \
                (g.user['id'], request.form['accept'],))
            db.commit()

            return redirect(url_for('.groupmanagement', username=g.user['username']))
        #deny invite request
        elif 'deny' in request.form:
            db.execute(
                'DELETE FROM group_members \
                WHERE member_id = ? \
                AND group_id = ?', (g.user['id'], request.form['deny']))
            db.commit()

            return redirect(url_for('.groupmanagement', username=g.user['username']))

        # Inviting a new member to a group
        elif 'invite' in request.form:
            invitee = db.execute(
                'SELECT username, id FROM user \
                WHERE username = ?', (request.form['invite'],)).fetchone()
            if invitee is None:
                error = "User does not exist"
            elif db.execute(
                'SELECT member_id FROM group_members \
                WHERE member_id = ? AND group_id = ?', \
                (invitee['id'], request.form['gid'],)).fetchone() is not None:
                error = "User is already in the group or has a pending invitation"
            else:
                db.execute(
                    'INSERT INTO group_members (group_id, member_id, permission) VALUES (?, ?, 0)', \
                    (request.form['gid'], invitee['id']))
                name = db.execute(
                'SELECT name FROM groups WHERE group_id = ?', \
                (request.form['gid'],)).fetchone()

                inv_msg = '{} has invited you to join {}.'.format(g.user['username'], name['name'])
                db.execute(
                    'INSERT INTO messages (sender_id, rec_id, mes, viewed) VALUES (?, ?, ?, 0)', \
                    (g.user['id'], invitee['id'], inv_msg,))
                db.commit()
                error = "Group Invitation Sent"
                #return redirect(url_for('.groupmanagement', username=g.user['username']))
        # Rename A Group
        elif 'rename' in request.form:
            if db.execute(
                'SELECT name FROM groups WHERE name = ?',\
                 (request.form['rename'],)).fetchone() is not None:
                error = 'Group Name Not Available'
            else:
                db.execute(
                    'UPDATE groups SET name = ? WHERE group_id = ?', \
                    (request.form['rename'], request.form['gid'],))
                db.commit()

                return redirect(url_for('.groupmanagement', username=g.user['username']))
        # Delete a Group
        elif 'delete' in request.form:
            # should make a delete utility function
            # any bills will be moved back to owners default groups
            # table owners bills should be deleted (?) or optional delete
            db.execute('DELETE FROM groups WHERE group_id = ?', (request.form['delete'],))
            db.commit()

            return redirect(url_for('.home', username=g.user['username']))
        # Level a Group as a member_id
        elif 'leavegrp' in request.form:
            db.execute(
                'DELETE FROM group_members WHERE group_id = ? and member_id = ?', \
                (request.form['leavegrp'], g.user['id']))
            db.commit()

            return redirect(url_for('.home', username=g.user['username']))

        if error is not None:
            flash(error)

    return render_template('user/groupmanagement.html', username=g.user['username'], group=group, invites=invites, topics=topics)

# Deleting A topic
@bp.route('/removetopic', methods=['POST'])
@login_required
def removetopic():
    db = get_db()
    topic_id = request.form['removetopic']
    # delete if owner move back to owner's default if not owner
    db.execute('DELETE FROM topics WHERE topic_id = ?', (topic_id,))
    db.commit()

    return redirect(url_for('.home', username=g.user['username']))

# Messages
@bp.route('/<username>/messages', methods=('GET', 'POST'))
@login_required
def messages(username):
    db = get_db()
    messages = db.execute(
        'SELECT mes_id, sender_id, rec_id, mes, viewed FROM messages WHERE rec_id = ? AND viewed = 0', \
        (g.user['id'],)).fetchall()

    if request.method == 'POST':
        if 'seen' in request.form:
            db.execute('UPDATE messages SET viewed =1 WHERE mes_id = ?', (request.form['seen'],))
            db.commit()
            return redirect(url_for('.messages', username = g.user['username']))

    return render_template('user/messages.html', username=g.user['username'], messages=messages)
