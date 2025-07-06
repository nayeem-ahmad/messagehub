#!/usr/bin/env python3
"""
Test script for enhanced datetime filtering in history dialog
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
import sqlite3
from datetime import datetime, timedelta
from features.history import show_history_dialog

def setup_test_data():
    """Insert test data with various timestamps"""
    from features.common import DB_FILE
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Ensure tables exist
    c.execute("""CREATE TABLE IF NOT EXISTS email_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        subject TEXT,
        body TEXT,
        email TEXT,
        status TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS email_campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        subject TEXT,
        body TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS email_campaign_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        contact_id INTEGER,
        timestamp TEXT,
        status TEXT,
        error TEXT,
        personalized_subject TEXT,
        personalized_body TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT
    )""")
    
    # Clear existing test data
    c.execute("DELETE FROM email_history WHERE subject LIKE 'Test%'")
    c.execute("DELETE FROM email_campaign_history WHERE campaign_id IN (SELECT id FROM email_campaigns WHERE name LIKE 'Test%')")
    c.execute("DELETE FROM email_campaigns WHERE name LIKE 'Test%'")
    c.execute("DELETE FROM contacts WHERE name LIKE 'Test%'")
    
    # Insert test contacts
    c.execute("INSERT INTO contacts (name, email) VALUES ('Test User 1', 'test1@example.com')")
    c.execute("INSERT INTO contacts (name, email) VALUES ('Test User 2', 'test2@example.com')")
    contact1_id = c.lastrowid - 1
    contact2_id = c.lastrowid
    
    # Insert test campaign
    c.execute("INSERT INTO email_campaigns (name, subject, body) VALUES (?, ?, ?)",
              ("Test Campaign", "Test Campaign Subject", "Test campaign body content"))
    campaign_id = c.lastrowid
    
    # Generate test data for different time periods
    now = datetime.now()
    
    # Today's data (various hours)
    for hour in [9, 12, 15, 18]:
        timestamp = now.replace(hour=hour, minute=30, second=0, microsecond=0)
        
        # Direct email
        c.execute("INSERT INTO email_history (timestamp, subject, body, email, status) VALUES (?, ?, ?, ?, ?)",
                  (timestamp.isoformat(), f"Test Direct Email {hour}:30", f"Direct email sent at {hour}:30", 
                   "test1@example.com", "Sent"))
        
        # Campaign email
        c.execute("INSERT INTO email_campaign_history (campaign_id, contact_id, timestamp, status, personalized_subject, personalized_body) VALUES (?, ?, ?, ?, ?, ?)",
                  (campaign_id, contact1_id, timestamp.isoformat(), "Sent", 
                   f"Test Campaign Subject for {timestamp.strftime('%H:%M')}", 
                   f"Personalized campaign content sent at {timestamp.strftime('%H:%M')}"))
    
    # Yesterday's data
    yesterday = now - timedelta(days=1)
    for hour in [10, 14, 16]:
        timestamp = yesterday.replace(hour=hour, minute=0, second=0, microsecond=0)
        c.execute("INSERT INTO email_history (timestamp, subject, body, email, status) VALUES (?, ?, ?, ?, ?)",
                  (timestamp.isoformat(), f"Test Yesterday Email {hour}:00", f"Email from yesterday at {hour}:00", 
                   "test2@example.com", "Sent"))
    
    # Last week's data
    week_ago = now - timedelta(days=7)
    timestamp = week_ago.replace(hour=11, minute=45, second=0, microsecond=0)
    c.execute("INSERT INTO email_history (timestamp, subject, body, email, status) VALUES (?, ?, ?, ?, ?)",
              (timestamp.isoformat(), "Test Week Ago Email", "Email from a week ago", "test1@example.com", "Sent"))
    
    # Last month's data
    month_ago = now - timedelta(days=30)
    timestamp = month_ago.replace(hour=13, minute=15, second=0, microsecond=0)
    c.execute("INSERT INTO email_campaign_history (campaign_id, contact_id, timestamp, status, personalized_subject, personalized_body) VALUES (?, ?, ?, ?, ?, ?)",
              (campaign_id, contact2_id, timestamp.isoformat(), "Sent", 
               "Test Month Ago Campaign", "Campaign email from a month ago"))
    
    conn.commit()
    conn.close()
    
    print("Test data inserted successfully!")
    print("Data includes:")
    print("- Today's emails at 9:30, 12:30, 15:30, 18:30")
    print("- Yesterday's emails at 10:00, 14:00, 16:00")
    print("- One email from a week ago at 11:45")
    print("- One campaign email from a month ago at 13:15")

def test_datetime_picker():
    """Test the datetime picker widget"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    from features.history import DateTimePicker
    
    def open_picker():
        picker = DateTimePicker(root, datetime.now(), "Test DateTime Picker")
        root.wait_window(picker)
        if picker.result:
            print(f"Selected datetime: {picker.result}")
            print(f"Formatted: {picker.result.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("No datetime selected")
        root.quit()
    
    root.after(100, open_picker)
    root.mainloop()

def main():
    """Main test function"""
    print("Testing Enhanced DateTime Filtering...")
    print("=" * 50)
    
    # Setup test data
    print("1. Setting up test data...")
    setup_test_data()
    
    # Test datetime picker
    print("\n2. Testing datetime picker...")
    print("A datetime picker window should open. Test the calendar and time selection.")
    test_datetime_picker()
    
    # Show history dialog
    print("\n3. Opening history dialog...")
    print("The history dialog should open with enhanced datetime filtering:")
    print("- DateTime input fields (YYYY-MM-DD HH:MM format)")
    print("- Calendar buttons (📅) for date/time selection")
    print("- Quick filter buttons: Today, 24hrs, 7 Days, 30 Days, All")
    print("- Default filter shows today's records only")
    
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    def show_dialog():
        show_history_dialog()
        root.quit()
    
    root.after(100, show_dialog)
    root.mainloop()
    
    print("\n4. Test scenarios to try:")
    print("- Default view should show today's 4 emails")
    print("- Click '24hrs' to see last 24 hours (should include yesterday's)")
    print("- Use calendar buttons to select specific date/time ranges")
    print("- Try manual datetime entry (format: YYYY-MM-DD HH:MM)")
    print("- Click 'All' to see all test records")
    print("- Switch between Email and SMS tabs")

if __name__ == "__main__":
    main()
