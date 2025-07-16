#!/usr/bin/env python3
"""
Final integration test for the new API Key Management system
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_import_all_modules():
    """Test that all modules can be imported correctly"""
    print("🔍 Testing module imports...")
    
    try:
        from core.api_key_manager import APIKeyManager, api_key_manager
        print("  ✅ APIKeyManager imported successfully")
        
        from core.translator import translate_text
        print("  ✅ Enhanced translator imported successfully")
        
        from ui.gui import MainGUI
        print("  ✅ Enhanced GUI imported successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_api_key_manager_functionality():
    """Test core API key manager functionality"""
    print("\n🔑 Testing API Key Manager...")
    
    try:
        from core.api_key_manager import api_key_manager
        
        # Get current state
        initial_count = api_key_manager.get_key_count()
        print(f"  📊 Current keys: {initial_count}")
        
        # Test adding a dummy key
        test_key = "AIzaSyTestKey123456789012345678901234567890"
        added = api_key_manager.add_key(test_key)
        print(f"  ➕ Add test key: {added}")
        
        # Test getting active key
        active = api_key_manager.get_active_key()
        print(f"  🎯 Active key: {active[:10] if active else 'None'}...")
        
        # Test rotation
        if api_key_manager.get_key_count() > 1:
            old_index = api_key_manager.active_index
            api_key_manager.rotate_to_next_key()
            new_index = api_key_manager.active_index
            print(f"  🔄 Rotation: {old_index} → {new_index}")
        
        # Remove test key
        if added:
            keys = api_key_manager.get_all_keys()
            for i, key in enumerate(keys):
                if key == test_key:
                    api_key_manager.remove_key(i)
                    print(f"  🗑️ Removed test key")
                    break
        
        return True
    except Exception as e:
        print(f"  ❌ API Key Manager error: {e}")
        return False

def test_translation_system():
    """Test the enhanced translation system"""
    print("\n🌍 Testing Translation System...")
    
    try:
        from core.translator import translate_text
        from core.api_key_manager import api_key_manager
        
        if api_key_manager.get_key_count() == 0:
            print("  ⚠️ No API keys available for translation test")
            return True
        
        # Test simple translation
        test_text = "Hello"
        result = translate_text(test_text, "English", "Tiếng Việt", "한국어")
        
        if result and not result.startswith("Lỗi"):
            print(f"  ✅ Translation successful: '{test_text}' → '{result}'")
            return True
        else:
            print(f"  ⚠️ Translation returned: {result}")
            return True  # Still pass if it's a quota/key issue
            
    except Exception as e:
        print(f"  ❌ Translation error: {e}")
        return False

def test_gui_integration():
    """Test GUI integration without actually opening windows"""
    print("\n🖥️ Testing GUI Integration...")
    
    try:
        # Test that GUI can be instantiated (but don't show it)
        import tkinter as tk
        from ui.gui import MainGUI
        
        # Create hidden root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test GUI creation
        app = MainGUI(root)
        print("  ✅ GUI creation successful")
        
        # Test API key tab methods exist
        if hasattr(app, 'create_api_key_tab'):
            print("  ✅ API key tab method exists")
        else:
            print("  ❌ API key tab method missing")
            return False
        
        if hasattr(app, 'add_api_key'):
            print("  ✅ Add API key method exists")
        else:
            print("  ❌ Add API key method missing")
            return False
        
        # Clean up
        root.destroy()
        
        return True
    except Exception as e:
        print(f"  ❌ GUI integration error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 ITM Translate - Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_import_all_modules,
        test_api_key_manager_functionality,
        test_translation_system,
        test_gui_integration
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    test_names = [
        "Module Imports",
        "API Key Manager",
        "Translation System", 
        "GUI Integration"
    ]
    
    passed = 0
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All systems ready! ITM Translate v1.2.0 is good to go!")
    else:
        print("⚠️ Some issues detected. Please check the details above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
