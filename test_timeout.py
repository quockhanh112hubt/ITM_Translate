#!/usr/bin/env python3
"""
Test script for timeout mechanism in ITM Translate
"""
import time
import threading
from core.translator import translate_text

def test_timeout_mechanism():
    """Test the timeout mechanism with various scenarios"""
    
    print("🧪 Testing ITM Translate Timeout Mechanism")
    print("=" * 50)
    
    # Test 1: Normal translation (should complete quickly)
    print("\n📋 Test 1: Normal translation")
    start_time = time.time()
    try:
        result = translate_text(
            "Hello world", 
            "Any Language", 
            "Tiếng Việt", 
            "English",
            return_language_info=False,
            timeout_seconds=5
        )
        elapsed = time.time() - start_time
        print(f"✅ Success in {elapsed:.2f}s: {result}")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Failed in {elapsed:.2f}s: {e}")
    
    # Test 2: Short timeout (should timeout)
    print("\n📋 Test 2: Short timeout (1 second)")
    start_time = time.time()
    try:
        result = translate_text(
            "This is a longer text that might take more time to translate by the AI model. Let's see if the timeout mechanism works correctly when we set a very short timeout period.",
            "Any Language", 
            "Tiếng Việt", 
            "English",
            return_language_info=False,
            timeout_seconds=1  # Very short timeout
        )
        elapsed = time.time() - start_time
        print(f"✅ Unexpected success in {elapsed:.2f}s: {result}")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"⏰ Expected timeout in {elapsed:.2f}s: {e}")
    
    # Test 3: Medium timeout (should work)
    print("\n📋 Test 3: Medium timeout (8 seconds)")
    start_time = time.time()
    try:
        result = translate_text(
            "Testing medium timeout with reasonable text length.",
            "Any Language", 
            "Tiếng Việt", 
            "English",
            return_language_info=True,
            timeout_seconds=8
        )
        elapsed = time.time() - start_time
        print(f"✅ Success in {elapsed:.2f}s")
        if isinstance(result, tuple) and len(result) == 3:
            translated, source, target = result
            print(f"   📝 Result: {translated}")
            print(f"   🔄 Direction: {source} → {target}")
        else:
            print(f"   📝 Result: {result}")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Failed in {elapsed:.2f}s: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Timeout mechanism test completed!")

if __name__ == "__main__":
    test_timeout_mechanism()
