#!/usr/bin/env python3
"""
Test script để simulation GUI update từ main app
"""

import sys
import os
import threading
import time

# Thêm thư mục hiện tại vào path
sys.path.insert(0, os.path.dirname(__file__))

from ui.gui import MainGUI
import tkinter as tk

def test_gui_update_integration():
    """Test integration update button trong GUI thực"""
    
    print("🔧 Testing GUI Update Integration...")
    
    # Tạo mock root window
    root = tk.Tk()
    root.title("ITM Translate - Test Update Integration")
    root.geometry("400x300")
    
    # Mock initial settings
    mock_hotkeys = {
        'translate_popup': '<ctrl>+q',
        'replace_translate': '<ctrl>+d',
        'translate_popup2': '<ctrl>+1',
        'replace_translate2': '<ctrl>+2',
        'Ngon_ngu_dau_tien': 'Any Language',
        'Ngon_ngu_thu_2': 'Tiếng Việt',
        'Ngon_ngu_thu_3': 'English',
        'Nhom2_Ngon_ngu_dau_tien': 'Any Language',
        'Nhom2_Ngon_ngu_thu_2': 'Tiếng Việt',
        'Nhom2_Ngon_ngu_thu_3': 'English'
    }
    
    # Tạo MainGUI instance
    gui = MainGUI(root)
    gui.set_initial_settings(mock_hotkeys, "test_api_key", False, True)
    
    # Override update_program để test
    original_update_program = gui.update_program
    
    def test_update_program():
        print("🚀 Testing update_program method...")
        print("📱 This should show loading popup and then update dialog")
        try:
            original_update_program()
            print("✅ update_program called successfully")
        except Exception as e:
            print(f"❌ Error in update_program: {e}")
            import traceback
            traceback.print_exc()
    
    # Tạo test buttons
    test_frame = tk.Frame(root, bg='lightgray', padx=20, pady=20)
    test_frame.pack(fill='both', expand=True)
    
    tk.Label(test_frame, text="🔧 Test Update Integration", 
             font=('Arial', 14, 'bold'), bg='lightgray').pack(pady=10)
    
    tk.Label(test_frame, text="Bấm nút để test chức năng update\ngiống như trong GUI thật",
             bg='lightgray', justify='center').pack(pady=5)
    
    tk.Button(test_frame, text="Test Update Button", 
              command=test_update_program,
              bg='blue', fg='white', font=('Arial', 12), 
              padx=20, pady=10).pack(pady=10)
    
    def show_real_gui():
        """Hiện GUI thật để so sánh"""
        try:
            new_root = tk.Toplevel(root)
            new_root.title("ITM Translate - Real GUI")
            real_gui = MainGUI(new_root)
            real_gui.set_initial_settings(mock_hotkeys, "test_api_key", False, True)
            print("✅ Real GUI opened successfully")
        except Exception as e:
            print(f"❌ Error opening real GUI: {e}")
    
    tk.Button(test_frame, text="Show Real GUI", 
              command=show_real_gui,
              bg='green', fg='white', font=('Arial', 12),
              padx=20, pady=10).pack(pady=5)
    
    tk.Button(test_frame, text="Exit Test", 
              command=root.quit,
              bg='red', fg='white', font=('Arial', 12),
              padx=20, pady=10).pack(pady=10)
    
    print("🎯 GUI Test ready!")
    print("- Bấm 'Test Update Button' để test update từ GUI")
    print("- Bấm 'Show Real GUI' để mở GUI thật") 
    print("- So sánh behavior giữa test và real GUI")
    
    root.mainloop()

if __name__ == "__main__":
    test_gui_update_integration()
