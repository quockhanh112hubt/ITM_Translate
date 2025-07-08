#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script để kiểm tra PyInstaller dependencies và DLL issues
"""

import sys
import os

def test_critical_imports():
    """Test tất cả critical imports"""
    print("=" * 50)
    print("Testing Critical Dependencies")
    print("=" * 50)
    
    imports_to_test = [
        ('sys', 'System module'),
        ('os', 'OS module'),
        ('tkinter', 'Tkinter GUI'),
        ('ttkbootstrap', 'TTKBootstrap theme'),
        ('pynput', 'Keyboard/Mouse input'),
        ('requests', 'HTTP requests'),
        ('PIL', 'Python Imaging Library'),
        ('google.generativeai', 'Google AI'),
        ('pythoncom', 'Python COM interface'),
        ('win32com.client', 'Win32 COM client'),
        ('json', 'JSON handling'),
        ('threading', 'Threading support'),
        ('tempfile', 'Temporary files'),
        ('subprocess', 'Process spawning'),
        ('shutil', 'Shell utilities'),
        ('zipfile', 'ZIP file handling'),
    ]
    
    failed_imports = []
    
    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name:20} - {description}")
        except ImportError as e:
            print(f"❌ {module_name:20} - FAILED: {e}")
            failed_imports.append(module_name)
        except Exception as e:
            print(f"⚠️  {module_name:20} - ERROR: {e}")
            failed_imports.append(module_name)
    
    print("\n" + "=" * 50)
    if failed_imports:
        print(f"❌ {len(failed_imports)} imports FAILED:")
        for module in failed_imports:
            print(f"   - {module}")
        return False
    else:
        print("🎉 All imports SUCCESSFUL!")
        return True

def test_file_access():
    """Test file access capabilities"""
    print("\n" + "=" * 50)
    print("Testing File Access")
    print("=" * 50)
    
    try:
        # Test reading
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Current directory: {current_dir}")
        
        # Test version file
        version_file = os.path.join(current_dir, "version.json")
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                content = f.read()
            print(f"✅ Version file readable ({len(content)} chars)")
        else:
            print("⚠️  Version file not found")
            
        # Test writing
        test_file = os.path.join(current_dir, "test_write.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        print("✅ Write access OK")
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        print("✅ File cleanup OK")
        
        return True
    except Exception as e:
        print(f"❌ File access failed: {e}")
        return False

def test_gui_creation():
    """Test basic GUI creation"""
    print("\n" + "=" * 50)
    print("Testing GUI Creation")
    print("=" * 50)
    
    try:
        import tkinter as tk
        from ttkbootstrap import Window
        
        # Test basic tkinter
        root = tk.Tk()
        root.withdraw()  # Hide window
        print("✅ Basic Tkinter OK")
        
        # Test ttkbootstrap
        boot_window = Window(themename="flatly")
        boot_window.withdraw()  # Hide window
        print("✅ TTKBootstrap OK")
        
        # Cleanup
        root.destroy()
        boot_window.destroy()
        
        return True
    except Exception as e:
        print(f"❌ GUI creation failed: {e}")
        return False

def test_executable_info():
    """Test executable information"""
    print("\n" + "=" * 50)
    print("Executable Information")
    print("=" * 50)
    
    print(f"Python executable: {sys.executable}")
    print(f"Frozen (PyInstaller): {getattr(sys, 'frozen', False)}")
    print(f"Script path: {__file__}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    if getattr(sys, 'frozen', False):
        print("🔧 Running as PyInstaller executable")
        # Test PyInstaller specific paths
        if hasattr(sys, '_MEIPASS'):
            print(f"PyInstaller temp dir: {sys._MEIPASS}")
    else:
        print("🐍 Running as Python script")

if __name__ == "__main__":
    print("ITM Translate - Dependency Test")
    print("This will help diagnose PyInstaller and DLL issues")
    
    all_tests_passed = True
    
    # Run all tests
    if not test_critical_imports():
        all_tests_passed = False
    
    if not test_file_access():
        all_tests_passed = False
        
    if not test_gui_creation():
        all_tests_passed = False
    
    test_executable_info()
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED - Application should work correctly!")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
        print("\nTroubleshooting:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. For PyInstaller builds: Update .spec file with missing imports")
        print("3. For DLL errors: Try rebuilding with --clean flag")
    print("=" * 60)
    
    input("\nPress Enter to exit...")
