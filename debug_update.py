#!/usr/bin/env python3
"""
Debug script để tìm nguyên nhân treo khi update
"""

import os
import sys
import time
import threading
import tempfile
import shutil

# Thêm thư mục hiện tại vào path
sys.path.insert(0, os.path.dirname(__file__))

from core.updater import Updater

def debug_update_process():
    """Debug từng bước của quá trình update"""
    print("🔍 DEBUG: Bắt đầu debug quá trình update...")
    
    # Tạo updater
    updater = Updater()
    updater.current_version = updater.get_current_version()
    
    print(f"📋 Version hiện tại: {updater.current_version}")
    print(f"📋 Update URL: {updater.update_server_url}")
    
    # Bước 1: Kiểm tra update
    print("\n🔍 BƯỚC 1: Kiểm tra update...")
    try:
        has_update, version, message = updater.check_for_updates()
        print(f"✅ Kết quả: has_update={has_update}, version={version}")
        print(f"📝 Message: {message}")
        
        if not has_update:
            print("ℹ️  Không có update để test")
            return
            
    except Exception as e:
        print(f"❌ Lỗi kiểm tra update: {e}")
        return
    
    # Bước 2: Test download (nếu có update)
    if has_update and updater.download_url:
        print(f"\n🔍 BƯỚC 2: Test download từ {updater.download_url}")
        try:
            def progress_callback(progress):
                print(f"📥 Download: {progress:.1f}%")
            
            downloaded_file = updater.download_update(progress_callback)
            print(f"✅ Download thành công: {downloaded_file}")
            print(f"📁 File size: {os.path.getsize(downloaded_file)} bytes")
            
            # Bước 3: Test apply update logic (không thực hiện thật)
            print(f"\n🔍 BƯỚC 3: Test apply update logic...")
            
            # Giả lập đường dẫn exe hiện tại
            if getattr(sys, 'frozen', False):
                current_exe_path = sys.executable
            else:
                current_exe_path = os.path.join(os.path.dirname(__file__), "ITM_Translate.exe")
            
            print(f"📍 Current exe path: {current_exe_path}")
            
            # Các đường dẫn liên quan
            new_exe_path = current_exe_path + ".new"
            backup_path = current_exe_path + ".backup"
            
            print(f"📍 New exe path: {new_exe_path}")
            print(f"📍 Backup path: {backup_path}")
            
            # Test copy file (không làm hỏng file gốc)
            print(f"\n🔧 Test copy file...")
            try:
                # Copy file tải về đến vị trí .new
                shutil.copy2(downloaded_file, new_exe_path)
                print(f"✅ Copy thành công đến {new_exe_path}")
                
                # Kiểm tra file
                if os.path.exists(new_exe_path):
                    size = os.path.getsize(new_exe_path)
                    print(f"✅ File .new đã tồn tại, size: {size} bytes")
                else:
                    print(f"❌ File .new không tồn tại")
                
                # Test tạo batch script
                print(f"\n🔧 Test tạo batch script...")
                
                batch_content = f'''@echo off
echo Starting update process...
timeout /t 2 /nobreak >nul
echo Replacing executable...
if exist "{new_exe_path}" (
    echo Deleting old executable...
    del "{current_exe_path}" >nul 2>&1
    echo Renaming new executable...
    ren "{new_exe_path}" "{os.path.basename(current_exe_path)}" >nul 2>&1
    echo Cleaning up backup...
    if exist "{backup_path}" del "{backup_path}" >nul 2>&1
    echo Update completed!
) else (
    echo ERROR: New executable not found!
)
echo Starting application...
start "" "{current_exe_path}"
echo Cleaning up batch file...
del "%~f0" >nul 2>&1
'''
                
                batch_path = os.path.join(os.path.dirname(current_exe_path), "debug_update_restart.bat")
                with open(batch_path, 'w', encoding='utf-8') as f:
                    f.write(batch_content)
                
                print(f"✅ Batch script tạo thành công: {batch_path}")
                print(f"📝 Nội dung script:")
                print(batch_content)
                
                # Cleanup test files
                print(f"\n🧹 Cleanup test files...")
                if os.path.exists(new_exe_path):
                    os.remove(new_exe_path)
                    print(f"✅ Đã xóa {new_exe_path}")
                
                if os.path.exists(batch_path):
                    os.remove(batch_path)
                    print(f"✅ Đã xóa {batch_path}")
                
                print(f"✅ Test apply update logic thành công!")
                
            except Exception as e:
                print(f"❌ Lỗi trong apply update logic: {e}")
                import traceback
                traceback.print_exc()
            
            # Cleanup downloaded file
            if updater.temp_dir and os.path.exists(updater.temp_dir):
                shutil.rmtree(updater.temp_dir, ignore_errors=True)
                print(f"🧹 Đã cleanup temp directory")
                
        except Exception as e:
            print(f"❌ Lỗi download: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎉 Debug hoàn tất!")

def test_file_locking():
    """Test xem có vấn đề file locking không"""
    print(f"\n🔍 TEST: File locking issues...")
    
    # Tạo file test
    test_file = os.path.join(tempfile.gettempdir(), "test_file_lock.txt")
    
    try:
        # Tạo file
        with open(test_file, 'w') as f:
            f.write("test content")
        
        print(f"✅ Tạo file test: {test_file}")
        
        # Test copy đè lên chính nó
        new_content = "new test content"
        temp_new = test_file + ".new"
        
        with open(temp_new, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Tạo file .new: {temp_new}")
        
        # Test replace
        backup = test_file + ".backup"
        shutil.copy2(test_file, backup)
        print(f"✅ Tạo backup: {backup}")
        
        # Replace (giống như update process)
        os.remove(test_file)
        os.rename(temp_new, test_file)
        print(f"✅ Replace file thành công")
        
        # Verify
        with open(test_file, 'r') as f:
            content = f.read()
        
        if content == new_content:
            print(f"✅ File replace hoạt động chính xác")
        else:
            print(f"❌ File replace không hoạt động đúng")
        
        # Cleanup
        for f in [test_file, backup]:
            if os.path.exists(f):
                os.remove(f)
        
        print(f"✅ Test file locking - OK")
        
    except Exception as e:
        print(f"❌ Lỗi test file locking: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_update_process()
    test_file_locking()
