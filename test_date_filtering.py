#!/usr/bin/env python3
"""
Test script to verify date filtering functionality in history
"""

import sqlite3
import os
from datetime import datetime, timedelta

def test_date_filtering():
    print("🗓️ Testing Date Filtering Functionality")
    print("=" * 45)
    
    db_path = os.path.join("private", "contacts.db")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Test date queries similar to what the history dialog uses
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    print(f"📅 Testing date ranges:")
    print(f"   Today: {today}")
    print(f"   Yesterday: {yesterday}")
    print(f"   Week ago: {week_ago}")
    
    # Test today's emails
    print(f"\n📧 Campaign emails from today ({today}):")
    c.execute("""
        SELECT COUNT(*), MIN(timestamp), MAX(timestamp)
        FROM email_campaign_history 
        WHERE DATE(timestamp) = ?
    """, (today.strftime("%Y-%m-%d"),))
    
    result = c.fetchone()
    count, min_time, max_time = result
    print(f"   Found {count} records")
    if count > 0:
        print(f"   Time range: {min_time} to {max_time}")
    
    # Test last 7 days
    print(f"\n📧 Campaign emails from last 7 days ({week_ago} to {today}):")
    c.execute("""
        SELECT COUNT(*), MIN(timestamp), MAX(timestamp)
        FROM email_campaign_history 
        WHERE DATE(timestamp) BETWEEN ? AND ?
    """, (week_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")))
    
    result = c.fetchone()
    count, min_time, max_time = result
    print(f"   Found {count} records")
    if count > 0:
        print(f"   Time range: {min_time} to {max_time}")
    
    # Test specific date
    test_date = "2025-07-06"  # Known date with records
    print(f"\n📧 Campaign emails from {test_date}:")
    c.execute("""
        SELECT COUNT(*), MIN(timestamp), MAX(timestamp)
        FROM email_campaign_history 
        WHERE DATE(timestamp) = ?
    """, (test_date,))
    
    result = c.fetchone()
    count, min_time, max_time = result
    print(f"   Found {count} records")
    if count > 0:
        print(f"   Time range: {min_time} to {max_time}")
        
        # Show a few sample records
        c.execute("""
            SELECT h.timestamp, ct.email, c.name
            FROM email_campaign_history h
            LEFT JOIN email_campaigns c ON h.campaign_id = c.id
            LEFT JOIN contacts ct ON h.contact_id = ct.id
            WHERE DATE(h.timestamp) = ?
            ORDER BY h.timestamp DESC
            LIMIT 3
        """, (test_date,))
        
        print("   Sample records:")
        for i, row in enumerate(c.fetchall(), 1):
            timestamp, email, campaign_name = row
            print(f"     {i}. {timestamp} | {email} | Campaign: {campaign_name}")
    
    # Test all records (no date filter)
    print(f"\n📧 All campaign emails (no date filter):")
    c.execute("SELECT COUNT(*) FROM email_campaign_history")
    total_count = c.fetchone()[0]
    print(f"   Total records: {total_count}")
    
    conn.close()
    print("\n✅ Date filtering test completed!")

if __name__ == "__main__":
    test_date_filtering()
