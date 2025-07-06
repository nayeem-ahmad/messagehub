#!/usr/bin/env python3
"""
Fix database to use WAL mode for better concurrency
"""

import sqlite3
import os
from features.common import DB_FILE

def setup_wal_mode():
    """Enable WAL mode and set up proper database configuration"""
    print(f"Setting up WAL mode for database: {DB_FILE}")
    
    try:
        # Connect and enable WAL mode
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        
        # Set busy timeout
        conn.execute("PRAGMA busy_timeout=30000")
        
        # Set synchronous mode for better performance with WAL
        conn.execute("PRAGMA synchronous=NORMAL")
        
        # Check the settings
        result = conn.execute("PRAGMA journal_mode").fetchone()
        print(f"Journal mode: {result[0]}")
        
        result = conn.execute("PRAGMA busy_timeout").fetchone()
        print(f"Busy timeout: {result[0]}ms")
        
        result = conn.execute("PRAGMA synchronous").fetchone()
        print(f"Synchronous mode: {result[0]}")
        
        conn.commit()
        conn.close()
        
        print("✅ Database configuration updated successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

if __name__ == "__main__":
    setup_wal_mode()
