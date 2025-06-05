import sqlite3
import os

from features.common import DB_FILE, PRIVATE_DIR

def init_db():
    os.makedirs(PRIVATE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_name TEXT UNIQUE NOT NULL,
            name TEXT,
            description TEXT
        )
    ''')
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS email_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            subject TEXT,
            body TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS email_campaign_contacts (
            campaign_id INTEGER,
            contact_id INTEGER,
            FOREIGN KEY(campaign_id) REFERENCES email_campaigns(id),
            FOREIGN KEY(contact_id) REFERENCES contacts(id),
            UNIQUE(campaign_id, contact_id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS email_campaign_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            contact_id INTEGER,
            timestamp TEXT,
            status TEXT,
            error TEXT
        )
    ''')
    conn.commit()
    conn.close()