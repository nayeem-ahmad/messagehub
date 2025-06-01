import sqlite3

def init_db():
    conn = sqlite3.connect("contacts.db")
    c = conn.cursor()
    # Add short_name and description to groups table
    c.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_name TEXT UNIQUE NOT NULL,
            name TEXT,
            description TEXT
        )
    ''')
    # If old groups table exists, migrate data (if needed)
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            group_id INTEGER,
            contact_id INTEGER,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(contact_id) REFERENCES contacts(id),
            UNIQUE(group_id, contact_id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            subject TEXT,
            body TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS campaign_contacts (
            campaign_id INTEGER,
            contact_id INTEGER,
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id),
            FOREIGN KEY(contact_id) REFERENCES contacts(id),
            UNIQUE(campaign_id, contact_id)
        )
    ''')
    conn.commit()
    conn.close()