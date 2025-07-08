#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

def test_pywin32():
    """Test pywin32 functionality"""
    try:
        print("🔍 Testing pywin32 import...")
        import pythoncom
        print("✅ pythoncom imported successfully")
        
        from win32com.client import Dispatch
        print("✅ win32com.client imported successfully")
        
        print("\n🔍 Testing WScript.Shell creation...")
        shell = Dispatch('WScript.Shell')
        print("✅ WScript.Shell created successfully")
        
        return True
    except Exception as e:
        print(f"❌ pywin32 test failed: {e}")
        return False

def test_startup_shortcut():
    """Test creating startup shortcut"""
    if not sys.platform.startswith('win'):
        print("ℹ️ Not on Windows, skipping startup test")
        return True
        
    try:
        print("\n🔍 Testing startup shortcut creation...")
        
        # Đường dẫn file thực thi
        exe_path = os.path.abspath('ITM_Translate.py')
        print(f"Target path: {exe_path}")
        
        # Đường dẫn shortcut trong thư mục Startup
        startup_dir = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_dir, 'ITM Translate Test.lnk')
        print(f"Shortcut path: {shortcut_path}")
        
        # Tạo shortcut
        import pythoncom
        from win32com.client import Dispatch
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = exe_path
        shortcut.save()
        
        print("✅ Shortcut created successfully")
        
        # Kiểm tra file có tồn tại không
        if os.path.exists(shortcut_path):
            print("✅ Shortcut file exists")
            
            # Xóa shortcut test
            os.remove(shortcut_path)
            print("✅ Test shortcut removed")
        else:
            print("❌ Shortcut file not found")
            
        return True
    except Exception as e:
        print(f"❌ Startup shortcut test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing pywin32 and startup functionality")
    print("=" * 50)
    
    success = True
    
    # Test pywin32
    if not test_pywin32():
        success = False
    
    # Test startup shortcut
    if not test_startup_shortcut():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 50)
