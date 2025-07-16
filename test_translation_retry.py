#!/usr/bin/env python3
"""
Test script for Translation with Retry Mechanism
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from core.translator import translate_text, api_key_manager

def test_translation_retry():
    print("=== Testing Translation with Retry Mechanism ===")
    
    # Check current keys
    print(f"\n1. Current API keys: {api_key_manager.get_key_count()}")
    active_key = api_key_manager.get_active_key()
    if active_key:
        print(f"   Active key: {active_key[:10]}...")
    else:
        print("   No active key found")
        return
    
    # Test translation
    test_text = "Hello, how are you today?"
    print(f"\n2. Testing translation:")
    print(f"   Input: {test_text}")
    
    try:
        # Test with language info
        result, source_lang, target_lang = translate_text(
            test_text,
            "Any Language",
            "Tiếng Việt", 
            "English",
            return_language_info=True
        )
        
        print(f"   Output: {result}")
        print(f"   Source: {source_lang}")
        print(f"   Target: {target_lang}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Translation Test Complete ===")

def test_with_invalid_keys():
    print("\n=== Testing with Invalid Keys ===")
    
    # Add some invalid keys for testing
    invalid_keys = [
        "invalid_key_1",
        "invalid_key_2", 
        "invalid_key_3"
    ]
    
    original_keys = api_key_manager.get_all_keys().copy()
    original_active = api_key_manager.active_index
    
    # Clear and add invalid keys
    for i in range(len(original_keys)):
        api_key_manager.remove_key(0)
    
    for key in invalid_keys:
        api_key_manager.add_key(key)
    
    print(f"Added {len(invalid_keys)} invalid keys for testing")
    
    # Test translation with invalid keys
    test_text = "Test with invalid keys"
    print(f"Testing translation with: {test_text}")
    
    try:
        result = translate_text(test_text, "English", "Tiếng Việt", "한국어")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Restore original keys
    for i in range(len(invalid_keys)):
        api_key_manager.remove_key(0)
    
    for key in original_keys:
        api_key_manager.add_key(key)
    
    api_key_manager.set_active_index(original_active)
    print("Restored original keys")

if __name__ == "__main__":
    test_translation_retry()
    test_with_invalid_keys()
