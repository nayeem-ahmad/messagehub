#!/usr/bin/env python3
"""
Test script for network resilience features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import email_utils

def test_connection_check():
    """Test the internet connection check"""
    print("Testing internet connection check...")
    if email_utils.check_internet_connection():
        print("✅ Internet connection is available")
        return True
    else:
        print("❌ No internet connection detected")
        return False

def test_retry_mechanism():
    """Test the retry mechanism with a failing function"""
    print("\nTesting retry mechanism...")
    
    attempt_count = [0]
    
    def failing_function():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise Exception(f"Simulated failure #{attempt_count[0]}")
        return "Success!"
    
    try:
        result = email_utils.retry_with_backoff(failing_function, max_retries=3)
        print(f"✅ Retry mechanism worked: {result}")
        print(f"   Total attempts: {attempt_count[0]}")
        return True
    except Exception as e:
        print(f"❌ Retry mechanism failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Network Resilience Features\n")
    
    tests = [
        ("Connection Check", test_connection_check),
        ("Retry Mechanism", test_retry_mechanism),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 Test Results Summary:")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Network resilience features are working.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
