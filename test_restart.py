#!/usr/bin/env python3
"""
Test script để verify logic restart của GUI
"""
import sys
import os

# Add current directory to path để import được modules
sys.path.insert(0, os.path.dirname(__file__))

from ui.gui import MainGUI
import tkinter as tk

def test_restart_logic():
    """Test logic tạo restart batch file"""
    print("🧪 Testing restart logic...")
    
    # Tạo mock root window
    root = tk.Tk()
    root.withdraw()  # Hide window
    
    # Tạo MainGUI instance
    gui = MainGUI(root)
    
    try:
        # Test tạo restart batch file
        gui._create_restart_batch_file()
        
        # Kiểm tra xem file đã được tạo chưa
        current_exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
        app_dir = os.path.dirname(current_exe_path)
        batch_file_path = os.path.join(app_dir, "restart.bat")
        
        if os.path.exists(batch_file_path):
            print(f"✅ Restart batch file created successfully: {batch_file_path}")
            
            # Đọc và hiển thị nội dung
            with open(batch_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("\n📄 Batch file content preview:")
            print("=" * 50)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("=" * 50)
            
            # Cleanup
            os.remove(batch_file_path)
            print("🧹 Test batch file cleaned up")
            
        else:
            print("❌ Restart batch file was not created")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        root.destroy()

if __name__ == "__main__":
    test_restart_logic()
    print("\n✅ Test completed!")
