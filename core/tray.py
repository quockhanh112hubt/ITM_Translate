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
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def create_image():
    # Sử dụng icon từ file Resource/translate.ico, nếu không có thì tạo icon mặc định
    icon_path = resource_path(os.path.join('Resource', 'translate.ico'))
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
        root.after(0, root.deiconify)
    def on_quit():
        root.after(0, root.destroy)
        icon.stop()
        os._exit(0)  # Đảm bảo thoát hoàn toàn process
    icon = pystray.Icon('ITM Translate', create_image(), menu=pystray.Menu(
        pystray.MenuItem('Hiện cửa sổ', on_show),
        pystray.MenuItem('Thoát', on_quit)
    ))
    def run():
        icon.run()
    threading.Thread(target=run, daemon=True).start()
    root.protocol('WM_DELETE_WINDOW', lambda: root.withdraw())
    return icon
