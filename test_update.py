#!/usr/bin/env python3
"""
Test script để kiểm tra chức năng update
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import tkinter as tk
from core.updater import Updater, UpdateDialog

def test_update_checker():
    """Test chức năng kiểm tra update"""
    print("Testing Update Checker...")
    
    updater = Updater()
    updater.current_version = updater.get_current_version()
    
    print(f"Current version: {updater.current_version}")
    print(f"Update server URL: {updater.update_server_url}")
    
    print("\nChecking for updates...")
    has_update, version, message = updater.check_for_updates()
    
    print(f"Has update: {has_update}")
    print(f"Version: {version}")
    print(f"Message: {message}")
    
    return has_update, version, message

def test_update_dialog():
    """Test UI dialog update"""
    print("\nTesting Update Dialog...")
    
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Test với update available
    has_update, version, message = test_update_checker()
    
    updater = Updater()
    dialog = UpdateDialog(root, updater, has_update, version or "1.0.1", message)
    
    # Keep window open for testing
    root.mainloop()

if __name__ == "__main__":
    print("ITM Translate - Update System Test")
    print("=" * 40)
    
    try:
        test_update_dialog()
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
