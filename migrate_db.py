#!/usr/bin/env python3
"""
Database migration script for background processing features
"""

import sqlite3
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from features.common import DB_FILE

def migrate_database():
    """Migrate the database to support background processing"""
    print("🔧 Starting database migration...")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Add status columns to existing email_campaigns table
    try:
        cursor.execute('ALTER TABLE email_campaigns ADD COLUMN status TEXT DEFAULT "draft"')
        print('✅ Added status to email_campaigns')
    except sqlite3.OperationalError:
        print('ℹ️  email_campaigns.status already exists')
    
    try:
        cursor.execute('ALTER TABLE email_campaigns ADD COLUMN last_updated TEXT')
        print('✅ Added last_updated to email_campaigns')
    except sqlite3.OperationalError:
        print('ℹ️  email_campaigns.last_updated already exists')
    
    try:
        cursor.execute('ALTER TABLE email_campaigns ADD COLUMN processing_details TEXT')
        print('✅ Added processing_details to email_campaigns')
    except sqlite3.OperationalError:
        print('ℹ️  email_campaigns.processing_details already exists')
    
    try:
        cursor.execute('ALTER TABLE email_campaigns ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP')
        print('✅ Added created_at to email_campaigns')
    except sqlite3.OperationalError:
        print('ℹ️  email_campaigns.created_at already exists')
    
    # Enhanced history columns
    try:
        cursor.execute('ALTER TABLE email_campaign_history ADD COLUMN personalized_subject TEXT')
        print('✅ Added personalized_subject to email_campaign_history')
    except sqlite3.OperationalError:
        print('ℹ️  email_campaign_history.personalized_subject already exists')
    
    try:
        cursor.execute('ALTER TABLE email_campaign_history ADD COLUMN personalized_body TEXT')
        print('✅ Added personalized_body to email_campaign_history')
    except sqlite3.OperationalError:
        print('ℹ️  email_campaign_history.personalized_body already exists')
    
    # Create SMS campaigns table
    cursor.execute('''
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
    print('✅ Created/updated sms_campaigns table')
    
    # Create SMS campaign contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sms_campaign_contacts (
            campaign_id INTEGER,
            contact_id INTEGER,
            FOREIGN KEY(campaign_id) REFERENCES sms_campaigns(id),
            FOREIGN KEY(contact_id) REFERENCES contacts(id),
            UNIQUE(campaign_id, contact_id)
        )
    ''')
    print('✅ Created sms_campaign_contacts table')
    
    # Create SMS campaign history table
    cursor.execute('''
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
    print('✅ Created sms_campaign_history table')
    
    # Create background jobs table
    cursor.execute('''
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
    print('✅ Created background_jobs table')
    
    conn.commit()
    conn.close()
    print('🎉 Database migration complete!')

if __name__ == "__main__":
    migrate_database()
