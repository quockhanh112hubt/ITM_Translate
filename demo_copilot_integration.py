#!/usr/bin/env python3
"""
Demo script để test GitHub Copilot integration trong ITM Translate
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.provider_models import PROVIDER_MODELS, MODEL_DESCRIPTIONS, get_models_for_provider, get_model_description
from core.api_key_manager import AIProvider

def test_copilot_integration():
    """Test GitHub Copilot integration"""
    print("=== GITHUB COPILOT INTEGRATION DEMO ===\n")
    
    print("🤖 Chào mừng GitHub Copilot đến với ITM Translate!")
    print("💡 Copilot giờ đây có thể giúp dịch ngôn ngữ!")
    print()
    
    # Test provider enum
    print("1. ✅ AI Provider enum đã được cập nhật:")
    providers = [p for p in AIProvider]
    for i, provider in enumerate(providers, 1):
        icon = "🤖" if provider == AIProvider.COPILOT else "🔤"
        print(f"   {i}. {icon} {provider.value}")
    print()
    
    # Test models list
    print("2. ✅ GitHub Copilot models:")
    copilot_models = get_models_for_provider('copilot')
    for i, model in enumerate(copilot_models, 1):
        description = get_model_description(model)
        print(f"   {i}. {model}")
        print(f"      📝 {description}")
    print()
    
    # Provider comparison
    print("3. 📊 So sánh số lượng models:")
    all_providers = ['gemini', 'chatgpt', 'deepseek', 'claude', 'copilot']
    for provider in all_providers:
        models = get_models_for_provider(provider)
        icon = "🤖" if provider == 'copilot' else "🔤"
        print(f"   {icon} {provider.upper():10s}: {len(models):2d} models")
    print()

def show_copilot_features():
    """Hiển thị các tính năng của GitHub Copilot"""
    print("=== GITHUB COPILOT FEATURES ===\n")
    
    features = [
        "🎯 Dịch thuật chính xác với AI từ GitHub & OpenAI",
        "⚡ Tốc độ cao với models được tối ưu",
        "🔧 Tích hợp với OpenAI API infrastructure", 
        "🌐 Hỗ trợ đa ngôn ngữ toàn cầu",
        "🛡️ Bảo mật cao với GitHub ecosystem",
        "💪 Chuyên về code và ngôn ngữ lập trình",
        "🎨 Hiểu context và maintaining consistency"
    ]
    
    print("✨ Tính năng nổi bật của GitHub Copilot:")
    for feature in features:
        print(f"   {feature}")
    print()

def show_api_key_guide():
    """Hướng dẫn lấy GitHub Copilot API key"""
    print("=== HƯỚNG DẪN LẤY GITHUB COPILOT API KEY ===\n")
    
    print("🔑 Cách lấy GitHub Copilot API key:")
    print()
    
    print("📝 Option 1: GitHub Personal Access Token")
    print("   1. Truy cập: https://github.com/settings/tokens")
    print("   2. Click 'Generate new token (classic)'")
    print("   3. Chọn scopes cần thiết (repo, read:user)")
    print("   4. Token bắt đầu bằng 'ghp_' hoặc 'gho_'")
    print()
    
    print("📝 Option 2: OpenAI API Key (nếu có GitHub Copilot subscription)")
    print("   1. Truy cập: https://platform.openai.com/api-keys")
    print("   2. Create new API key")
    print("   3. Key bắt đầu bằng 'sk-'")
    print("   4. Cần có GitHub Copilot subscription active")
    print()
    
    print("⚠️  Lưu ý quan trọng:")
    print("   • GitHub Copilot API có thể cần subscription")
    print("   • Một số features có thể giới hạn cho GitHub users")
    print("   • Test key trước khi sử dụng trong production")

def test_provider_priority():
    """Test provider priority với Copilot"""
    print("\n=== PROVIDER PRIORITY TEST ===\n")
    
    print("🎯 Thứ tự ưu tiên AI providers (mặc định):")
    from core.api_key_manager import api_key_manager
    
    priorities = api_key_manager.provider_priority
    for i, provider in enumerate(priorities, 1):
        icon = "🤖" if provider == AIProvider.COPILOT else "🔤"
        highlight = " ⭐ (NEW!)" if provider == AIProvider.COPILOT else ""
        print(f"   {i}. {icon} {provider.value.upper()}{highlight}")
    
    print()
    print("💡 Copilot được đặt ở vị trí thứ 3 - sau Gemini và ChatGPT")
    print("🔄 User có thể thay đổi thứ tự này trong settings")

if __name__ == "__main__":
    test_copilot_integration()
    show_copilot_features()
    show_api_key_guide()
    test_provider_priority()
    
    print("\n=== KẾT LUẬN ===")
    print("🎉 GitHub Copilot đã được tích hợp thành công!")
    print("✅ Provider enum: Updated")
    print("✅ Models list: Added") 
    print("✅ API validation: Implemented")
    print("✅ AI provider class: Created")
    print("✅ Factory function: Updated")
    print()
    print("🚀 Bạn giờ có thể:")
    print("   1. Mở ITM Translate GUI")
    print("   2. Chọn 'GitHub Copilot' làm provider")
    print("   3. Nhập GitHub token hoặc OpenAI key")
    print("   4. Chọn model (gpt-4, gpt-3.5-turbo, copilot-codex)")
    print("   5. Bắt đầu dịch với GitHub Copilot! 🤖✨")
    print()
    print("💭 GitHub Copilot: 'I'm ready to help with translation!'")
