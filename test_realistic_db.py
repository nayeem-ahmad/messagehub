#!/usr/bin/env python3
"""
Test realistic campaign processing database usage
"""

import sqlite3
import time
import threading
from features.common import DB_FILE

def update_campaign_status_simple(campaign_id, status, details):
    """Simple campaign status update like the processor does"""
    try:
        conn = sqlite3.connect(DB_FILE, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        
        cursor = conn.cursor()
        timestamp = time.time()
        
        cursor.execute("""
            UPDATE email_campaigns 
            SET status = ?, last_updated = ?, processing_details = ?
            WHERE id = ?
        """, (status, str(timestamp), details, campaign_id))
        
        conn.commit()
        conn.close()
        print(f"✅ Updated campaign {campaign_id} to {status}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update campaign {campaign_id}: {e}")
        return False

def concurrent_update_test():
    """Test concurrent updates like what might happen in background processing"""
    print("Testing concurrent campaign status updates...")
    
    def worker(worker_id):
        for i in range(3):
            success = update_campaign_status_simple(8, f"test_{worker_id}_{i}", f"Worker {worker_id} iteration {i}")
            time.sleep(0.1)
    
    # Start multiple threads updating the same campaign
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("Concurrent update test completed")

def simple_update_test():
    """Test simple sequential updates"""
    print("Testing simple sequential updates...")
    
    for i in range(5):
        success = update_campaign_status_simple(8, f"sequential_{i}", f"Sequential update {i}")
        if not success:
            print(f"Failed at iteration {i}")
            break
        time.sleep(0.1)
    
    print("Sequential update test completed")

if __name__ == "__main__":
    print("🔧 Testing Realistic Database Usage")
    print("=" * 50)
    
    # Test 1: Simple updates
    simple_update_test()
    
    print()
    
    # Test 2: Concurrent updates
    concurrent_update_test()
    
    print()
    print("🏁 Test completed")
