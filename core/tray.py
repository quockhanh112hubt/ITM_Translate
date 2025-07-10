import pystray
from PIL import Image, ImageDraw
import threading
import os
import sys

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
        root.after(0, lambda: (root.deiconify(), root.lift()))
    
    def on_quit():
        root.after(0, root.destroy)
        icon.stop()
        try:
            from lockfile import release_lock
            release_lock()
        except Exception:
            pass
        os._exit(0)
    
    def on_tray_double_click(icon, item=None):
        # Double-click sẽ hiện cửa sổ giống như menu "Hiện cửa sổ"
        on_show()
    
    # Tạo tray icon với menu
    icon = pystray.Icon('ITM Translate', create_image(), menu=pystray.Menu(
        pystray.MenuItem('Hiện cửa sổ', on_show),
        pystray.MenuItem('Thoát', on_quit)
    ))
    
    # Gán handler cho double-click
    icon.default_action = on_show  # Phương pháp đơn giản và reliable hơn
    
    def setup_icon_events():
        """Setup events cho tray icon, bao gồm double-click"""
        try:
            # Monkey patch để xử lý double-click trên Windows
            if hasattr(icon, "_listener") and hasattr(icon._listener, "_on_notify"):
                original_on_notify = icon._listener._on_notify
                
                def enhanced_on_notify(hwnd, msg, wparam, lparam):
                    # WM_LBUTTONDBLCLK = 0x203 (double-click chuột trái)
                    if msg == 0x203:
                        try:
                            on_tray_double_click(icon)
                        except Exception:
                            pass
                    # Gọi handler gốc
                    return original_on_notify(hwnd, msg, wparam, lparam)
                
                icon._listener._on_notify = enhanced_on_notify
        except Exception:
            # Nếu monkey patch thất bại, vẫn có default_action làm fallback
            pass
    
    def run():
        setup_icon_events()
        icon.run()
    
    # Chạy tray icon trong thread riêng
    threading.Thread(target=run, daemon=True).start()
    
    # Khi đóng cửa sổ, ẩn thay vì thoát
    root.protocol('WM_DELETE_WINDOW', lambda: root.withdraw())
    
    return icon
