#!/usr/bin/env python3
"""
Test script to verify that history displays both direct emails and campaign emails
"""

import sqlite3
import os

def test_history_query():
    print("🔍 Testing History Display Query")
    print("=" * 50)
    
    # Database file path
    db_file = os.path.join("private", "contacts.db")
    
    if not os.path.exists(db_file):
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # Simulate the history query logic
    print("📧 Direct Emails:")
    c.execute("SELECT timestamp, email, subject, body, status FROM email_history ORDER BY timestamp DESC")
    direct_rows = [(row[0], row[1], row[2], row[3], row[4], "Direct") for row in c.fetchall()]
    print(f"   Found {len(direct_rows)} direct email records")
    
    print("\n📨 Campaign Emails:")
    c.execute("""
        SELECT h.timestamp, ct.email, c.name, 
               COALESCE(h.personalized_body, c.body) as body_content, 
               h.status 
        FROM email_campaign_history h
        LEFT JOIN email_campaigns c ON h.campaign_id = c.id
        LEFT JOIN contacts ct ON h.contact_id = ct.id
        ORDER BY h.timestamp DESC
    """)
    campaign_rows = [(row[0], row[1], f"Campaign: {row[2]}", row[3], row[4], "Campaign") for row in c.fetchall()]
    print(f"   Found {len(campaign_rows)} campaign email records")
    
    # Combine and sort
    all_rows = direct_rows + campaign_rows
    rows = sorted(all_rows, key=lambda x: x[0], reverse=True)[:10]  # Top 10
    
    print(f"\n📋 Combined History (Latest 10):")
    print("-" * 70)
    for i, row in enumerate(rows, 1):
        timestamp, recipient, subject, body, status, email_type = row
        print(f"{i:2}. {timestamp} | {email_type:8} | {recipient:30} | {status}")
        if subject and subject.strip():
            print(f"    Subject: {subject[:50]}...")
        if body and body.strip():
            print(f"    Body: {body[:100]}...")
        print()
    
    conn.close()
    print(f"\n✅ Total records available for display: {len(all_rows)}")

if __name__ == "__main__":
    test_history_query()
