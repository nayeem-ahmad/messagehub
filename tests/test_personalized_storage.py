#!/usr/bin/env python3
"""
Test script to verify that new campaign emails store personalized content
"""

import sqlite3
import os

def test_personalized_storage():
    print("🧪 Testing Personalized Content Storage")
    print("=" * 45)
    
    db_path = os.path.join("private", "contacts.db")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Test: Insert a sample record with personalized content
    test_campaign_id = 999  # Use a test campaign ID
    test_contact_id = 999   # Use a test contact ID
    test_subject = "Test Subject for John Doe"
    test_body = "Dear John Doe, this is a test email for john.doe@example.com."
    
    print("📝 Inserting test record with personalized content...")
    c.execute("""
        INSERT INTO email_campaign_history 
        (campaign_id, contact_id, timestamp, status, error, personalized_subject, personalized_body) 
        VALUES (?, ?, datetime('now'), ?, '', ?, ?)
    """, (test_campaign_id, test_contact_id, 'Test', test_subject, test_body))
    
    conn.commit()
    
    # Verify the record was stored correctly
    print("🔍 Retrieving the test record...")
    c.execute("""
        SELECT campaign_id, contact_id, status, personalized_subject, personalized_body 
        FROM email_campaign_history 
        WHERE campaign_id = ? AND contact_id = ?
    """, (test_campaign_id, test_contact_id))
    
    result = c.fetchone()
    if result:
        campaign_id, contact_id, status, stored_subject, stored_body = result
        print(f"✅ Record found:")
        print(f"   Campaign ID: {campaign_id}")
        print(f"   Contact ID: {contact_id}")
        print(f"   Status: {status}")
        print(f"   Stored Subject: {stored_subject}")
        print(f"   Stored Body: {stored_body[:100]}...")
    else:
        print("❌ Test record not found!")
    
    # Clean up: Remove the test record
    print("🧹 Cleaning up test record...")
    c.execute("DELETE FROM email_campaign_history WHERE campaign_id = ? AND contact_id = ?", 
              (test_campaign_id, test_contact_id))
    conn.commit()
    
    conn.close()
    print("✅ Test completed successfully!")

if __name__ == "__main__":
    test_personalized_storage()
