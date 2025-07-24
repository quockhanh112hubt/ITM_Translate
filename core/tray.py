import pystray
from pystray import mouse
from PIL import Image, ImageDraw
import threading
import os
import sys
from core.i18n import get_language_manager, _

# Import Windows GUI libraries for advanced tray handling
try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

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
    
    # Debug: in ra đường dẫn icon thực tế
    # print(f"Icon path: {icon_path} (floating_button_enabled: {floating_button_enabled})")
    
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
                return bool(data.get("floating_button", False))  # Mặc định tắt
    except Exception:
        pass
    return False  # Mặc định tắt

def create_tray_icon(root, app):
    # Biến để track trạng thái floating button
    floating_button_enabled = load_floating_button_enabled()
    
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

    def update_tray_icon():
        """Cập nhật icon của tray dựa trên trạng thái floating button"""
        nonlocal icon
        try:
            new_image = create_image(floating_button_enabled)
            icon.icon = new_image
            
            # Cập nhật menu
            icon.menu = pystray.Menu(
                pystray.MenuItem(
                    f"{'✅' if floating_button_enabled else '❌'} {_('floating_button_toggle')}", 
                    menu_toggle_floating
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(_('tray_show_window'), menu_show_window),
                pystray.MenuItem(_('tray_exit'), menu_exit)
            )
            
            print(f"🔄 Tray icon and menu updated: floating_button_enabled = {floating_button_enabled}")
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
        """Xử lý left-click - Toggle floating button"""
        print("🖱️ Tray: Single-click detected - Toggling floating button")
        try:
            toggle_floating_button()
        except Exception as e:
            print(f"❌ Tray: Error in on_left_click: {e}")
    
    def on_right_click(icon, item):
        """Xử lý right-click - Show menu"""
        print("🖱️ Tray: Right-click detected - Menu will show")
        # Menu sẽ tự động hiện, không cần xử lý gì thêm
    
    
    # Tạo tray icon với trạng thái hiện tại
    app_version = get_app_version()
    
    # Menu items với click handlers
    def menu_toggle_floating():
        """Menu item để toggle floating button"""
        print("📋 Tray Menu: Toggle floating button clicked")
        toggle_floating_button()
    
    def menu_show_window():
        """Menu item để hiện cửa sổ"""
        print("📋 Tray Menu: Show window clicked")
        on_show()
    
    def menu_exit():
        """Menu item để thoát"""
        print("📋 Tray Menu: Exit clicked")
        on_quit()
    
    icon = pystray.Icon(
        f'ITM Translate v{app_version}', 
        create_image(floating_button_enabled), 
        menu=pystray.Menu(
            pystray.MenuItem(
                f"{'✅' if floating_button_enabled else '❌'} {_('floating_button_toggle')}", 
                menu_toggle_floating
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(_('tray_show_window'), menu_show_window),
            pystray.MenuItem(_('tray_exit'), menu_exit)
        )
    )
    
    # Thêm click handler trực tiếp cho pystray
    def on_click(icon, button, time):
        """Handler cho click events của pystray"""
        if button == mouse.Button.left:
            print("🖱️ Tray: pystray left-click detected")
            try:
                toggle_floating_button()
            except Exception as e:
                print(f"❌ Tray: Error in pystray click handler: {e}")
    
    # Gán click handler
    try:
        icon.on_click = on_click
        print("✅ Tray: pystray click handler assigned")
    except Exception as e:
        print(f"⚠️ Tray: Could not assign pystray click handler: {e}")
    
    def setup_click_handlers():
        """Setup click handlers cho tray icon"""
        print("🔧 Tray: Setting up click handlers...")
        try:
            if WIN32_AVAILABLE:
                # Sử dụng Windows API để xử lý tray messages
                print("🔧 Tray: Setting up Windows API handlers")
                
                # Monkey patch pystray's message handling
                if hasattr(icon, '_listener') and hasattr(icon._listener, '_on_notify'):
                    original_on_notify = icon._listener._on_notify
                    
                    def enhanced_on_notify(hwnd, msg, wparam, lparam):
                        try:
                            # Chỉ xử lý single-click, bỏ double-click
                            if msg == 0x201:  # WM_LBUTTONDOWN
                                print("🖱️ Tray: Single-click message received via Windows API")
                                on_left_click(icon, None)
                                return 0
                            # Bỏ xử lý double-click để tránh conflict
                        except Exception as e:
                            print(f"❌ Tray: Error in enhanced_on_notify: {e}")
                        
                        # Gọi handler gốc
                        try:
                            return original_on_notify(hwnd, msg, wparam, lparam)
                        except Exception as e:
                            print(f"❌ Tray: Error in original_on_notify: {e}")
                            return 0
                    
                    icon._listener._on_notify = enhanced_on_notify
                    print("✅ Tray: Windows API handlers installed successfully")
                else:
                    print("⚠️ Tray: Could not find _listener._on_notify, using fallback")
            else:
                print("⚠️ Tray: Windows API not available, using fallback")
            
            # Default action cho single-click (fallback)
            def default_action(icon, item=None):
                """Default action khi click"""
                print("🖱️ Tray: Default action triggered - Toggling floating button")
                try:
                    toggle_floating_button()
                except Exception as e:
                    print(f"❌ Tray: Error in default_action: {e}")
            
            # Gán default action
            icon.default_action = default_action
            print("✅ Tray: Default action set")
            
        except Exception as e:
            print(f"❌ Tray: Error in setup_click_handlers: {e}")
            # Fallback minimal
            def minimal_fallback(icon, item=None):
                print("🖱️ Tray: Minimal fallback action - Toggling floating button")
                try:
                    toggle_floating_button()
                except Exception as e:
                    print(f"❌ Tray: Error in minimal fallback: {e}")
            icon.default_action = minimal_fallback
    
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
    
    # Thêm method để update icon từ external modules
    icon.update_floating_button_state = lambda enabled: (
        setattr(icon, '_floating_button_enabled', enabled),
        update_icon_and_menu(enabled)
    )
    
    def update_icon_and_menu(enabled):
        """Update both icon and menu for external calls"""
        try:
            # Update internal state
            nonlocal floating_button_enabled
            floating_button_enabled = enabled
            
            # Update icon
            icon.icon = create_image(enabled)
            
            # Update menu
            icon.menu = pystray.Menu(
                pystray.MenuItem(
                    f"{'✅' if enabled else '❌'} {_('floating_button_toggle')}", 
                    menu_toggle_floating
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(_('tray_show_window'), menu_show_window),
                pystray.MenuItem(_('tray_exit'), menu_exit)
            )
            
            print(f"🔄 External tray icon and menu update: floating_button_enabled = {enabled}")
        except Exception as e:
            print(f"❌ Error in external update: {e}")
    
    return icon
