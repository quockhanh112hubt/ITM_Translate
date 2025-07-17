#!/usr/bin/env python3
"""
Test script to verify model availability and fix issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.api_key_manager import APIKeyManager, AIProvider

def test_model_availability():
    """Test different Gemini models to find working ones"""
    
    print("🧪 Testing Gemini Model Availability")
    print("=" * 50)
    
    # List of Gemini models to test
    gemini_models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-pro",
        "gemini-1.0-pro",
        "gemini-2.0-flash-exp"
    ]
    
    api_manager = APIKeyManager()
    
    if api_manager.get_key_count() == 0:
        print("❌ No API keys found. Please add a Gemini API key first.")
        return
    
    # Get first Gemini key
    gemini_keys = [k for k in api_manager.get_all_keys() if k.provider == AIProvider.GEMINI]
    if not gemini_keys:
        print("❌ No Gemini API key found.")
        return
    
    gemini_key = gemini_keys[0]
    print(f"🔑 Testing with key: ...{gemini_key.key[-8:]}")
    
    import google.generativeai as genai
    genai.configure(api_key=gemini_key.key)
    
    working_models = []
    
    for model_name in gemini_models:
        print(f"\n🧪 Testing model: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            # Test with simple prompt
            response = model.generate_content("Hello")
            if response and response.text:
                print(f"✅ {model_name} - WORKING")
                working_models.append(model_name)
            else:
                print(f"⚠️ {model_name} - No response")
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"🚫 {model_name} - QUOTA EXCEEDED (might work with valid quota)")
                working_models.append(f"{model_name} (quota limited)")
            elif "404" in error_msg or "not found" in error_msg.lower():
                print(f"❌ {model_name} - MODEL NOT FOUND")
            else:
                print(f"❌ {model_name} - ERROR: {str(e)[:100]}")
    
    print(f"\n📊 Summary:")
    print(f"   Working models: {len([m for m in working_models if 'quota' not in m])}")
    print(f"   Quota-limited: {len([m for m in working_models if 'quota' in m])}")
    
    if working_models:
        print(f"\n✅ Recommended models:")
        for model in working_models:
            print(f"   - {model}")
    else:
        print(f"\n❌ No working models found. Check your API key or quota.")

def fix_existing_keys():
    """Fix existing keys with new model names"""
    print(f"\n🔧 Fixing existing API keys...")
    
    api_manager = APIKeyManager()
    updated = False
    
    for key_info in api_manager.get_all_keys():
        if key_info.provider == AIProvider.GEMINI and key_info.model == "gemini-2.0-flash-exp":
            print(f"🔄 Updating {key_info.name}: gemini-2.0-flash-exp → gemini-1.5-flash")
            key_info.model = "gemini-1.5-flash"
            # Reset failure count
            key_info.failed_count = 0
            key_info.last_error = ""
            key_info.is_active = True
            updated = True
    
    if updated:
        api_manager.save_keys()
        print("✅ Keys updated successfully!")
    else:
        print("ℹ️ No keys needed updating.")

if __name__ == "__main__":
    try:
        fix_existing_keys()
        test_model_availability()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
