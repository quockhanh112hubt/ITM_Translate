#!/usr/bin/env python3
"""
Test script để kiểm tra GUI update dialog
"""

import tkinter as tk
import sys
import os

# Thêm thư mục hiện tại vào path
sys.path.insert(0, os.path.dirname(__file__))

from core.updater import Updater, UpdateDialog

def test_update_dialog():
    """Test update dialog với dữ liệu giả"""
    root = tk.Tk()
    root.title("Test Update Dialog")
    root.geometry("300x200")
    
    # Tạo mock updater
    updater = Updater()
    updater.current_version = "1.0.0"
    updater.new_version = "1.0.3"
    updater.download_url = "https://github.com/quockhanh112hubt/ITM_Translate/releases/download/v1.0.3/ITM_Translate.exe"
    
    def show_update_available():
        changelog = """## Cập nhật mới v1.0.3

- ✅ Auto-update từ GitHub releases
- 🔄 Chạy trong system tray  
- 🎯 Popup hiển thị kết quả dịch
- 🔧 Sửa lỗi và cải thiện hiệu suất

## Cài đặt:
1. Download file ITM_Translate.exe
2. Chạy và cấu hình API key trong tab "Nâng Cao"
3. Tận hưởng!"""
        
        UpdateDialog(root, updater, has_update=True, new_version="1.0.3", changelog=changelog)
    
    def show_no_update():
        UpdateDialog(root, updater, has_update=False, new_version="1.0.0", 
                    changelog="Bạn đang sử dụng phiên bản mới nhất")
    
    def test_real_check():
        """Test kiểm tra update thật từ GitHub"""
        real_updater = Updater()
        real_updater.current_version = real_updater.get_current_version()
        
        def check_worker():
            try:
                has_update, version, message = real_updater.check_for_updates()
                print(f"Kết quả kiểm tra: has_update={has_update}, version={version}")
                print(f"Message: {message}")
                
                root.after(0, lambda: UpdateDialog(root, real_updater, has_update, version, message))
            except Exception as e:
                print(f"Lỗi kiểm tra: {e}")
        
        import threading
        threading.Thread(target=check_worker, daemon=True).start()
    
    # Tạo buttons để test
    tk.Button(root, text="Test: Có Update", command=show_update_available, 
              bg='green', fg='white', font=('Arial', 12)).pack(pady=10)
    
    tk.Button(root, text="Test: Không có Update", command=show_no_update,
              bg='blue', fg='white', font=('Arial', 12)).pack(pady=10)
    
    tk.Button(root, text="Test: Kiểm tra thật từ GitHub", command=test_real_check,
              bg='orange', fg='white', font=('Arial', 12)).pack(pady=10)
    
    tk.Button(root, text="Thoát", command=root.quit,
              bg='red', fg='white', font=('Arial', 12)).pack(pady=10)
    
    print("🔧 Test Update GUI - Sẵn sàng!")
    print("- Bấm các nút để test dialog update")
    print("- Kiểm tra luồng download và install")
    print("- Xem message và UI hoạt động như thế nào")
    
    root.mainloop()

if __name__ == "__main__":
    test_update_dialog()
