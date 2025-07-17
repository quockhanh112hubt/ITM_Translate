#!/usr/bin/env python3
"""
Test Failover Mechanism - Test cơ chế failover khi gặp lỗi API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.translator import translate_text
from core.api_key_manager import api_key_manager

def test_translation_with_failover():
    """Test translation với DeepSeek bị lỗi, xem có chuyển sang Gemini không"""
    
    print("🧪 Testing Translation Failover Mechanism")
    print("=" * 50)
    
    # Show current API keys status
    all_keys = api_key_manager.get_all_keys()
    print(f"📋 Available API Keys: {len(all_keys)}")
    for i, key in enumerate(all_keys):
        status = "❌ Failed" if not key.is_active or key.failed_count >= 3 else "✅ Working"
        if key.failed_count > 0:
            status += f" (failed: {key.failed_count})"
        print(f"   {i+1}. {key.name} ({key.provider.value}) - {status}")
    
    print(f"\n🎯 Current Active: {api_key_manager.get_provider_info()['name']}")
    
    # Test translations
    test_cases = [
        ("Hello world", "Any Language", "Tiếng Việt", "English"),
        ("Xin chào thế giới", "Any Language", "Tiếng Việt", "English"),
        ("This is a test of the failover system", "Any Language", "Tiếng Việt", "English")
    ]
    
    for i, (text, lang1, lang2, lang3) in enumerate(test_cases, 1):
        print(f"\n🔄 Test {i}: '{text}'")
        print("-" * 40)
        
        try:
            result = translate_text(text, lang1, lang2, lang3)
            print(f"✅ Result: {result}")
            
            # Show which provider was used
            provider_info = api_key_manager.get_provider_info()
            print(f"🎯 Used: {provider_info['name']} ({provider_info['provider']})")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Show final status
    print(f"\n📊 Final Status:")
    print(f"   Active: {api_key_manager.get_provider_info()['name']}")
    
    all_keys = api_key_manager.get_all_keys()
    failed_keys = [key for key in all_keys if not key.is_active or key.failed_count >= 3]
    working_count = len(all_keys) - len(failed_keys)
    print(f"   Working keys: {working_count}/{len(all_keys)}")
    
    if failed_keys:
        print(f"   Failed keys:")
        for key_info in failed_keys:
            print(f"      • {key_info.name} ({key_info.provider.value}) - {key_info.last_error}")

if __name__ == "__main__":
    test_translation_with_failover()
