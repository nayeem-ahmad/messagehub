#!/usr/bin/env python3
"""
Test database access to identify locking issues
"""

import sqlite3
import time
import os
from features.common import DB_FILE

def test_database_access():
    """Test database access patterns"""
    print(f"Testing database access: {DB_FILE}")
    
    # Test 1: Quick connection
    print("\n1. Testing quick connection...")
    try:
        conn = sqlite3.connect(DB_FILE, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM email_campaigns")
        count = cursor.fetchone()[0]
        print(f"   ✅ Quick access: Found {count} email campaigns")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Quick access failed: {e}")
    
    # Test 2: Long connection
    print("\n2. Testing with held connection...")
    try:
        conn1 = sqlite3.connect(DB_FILE, timeout=5.0)
        conn1.execute("PRAGMA journal_mode=WAL")
        conn1.execute("PRAGMA busy_timeout=5000")
        
        # Try to update from another connection
        conn2 = sqlite3.connect(DB_FILE, timeout=5.0)
        conn2.execute("PRAGMA journal_mode=WAL")
        conn2.execute("PRAGMA busy_timeout=5000")
        
        # Start a transaction on conn1
        cursor1 = conn1.cursor()
        cursor1.execute("BEGIN IMMEDIATE")
        
        print("   📝 Started transaction on connection 1")
        
        # Try to write from conn2
        cursor2 = conn2.cursor()
        cursor2.execute("UPDATE email_campaigns SET last_updated = ? WHERE id = 8", (time.time(),))
        conn2.commit()
        
        print("   ✅ Update from connection 2 succeeded")
        
        # Cleanup
        conn1.rollback()
        conn1.close()
        conn2.close()
        
    except Exception as e:
        print(f"   ❌ Concurrent access test failed: {e}")
        try:
            conn1.close()
            conn2.close()
        except:
            pass
    
    # Test 3: Check for WAL files
    print("\n3. Checking database files...")
    db_dir = os.path.dirname(DB_FILE)
    db_name = os.path.basename(DB_FILE)
    
    for file in os.listdir(db_dir):
        if file.startswith(db_name):
            file_path = os.path.join(db_dir, file)
            size = os.path.getsize(file_path)
            print(f"   📁 {file}: {size} bytes")

if __name__ == "__main__":
    test_database_access()
