#!/usr/bin/env python3
"""
Demo Model Selection - Test tính năng chọn model mới trong GUI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.provider_models import *

def demo_model_selection():
    """Demo tính năng chọn model"""
    
    print("🎯 Demo Model Selection Feature")
    print("=" * 50)
    
    # Test tất cả providers
    providers = ['gemini', 'chatgpt', 'deepseek', 'claude']
    
    for provider in providers:
        print(f"\n📱 Provider: {provider.upper()}")
        print("-" * 30)
        
        models = get_models_for_provider(provider)
        default = get_default_model(provider)
        
        print(f"Default model: {default}")
        print(f"Available models ({len(models)}):")
        
        for i, model in enumerate(models, 1):
            description = get_model_description(model)
            status = "⭐ Default" if model == default else "  "
            print(f"  {i:2d}. {status} {model}")
            print(f"      💡 {description}")
    
    print(f"\n" + "=" * 50)
    print("✅ Model Selection Demo Complete!")
    print("\n💡 Hướng dẫn sử dụng trong GUI:")
    print("   1. Chọn Provider từ dropdown")
    print("   2. Model dropdown sẽ tự động cập nhật")
    print("   3. Hover vào model để xem mô tả")
    print("   4. 'auto' = sử dụng model mặc định")

if __name__ == "__main__":
    demo_model_selection()
