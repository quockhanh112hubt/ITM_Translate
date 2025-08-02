#!/usr/bin/env python3
"""
Quick test for replace mode detection
"""

import sys
import os

# Add the parent directory to sys.path to import ITM_Translate modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_replace_mode():
    """Quick test to verify replace mode is working"""
    try:
        from core.translator import translate_text
        
        print("🧪 Testing Replace Mode Detection")
        print("=" * 50)
        
        test_text = "Hello world"
        
        # Test 1: Popup mode (should show language detection)
        print("\n📋 TEST 1: Popup Mode (return_language_info=True)")
        try:
            result = translate_text(
                test_text,
                "Any Language",
                "Tiếng Việt", 
                "English",
                return_language_info=True
            )
            print(f"✅ Popup mode result type: {type(result)}")
            if isinstance(result, tuple):
                print(f"   📝 Translation: {result[0]}")
                print(f"   🌐 Languages: {result[1]} → {result[2]}")
        except Exception as e:
            print(f"❌ Popup mode failed: {e}")
        
        print("\n" + "-" * 50)
        
        # Test 2: Replace mode (should use smart prompt)
        print("\n📋 TEST 2: Replace Mode (return_language_info=False)")
        try:
            result = translate_text(
                test_text,
                "Any Language",
                "Tiếng Việt",
                "English", 
                return_language_info=False
            )
            print(f"✅ Replace mode result type: {type(result)}")
            print(f"   📝 Translation: {result}")
        except Exception as e:
            print(f"❌ Replace mode failed: {e}")
            
        print("\n" + "=" * 50)
        print("🏁 Test completed. Check the logs above for:")
        print("   • '🔄 [REPLACE MODE]' messages in Test 2")
        print("   • 'Detected source language:' only in Test 1")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")

if __name__ == "__main__":
    test_replace_mode()
