import pystray
from PIL import Image, ImageDraw
import threading
import os
import sys

# Import Windows GUI libraries for advanced tray handling
try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

def resource_path(relative_path):
    # Lấy đường dẫn thực tế tới resource, hỗ trợ cả khi đóng gói bằng PyInstaller
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # Lấy thư mục gốc project (1 cấp trên)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def create_image():
    # Sử dụng icon từ file Resource/icon.ico, nếu không có thì tạo icon mặc định
    icon_path = resource_path(os.path.join('Resource', 'icon.ico'))
    # Debug: in ra đường dẫn icon thực tế
    # print("Icon path:", icon_path)
    if os.path.exists(icon_path):
        return Image.open(icon_path)
    # Tạo icon mặc định (32x32, hình tròn xanh dương)
    img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((4, 4, 28, 28), fill=(30, 144, 255, 255))  # Màu xanh dương
    draw.text((10, 8), "T", fill=(255,255,255,255))  # Chữ T trắng
    return img

def create_tray_icon(root, app):
    def on_show():
        """Hiện cửa sổ chính"""
        try:
            root.after(0, lambda: (root.deiconify(), root.lift(), root.focus_force()))
            print("Tray: Show window triggered")  # Debug log
        except Exception as e:
            print(f"Tray: Error showing window: {e}")
    
    def on_quit():
        """Thoát ứng dụng"""
        root.after(0, root.destroy)
        icon.stop()
        try:
            from lockfile import release_lock
            release_lock()
        except Exception:
            pass
        os._exit(0)
    
    def on_left_click(icon, item):
        """Xử lý left-click (single click)"""
        print("Tray: Left click detected")  # Debug log
        # Single click không làm gì, chỉ double-click mới mở cửa sổ
        pass
    
    def on_double_click(icon, item):
        """Xử lý double-click vào tray icon"""
        print("Tray: Double-click detected")  # Debug log
        on_show()
    
    # Tạo tray icon với menu
    icon = pystray.Icon('ITM Translate', create_image(), menu=pystray.Menu(
        pystray.MenuItem('Hiện cửa sổ', on_show, default=True),  # Đặt làm default action
        pystray.MenuItem('Thoát', on_quit)
    ))
    
    def setup_click_handlers():
        """Setup click handlers cho tray icon"""
        try:
            if WIN32_AVAILABLE:
                # Sử dụng Windows API để xử lý tray messages
                print("Tray: Setting up Windows API handlers")  # Debug log
                
                # Monkey patch pystray's message handling
                if hasattr(icon, '_listener') and hasattr(icon._listener, '_on_notify'):
                    original_on_notify = icon._listener._on_notify
                    
                    def enhanced_on_notify(hwnd, msg, wparam, lparam):
                        try:
                            # WM_LBUTTONDBLCLK = 0x203 (double-click chuột trái)
                            if msg == 0x203:
                                print("Tray: Double-click message received")  # Debug log
                                on_double_click(icon, None)
                                return 0
                            elif msg == 0x201:  # WM_LBUTTONDOWN
                                print("Tray: Single-click message received")  # Debug log
                                on_left_click(icon, None)
                                return 0
                        except Exception as e:
                            print(f"Tray: Error in enhanced_on_notify: {e}")
                        
                        # Gọi handler gốc
                        try:
                            return original_on_notify(hwnd, msg, wparam, lparam)
                        except Exception as e:
                            print(f"Tray: Error in original_on_notify: {e}")
                            return 0
                    
                    icon._listener._on_notify = enhanced_on_notify
                else:
                    print("Tray: Could not find _listener._on_notify")
            else:
                print("Tray: Windows API not available, using fallback")
            
            # Fallback: Sử dụng pystray's default action
            def default_action(icon):
                """Default action khi double-click"""
                print("Tray: Default action triggered")  # Debug log
                on_show()
            
            # Gán default action (luôn luôn có sẵn)
            icon.default_action = default_action
            print("Tray: Default action set")  # Debug log
            
        except Exception as e:
            print(f"Tray: Error in setup_click_handlers: {e}")
            # Fallback minimal
            icon.default_action = lambda icon: on_show()
    
    def run():
        """Chạy tray icon"""
        setup_click_handlers()
        print("Tray: Icon starting...")  # Debug log
        icon.run()
    
    # Chạy tray icon trong thread riêng
    threading.Thread(target=run, daemon=True).start()
    
    # Khi đóng cửa sổ, ẩn thay vì thoát
    def on_window_close():
        print("Tray: Window closing, minimizing to tray")  # Debug log
        root.withdraw()
    
    root.protocol('WM_DELETE_WINDOW', on_window_close)
    
    return icon
