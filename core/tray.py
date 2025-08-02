import pystray
from PIL import Image, ImageDraw
import threading
import os
import sys
import queue
from core.i18n import get_language_manager, _

# Import Windows API cho tray handling
try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
    print("✅ Windows API available for tray handling")
except ImportError:
    WIN32_AVAILABLE = False
    print("⚠️ Windows API not available, using fallback")

def get_app_version():
    """Đọc version từ file version.json"""
    try:
        import json
        # Thử đọc từ thư mục gốc trước
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        version_file = os.path.join(base_path, "version.json")
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', '1.0.0')
        
        # Thử đọc từ core/version.json
        core_version_file = os.path.join(os.path.dirname(__file__), "version.json")
        if os.path.exists(core_version_file):
            with open(core_version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', '1.0.0')
    except Exception:
        pass
    return '1.0.0'

def resource_path(relative_path):
    # Lấy đường dẫn thực tế tới resource, hỗ trợ cả khi đóng gói bằng PyInstaller
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # Lấy thư mục gốc project (1 cấp trên)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def create_image(floating_button_enabled=False):
    # Chọn icon dựa trên trạng thái floating button
    icon_name = 'icon_ON.ico' if floating_button_enabled else 'icon_OFF.ico'
    icon_path = resource_path(os.path.join('Resource', icon_name))
    
    if os.path.exists(icon_path):
        return Image.open(icon_path)
    
    # Tạo icon mặc định dựa trên trạng thái
    img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    if floating_button_enabled:
        # Icon ON: màu xanh dương sáng
        draw.ellipse((4, 4, 28, 28), fill=(30, 144, 255, 255))
        draw.text((10, 8), "T", fill=(255,255,255,255))
    else:
        # Icon OFF: màu xám
        draw.ellipse((4, 4, 28, 28), fill=(128, 128, 128, 255))
        draw.text((10, 8), "T", fill=(255,255,255,255))
    
    return img

def load_floating_button_enabled():
    """Load trạng thái floating button từ startup.json"""
    try:
        import json
        startup_file = "startup.json"
        if os.path.exists(startup_file):
            with open(startup_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("floating_button", False))
    except Exception:
        pass
    return False

def load_auto_close_popup_enabled():
    """Load trạng thái auto close popup từ startup.json"""
    try:
        import json
        startup_file = "startup.json"
        if os.path.exists(startup_file):
            with open(startup_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("auto_close_popup", True))  # Mặc định bật
    except Exception:
        pass
    return True  # Mặc định bật

def create_tray_icon(root, app):
    # Biến để track trạng thái floating button và auto close popup
    floating_button_enabled = load_floating_button_enabled()
    auto_close_popup_enabled = load_auto_close_popup_enabled()
    
    # Queue để communicate giữa Windows API callback và main thread
    tray_action_queue = queue.Queue()
    
    def process_tray_actions():
        """Xử lý actions từ Windows API trong main thread"""
        try:
            while True:
                action = tray_action_queue.get_nowait()
                if action == 'toggle_floating':
                    toggle_floating_button()
                elif action == 'toggle_auto_close_popup':
                    toggle_auto_close_popup()
                elif action == 'show_window':
                    on_show()
                elif action == 'exit':
                    on_quit()
        except queue.Empty:
            pass
        # Schedule lại sau 50ms
        root.after(50, process_tray_actions)
    
    # Bắt đầu xử lý actions
    root.after(100, process_tray_actions)
    
    def save_floating_button_enabled(enabled):
        """Lưu trạng thái floating button vào startup.json"""
        try:
            import json
            startup_file = "startup.json"
            data = {}
            if os.path.exists(startup_file):
                with open(startup_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            data["floating_button"] = enabled
            
            with open(startup_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 Saved floating button state: {enabled}")
        except Exception as e:
            print(f"❌ Error saving floating button state: {e}")

    def save_auto_close_popup_enabled(enabled):
        """Lưu trạng thái auto close popup vào startup.json"""
        try:
            import json
            startup_file = "startup.json"
            data = {}
            if os.path.exists(startup_file):
                with open(startup_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            data["auto_close_popup"] = enabled
            
            with open(startup_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 Saved auto close popup state: {enabled}")
        except Exception as e:
            print(f"❌ Error saving auto close popup state: {e}")

    def update_tray_icon():
        """Cập nhật icon của tray dựa trên trạng thái floating button và auto close popup"""
        nonlocal icon, floating_button_enabled, auto_close_popup_enabled
        try:
            # Reload trạng thái mới nhất từ file (cho trường hợp GUI thay đổi)
            floating_button_enabled = load_floating_button_enabled()
            auto_close_popup_enabled = load_auto_close_popup_enabled()
            
            new_image = create_image(floating_button_enabled)
            icon.icon = new_image
            
            # Tạo menu mới với tất cả handlers (bao gồm cả hidden menu item cho left-click)
            new_menu = pystray.Menu(
                # Hidden default item cho left-click compatibility
                pystray.MenuItem("Toggle Floating Button", on_left_click, default=True, visible=False),
                # Menu items hiển thị
                pystray.MenuItem(
                    f"{'✅' if floating_button_enabled else '🟩'} {_('floating_button_toggle')}", 
                    menu_toggle_floating
                ),
                pystray.MenuItem(
                    f"{'✅' if auto_close_popup_enabled else '🟩'} {_('auto_close_popup')}", 
                    menu_toggle_auto_close_popup
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(_('tray_show_window'), menu_show_window),
                pystray.MenuItem(_('tray_exit'), menu_exit)
            )
            
            # Cập nhật menu
            icon.menu = new_menu
            
            # Đảm bảo left-click handler vẫn hoạt động sau khi cập nhật menu
            try:
                # Re-assign default action
                icon.default_action = on_left_click
                print("✅ Left-click handler re-assigned after menu update")
            except Exception as e:
                print(f"⚠️ Could not re-assign left-click handler: {e}")
            
            print(f"🔄 Tray icon and menu updated: floating_button_enabled = {floating_button_enabled}, auto_close_popup_enabled = {auto_close_popup_enabled}")
        except Exception as e:
            print(f"❌ Error updating tray icon: {e}")

    def toggle_floating_button():
        """Toggle trạng thái floating button"""
        nonlocal floating_button_enabled
        floating_button_enabled = not floating_button_enabled
        
        # Lưu trạng thái mới
        save_floating_button_enabled(floating_button_enabled)
        
        # Cập nhật icon
        update_tray_icon()
        
        # Gọi callback để cập nhật chức năng floating button
        try:
            # Import từ ITM_Translate.py để gọi function set_floating_button_enabled
            import sys
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, 'set_floating_button_enabled'):
                main_module.set_floating_button_enabled(floating_button_enabled)
            
            # Cập nhật GUI nếu có
            if hasattr(app, 'floating_button_enabled') and app.floating_button_enabled:
                root.after(0, lambda: app.floating_button_enabled.set(floating_button_enabled))
                
            print(f"🖱️ Floating button toggled: {floating_button_enabled}")
        except Exception as e:
            print(f"❌ Error toggling floating button: {e}")

    def toggle_auto_close_popup():
        """Toggle trạng thái auto close popup"""
        nonlocal auto_close_popup_enabled
        auto_close_popup_enabled = not auto_close_popup_enabled
        
        # Lưu trạng thái mới
        save_auto_close_popup_enabled(auto_close_popup_enabled)
        
        # Cập nhật icon (menu sẽ được update)
        update_tray_icon()
        
        # Gọi callback để cập nhật chức năng auto close popup
        try:
            # Cập nhật GUI nếu có
            if hasattr(app, 'auto_close_popup_var') and app.auto_close_popup_var:
                root.after(0, lambda: app.auto_close_popup_var.set(auto_close_popup_enabled))
            
            # Import function save_auto_close_popup từ ITM_Translate.py nếu có
            import sys
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, 'save_auto_close_popup'):
                main_module.save_auto_close_popup(auto_close_popup_enabled)
                
            print(f"🖱️ Auto close popup toggled: {auto_close_popup_enabled}")
        except Exception as e:
            print(f"❌ Error toggling auto close popup: {e}")

    def on_show():
        """Hiện cửa sổ chính"""
        try:
            root.after(0, lambda: (root.deiconify(), root.lift(), root.focus_force()))
            print("Tray: Show window triggered")
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

    # Tạo tray icon với trạng thái hiện tại
    app_version = get_app_version()
    
    # Left-click handler đơn giản cho pystray
    def on_left_click(icon, item):
        """Xử lý left-click - Toggle floating button"""
        print("🖱️ Tray: Left-click detected - Toggling floating button")
        tray_action_queue.put('toggle_floating')

    # Menu items với click handlers
    def menu_toggle_floating():
        """Menu item để toggle floating button"""
        print("📋 Tray Menu: Toggle floating button clicked")
        tray_action_queue.put('toggle_floating')
    
    def menu_toggle_auto_close_popup():
        """Menu item để toggle auto close popup"""
        print("📋 Tray Menu: Toggle auto close popup clicked")
        tray_action_queue.put('toggle_auto_close_popup')
    
    def menu_show_window():
        """Menu item để hiện cửa sổ"""
        print("📋 Tray Menu: Show window clicked")
        tray_action_queue.put('show_window')
    
    def menu_exit():
        """Menu item để thoát"""
        print("📋 Tray Menu: Exit clicked")
        tray_action_queue.put('exit')
    
    icon = pystray.Icon(
        f'ITM Translate v{app_version}', 
        create_image(floating_button_enabled), 
        menu=pystray.Menu(
            # Hidden default item cho left-click compatibility
            pystray.MenuItem("Toggle Floating Button", on_left_click, default=True, visible=False),
            # Menu items hiển thị
            pystray.MenuItem(
                f"{'✅' if floating_button_enabled else '🟩'} {_('floating_button_toggle')}", 
                menu_toggle_floating
            ),
            pystray.MenuItem(
                f"{'✅' if auto_close_popup_enabled else '🟩'} {_('auto_close_popup')}", 
                menu_toggle_auto_close_popup
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(_('tray_show_window'), menu_show_window),
            pystray.MenuItem(_('tray_exit'), menu_exit)
        )
    )
    
    # Thử nhiều cách gán left-click handler
    try:
        # Method 1: default_action
        icon.default_action = on_left_click
        print("✅ Method 1: default_action assigned")
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    try:
        # Method 2: Thêm menu item ẩn cho left-click
        # Một số version pystray cần menu item đầu tiên làm default action
        original_menu = icon.menu
        icon.menu = pystray.Menu(
            pystray.MenuItem("Toggle Floating Button", on_left_click, default=True, visible=False),
            *original_menu
        )
        print("✅ Method 2: Hidden default menu item added")
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    # Chạy tray icon trong thread riêng
    threading.Thread(target=icon.run, daemon=True).start()
    
    # Khi đóng cửa sổ, ẩn thay vì thoát
    def on_window_close():
        print("Tray: Window closing, minimizing to tray")
        root.withdraw()
    
    root.protocol('WM_DELETE_WINDOW', on_window_close)
    
    # Tạo wrapper object để expose update_tray_icon method
    class TrayWrapper:
        def __init__(self, icon, update_func):
            self.icon = icon
            self.update_tray_icon = update_func
            
        def stop(self):
            """Delegate stop method to icon"""
            return self.icon.stop()
            
        def __getattr__(self, name):
            """Delegate other attributes to icon"""
            return getattr(self.icon, name)
    
    return TrayWrapper(icon, update_tray_icon)
