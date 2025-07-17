#!/usr/bin/env python3
"""
Demo Multi-Provider AI Translation System
Hiển thị tính năng mới: Multiple AI Providers với Auto Failover
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.api_key_manager import APIKeyManager, AIProvider
from core.translator import translate_text, detect_language

def demo_multi_provider():
    """Demo hệ thống multi-provider với failover"""
    print("🌟 ITM Translate v1.1.3 - Multi-Provider AI Demo")
    print("=" * 60)
    
    # Initialize API key manager
    api_manager = APIKeyManager()
    
    print("📊 Current Configuration:")
    print(f"   Total API Keys: {api_manager.get_key_count()}")
    
    if api_manager.get_key_count() == 0:
        print("⚠️  No API keys found. Adding demo configuration...")
        
        # Demo: Add sample keys (replace with real keys for testing)
        demo_keys = [
            ("YOUR_GEMINI_KEY_HERE", AIProvider.GEMINI, "gemini-2.0-flash-exp", "Primary Gemini"),
            ("YOUR_CHATGPT_KEY_HERE", AIProvider.CHATGPT, "gpt-3.5-turbo", "Backup ChatGPT"),
            ("YOUR_DEEPSEEK_KEY_HERE", AIProvider.DEEPSEEK, "deepseek-chat", "Alternative DeepSeek"),
        ]
        
        for key, provider, model, name in demo_keys:
            if key != f"YOUR_{provider.value.upper()}_KEY_HERE":
                api_manager.add_key(key, provider, model, name)
                print(f"   ✅ Added {provider.value.title()} key: {name}")
    
    # Display current keys
    all_keys = api_manager.get_all_keys()
    print(f"\n🔑 API Keys ({len(all_keys)} total):")
    for i, key_info in enumerate(all_keys):
        status = "🎯 ACTIVE" if i == api_manager.active_index else "⚪"
        health = "❌ FAILED" if key_info.failed_count > 0 else "✅ OK"
        print(f"   {status} {key_info.provider.value.title()} ({key_info.model}) - {health}")
        if key_info.failed_count > 0:
            print(f"      Last error: {key_info.last_error}")
    
    # Show provider priority
    print(f"\n🎯 Provider Priority Order:")
    for i, provider in enumerate(api_manager.provider_priority, 1):
        print(f"   {i}. {provider.value.title()}")
    
    # Demo translation with language detection
    test_texts = [
        "Hello world, this is a test",
        "Xin chào thế giới, đây là bài kiểm tra",
        "OK tôi sẽ check cái đó later",  # Mixed language
        "今天天気がいいですね。",  # Japanese
        "Bonjour le monde!"  # French
    ]
    
    print(f"\n🔄 Testing Translation & Language Detection:")
    print("-" * 50)
    
    for text in test_texts:
        print(f"\n📝 Input: {text}")
        
        # Detect language
        detected = detect_language(text)
        print(f"🔍 Detected Language: {detected}")
        
        # Get current provider info
        provider_info = api_manager.get_provider_info()
        print(f"🤖 Using: {provider_info['provider'].title()} ({provider_info['model']})")
        
        # Translate
        try:
            if api_manager.get_key_count() > 0:
                translated, source, target = translate_text(
                    text, 
                    "Any Language",  # Auto-detect 
                    "Tiếng Việt", 
                    "English",
                    return_language_info=True
                )
                print(f"🎯 Translation ({source} → {target}): {translated}")
            else:
                print("⚠️  No valid API keys available for translation")
        except Exception as e:
            print(f"❌ Translation error: {e}")
    
    # Demo failover mechanism
    print(f"\n🔄 Testing Failover Mechanism:")
    print("-" * 40)
    
    if api_manager.get_key_count() > 1:
        print("🧪 Simulating API failures...")
        
        # Mark current key as failed
        current_key = api_manager.get_active_key()
        if current_key:
            original_provider = current_key.provider.value
            api_manager.mark_key_failed(current_key, "DEMO_FAILURE")
            print(f"❌ Marked {original_provider.title()} as failed")
            
            # Find next working key
            next_key = api_manager.find_next_working_key(exclude_current=True)
            if next_key:
                print(f"🔄 Auto-switched to {next_key.provider.value.title()}")
                
                # Reset for demo
                api_manager.reset_key_failures(current_key)
                print(f"🔧 Reset {original_provider.title()} failure count")
            else:
                print("⚠️  No alternative providers available")
    else:
        print("ℹ️  Need multiple API keys to demo failover")
    
    print(f"\n✨ Demo Features Showcased:")
    print("   🔹 Multiple AI Provider Support (Gemini, ChatGPT, DeepSeek, Claude)")
    print("   🔹 Automatic Language Detection")
    print("   🔹 Smart Provider Failover")
    print("   🔹 Provider Priority Management")
    print("   🔹 Failed Provider Tracking")
    print("   🔹 Enhanced Error Handling")
    
    print(f"\n🎉 ITM Translate Multi-Provider System Demo Complete!")
    
    # Show final status
    provider_info = api_manager.get_provider_info()
    if provider_info['provider'] != 'none':
        print(f"🎯 Current Active: {provider_info['name']} ({provider_info['provider'].title()})")

if __name__ == "__main__":
    try:
        demo_multi_provider()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
