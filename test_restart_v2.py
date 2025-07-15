#!/usr/bin/env python3
"""
Test script để verify logic restart mới
"""
import sys
import os

# Add current directory to path để import được modules
sys.path.insert(0, os.path.dirname(__file__))

from ui.gui import MainGUI
import tkinter as tk

def test_restart_batch_creation():
    """Test tạo restart batch file"""
    print("🧪 Testing new restart batch logic...")
    
    # Tạo mock root window
    root = tk.Tk()
    root.withdraw()  # Hide window
    
    # Tạo MainGUI instance
    gui = MainGUI(root)
    
    try:
        # Test tạo restart batch file
        batch_path = gui._create_restart_batch()
        
        if os.path.exists(batch_path):
            print(f"✅ Restart batch file created successfully: {batch_path}")
            
            # Đọc và hiển thị nội dung
            with open(batch_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("\n📄 Batch file content preview:")
            print("=" * 60)
            lines = content.split('\n')
            for i, line in enumerate(lines[:15]):  # Show first 15 lines
                print(f"{i+1:2}: {line}")
            if len(lines) > 15:
                print("...")
                print(f"Total {len(lines)} lines")
            print("=" * 60)
            
            # Cleanup
            os.remove(batch_path)
            print("🧹 Test batch file cleaned up")
            
            return True
        else:
            print("❌ Restart batch file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        root.destroy()

def test_restart_flow():
    """Test toàn bộ restart flow (nhưng không thực sự restart)"""
    print("\n🧪 Testing complete restart flow (simulation)...")
    
    root = tk.Tk()
    root.withdraw()
    
    gui = MainGUI(root)
    
    try:
        # Test step 1: Create batch
        print("Step 1: Creating restart batch...")
        batch_path = gui._create_restart_batch()
        print(f"✅ Batch created: {batch_path}")
        
        # Test step 2: Verify batch exists for admin execution
        print("Step 2: Verifying batch for admin execution...")
        if os.path.exists(batch_path):
            print("✅ Batch file exists and ready for admin execution")
            
            # Simulate step 3 (không thực sự run với admin)
            print("Step 3: [SIMULATION] Would run with admin privileges")
            print("Step 4: [SIMULATION] Would exit application")
            print("✅ Restart flow simulation completed successfully")
            
            # Cleanup
            os.remove(batch_path)
            print("🧹 Test batch file cleaned up")
            
            return True
        else:
            print("❌ Batch file not found for admin execution")
            return False
            
    except Exception as e:
        print(f"❌ Error in restart flow test: {e}")
        return False
    
    finally:
        root.destroy()

if __name__ == "__main__":
    print("🚀 ITM Translate - Restart Logic Test")
    print("=" * 50)
    
    # Test 1: Batch creation
    success1 = test_restart_batch_creation()
    
    # Test 2: Complete flow simulation
    success2 = test_restart_flow()
    
    print("\n📊 Test Results:")
    print(f"├─ Batch Creation: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"├─ Restart Flow: {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"└─ Overall: {'✅ ALL TESTS PASSED' if success1 and success2 else '❌ SOME TESTS FAILED'}")
    
    print("\n✅ Test completed!")
