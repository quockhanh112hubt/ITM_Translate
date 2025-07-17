#!/usr/bin/env python3
"""
Check Auto Model Selection - Xem model nào được chọn khi dùng "auto"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ai_providers import create_ai_provider
from core.api_key_manager import api_key_manager, AIProvider, APIKeyInfo

def check_auto_models():
    """Kiểm tra model nào được chọn khi dùng 'auto'"""
    
    print("🔍 Checking Auto Model Selection")
    print("=" * 50)
    
    providers = ['gemini', 'chatgpt', 'deepseek', 'claude']
    
    for provider_name in providers:
        print(f"\n📱 Provider: {provider_name.upper()}")
        print("-" * 30)
        
        try:
            # Create dummy key info with "auto" model
            provider = AIProvider(provider_name)
            dummy_key = APIKeyInfo(
                key="dummy_key_for_testing",
                provider=provider,
                model="auto",
                name=f"Test {provider_name} Auto"
            )
            
            # Create provider instance
            ai_provider = create_ai_provider(dummy_key)
            actual_model = ai_provider.model
            default_model = ai_provider.get_default_model()
            
            print(f"   Model setting: 'auto'")
            print(f"   → Actual model used: {actual_model}")
            print(f"   → Default model: {default_model}")
            print(f"   → Provider name: {ai_provider.get_provider_name()}")
            
            # Show description
            try:
                from core.provider_models import get_model_description
                description = get_model_description(actual_model)
                print(f"   💡 Description: {description}")
            except ImportError:
                print(f"   💡 Description: Model được chọn tự động")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n" + "=" * 50)
    print("✅ Auto Model Selection Summary:")
    print("   • 'auto' = Hệ thống chọn model tốt nhất cho từng provider")
    print("   • Đây là setting khuyến nghị cho hầu hết user")
    print("   • Không cần biết technical details về model")
    print("   • Model sẽ được optimize cho cost-performance")

def show_current_active_model():
    """Hiển thị model đang được sử dụng bởi API key active"""
    
    print(f"\n🎯 Current Active API Key Model")
    print("-" * 40)
    
    try:
        active_key = api_key_manager.get_active_key()
        if active_key:
            provider_info = api_key_manager.get_provider_info()
            
            print(f"   Active key: {provider_info['name']}")
            print(f"   Provider: {provider_info['provider'].title()}")
            print(f"   Model setting: {active_key.model}")
            
            # Get actual model used
            if active_key.model == "auto":
                ai_provider = create_ai_provider(active_key)
                actual_model = ai_provider.model
                print(f"   → Actual model: {actual_model}")
            else:
                print(f"   → Using specific model: {active_key.model}")
                
        else:
            print("   ⚠️ No active API key found")
            
    except Exception as e:
        print(f"   ❌ Error checking active key: {e}")

if __name__ == "__main__":
    check_auto_models()
    show_current_active_model()
