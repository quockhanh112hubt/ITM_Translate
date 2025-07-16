#!/usr/bin/env python3
"""
Test script for API Key Manager
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from core.api_key_manager import APIKeyManager

def test_api_key_manager():
    print("=== Testing API Key Manager ===")
    
    # Initialize manager
    manager = APIKeyManager("test_api_keys.json")
    
    # Test 1: Add keys
    print("\n1. Testing add_key():")
    test_keys = [
        "AIzaSyTest1234567890abcdef1234567890abcd",
        "AIzaSyTest2345678901bcdef12345678901bcde", 
        "AIzaSyTest3456789012cdef123456789012cdef"
    ]
    
    for key in test_keys:
        result = manager.add_key(key)
        print(f"  Added '{key[:10]}...': {result}")
    
    # Test 2: Display all keys
    print(f"\n2. Total keys: {manager.get_key_count()}")
    all_keys = manager.get_all_keys()
    for i, key in enumerate(all_keys):
        active = " (ACTIVE)" if i == manager.active_index else ""
        print(f"  {i+1}. {key[:10]}...{active}")
    
    # Test 3: Get active key
    active_key = manager.get_active_key()
    print(f"\n3. Active key: {active_key[:10] if active_key else 'None'}...")
    
    # Test 4: Rotate keys
    print(f"\n4. Testing key rotation:")
    for i in range(len(test_keys) + 1):
        current = manager.get_active_key()
        next_key = manager.rotate_to_next_key()
        print(f"  Rotation {i+1}: {current[:10] if current else 'None'}... → {next_key[:10] if next_key else 'None'}...")
    
    # Test 5: Set specific active key
    print(f"\n5. Setting key 2 as active:")
    success = manager.set_active_index(1)
    active_key = manager.get_active_key()
    print(f"  Success: {success}, Active: {active_key[:10] if active_key else 'None'}...")
    
    # Test 6: Remove key
    print(f"\n6. Removing key 2:")
    success = manager.remove_key(1)
    print(f"  Success: {success}, Remaining keys: {manager.get_key_count()}")
    
    active_key = manager.get_active_key()
    print(f"  New active: {active_key[:10] if active_key else 'None'}...")
    
    # Clean up test file
    if os.path.exists("test_api_keys.json"):
        os.remove("test_api_keys.json")
        print(f"\n✅ Test file cleaned up")
    
    print("\n=== API Key Manager Test Complete ===")

if __name__ == "__main__":
    test_api_key_manager()
