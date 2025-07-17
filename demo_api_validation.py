#!/usr/bin/env python3
"""
Demo API Key Validation - Test tính năng validation mới
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.api_key_validator import APIKeyValidator, ValidationResult, get_validation_message

def demo_validation():
    """Demo tính năng validation API key"""
    
    print("🔐 API Key Validation Demo")
    print("=" * 50)
    
    # Test cases với different scenarios
    test_cases = [
        # Format validation tests
        ("gemini", "", "Empty key test"),
        ("gemini", "invalid_key", "Invalid Gemini format"),
        ("gemini", "AIza123", "Too short Gemini key"),
        ("chatgpt", "invalid_key", "Invalid OpenAI format"),
        ("deepseek", "sk-123", "Too short DeepSeek key"),
        ("claude", "invalid_key", "Invalid Claude format"),
        
        # Valid format tests (nhưng key giả)
        ("gemini", "AIzaSyDummyKeyForTestingPurposes123456789", "Valid Gemini format (fake key)"),
        ("chatgpt", "sk-dummykey1234567890abcdefghijklmnopqrstuvwxyz", "Valid OpenAI format (fake key)"),
        ("deepseek", "sk-dummykey1234567890abcdefghijklmnopqrstuvwxyz", "Valid DeepSeek format (fake key)"),
        ("claude", "sk-ant-dummykey1234567890abcdefghijklmnopqrstuvwxyz123456", "Valid Claude format (fake key)"),
    ]
    
    for provider, key, description in test_cases:
        print(f"\n🧪 Test: {description}")
        print(f"   Provider: {provider}")
        print(f"   Key: {key[:20]}{'...' if len(key) > 20 else ''}")
        print("-" * 40)
        
        # Test format validation
        format_valid, format_msg = APIKeyValidator.validate_format(provider, key)
        print(f"   📋 Format: {'✅' if format_valid else '❌'} {format_msg}")
        
        if format_valid:
            # Test full validation (sẽ fail vì key giả)
            result, message = APIKeyValidator.validate_api_key(provider, key, "auto")
            validation_info = get_validation_message(result, message)
            
            print(f"   🌐 API Test: {validation_info['type'].upper()}")
            print(f"   💬 Message: {validation_info['message']}")
            print(f"   💾 Allow Save: {'✅' if validation_info['allow_save'] else '❌'}")

def demo_real_key_test():
    """Demo test với real key (nếu user muốn test)"""
    
    print(f"\n" + "=" * 50)
    print("🔑 Real API Key Test (Optional)")
    print("=" * 50)
    print("⚠️  Lưu ý: Chức năng này để test real API key")
    print("💡 Không nhập real key vào console log!")
    print("\nNếu muốn test real key, hãy:")
    print("1. Mở ITM Translate GUI")
    print("2. Vào tab 'Quản lý API KEY'")
    print("3. Thêm API key thực -> Hệ thống sẽ auto validate")
    print("4. Xem kết quả validation real-time")

def show_validation_flow():
    """Hiển thị flow validation trong GUI"""
    
    print(f"\n" + "=" * 50)
    print("🎯 GUI Validation Flow")
    print("=" * 50)
    
    flow = """
    1. User nhập API key + chọn provider/model
    2. User nhấn "Thêm Key"
    3. 🔄 Button chuyển thành "Đang kiểm tra..."
    4. 📋 System validate format (instant)
    5. 🌐 System test API connection (background)
    6. 📊 Show validation result:
       ✅ SUCCESS: "API key hợp lệ! Lưu không?"
       ⚠️  WARNING: "Có issue nhưng vẫn lưu được"
       ❌ ERROR: "API key không hợp lệ"
    7. 💾 Save nếu user đồng ý
    8. 🔄 Refresh API key list
    """
    
    print(flow)
    
    print("\n🎨 UI/UX Improvements:")
    print("   • Loading state với progress feedback")
    print("   • Detailed error messages với solutions")
    print("   • Smart save decision based on validation")
    print("   • Graceful handling của network errors")

if __name__ == "__main__":
    demo_validation()
    demo_real_key_test()
    show_validation_flow()
    
    print(f"\n🎉 API Key Validation Demo Complete!")
    print(f"💡 Để test với real keys: Chạy ITM Translate GUI")
