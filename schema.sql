DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS topics;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS group_members;
DROP TABLE IF EXISTS topic_members;
DROP TABLE IF EXISTS bill_members;
DROP TABLE IF EXISTS messages;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE groups (
  group_id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES user (id)
    ON DELETE CASCADE
);

CREATE TABLE topics (
  topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  group_id INTEGER NOT NULL,
  topic TEXT NOT NULL,
  default_enabled BOOLEAN,
  FOREIGN KEY (user_id) REFERENCES user (id)
    ON DELETE CASCADE,
  FOREIGN KEY (group_id) REFERENCES groups (group_id)
    ON DELETE CASCADE
);

CREATE TABLE bills (
  bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  group_id INTEGER NOT NULL,
  topic_id INTEGER NOT NULL,
  total REAL NOT NULL,
  posted_date DATE,
  due_date DATE NOT NULL,
  paid BOOLEAN NOT NULL,
  past_due BOOLEAN NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES user (id)
    ON DELETE CASCADE,
  FOREIGN KEY (topic_id) REFERENCES topics (topic_id)
    ON DELETE CASCADE,
  FOREIGN KEY (group_id) REFERENCES groups (group_id)
    ON DELETE CASCADE
);

/* permission levels: 0-pending, 1-member, 2-owner */
CREATE TABLE group_members (
  group_id INTEGER NOT NULL,
  member_id INTEGER NOT NULL,
  permission INTEGER NOT NULL,
  FOREIGN KEY (group_id) REFERENCES groups (group_id)
    ON DELETE CASCADE
);

CREATE TABLE topic_members (
  topic_id INTEGER NOT NULL,
  member_id INTEGER NOT NULL,
  percentage INTEGER NOT NULL,
  FOREIGN KEY (topic_id) REFERENCES topics (topic_id)
    ON DELETE CASCADE,
  FOREIGN KEY (member_id) REFERENCES user (id)
    ON DELETE CASCADE
);

CREATE TABLE bill_members (
  bill_id INTEGER NOT NULL,
  member_id INTEGER NOT NULL,
  member_sum INTEGER NOT NULL,
  member_paid BOOLEAN NOT NULL,
  FOREIGN KEY (bill_id) REFERENCES bills (bill_id)
    ON DELETE CASCADE,
  FOREIGN KEY (member_id) REFERENCES user (id)
    ON DELETE CASCADE
);


CREATE TABLE messages (
  mes_id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender_id INTEGER,
  rec_id INTEGER NOT NULL,
  mes TEXT,
  viewed BOOLEAN,
  date_stamp DATE,
  FOREIGN KEY (rec_id) REFERENCES user (id)
    ON DELETE CASCADE
);
