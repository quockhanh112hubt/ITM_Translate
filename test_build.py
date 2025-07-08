#!/usr/bin/env python3
"""
Test script để kiểm tra build output
"""
import os
import sys
import subprocess
import time

def test_build_output():
    """Test executable được build có hoạt động không"""
    print("Testing Build Output...")
    print("=" * 40)
    
    # Tìm file executable
    exe_paths = [
        "dist/ITM_Translate.exe",
        "dist/ITM_Translate/ITM_Translate.exe",
        "dist/ITM_Translate"
    ]
    
    exe_path = None
    for path in exe_paths:
        if os.path.exists(path):
            exe_path = path
            break
    
    if not exe_path:
        print("❌ ERROR: Không tìm thấy file executable!")
        print("Các đường dẫn đã kiểm tra:")
        for path in exe_paths:
            print(f"  - {path}")
        return False
    
    print(f"✅ Tìm thấy executable: {exe_path}")
    
    # Kiểm tra kích thước file
    file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
    print(f"📊 Kích thước file: {file_size:.1f} MB")
    
    if file_size < 10:
        print("⚠️  WARNING: File có vẻ nhỏ, có thể thiếu dependencies")
    elif file_size > 200:
        print("⚠️  WARNING: File khá lớn, có thể cần optimize")
    else:
        print("✅ Kích thước file hợp lý")
    
    # Test chạy executable (timeout 10s)
    print("\n🧪 Testing executable startup...")
    try:
        # Chạy với timeout để tránh hang
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait 5 seconds để app khởi động
        time.sleep(5)
        
        # Kiểm tra process còn chạy không
        if process.poll() is None:
            print("✅ Executable khởi động thành công!")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ Executable crash khi khởi động!")
            if stderr:
                print(f"Error: {stderr.decode('utf-8', errors='ignore')}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi test executable: {e}")
        return False

def check_dependencies():
    """Kiểm tra các file dependencies cần thiết"""
    print("\n📦 Checking Dependencies...")
    print("=" * 40)
    
    required_files = [
        "version.json",
        "config.json",
        "Resource/icon.ico",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Thiếu {len(missing_files)} file(s) cần thiết!")
        return False
    else:
        print("\n✅ Tất cả dependencies đều có")
        return True

def main():
    print("ITM Translate - Build Test")
    print("=" * 50)
    
    deps_ok = check_dependencies()
    build_ok = test_build_output()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Dependencies: {'✅ OK' if deps_ok else '❌ FAIL'}")
    print(f"Build Output: {'✅ OK' if build_ok else '❌ FAIL'}")
    
    if deps_ok and build_ok:
        print("\n🎉 Build test PASSED! Sẵn sàng để release.")
        return 0
    else:
        print("\n❌ Build test FAILED! Cần sửa lỗi trước khi release.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
