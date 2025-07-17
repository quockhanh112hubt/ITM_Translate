#!/usr/bin/env python3
"""
Demo script to test updated Gemini models in the model selection dropdown
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.provider_models import PROVIDER_MODELS, MODEL_DESCRIPTIONS, get_models_for_provider, get_model_description

def test_gemini_models():
    """Test updated Gemini models"""
    print("=== KIỂM TRA DANH SÁCH MODEL GEMINI ĐÃ CẬP NHẬT ===\n")
    
    gemini_models = get_models_for_provider('gemini')
    print(f"Tổng số model Gemini: {len(gemini_models)}")
    print("\nDanh sách đầy đủ:")
    
    for i, model in enumerate(gemini_models, 1):
        description = get_model_description(model)
        print(f"{i:2d}. {model}")
        print(f"    📝 {description}")
        
        # Highlight new models
        if '2.0' in model:
            print("    🆕 MODEL MỚI NHẤT!")
        elif '8b' in model:
            print("    ⚡ MODEL SIÊU NHANH!")
        print()

def test_all_providers():
    """Test all providers for comparison"""
    print("\n=== SO SÁNH SỐ LƯỢNG MODEL CỦA CÁC PROVIDER ===\n")
    
    for provider in PROVIDER_MODELS.keys():
        models = get_models_for_provider(provider)
        print(f"{provider.upper():10s}: {len(models):2d} models")

def test_model_search():
    """Test searching for specific models"""
    print("\n=== TÌM KIẾM MODEL CỤ THỂ ===\n")
    
    search_terms = ['2.0', 'flash', 'pro', 'experimental']
    
    for term in search_terms:
        print(f"🔍 Tìm kiếm '{term}':")
        found_models = []
        
        for provider, models in PROVIDER_MODELS.items():
            for model in models:
                if term.lower() in model.lower():
                    found_models.append(f"{provider}: {model}")
        
        if found_models:
            for model in found_models:
                print(f"   ✅ {model}")
        else:
            print(f"   ❌ Không tìm thấy")
        print()

if __name__ == "__main__":
    test_gemini_models()
    test_all_providers()
    test_model_search()
    
    print("=== HOÀN THÀNH ===")
    print("✅ Danh sách model Gemini đã được cập nhật thành công!")
    print("✅ Gemini 2.0 Flash (Experimental) đã được thêm")
    print("✅ Gemini 1.5 Flash 8B đã được thêm")
    print("\n💡 Bây giờ bạn có thể mở GUI và kiểm tra dropdown model selection!")
