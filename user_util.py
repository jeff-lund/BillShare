from billshare.db import get_db

def reset_bills(group_id):
    db = get_db()
    topics = db.execute('SELECT topic_id, default_enabled FROM topics \
        WHERE group_id=?', (group_id,)).fetchall()
    for t in topics:
        bills = db.execute('SELECT bill_id FROM bills \
        WHERE topic_id=? AND paid=0' \
            ,(t['topic_id'],)).fetchall()
        if t['default_enabled']:
            for b in bills:
                even_split(b['bill_id'], t['topic_id'], group_id)
        else:
            for b in bills:
                custom_split(b['bill_id'], t['topic_id'], group_id)


def even_split(bill_id, topic_id, group_id):
    db = get_db()
    members = db.execute(
        'SELECT * FROM group_members \
        WHERE group_id=? AND permission > 0', \
        (group_id,)).fetchall()
    num_members = len(members)
    bill = db.execute(
        'SELECT * from bills WHERE bill_id=?', \
        (bill_id,)).fetchone()
    member_portion = (1/num_members)*bill['total']
    for m in members:
        db.execute('UPDATE bill_members SET member_sum = ? \
        WHERE member_id=? AND bill_id=?',\
         (member_portion, m['member_id'], bill_id,))
    db.commit()
    return

def custom_split(bill_id, topic_id, group_id):
    pass

def get_member_list(groups):
    db = get_db()
    members = {}

    for gr in groups:
        mem = db.execute('SELECT username FROM user \
            JOIN group_members on group_members.member_id = user.id \
            WHERE group_members.group_id=? AND group_members.permission > 0', \
            (gr['group_id'],)).fetchall()
        member_list = [m['username'] for m in mem]
        members[gr['group_id']] = member_list

    return members

#def reset_bill_paid():
#    db = get_db()
#    db.execute("UPDATE bill_members SET member_paid=0")
#    db.commit()
