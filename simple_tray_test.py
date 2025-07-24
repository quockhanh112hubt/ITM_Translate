#!/usr/bin/env python3
"""
Simple test để test tray icon click functionality
"""
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    import pystray
    from pystray import mouse
    from PIL import Image, ImageDraw
    import threading
    
    def create_test_image():
        """Tạo icon test đơn giản"""
        img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((4, 4, 28, 28), fill=(30, 144, 255, 255))
        draw.text((10, 8), "T", fill=(255,255,255,255))
        return img

    def on_click(icon, button, time):
        """Test click handler"""
        if button == mouse.Button.left:
            print("✅ LEFT CLICK DETECTED! Function works!")
        elif button == mouse.Button.right:
            print("✅ RIGHT CLICK DETECTED! Menu will show!")

    def on_menu_test():
        print("✅ MENU TEST CLICKED! Menu works!")

    def on_exit():
        print("🛑 Exit clicked")
        icon.stop()

    print("🧪 Testing simple tray icon click...")
    print("📋 Instructions:")
    print("   • Left-click: Should print 'LEFT CLICK DETECTED!'")
    print("   • Right-click: Should show menu")
    print("   • Menu 'Test': Should print 'MENU TEST CLICKED!'")
    print("")

    # Tạo icon với menu đơn giản
    icon = pystray.Icon(
        'Test Tray',
        create_test_image(),
        menu=pystray.Menu(
            pystray.MenuItem('Test Click', on_menu_test),
            pystray.MenuItem('Exit', on_exit)
        )
    )

    # Gán click handler
    icon.on_click = on_click

    print("🚀 Starting tray icon test...")
    print("⏱️  Test will run for 30 seconds or until you click Exit")
    
    # Auto-stop sau 30 giây
    def auto_stop():
        time.sleep(30)
        print("⏰ Auto-stopping test...")
        icon.stop()
    
    threading.Thread(target=auto_stop, daemon=True).start()
    
    # Chạy icon
    icon.run()
    print("✅ Test completed!")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure you have pystray and PIL installed:")
    print("pip install pystray pillow")
