#!/usr/bin/env python3
"""
Check email history in the database
"""

import sqlite3
import os

def check_email_history():
    db_path = os.path.join("private", "contacts.db")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Check if email_history table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='email_history'")
        if not c.fetchone():
            print("❌ email_history table does not exist!")
            return
        
        # Get table schema
        c.execute("PRAGMA table_info(email_history)")
        columns = c.fetchall()
        print("📋 Email History Table Schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Count total records
        c.execute("SELECT COUNT(*) FROM email_history")
        total = c.fetchone()[0]
        print(f"\n📊 Total email history records: {total}")
        
        if total > 0:
            # Get recent records
            c.execute("SELECT timestamp, email, subject, status FROM email_history ORDER BY id DESC LIMIT 10")
            rows = c.fetchall()
            print("\n📨 Recent 10 email records:")
            for i, row in enumerate(rows, 1):
                print(f"  {i}. {row[0]} | {row[1]} | {row[2][:30]}... | {row[3]}")
        else:
            print("\n⚠️ No email history records found!")
        
        # Check email_campaign_history too
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='email_campaign_history'")
        if c.fetchone():
            # Get campaign table schema first
            c.execute("PRAGMA table_info(email_campaign_history)")
            campaign_columns = c.fetchall()
            print("\n📬 Email Campaign History Table Schema:")
            for col in campaign_columns:
                print(f"  {col[1]} ({col[2]})")
            
            c.execute("SELECT COUNT(*) FROM email_campaign_history")
            campaign_total = c.fetchone()[0]
            print(f"\n📈 Email campaign history records: {campaign_total}")
            
            if campaign_total > 0:
                # Use raw query first to see actual data
                c.execute("SELECT * FROM email_campaign_history ORDER BY id DESC LIMIT 5")
                rows = c.fetchall()
                print("\n📬 Recent 5 campaign email records (raw):")
                for i, row in enumerate(rows, 1):
                    print(f"  {i}. {row}")
                
                # Try the join query
                try:
                    c.execute("""
                        SELECT h.timestamp, c.name, ct.email, h.status 
                        FROM email_campaign_history h
                        LEFT JOIN email_campaigns c ON h.campaign_id = c.id
                        LEFT JOIN contacts ct ON h.contact_id = ct.id
                        ORDER BY h.id DESC LIMIT 5
                    """)
                    join_rows = c.fetchall()
                    print("\n📬 Recent 5 campaign email records (joined):")
                    for i, row in enumerate(join_rows, 1):
                        print(f"  {i}. {row[0]} | Campaign: {row[1]} | To: {row[2]} | Status: {row[3]}")
                except Exception as join_error:
                    print(f"\n⚠️ Join query failed: {join_error}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_email_history()
