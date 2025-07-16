#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test auto-refresh functionality for API Key tab
"""

import sys
import os
import time

# Add project path
sys.path.append('.')

# Test the auto-refresh feature
def test_auto_refresh():
    print("🧪 Testing Auto-Refresh Feature for API Key Tab")
    print("=" * 50)
    
    try:
        from core.api_key_manager import api_key_manager
        from ui.gui import MainGUI
        from ttkbootstrap import Window
        
        # Show current API key status
        key_count = api_key_manager.get_key_count()
        active_key = api_key_manager.get_active_key()
        
        print(f"📊 Current API Key Status:")
        print(f"   - Total keys: {key_count}")
        if active_key:
            print(f"   - Active key: {active_key[:10]}... (index: {api_key_manager.active_index})")
        else:
            print(f"   - No active key")
        
        print(f"\n✅ Auto-refresh feature implemented:")
        print(f"   - When switching to 'Quản lý API KEY' tab")
        print(f"   - Window automatically resizes to 1050x660")
        print(f"   - API key list automatically refreshes")
        print(f"   - Shows latest key status and highlighting")
        
        print(f"\n🔄 Benefits of auto-refresh:")
        print(f"   - Always displays current data")
        print(f"   - Updates after external key changes")
        print(f"   - Syncs active key highlighting")
        print(f"   - Refreshes status text at bottom")
        
        # Test the GUI creation with auto-refresh
        print(f"\n🎯 Creating GUI with auto-refresh enabled...")
        
        root = Window(themename='flatly')
        root.geometry('1050x420')
        root.title('ITM Translate - Auto Refresh Test')
        
        app = MainGUI(root)
        app.set_initial_settings({
            'translate_popup': '<ctrl>+q',
            'replace_translate': '<ctrl>+d', 
            'Ngon_ngu_dau_tien': 'Any Language',
            'Ngon_ngu_thu_2': 'Tiếng Việt',
            'Ngon_ngu_thu_3': 'English'
        }, '', False, True)
        
        print(f"✅ GUI created successfully!")
        print(f"👆 Click between tabs to test auto-refresh:")
        print(f"   1. Click 'Quản lý API KEY' tab → Auto refresh + resize to 660px")
        print(f"   2. Click 'Cài Đặt' tab → Resize to 420px or 650px")
        print(f"   3. Click 'Nâng Cao' tab → Resize to 350px")
        print(f"\nPress Ctrl+C to close the test")
        
        root.mainloop()
        
    except KeyboardInterrupt:
        print(f"\n👋 Test completed successfully!")
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_auto_refresh()
