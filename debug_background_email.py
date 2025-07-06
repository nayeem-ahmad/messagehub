#!/usr/bin/env python3
"""
Debug script for background email campaign issues
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from features.common import DB_FILE, get_settings
from services import email_utils
from campaign_processor import CampaignProcessor

def test_email_sending():
    """Test email sending directly"""
    print("🧪 Testing Email Sending Functions")
    print("=" * 50)
    
    settings = get_settings()
    recipient = settings.get('sender_email')  # Send to self for testing
    
    print(f"📧 Testing email to: {recipient}")
    
    # Test 1: Direct SMTP simple function
    print(f"\n1️⃣ Testing send_email_smtp_simple directly:")
    try:
        result = email_utils.send_email_smtp_simple(
            settings.get('smtp_server'),
            settings.get('smtp_port', 587),
            settings.get('sender_email'),
            settings.get('sender_pwd'),
            recipient,
            "Direct Test",
            "Testing send_email_smtp_simple function directly",
            settings.get('sender_name', '')
        )
        print(f"   ✅ Direct function test: SUCCESS")
    except Exception as e:
        print(f"   ❌ Direct function test: FAILED - {e}")
    
    # Test 2: Campaign processor email sending method
    print(f"\n2️⃣ Testing campaign processor _send_email method:")
    try:
        processor = CampaignProcessor(999, 'email')  # Use dummy campaign ID
        result = processor._send_email(
            settings,
            "SMTP",
            recipient,
            "Processor Test", 
            "Testing campaign processor _send_email method"
        )
        print(f"   ✅ Processor method test: SUCCESS")
    except Exception as e:
        print(f"   ❌ Processor method test: FAILED - {e}")
        import traceback
        traceback.print_exc()

def check_campaign_8():
    """Check the specific campaign 8 that failed"""
    print(f"\n📋 Checking Campaign 8 Details")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get campaign details
    cursor.execute("SELECT * FROM email_campaigns WHERE id = 8")
    campaign = cursor.fetchone()
    
    if campaign:
        print(f"📧 Campaign 8 found:")
        columns = [description[0] for description in cursor.description]
        for i, value in enumerate(campaign):
            print(f"   {columns[i]}: {value}")
    else:
        print(f"❌ Campaign 8 not found")
        return
    
    # Get campaign contacts
    cursor.execute("""
        SELECT c.id, c.name, c.email, c.mobile 
        FROM contacts c
        JOIN email_campaign_contacts ecc ON c.id = ecc.contact_id
        WHERE ecc.campaign_id = 8
    """)
    
    contacts = cursor.fetchall()
    print(f"\n👥 Campaign 8 contacts ({len(contacts)}):")
    for contact_id, name, email, mobile in contacts:
        print(f"   {contact_id}: {name} ({email})")
    
    # Get campaign history
    cursor.execute("""
        SELECT timestamp, status, error
        FROM email_campaign_history
        WHERE campaign_id = 8
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    
    history = cursor.fetchall()
    print(f"\n📜 Recent campaign 8 history:")
    for timestamp, status, error in history:
        print(f"   {timestamp}: {status} - {error}")
    
    conn.close()

def test_campaign_processor_import():
    """Test if campaign processor can import all needed modules"""
    print(f"\n🔍 Testing Campaign Processor Imports")
    print("=" * 50)
    
    try:
        import campaign_processor
        print(f"✅ campaign_processor imported successfully")
        
        from services import email_utils
        print(f"✅ email_utils imported successfully")
        
        # Check specific function
        func = getattr(email_utils, 'send_email_smtp_simple', None)
        if func:
            print(f"✅ send_email_smtp_simple function found")
        else:
            print(f"❌ send_email_smtp_simple function NOT found")
            
        # List all available functions
        functions = [attr for attr in dir(email_utils) if callable(getattr(email_utils, attr)) and not attr.startswith('_')]
        print(f"📋 Available email_utils functions: {functions}")
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()

def test_full_campaign_processing():
    """Test running a complete campaign process with the fixed code"""
    print(f"\n🚀 Testing Full Campaign Processing")
    print("=" * 50)
    
    try:
        # Test campaign 8 with the fixed processor
        print(f"Testing campaign 8 with fixed processor...")
        processor = CampaignProcessor(8, 'email')
        
        # Update campaign status to draft so it can be processed again
        import sqlite3
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE email_campaigns SET status = 'draft' WHERE id = 8")
        conn.commit()
        conn.close()
        
        print(f"Reset campaign 8 status to 'draft'")
        
        # Run the campaign
        print(f"Running campaign 8...")
        result = processor.process_email_campaign()
        
        if result:
            print(f"   ✅ Campaign 8 completed successfully!")
        else:
            print(f"   ❌ Campaign 8 failed")
            
        # Check final status
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT status, processing_details FROM email_campaigns WHERE id = 8")
        status_result = cursor.fetchone()
        if status_result:
            status, details = status_result
            print(f"   Final status: {status}")
            print(f"   Details: {details}")
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Full campaign test failed: {e}")
        import traceback
        traceback.print_exc()

def test_background_job_manager():
    """Test the background job manager with campaign 8"""
    print(f"\n🖥️ Testing Background Job Manager")
    print("=" * 50)
    
    try:
        from services.background_jobs import get_job_manager
        job_manager = get_job_manager()
        
        # Try to start campaign 8 in background
        print(f"Starting campaign 8 in background...")
        success = job_manager.start_campaign_background(8, 'email')
        
        if success:
            print(f"   ✅ Campaign 8 started in background")
            
            # Wait a moment and check status
            import time
            time.sleep(3)
            
            status = job_manager.get_campaign_status(8, 'email')
            print(f"   Status after 3 seconds:")
            print(f"     Campaign status: {status.get('campaign_status')}")
            print(f"     Is running: {status.get('is_running')}")
            print(f"     Details: {status.get('processing_details', 'None')}")
            
        else:
            print(f"   ❌ Failed to start campaign 8 in background")
            
    except Exception as e:
        print(f"   ❌ Background job manager test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("🔧 Background Email Campaign Debug")
    print("=" * 60)
    
    # Test imports first
    test_campaign_processor_import()
    
    # Test email sending
    test_email_sending()
    
    # Check the specific campaign that failed
    check_campaign_8()
    
    # Test full campaign processing
    test_full_campaign_processing()
    
    # Test background job manager
    test_background_job_manager()
    
    print(f"\n🏁 Debug Complete")

if __name__ == "__main__":
    main()
