DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS topics;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS group_members;
DROP TABLE IF EXISTS messages;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE topics (
  id INTEGER,
  group_id INTEGER NOT NULL,
  topic TEXT NOT NULL,
  FOREIGN KEY (id) REFERENCES user (id)
    ON DELETE CASCADE,
  FOREIGN KEY (group_id) REFERENCES groups (group_id)
    ON DELETE CASCADE
);

CREATE TABLE bills (
  owner_id INTEGER NOT NULL,
  bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
  group_id INTEGER NOT NULL,
  topic TEXT NOT NULL,
  total REAL NOT NULL,
  member_portion REAL,
  owner_portion REAL,
  posted_date TEXT,
  due_date TEXT NOT NULL,
  paid INTEGER NOT NULL,
  past_due INTEGER NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES user (id)
    ON DELETE CASCADE,
  FOREIGN KEY (topic) REFERENCES topics (topic)
    ON DELETE CASCADE,
  FOREIGN KEY (group_id) REFERENCES groups (group_id)
    ON DELETE CASCADE
);

CREATE TABLE groups (
  group_id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES user (id)
    ON DELETE CASCADE
);

/* permission levels: 0-pending, 1-member, 2-owner */
CREATE TABLE group_members (
  group_id INTEGER NOT NULL,
  member_id INTEGER NOT NULL,
  permission INTEGER NOT NULL,
  FOREIGN KEY (group_id) REFERENCES groups(group_id)
    ON DELETE CASCADE
);

CREATE TABLE messages (
  mes_id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender_id INTEGER,
  rec_id INTEGER,
  mes TEXT,
  viewed INTEGER
);
