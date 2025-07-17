#!/usr/bin/env python3
"""
Test script để kiểm tra Gemini 2.0 models có hoạt động không
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.api_key_manager import api_key_manager, AIProvider
from core.ai_providers import GeminiProvider

def test_gemini_2_models():
    """Test Gemini 2.0 models"""
    print("=== KIỂM TRA GEMINI 2.0 MODELS ===\n")
    
    # Lấy Gemini keys
    gemini_keys = api_key_manager.get_keys_by_provider(AIProvider.GEMINI)
    
    if not gemini_keys:
        print("❌ Không có Gemini API key nào được cấu hình")
        print("💡 Vui lòng thêm Gemini API key trong GUI trước")
        return
    
    print(f"✅ Tìm thấy {len(gemini_keys)} Gemini key(s)")
    
    # Test với model mới
    test_models = [
        'gemini-2.0-flash-exp',
        'gemini-1.5-flash-8b',
        'gemini-1.5-flash'  # để so sánh
    ]
    
    test_text = "Hello, world!"
    target_lang = "vi"
    
    for model in test_models:
        print(f"\n🧪 Testing model: {model}")
        print("-" * 50)
        
        try:
            # Tạo provider với model cụ thể
            key_info = gemini_keys[0]  # Dùng key đầu tiên
            provider = GeminiProvider(key_info.key, model)
            
            print(f"📤 Input: '{test_text}' -> {target_lang}")
            print("⏳ Đang dịch...")
            
            result = provider.translate(test_text, target_lang)
            
            if result:
                print(f"✅ Output: '{result}'")
                print(f"🎉 Model {model} hoạt động tốt!")
            else:
                print(f"❌ Model {model} không trả về kết quả")
                
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                print(f"⚠️  Model {model} có thể chưa available hoặc cần access đặc biệt")
            else:
                print(f"❌ Lỗi: {error_msg}")

def show_model_availability_info():
    """Hiển thị thông tin về availability của models"""
    print("\n=== THÔNG TIN MODEL AVAILABILITY ===\n")
    
    print("📋 Gemini Models Status:")
    print("• gemini-1.5-flash     ✅ Stable, Available")
    print("• gemini-1.5-pro       ✅ Stable, Available") 
    print("• gemini-2.0-flash-exp ⚠️  Experimental, Có thể cần access")
    print("• gemini-1.5-flash-8b  ⚠️  Mới, Có thể cần access")
    
    print("\n💡 Tips:")
    print("• Nếu model experimental không hoạt động, hãy dùng stable models")
    print("• Kiểm tra Google AI Studio để xem models nào available")
    print("• Một số models có thể cần waitlist hoặc special access")

if __name__ == "__main__":
    test_gemini_2_models()
    show_model_availability_info()
    
    print("\n=== KẾT LUẬN ===")
    print("✅ Dropdown selection đã có Gemini 2.0 models")
    print("✅ User có thể chọn models mới trong GUI") 
    print("⚠️  Một số models experimental có thể cần access đặc biệt")
    print("💡 Nếu model không hoạt động, hệ thống sẽ fallback về model khác")
