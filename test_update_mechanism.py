#!/usr/bin/env python3
"""
Test update mechanism với file executable
"""
import os
import sys
import shutil
import tempfile
import subprocess
import time

def create_test_environment():
    """Tạo môi trường test với file exe cũ"""
    print("🧪 Tạo môi trường test...")
    
    # Tạo thư mục test tạm thời
    test_dir = tempfile.mkdtemp(prefix="itm_update_test_")
    print(f"📁 Test directory: {test_dir}")
    
    # Copy file exe hiện tại vào test dir
    current_exe = "dist/ITM_Translate.exe"
    if not os.path.exists(current_exe):
        print("❌ Không tìm thấy dist/ITM_Translate.exe")
        return None
    
    test_exe = os.path.join(test_dir, "ITM_Translate.exe")
    shutil.copy2(current_exe, test_exe)
    
    # Copy config và version files
    for file in ["config.json", "version.json"]:
        if os.path.exists(file):
            shutil.copy2(file, test_dir)
    
    # Copy Resource folder
    if os.path.exists("Resource"):
        shutil.copytree("Resource", os.path.join(test_dir, "Resource"))
    
    print(f"✅ Test environment ready: {test_exe}")
    return test_dir, test_exe

def simulate_old_version(test_dir):
    """Giả lập version cũ trong test environment"""
    version_file = os.path.join(test_dir, "version.json")
    
    # Tạo version cũ
    old_version_data = {
        "version": "1.0.0",
        "build": "2025010100",
        "release_date": "2025-01-01",
        "description": "Test old version"
    }
    
    import json
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(old_version_data, f, indent=4, ensure_ascii=False)
    
    print("📝 Đã set version thành 1.0.0 (để test update)")

def test_update_mechanism():
    """Test update mechanism"""
    print("\n" + "="*50)
    print("🚀 TEST UPDATE MECHANISM")
    print("="*50)
    
    # Tạo test environment
    result = create_test_environment()
    if not result:
        return False
    
    test_dir, test_exe = result
    
    try:
        # Simulate old version
        simulate_old_version(test_dir)
        
        # Chạy test executable
        print(f"\n🎮 Chạy test executable...")
        print(f"Path: {test_exe}")
        print("💡 Hướng dẫn test:")
        print("1. Chương trình sẽ mở với version 1.0.0")
        print("2. Vào tab 'Nâng Cao' → Click 'Cập nhật chương trình'")
        print("3. Kiểm tra có detect được version 1.0.4")
        print("4. Test download và install process")
        print("5. Kiểm tra restart mechanism")
        
        # Start executable
        process = subprocess.Popen([test_exe], cwd=test_dir)
        
        print(f"\n⏳ Test executable đang chạy (PID: {process.pid})")
        print("📋 Nhấn Enter sau khi test xong để cleanup...")
        input()
        
        # Cleanup
        try:
            process.terminate()
            process.wait(timeout=5)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup test directory
        try:
            shutil.rmtree(test_dir, ignore_errors=True)
            print(f"🧹 Cleaned up test directory")
        except Exception:
            print(f"⚠️  Could not cleanup {test_dir}")

def test_update_logic_only():
    """Test chỉ logic update, không chạy GUI"""
    print("\n" + "="*50)
    print("🔧 TEST UPDATE LOGIC ONLY")
    print("="*50)
    
    try:
        from core.updater import Updater
        
        # Test với version cũ
        updater = Updater()
        updater.current_version = "1.0.0"
        
        print(f"📋 Current version: {updater.current_version}")
        print(f"🌐 Update URL: {updater.update_server_url}")
        
        # Check for updates
        has_update, version, message = updater.check_for_updates()
        
        print(f"\n✅ Update check results:")
        print(f"Has update: {has_update}")
        print(f"New version: {version}")
        print(f"Message: {message[:100]}..." if len(message) > 100 else f"Message: {message}")
        
        if has_update:
            print(f"📥 Download URL: {updater.download_url}")
            return True
        else:
            print("ℹ️  No update available")
            return False
            
    except Exception as e:
        print(f"❌ Logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("ITM Translate - Update Mechanism Test")
    print("=" * 50)
    
    # Test logic trước
    logic_ok = test_update_logic_only()
    
    if logic_ok:
        print("\n🎯 Logic test PASSED!")
        
        choice = input("\nBạn có muốn test GUI update mechanism? (y/N): ")
        if choice.lower() == 'y':
            gui_ok = test_update_mechanism()
            if gui_ok:
                print("\n🎉 ALL TESTS PASSED!")
            else:
                print("\n❌ GUI test failed")
        else:
            print("\n✅ Logic test completed successfully")
    else:
        print("\n❌ Logic test failed - không thể tiếp tục")
