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
            body TEXT,
            status TEXT DEFAULT 'draft',
            last_updated TEXT,
            processing_details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
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
            error TEXT,
            personalized_subject TEXT,
            personalized_body TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sms_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'draft',
            last_updated TEXT,
            processing_details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sms_campaign_contacts (
            campaign_id INTEGER,
            contact_id INTEGER,
            FOREIGN KEY(campaign_id) REFERENCES sms_campaigns(id),
            FOREIGN KEY(contact_id) REFERENCES contacts(id),
            UNIQUE(campaign_id, contact_id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sms_campaign_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            contact_id INTEGER,
            timestamp TEXT,
            status TEXT,
            error TEXT,
            personalized_message TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS background_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            campaign_type TEXT,
            status TEXT DEFAULT 'pending',
            pid INTEGER,
            started_at TEXT,
            completed_at TEXT,
            error_message TEXT
        )
    ''')
    
    # Ensure status columns exist for email campaigns (for backwards compatibility)
    try:
        c.execute("ALTER TABLE email_campaigns ADD COLUMN status TEXT DEFAULT 'draft'")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        c.execute("ALTER TABLE email_campaigns ADD COLUMN last_updated TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE email_campaigns ADD COLUMN processing_details TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE email_campaigns ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass
        
    # Ensure enhanced history columns exist
    try:
        c.execute("ALTER TABLE email_campaign_history ADD COLUMN personalized_subject TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE email_campaign_history ADD COLUMN personalized_body TEXT")
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()