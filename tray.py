import pystray
from PIL import Image
import threading
import os

def create_image():
    # Sử dụng icon từ file Resource/translate.ico
    icon_path = os.path.join(os.path.dirname(__file__), 'Resource', 'translate.ico')
    return Image.open(icon_path)

def create_tray_icon(root, app):
    def on_show():
        root.after(0, root.deiconify)
    def on_quit():
        root.after(0, root.destroy)
        icon.stop()
    icon = pystray.Icon('ITM Translate', create_image(), menu=pystray.Menu(
        pystray.MenuItem('Hiện cửa sổ', on_show),
        pystray.MenuItem('Thoát', on_quit)
    ))
    def run():
        icon.run()
    threading.Thread(target=run, daemon=True).start()
    root.protocol('WM_DELETE_WINDOW', lambda: root.withdraw())
    return icon
