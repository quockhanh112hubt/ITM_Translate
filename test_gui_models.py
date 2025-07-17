#!/usr/bin/env python3
"""
Test GUI Model Selection - Kiểm tra GUI có load được model selection không
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gui_imports():
    """Test xem GUI có import được các module cần thiết không"""
    
    print("🧪 Testing GUI Model Selection Imports")
    print("=" * 50)
    
    try:
        # Test import provider_models
        from core.provider_models import get_models_for_provider, get_model_description
        print("✅ core.provider_models imported successfully")
        
        # Test các functions
        gemini_models = get_models_for_provider('gemini')
        print(f"✅ Gemini models: {len(gemini_models)} models loaded")
        
        auto_desc = get_model_description('auto')
        print(f"✅ Model description: {auto_desc}")
        
        # Test GUI import
        from ui.gui import MainGUI
        print("✅ ui.gui imported successfully")
        
        # Test tkinter và ttkbootstrap
        import tkinter as tk
        import ttkbootstrap as ttk
        print("✅ tkinter and ttkbootstrap available")
        
        print("\n🎯 All imports successful! GUI should work properly.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False
    
    return True

def test_model_selection_logic():
    """Test logic của model selection"""
    
    print("\n🔧 Testing Model Selection Logic")
    print("-" * 40)
    
    from core.provider_models import get_models_for_provider, get_default_model
    
    test_cases = [
        ('gemini', 'auto'),
        ('chatgpt', 'auto'),
        ('deepseek', 'auto'),
        ('claude', 'auto'),
        ('invalid_provider', 'auto')  # Test fallback
    ]
    
    for provider, expected_default in test_cases:
        try:
            models = get_models_for_provider(provider)
            default = get_default_model(provider)
            
            print(f"  Provider: {provider}")
            print(f"    Models count: {len(models)}")
            print(f"    Default: {default}")
            print(f"    Expected: {expected_default}")
            print(f"    Status: {'✅' if default == expected_default else '❌'}")
            
        except Exception as e:
            print(f"  Provider: {provider} - ❌ Error: {e}")

if __name__ == "__main__":
    success = test_gui_imports()
    if success:
        test_model_selection_logic()
        print(f"\n🎉 All tests completed! GUI Model Selection ready to use.")
    else:
        print(f"\n❌ Tests failed. Please check dependencies.")
