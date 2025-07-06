#!/usr/bin/env python3
"""
SMTP Connection Test Script
Diagnoses SMTP connection issues with detailed logging
"""

import sys
import os
import smtplib
from email.mime.text import MIMEText

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from features.common import get_settings
from services import email_utils

def test_smtp_connection():
    """Test SMTP connection with the current settings"""
    print("🧪 SMTP Connection Test")
    print("=" * 40)
    
    # Load settings
    settings = get_settings()
    
    # Extract SMTP settings
    smtp_server = settings.get('smtp_server', '')
    smtp_port = settings.get('smtp_port', '587')
    sender_email = settings.get('sender_email', '')
    sender_pwd = settings.get('sender_pwd', '')
    sender_name = settings.get('sender_name', '')
    
    print(f"📋 Configuration:")
    print(f"   SMTP Server: {smtp_server}")
    print(f"   SMTP Port: {smtp_port}")
    print(f"   Sender Email: {sender_email}")
    print(f"   Sender Name: {sender_name}")
    print(f"   Password: {'*' * len(sender_pwd) if sender_pwd else 'Not set'}")
    
    if not smtp_server or not smtp_port or not sender_email or not sender_pwd:
        print("\n❌ Missing required SMTP settings!")
        return False
    
    print(f"\n🔗 Testing SMTP Connection...")
    
    # Test 1: Basic SMTP object creation
    print(f"\n1️⃣ Testing SMTP object creation...")
    try:
        server = smtplib.SMTP(smtp_server, int(smtp_port))
        print(f"   ✅ SMTP object created: {type(server)}")
        print(f"   📊 Available methods: {[m for m in dir(server) if not m.startswith('_')]}")
        
        # Check for settimeout method
        if hasattr(server, 'settimeout'):
            print("   ✅ settimeout method available")
            server.settimeout(30)
            print("   ✅ Timeout set successfully")
        else:
            print("   ❌ settimeout method NOT available")
            print(f"   📝 Object type: {type(server)}")
            print(f"   📝 Module: {server.__class__.__module__}")
        
        server.quit()
        
    except Exception as e:
        print(f"   ❌ Failed to create SMTP object: {e}")
        return False
    
    # Test 2: Full connection test
    print(f"\n2️⃣ Testing full SMTP connection...")
    try:
        email_utils.send_email_smtp_simple(
            smtp_server,
            smtp_port,
            sender_email,
            sender_pwd,
            sender_email,  # Send to self for testing
            "SMTP Test Email",
            "This is a test email to verify SMTP connectivity.",
            sender_name
        )
        print("   ✅ SMTP connection test successful!")
        return True
        
    except Exception as e:
        print(f"   ❌ SMTP connection test failed: {e}")
        return False

def test_email_utils_functions():
    """Test the email utility functions"""
    print(f"\n🔧 Testing Email Utility Functions...")
    
    # Load settings
    settings = get_settings()
    
    # Test the original function
    print(f"\n3️⃣ Testing send_email_smtp function...")
    try:
        smtp_settings = {
            "server": settings.get('smtp_server'),
            "port": int(settings.get('smtp_port', 587))
        }
        email_utils.send_email_smtp(
            smtp_settings,
            settings.get('sender_email'),
            settings.get('sender_pwd'),
            settings.get('sender_email'),
            "Original Function Test",
            "Testing the original send_email_smtp function.",
            settings.get('sender_name', '')
        )
        print("   ✅ Original send_email_smtp function works!")
        
    except Exception as e:
        print(f"   ❌ Original send_email_smtp function failed: {e}")
    
    # Test the connection check function
    print(f"\n4️⃣ Testing send_email_with_connection_check function...")
    try:
        smtp_settings = {"server": settings.get('smtp_server'), "port": int(settings.get('smtp_port', 587))}
        email_utils.send_email_with_connection_check(
            'smtp',
            smtp_settings,
            settings.get('sender_email'),
            settings.get('sender_pwd'),
            settings.get('sender_email'),
            "Connection Check Test",
            "Testing the send_email_with_connection_check function.",
            settings.get('sender_name', '')
        )
        print("   ✅ send_email_with_connection_check function works!")
        
    except Exception as e:
        print(f"   ❌ send_email_with_connection_check function failed: {e}")

def main():
    """Main test function"""
    print("🔍 MessageHub SMTP Diagnostics")
    print("=" * 50)
    
    # Test basic SMTP connection
    success = test_smtp_connection()
    
    if success:
        print(f"\n🎉 Basic SMTP test passed! Testing utility functions...")
        test_email_utils_functions()
    else:
        print(f"\n💡 Troubleshooting Tips:")
        print(f"   • Check SMTP server address and port")
        print(f"   • Verify username and password")
        print(f"   • Check firewall and network settings")
        print(f"   • Try enabling 'Less secure apps' (Gmail)")
        print(f"   • Use app-specific passwords (Gmail, Outlook)")
    
    print(f"\n🏁 SMTP Diagnostics Complete")

if __name__ == "__main__":
    main()
