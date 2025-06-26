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
    # Sử dụng icon từ file Resource/icon.png, nếu không có thì tạo icon mặc định
    icon_path = resource_path(os.path.join('Resource', 'icon.png'))
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
        on_show()
    icon = pystray.Icon('ITM Translate', create_image(), menu=pystray.Menu(
        pystray.MenuItem('Hiện cửa sổ', on_show),
        pystray.MenuItem('Thoát', on_quit)
    ))
    icon._on_double_click = on_tray_double_click
    def setup_icon_events():
        # Monkey patch _on_notify để bắt double-click trên Windows
        def patch_notify(obj):
            if hasattr(obj, "__call__"):
                orig = obj
                def custom(hwnd, msg, wparam, lparam):
                    if msg == 0x203:  # WM_LBUTTONDBLCLK
                        icon._on_double_click(icon)
                    return orig(hwnd, msg, wparam, lparam)
                return custom
            return obj
        # Patch _on_notify
        if hasattr(icon, "_on_notify"):
            icon._on_notify = patch_notify(icon._on_notify)
        # Patch _listener.on_notify nếu có
        if hasattr(icon, "_listener") and hasattr(icon._listener, "on_notify"):
            icon._listener.on_notify = patch_notify(icon._listener.on_notify)
    def run():
        setup_icon_events()
        icon.run()
    threading.Thread(target=run, daemon=True).start()
    root.protocol('WM_DELETE_WINDOW', lambda: root.withdraw())
    return icon
