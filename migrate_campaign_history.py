#!/usr/bin/env python3
"""
Database migration: Add personalized_subject and personalized_body columns to email_campaign_history
"""

import sqlite3
import os

def migrate_database():
    db_path = os.path.join("private", "contacts.db")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Check if columns already exist
        c.execute("PRAGMA table_info(email_campaign_history)")
        columns = [col[1] for col in c.fetchall()]
        
        print(f"📋 Current columns: {columns}")
        
        # Add personalized_subject column if it doesn't exist
        if 'personalized_subject' not in columns:
            print("📝 Adding personalized_subject column...")
            c.execute("ALTER TABLE email_campaign_history ADD COLUMN personalized_subject TEXT")
            print("✅ Added personalized_subject column")
        else:
            print("ℹ️ personalized_subject column already exists")
        
        # Add personalized_body column if it doesn't exist
        if 'personalized_body' not in columns:
            print("📝 Adding personalized_body column...")
            c.execute("ALTER TABLE email_campaign_history ADD COLUMN personalized_body TEXT")
            print("✅ Added personalized_body column")
        else:
            print("ℹ️ personalized_body column already exists")
        
        conn.commit()
        
        # Verify the changes
        c.execute("PRAGMA table_info(email_campaign_history)")
        new_columns = [col[1] for col in c.fetchall()]
        print(f"📋 Updated columns: {new_columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    if migrate_database():
        print("✅ Database migration completed successfully!")
    else:
        print("❌ Database migration failed!")
