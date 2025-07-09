#!/usr/bin/env python3
"""
Debug Background Email Campaign with Detailed Logging
This script will run a background email campaign and show all logs in real-time
"""

import sys
import os
import sqlite3
import time
import subprocess
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from features.common import DB_FILE, get_settings
from services.background_jobs import BackgroundJobManager

def check_campaign_settings():
    """Check if email settings are properly configured"""
    print("🔧 Checking Email Configuration")
    print("=" * 50)
    
    settings = get_settings()
    email_method = settings.get('email_method', 'SMTP')
    
    print(f"📧 Email Method: {email_method}")
    
    if email_method == "SMTP":
        print(f"🔧 SMTP Server: {settings.get('smtp_server', 'Not set')}")
        print(f"🔧 SMTP Port: {settings.get('smtp_port', 'Not set')}")
        print(f"🔧 Sender Email: {settings.get('sender_email', 'Not set')}")
        print(f"🔧 Sender Name: {settings.get('sender_name', 'Not set')}")
        print(f"🔧 Password: {'✅ Set' if settings.get('sender_pwd') else '❌ Not set'}")
        
        required = ['sender_email', 'sender_pwd', 'smtp_server', 'smtp_port']
        missing = [key for key in required if not settings.get(key)]
        
        if missing:
            print(f"❌ Missing required settings: {missing}")
            return False
        else:
            print(f"✅ All SMTP settings configured")
            return True
    
    return True

def get_test_campaign():
    """Get or create a test campaign"""
    print("\n📋 Setting up Test Campaign")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check for existing test campaign
    cursor.execute("SELECT id, name, subject, body FROM email_campaigns WHERE name LIKE '%Debug%' ORDER BY id DESC LIMIT 1")
    campaign = cursor.fetchone()
    
    if campaign:
        campaign_id, name, subject, body = campaign
        print(f"📧 Found existing campaign: {campaign_id} - {name}")
    else:
        # Create a simple test campaign
        print("📝 Creating new debug test campaign...")
        cursor.execute("""
            INSERT INTO email_campaigns (name, subject, body, status)
            VALUES (?, ?, ?, ?)
        """, (
            "Debug Email Test", 
            "Debug Test Email", 
            "Hello {{name}},\n\nThis is a debug test email from MessageHub.\n\nBest regards,\nMessageHub Team",
            "draft"
        ))
        
        campaign_id = cursor.lastrowid
        print(f"✅ Created campaign {campaign_id}")
        
        # Add a test contact if none exist
        cursor.execute("SELECT id, name, email FROM contacts WHERE email IS NOT NULL LIMIT 1")
        contact = cursor.fetchone()
        
        if contact:
            contact_id, contact_name, contact_email = contact
            print(f"👤 Found contact: {contact_name} ({contact_email})")
            
            # Link campaign to contact
            cursor.execute("""
                INSERT OR IGNORE INTO email_campaign_contacts (campaign_id, contact_id)
                VALUES (?, ?)
            """, (campaign_id, contact_id))
            
        else:
            print("❌ No contacts found in database!")
            conn.close()
            return None
    
    # Reset campaign status to draft
    cursor.execute("UPDATE email_campaigns SET status = 'draft' WHERE id = ?", (campaign_id,))
    
    # Check campaign contacts
    cursor.execute("""
        SELECT c.id, c.name, c.email 
        FROM contacts c
        JOIN email_campaign_contacts ecc ON c.id = ecc.contact_id
        WHERE ecc.campaign_id = ? AND c.email IS NOT NULL
    """, (campaign_id,))
    
    contacts = cursor.fetchall()
    print(f"👥 Campaign has {len(contacts)} contacts:")
    for contact_id, name, email in contacts:
        print(f"   - {name} ({email})")
    
    conn.commit()
    conn.close()
    
    return campaign_id

def run_background_campaign_with_logging(campaign_id):
    """Run background campaign and monitor logs"""
    print(f"\n🚀 Starting Background Campaign {campaign_id}")
    print("=" * 50)
    
    # Start the campaign
    manager = BackgroundJobManager()
    success = manager.start_campaign_background(campaign_id, 'email')
    
    if not success:
        print("❌ Failed to start background campaign")
        return False
    
    print(f"✅ Background campaign {campaign_id} started")
    
    # Monitor the campaign
    print("\n📊 Monitoring Campaign Progress...")
    print("-" * 50)
    
    max_wait_time = 120  # 2 minutes max
    check_interval = 2   # Check every 2 seconds
    checks = 0
    
    while checks < (max_wait_time // check_interval):
        time.sleep(check_interval)
        checks += 1
        
        # Get campaign status
        status_info = manager.get_campaign_status(campaign_id, 'email')
        campaign_status = status_info.get('campaign_status', 'unknown')
        is_running = status_info.get('is_running', False)
        details = status_info.get('processing_details', '')
        
        elapsed_time = checks * check_interval
        print(f"⏱️  {elapsed_time:3d}s | Status: {campaign_status:10s} | Running: {is_running} | {details}")
        
        # Check if campaign is finished
        if campaign_status in ['completed', 'failed', 'stopped'] and not is_running:
            print(f"\n🏁 Campaign finished with status: {campaign_status}")
            break
    
    return True

def show_campaign_logs(campaign_id):
    """Show recent campaign logs"""
    print(f"\n📜 Campaign {campaign_id} Logs")
    print("=" * 50)
    
    # Check for log files
    logs_dir = os.path.join(project_root, 'logs')
    if os.path.exists(logs_dir):
        log_files = [f for f in os.listdir(logs_dir) if f.startswith(f'email_campaign_{campaign_id}')]
        
        if log_files:
            # Get the most recent log file
            latest_log = max(log_files, key=lambda f: os.path.getmtime(os.path.join(logs_dir, f)))
            log_path = os.path.join(logs_dir, latest_log)
            
            print(f"📄 Reading log file: {latest_log}")
            print("-" * 50)
            
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    logs = f.read()
                    print(logs)
            except Exception as e:
                print(f"❌ Error reading log file: {e}")
        else:
            print("⚠️  No log files found for this campaign")
    else:
        print("⚠️  Logs directory not found")

def show_campaign_history(campaign_id):
    """Show campaign history from database"""
    print(f"\n📚 Campaign {campaign_id} History")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get campaign history
    cursor.execute("""
        SELECT h.timestamp, h.status, h.error, c.name, c.email
        FROM email_campaign_history h
        LEFT JOIN contacts c ON h.contact_id = c.id
        WHERE h.campaign_id = ?
        ORDER BY h.timestamp DESC
        LIMIT 20
    """, (campaign_id,))
    
    history = cursor.fetchall()
    
    if history:
        print(f"📋 Recent {len(history)} entries:")
        for timestamp, status, error, name, email in history:
            if name and email:
                print(f"   {timestamp} | {status:8s} | {name} ({email}) | {error or ''}")
            else:
                print(f"   {timestamp} | {status:8s} | {error or ''}")
    else:
        print("⚠️  No history entries found")
    
    conn.close()

def main():
    """Main debug function"""
    print("🔍 Background Email Campaign Debug with Detailed Logging")
    print("=" * 70)
    
    # Step 1: Check email configuration
    if not check_campaign_settings():
        print("\n❌ Email configuration issues detected. Please fix settings first.")
        return
    
    # Step 2: Get test campaign
    campaign_id = get_test_campaign()
    if not campaign_id:
        print("\n❌ Could not set up test campaign")
        return
    
    # Step 3: Run background campaign with monitoring
    success = run_background_campaign_with_logging(campaign_id)
    
    # Step 4: Show detailed logs
    show_campaign_logs(campaign_id)
    
    # Step 5: Show database history
    show_campaign_history(campaign_id)
    
    print("\n🏁 Debug Complete")
    print("Check the logs above for detailed information about any failures.")

if __name__ == "__main__":
    main()
