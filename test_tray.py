#!/usr/bin/env python3
"""
Test script để kiểm tra tray icon functionality
"""
import tkinter as tk
from ttkbootstrap import Window
from core.tray import create_tray_icon
import time
import sys
import os

# Setup minimal environment
sys.path.insert(0, os.path.dirname(__file__))

class MockApp:
    def __init__(self):
        self.floating_button_enabled = None

def test_tray_icon():
    print("🧪 Starting tray icon test...")
    
    # Tạo root window
    root = Window(themename="flatly")
    root.withdraw()  # Ẩn window để chỉ test tray
    
    # Mock app object
    app = MockApp()
    
    # Tạo tray icon
    print("🔧 Creating tray icon...")
    tray = create_tray_icon(root, app)
    
    print("✅ Tray icon created successfully!")
    print("📋 Available actions:")
    print("   • Single-click: Toggle floating button")
    print("   • Right-click: Open menu")
    print("   • Menu option: Toggle floating button") 
    print("   • Double-click: Show main window (will show hidden window)")
    print("")
    print("🔍 Watch console for debug messages when you interact with tray icon")
    print("⏱️  Test will run for 30 seconds...")
    
    # Schedule auto-close after 30 seconds
    def auto_close():
        print("⏰ Test timeout - closing...")
        root.quit()
    
    root.after(30000, auto_close)  # 30 seconds
    
    # Start event loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("🛑 Test interrupted by user")
    finally:
        print("🧪 Test completed")

if __name__ == "__main__":
    test_tray_icon()
