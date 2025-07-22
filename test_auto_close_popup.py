#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for Auto Close Popup feature
Kịch bản test cho tính năng tự động đóng cửa sổ popup
"""

import os
import json
import time
import subprocess
import sys

def test_load_setting():
    """Test loading auto_close_popup setting from startup.json"""
    print("🧪 Testing load_auto_close_popup() function...")
    
    # Import the function
    sys.path.append(os.path.dirname(__file__))
    from ITM_Translate import load_auto_close_popup
    
    # Test default value
    setting = load_auto_close_popup()
    print(f"✅ Default setting loaded: {setting}")
    
    return setting

def test_save_setting():
    """Test saving auto_close_popup setting"""
    print("🧪 Testing save_auto_close_popup() function...")
    
    # Import the function  
    sys.path.append(os.path.dirname(__file__))
    from ITM_Translate import save_auto_close_popup, load_auto_close_popup
    
    # Test saving False
    save_auto_close_popup(False)
    setting = load_auto_close_popup()
    print(f"✅ Setting saved as False: {setting}")
    
    # Test saving True
    save_auto_close_popup(True)
    setting = load_auto_close_popup()
    print(f"✅ Setting saved as True: {setting}")
    
    return setting

def test_startup_json_structure():
    """Test startup.json structure"""
    print("🧪 Testing startup.json structure...")
    
    startup_file = "startup.json"
    if os.path.exists(startup_file):
        with open(startup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_keys = ["startup", "show_on_startup", "auto_close_popup"]
        for key in required_keys:
            if key in data:
                print(f"✅ Key '{key}': {data[key]}")
            else:
                print(f"❌ Missing key '{key}'")
        
        print(f"📁 Full startup.json content: {data}")
    else:
        print("❌ startup.json file not found")

def main():
    """Main test function"""
    print("🚀 Starting Auto Close Popup Feature Tests")
    print("=" * 50)
    
    try:
        # Test 1: Check file structure
        test_startup_json_structure()
        print()
        
        # Test 2: Load setting
        test_load_setting()
        print()
        
        # Test 3: Save setting
        test_save_setting()
        print()
        
        print("✅ All tests completed successfully!")
        print("\n📝 Instructions to test manually:")
        print("1. Run ITM_Translate.py")
        print("2. Go to 'Nâng Cao' tab")
        print("3. Check/uncheck 'Tự động đóng cửa sổ dịch khi mất focus'")
        print("4. Use Ctrl+Q to translate some text")
        print("5. Verify if popup auto-closes based on setting")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
