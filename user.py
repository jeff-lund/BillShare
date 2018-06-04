#imports
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from billshare.auth import login_required
from billshare.db import get_db
import datetime
import sqlite3
from billshare.user_util import even_split, custom_split, reset_bills, get_member_list
bp = Blueprint('user', __name__)

# user home page
@bp.route('/<username>/home', methods=('GET', 'POST'))
@login_required
def home(username):
    db = get_db()
    error = None
    date = datetime.date.today()
    has_paid = {}
    valid_bill_ids = set()
    groups = db.execute(
        'SELECT * FROM groups \
        JOIN group_members on groups.group_id = group_members.group_id  \
        WHERE group_members.member_id = ? AND group_members.permission > 0', (g.user['id'],)).fetchall()
    cat = db.execute('SELECT * FROM topics \
        JOIN group_members on topics.group_id=group_members.group_id \
        WHERE group_members.member_id = ?', (g.user['id'],)).fetchall()
    bills = db.execute(
        'SELECT * FROM bills \
        JOIN group_members on bills.group_id=group_members.group_id \
        JOIN bill_members on bill_members.bill_id=bills.bill_id \
        WHERE group_members.member_id = ? AND bills.paid = 0 AND bill_members.member_id = ?' \
        , (g.user['id'], g.user['id'],)).fetchall()
    for b in bills:
        valid_bill_ids.add(b['bill_id'])
    members = get_member_list(groups)
    for gr in groups:
        has_paid[gr['group_id']] = {}
        for m in members[gr['group_id']]:
            has_paid[gr['group_id']][m] = {}
            member_data = db.execute('SELECT username, bill_id, member_paid \
                FROM user INNER JOIN bill_members \
                on user.id=bill_members.member_id \
                WHERE user.username=?', (m,)).fetchall()
            for entry in member_data:
                if(entry['bill_id'] in valid_bill_ids):
                    has_paid[gr['group_id']][m][entry['bill_id']] = entry['member_paid']

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

    return render_template('user/home.html', cat=cat, bills=bills, groups=groups, username=g.user['username'], members=members, has_paid=has_paid)

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
            'INSERT INTO topics (user_id, topic, group_id, default_enabled) \
            VALUES (?, ?, ?, ?)', \
            (g.user['id'], category, group_id, request.form['split_type']))
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
    default = db.execute(
        'SELECT default_enabled FROM topics \
        WHERE topic_id = ?', (topic_id,)).fetchone()
    last = db.execute('INSERT INTO bills \
        (owner_id, group_id, topic_id, total, posted_date, due_date, paid, past_due) \
        VALUES (?, ?, ?, ?, ?, ?, 0, 0)', \
        (g.user['id'], group_id, topic_id, total, posted, due,)).lastrowid


    #initialze bill_members
    members = db.execute(
        'SELECT member_id FROM group_members WHERE group_id = ?', \
        (group_id)).fetchall()
    for m in members:
        db.execute('INSERT INTO bill_members (bill_id, member_id, member_paid) \
        VALUES (?, ?, 0)', (last, m[0]))

    db.commit()
    if default['default_enabled'] == 1:
        even_split(last, topic_id, group_id)
    else:
        custom_split(last, topic_id, group_id)

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
            gid = db.execute('INSERT INTO groups (owner_id, name) \
                VALUES (?, ?)', (g.user['id'], name,)).lastrowid
            db.commit()
            db.execute('INSERT INTO group_members (group_id, member_id, permission) VALUES (?, ?, 2)', (gid, g.user['id'],))
            db.commit()
            return redirect(url_for('.home', username=g.user['username']))

        flash(error)

    return render_template('user/addgroup.html', username=g.user['username'])

# Group Management
@bp.route('/<username>/groupmanagement', methods=('GET', 'POST'))
@login_required
def groupmanagement(username):
    db = get_db()
    members = {}
    error = None

    invites = db.execute('SELECT * FROM groups \
    INNER JOIN group_members on groups.group_id=group_members.group_id \
    WHERE group_members.member_id=? AND group_members.permission=0', \
    (g.user['id'],)).fetchall()

    group = db.execute(
        'SELECT * FROM groups \
        INNER JOIN group_members on groups.group_id=group_members.group_id \
        WHERE group_members.member_id=? AND group_members.permission != 0', \
        (g.user['id'],)).fetchall()

    topics = db.execute('SELECT * FROM topics \
        INNER JOIN group_members on topics.group_id = group_members.group_id \
        WHERE group_members.member_id=? AND group_members.permission > 0', \
        (g.user['id'], )).fetchall()
    members = get_member_list(group)

    if request.method == 'POST':
        # Accept invite request
        if 'accept' in request.form:
            gid = request.form['accept']
            db.execute('UPDATE group_members SET permission = 1 \
                WHERE member_id = ? AND group_id = ?', \
                (g.user['id'], gid,))
            db.commit()
            cat = db.execute('SELECT topic_id from topics WHERE group_id = ?', (request.form['accept'],)).fetchall()
            for entry in cat:
                bills = db.execute('SELECT bill_id FROM bills \
                    WHERE topic_id = ? AND paid = 0 AND past_due = 0', \
                    (entry['topic_id'],)).fetchall()
                for b in bills:
                    db.execute('INSERT INTO bill_members (bill_id, member_id, member_paid) \
                    VALUES (?, ?, 0)', (b['bill_id'], g.user['id'],))
                    db.commit()
                    even_split(b['bill_id'], entry['topic_id'], gid)

                return redirect(url_for('.groupmanagement', username=g.user['username']))
        #deny invite request
        elif 'deny' in request.form:
            db.execute(
                'DELETE FROM group_members \
                WHERE member_id=? \
                AND group_id=?', (g.user['id'], request.form['deny']))
            db.commit()
            return redirect(url_for('.groupmanagement', username=g.user['username']))
        # Remove topic
        elif 'removetopic' in request.form and request.form['removetopic'] is not 'None':
                db.execute("DELETE FROM topics WHERE topic_id=(?)", (request.form['removetopic'],))
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
                return redirect(url_for('.groupmanagement', username=g.user['username']))
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

            return redirect(url_for('.groupmanagement', username=g.user['username']))
        # Leave a Group
        elif 'leavegrp' in request.form:
            db.execute(
                'DELETE FROM group_members WHERE group_id = ? and member_id = ?', \
                (request.form['leavegrp'], g.user['id']))
            db.commit()
            reset_bills(request.form['leavegrp'])

            return redirect(url_for('.groupmanagement', username=g.user['username']))

    if error is not None:
        flash(error)

    return render_template('user/groupmanagement.html', username=g.user['username'], group=group, invites=invites, topics=topics, members=members)

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
