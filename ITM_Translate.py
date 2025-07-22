import sys
import threading
import time
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController, Key
from core.translator import translate_text
from ui.popup import show_popup, show_loading_popup
import tkinter as tk
from ui.gui import MainGUI
from core.tray import create_tray_icon
from core.lockfile import acquire_lock, release_lock
import ctypes
import os
import json
import atexit
from ttkbootstrap import Window
import queue
from core.i18n import get_language_manager, _


acquire_lock()
atexit.register(release_lock)

# Patch os._exit để luôn gọi release_lock
import os as _os
_os_exit = _os._exit
def safe_exit(code=0):
    try:
        release_lock()
    except Exception:
        pass
    _os_exit(code)
_os._exit = safe_exit
# --- END LOCK FILE ---

kb = KeyboardController()

def set_system_cursor_wait():
    # Chỉ hỗ trợ Windows
    if sys.platform.startswith("win"):
        ctypes.windll.user32.LoadCursorW.restype = ctypes.c_void_p
        hcursor = ctypes.windll.user32.LoadCursorW(0, 32514)  # IDC_WAIT
        ctypes.windll.user32.SetSystemCursor(hcursor, 32512)  # OCR_NORMAL

def restore_system_cursor():
    if sys.platform.startswith("win"):
        ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, 0, 0)  # SPI_SETCURSORS

def get_clipboard():
    try:
        return root.clipboard_get()
    except Exception:
        return ''

def set_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()  # Đảm bảo clipboard được cập nhật

action_queue = queue.Queue()

def on_activate_translate():
    action_queue.put(('translate', 'group1'))

def on_activate_replace():
    action_queue.put(('replace', 'group1'))

def on_activate_translate2():
    action_queue.put(('translate', 'group2'))

def on_activate_replace2():
    action_queue.put(('replace', 'group2'))

def check_queue():
    try:
        while True:
            action = action_queue.get_nowait()
            if action[0] == 'translate':
                if len(action) > 1 and action[1] == 'group2':
                    _on_activate_translate_group2()
                else:
                    _on_activate_translate()
            elif action[0] == 'replace':
                if len(action) > 1 and action[1] == 'group2':
                    _on_activate_replace_group2()
                else:
                    _on_activate_replace()
    except queue.Empty:
        pass
    root.after(50, check_queue)

# --- Floating Translate Button Feature ---
floating_btn = None
floating_btn_timer = None
last_clipboard_text = ''
mouse_drag_start = None
is_dragging = False

def show_floating_translate_button(mouse_x, mouse_y):
    """Hiển thị nút dịch floating cạnh vị trí chuột"""
    global floating_btn, floating_btn_timer
    
    # Đóng nút cũ nếu có
    if floating_btn is not None:
        try:
            if floating_btn.winfo_exists():
                floating_btn.destroy()
        except:
            pass
        floating_btn = None
    
    # Tạo nút mới
    floating_btn = tk.Toplevel(root)
    floating_btn.overrideredirect(True)  # Không có title bar
    floating_btn.attributes('-topmost', True)  # Luôn ở trên cùng
    floating_btn.attributes('-alpha', 0.95)  # Hơi trong suốt
    
    # Đặt vị trí cạnh chuột (offset để không che text)
    floating_btn.geometry(f'+{mouse_x + 15}+{mouse_y + 10}')
    
    # Styling cho nút
    floating_btn.configure(bg='#1976d2')
    
    # Nút dịch với icon và text
    btn = tk.Button(floating_btn, 
                   text=_('translate_button'), 
                   font=('Segoe UI', 9, 'bold'), 
                   bg='#1976d2', 
                   fg='white',
                   relief='flat', 
                   padx=8, 
                   pady=3, 
                   cursor='hand2',
                   border=0,
                   command=lambda: on_floating_translate_click())
    btn.pack()
    
    # Hover effects
    def on_enter(e):
        btn.configure(bg='#1565c0')
    
    def on_leave(e):
        btn.configure(bg='#1976d2')
    
    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)
    
    # Auto hide sau 5 giây
    if floating_btn_timer:
        root.after_cancel(floating_btn_timer)
    floating_btn_timer = root.after(5000, hide_floating_button)
    
    # Hide khi click ra ngoài (lose focus)
    def on_focus_out(event):
        # Delay một chút để tránh hide ngay khi click vào nút
        root.after(100, hide_floating_button)
    
    floating_btn.bind('<FocusOut>', on_focus_out)
    
    # Focus để có thể nhận FocusOut event
    try:
        floating_btn.focus_force()
    except:
        pass

def hide_floating_button():
    """Ẩn nút floating"""
    global floating_btn, floating_btn_timer
    
    if floating_btn_timer:
        root.after_cancel(floating_btn_timer)
        floating_btn_timer = None
    
    if floating_btn is not None:
        try:
            if floating_btn.winfo_exists():
                floating_btn.destroy()
        except:
            pass
        floating_btn = None

def on_floating_translate_click():
    """Xử lý khi click vào nút floating translate"""
    hide_floating_button()  # Ẩn nút trước
    # Trigger translate như Ctrl+Q
    action_queue.put(('translate', 'group1'))
    print("🖱️ [FLOATING] Translation triggered from floating button")

def on_mouse_click(x, y, button, pressed):
    """Xử lý mouse click events"""
    global mouse_drag_start, is_dragging
    
    if button == mouse.Button.left:
        if pressed:
            # Bắt đầu có thể drag (select text)
            mouse_drag_start = (x, y)
            is_dragging = False
        else:
            # Kết thúc click/drag
            if mouse_drag_start and is_dragging:
                # Đã drag (select text), check clipboard sau một chút
                root.after(200, lambda: check_for_new_selection(x, y))
            
            mouse_drag_start = None
            is_dragging = False

def on_mouse_move(x, y):
    """Xử lý mouse move events"""
    global mouse_drag_start, is_dragging
    
    if mouse_drag_start:
        # Tính khoảng cách drag
        dx = abs(x - mouse_drag_start[0])
        dy = abs(y - mouse_drag_start[1])
        
        # Nếu drag đủ xa (> 10 pixels) thì coi là đang select text
        if dx > 10 or dy > 10:
            is_dragging = True

def check_for_new_selection(mouse_x, mouse_y):
    """Kiểm tra xem có text mới được select không"""
    global last_clipboard_text
    
    try:
        # Copy text đã select (simulate Ctrl+C)
        kb.press(Key.ctrl)
        kb.press('c')
        kb.release('c')
        kb.release(Key.ctrl)
        
        # Đợi clipboard update
        time.sleep(0.1)
        
        current_text = get_clipboard()
        
        # Nếu có text mới và khác text trước đó
        if current_text and current_text.strip() and current_text != last_clipboard_text:
            last_clipboard_text = current_text
            # Hiển thị floating button
            show_floating_translate_button(mouse_x, mouse_y)
            print(f"🖱️ [FLOATING] New text selected: {current_text[:30]}...")
            
    except Exception as e:
        print(f"❌ [FLOATING] Error checking selection: {e}")

# Khởi tạo mouse listener
mouse_listener = mouse.Listener(
    on_click=on_mouse_click,
    on_move=on_mouse_move
)

def start_mouse_listener():
    """Khởi tạo và bắt đầu mouse listener"""
    global mouse_listener
    if mouse_listener is None or not mouse_listener.running:
        mouse_listener = mouse.Listener(
            on_click=on_mouse_click,
            on_move=on_mouse_move
        )
        mouse_listener.start()

def load_language_settings_from_file():
    if os.path.exists(HOTKEYS_FILE):
        try:
            with open(HOTKEYS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k in ['Ngon_ngu_dau_tien', 'Ngon_ngu_thu_2', 'Ngon_ngu_thu_3', 'Nhom2_Ngon_ngu_dau_tien', 'Nhom2_Ngon_ngu_thu_2', 'Nhom2_Ngon_ngu_thu_3']:
                    if k in data:
                        global_language_settings[k] = data[k]
        except Exception:
            pass

def _on_activate_translate():
    loading = show_loading_popup(root)
    def do_translate():
        try:
            load_language_settings_from_file()
            kb.press(Key.ctrl)
            kb.press('c')
            kb.release('c')
            kb.release(Key.ctrl)
            time.sleep(0.15)  # Đợi clipboard cập nhật
            selected_text = get_clipboard()
            if selected_text.strip():
                # Print current API key info before translation
                from core.api_key_manager import api_key_manager
                provider_info = api_key_manager.get_provider_info()
                if provider_info['provider'] != 'none':
                    print(f"🔑 [GROUP 1] Using {provider_info['provider'].title()}: {provider_info['key_preview']} (index: {api_key_manager.active_index})")
                else:
                    print("⚠️ [GROUP 1] No API key available!")
                
                # Get translation with actual language info
                translated, actual_source, actual_target = translate_text(
                    selected_text, 
                    global_language_settings['Ngon_ngu_dau_tien'], 
                    global_language_settings['Ngon_ngu_thu_2'], 
                    global_language_settings['Ngon_ngu_thu_3'],
                    return_language_info=True
                )
                
                # Print result info
                print(f"✨ [GROUP 1] Translation result: {translated[:50]}..." if len(translated) > 50 else f"✨ [GROUP 1] Translation result: {translated}")
                
                def show_result():
                    if loading and loading.winfo_exists():
                        loading._running = False
                        loading.destroy()
                    # Import version từ popup module
                    from ui.popup import get_app_version
                    version = get_app_version()
                    
                    # Use actual language info if available, fallback to settings
                    display_source = actual_source if actual_source else global_language_settings['Ngon_ngu_dau_tien']
                    display_target = actual_target if actual_target else global_language_settings['Ngon_ngu_thu_2']
                    
                    show_popup(translated, master=root, 
                              source_lang=display_source,
                              target_lang=display_target,
                              version=version,
                              auto_close_enabled=load_auto_close_popup())
                root.after(0, show_result)
            else:
                def close_loading():
                    if loading and loading.winfo_exists():
                        loading._running = False
                        loading.destroy()
                root.after(0, close_loading)
        finally:
            root.after(0, restore_system_cursor)
    threading.Thread(target=do_translate, daemon=True).start()

def _on_activate_replace():
    loading = show_loading_popup(root)
    def do_replace():
        try:
            load_language_settings_from_file()
            kb.press(Key.ctrl)
            kb.press('c')
            kb.release('c')
            kb.release(Key.ctrl)
            time.sleep(0.15)
            selected_text = get_clipboard()
            if selected_text.strip():
                # Print current API key info before translation
                from core.api_key_manager import api_key_manager
                provider_info = api_key_manager.get_provider_info()
                if provider_info['provider'] != 'none':
                    print(f"🔑 [GROUP 1 REPLACE] Using {provider_info['provider'].title()}: {provider_info['key_preview']} (index: {api_key_manager.active_index})")
                else:
                    print("⚠️ [GROUP 1 REPLACE] No API key available!")
                
                # Use same logic as translate popup - detect language for proper direction
                translated, actual_source, actual_target = translate_text(
                    selected_text, 
                    global_language_settings['Ngon_ngu_dau_tien'], 
                    global_language_settings['Ngon_ngu_thu_2'], 
                    global_language_settings['Ngon_ngu_thu_3'],
                    return_language_info=True
                )
                
                # Print result info
                print(f"✨ [GROUP 1 REPLACE] Translation result: {translated[:50]}..." if len(translated) > 50 else f"✨ [GROUP 1 REPLACE] Translation result: {translated}")
                def do_paste():
                    if loading and loading.winfo_exists():
                        loading._running = False
                        loading.destroy()
                    set_clipboard(translated)
                    time.sleep(0.05)
                    kb.press(Key.ctrl)
                    kb.press('v')
                    kb.release('v')
                    kb.release(Key.ctrl)
                    time.sleep(0.15)
                    kb.press(Key.ctrl)
                    kb.press('c')
                    kb.release('c')
                    kb.release(Key.ctrl)
                    time.sleep(0.1)
                    pasted = get_clipboard()
                    if pasted.strip() != translated.strip():
                        def show_fail():
                            from ui.popup import get_app_version
                            version = get_app_version()
                            show_popup('Không thể thay thế văn bản tự động. Vị trí dán không cho phép.', 
                                      master=root, version=version, auto_close_enabled=load_auto_close_popup())
                        root.after(0, show_fail)
                root.after(0, do_paste)
            else:
                def close_loading():
                    if loading and loading.winfo_exists():
                        loading._running = False
                        loading.destroy()
                root.after(0, close_loading)
        finally:
            root.after(0, restore_system_cursor)
    threading.Thread(target=do_replace, daemon=True).start()

def _on_activate_translate_group2():
    loading = show_loading_popup(root)
    def do_translate():
        try:
            load_language_settings_from_file()
            kb.press(Key.ctrl)
            kb.press('c')
            kb.release('c')
            kb.release(Key.ctrl)
            time.sleep(0.15)
            selected_text = get_clipboard()
            if selected_text.strip():
                # Print current API key info before translation
                from core.api_key_manager import api_key_manager
                provider_info = api_key_manager.get_provider_info()
                if provider_info['provider'] != 'none':
                    print(f"🔑 [GROUP 2] Using {provider_info['provider'].title()}: {provider_info['key_preview']} (index: {api_key_manager.active_index})")
                else:
                    print("⚠️ [GROUP 2] No API key available!")
                
                # Get translation with actual language info for Group 2
                translated, actual_source, actual_target = translate_text(
                    selected_text, 
                    global_language_settings['Nhom2_Ngon_ngu_dau_tien'], 
                    global_language_settings['Nhom2_Ngon_ngu_thu_2'], 
                    global_language_settings['Nhom2_Ngon_ngu_thu_3'],
                    return_language_info=True
                )
                
                # Print result info
                print(f"✨ [GROUP 2] Translation result: {translated[:50]}..." if len(translated) > 50 else f"✨ [GROUP 2] Translation result: {translated}")
                
                def show_result():
                    if loading and loading.winfo_exists():
                        loading._running = False
                        loading.destroy()
                    # Import version từ popup module
                    from ui.popup import get_app_version
                    version = get_app_version()
                    
                    # Use actual language info if available, fallback to Group 2 settings
                    display_source = actual_source if actual_source else global_language_settings['Nhom2_Ngon_ngu_dau_tien']
                    display_target = actual_target if actual_target else global_language_settings['Nhom2_Ngon_ngu_thu_2']
                    
                    show_popup(translated, master=root, 
                              source_lang=display_source,
                              target_lang=display_target,
                              version=version,
                              auto_close_enabled=load_auto_close_popup())
                root.after(0, show_result)
            else:
                def close_loading():
                    if loading and loading.winfo_exists():
                        loading._running = False
                        loading.destroy()
                root.after(0, close_loading)
        finally:
            root.after(0, restore_system_cursor)
    threading.Thread(target=do_translate, daemon=True).start()

def _on_activate_replace_group2():
    loading = show_loading_popup(root)
    def do_replace():
        try:
            load_language_settings_from_file()
            kb.press(Key.ctrl)
            kb.press('c')
            kb.release('c')
            kb.release(Key.ctrl)
            time.sleep(0.15)
            selected_text = get_clipboard()
            if selected_text.strip():
                # Print current API key info before translation
                from core.api_key_manager import api_key_manager
                provider_info = api_key_manager.get_provider_info()
                if provider_info['provider'] != 'none':
                    print(f"🔑 [GROUP 2 REPLACE] Using {provider_info['provider'].title()}: {provider_info['key_preview']} (index: {api_key_manager.active_index})")
                else:
                    print("⚠️ [GROUP 2 REPLACE] No API key available!")
                
                # Use same logic as translate popup for Group 2 - detect language for proper direction
                translated, actual_source, actual_target = translate_text(
                    selected_text, 
                    global_language_settings['Nhom2_Ngon_ngu_dau_tien'], 
                    global_language_settings['Nhom2_Ngon_ngu_thu_2'], 
                    global_language_settings['Nhom2_Ngon_ngu_thu_3'],
                    return_language_info=True
                )
                
                # Print result info
                print(f"✨ [GROUP 2 REPLACE] Translation result: {translated[:50]}..." if len(translated) > 50 else f"✨ [GROUP 2 REPLACE] Translation result: {translated}")
                def do_paste():
                    if loading and loading.winfo_exists():
                        loading._running = False
                        loading.destroy()
                    set_clipboard(translated)
                    time.sleep(0.05)
                    kb.press(Key.ctrl)
                    kb.press('v')
                    kb.release('v')
                    kb.release(Key.ctrl)
                    time.sleep(0.15)
                    kb.press(Key.ctrl)
                    kb.press('c')
                    kb.release('c')
                    kb.release(Key.ctrl)
                    time.sleep(0.1)
                    pasted = get_clipboard()
                    if pasted.strip() != translated.strip():
                        def show_fail():
                            from ui.popup import get_app_version
                            version = get_app_version()
                            show_popup('Không thể thay thế văn bản tự động. Vị trí dán không cho phép.', 
                                      master=root, version=version, auto_close_enabled=load_auto_close_popup())
                        root.after(0, show_fail)
                root.after(0, do_paste)
            else:
                def close_loading():
                    if loading and loading.winfo_exists():
                        loading._running = False
                        loading.destroy()
                root.after(0, close_loading)
        finally:
            root.after(0, restore_system_cursor)
    threading.Thread(target=do_replace, daemon=True).start()

def for_canonical(listener, f):
    return lambda *args: f(listener.canonical(args[0]))

HOTKEYS_FILE = "hotkeys.json"
ENV_FILE = ".env"
STARTUP_FILE = "startup.json"

global_language_settings = {
    'Ngon_ngu_dau_tien': 'Any Language',
    'Ngon_ngu_thu_2': 'Tiếng Việt',
    'Ngon_ngu_thu_3': 'English',
    'Nhom2_Ngon_ngu_dau_tien': '',
    'Nhom2_Ngon_ngu_thu_2': '',
    'Nhom2_Ngon_ngu_thu_3': '',
}

def load_hotkeys():
    if os.path.exists(HOTKEYS_FILE):
        try:
            with open(HOTKEYS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Cập nhật biến ngôn ngữ toàn cục cho cả 2 nhóm
                for k in ['Ngon_ngu_dau_tien', 'Ngon_ngu_thu_2', 'Ngon_ngu_thu_3', 'Nhom2_Ngon_ngu_dau_tien', 'Nhom2_Ngon_ngu_thu_2', 'Nhom2_Ngon_ngu_thu_3']:
                    if k in data:
                        global_language_settings[k] = data[k]
                return data
        except Exception:
            pass
    return {
        "translate_popup": "<ctrl>+q",
        "replace_translate": "<ctrl>+d",
        "translate_popup2": "",
        "replace_translate2": "",
        "Ngon_ngu_dau_tien": global_language_settings['Ngon_ngu_dau_tien'],
        "Ngon_ngu_thu_2": global_language_settings['Ngon_ngu_thu_2'],
        "Ngon_ngu_thu_3": global_language_settings['Ngon_ngu_thu_3'],
        "Nhom2_Ngon_ngu_dau_tien": global_language_settings['Nhom2_Ngon_ngu_dau_tien'],
        "Nhom2_Ngon_ngu_thu_2": global_language_settings['Nhom2_Ngon_ngu_thu_2'],
        "Nhom2_Ngon_ngu_thu_3": global_language_settings['Nhom2_Ngon_ngu_thu_3'],
    }

def save_hotkeys(hotkeys_dict):
    with open(HOTKEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(hotkeys_dict, f, ensure_ascii=False, indent=2)

def load_ITM_TRANSLATE_KEY():
    # Ưu tiên biến môi trường, sau đó đọc từ file .env
    key = os.environ.get("ITM_TRANSLATE_KEY")
    if key:
        return key
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("ITM_TRANSLATE_KEY="):
                    return line.strip().split("=", 1)[1]
    return ""

def save_ITM_TRANSLATE_KEY(new_key):
    # Ghi đè hoặc thêm vào file .env
    lines = []
    found = False
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("ITM_TRANSLATE_KEY="):
                    lines.append(f"ITM_TRANSLATE_KEY={new_key}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"ITM_TRANSLATE_KEY={new_key}\n")
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

def load_startup_enabled():
    if os.path.exists(STARTUP_FILE):
        try:
            with open(STARTUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("startup", False))
        except Exception:
            pass
    return False

def load_floating_button_enabled():
    if os.path.exists(STARTUP_FILE):
        try:
            with open(STARTUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("floating_button", True))  # Mặc định bật
        except Exception:
            pass
    return True  # Mặc định bật

def load_auto_close_popup():
    if os.path.exists(STARTUP_FILE):
        try:
            with open(STARTUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("auto_close_popup", True))  # Mặc định bật
        except Exception:
            pass
    return True  # Mặc định bật

def save_auto_close_popup(enabled):
    """Lưu setting auto close popup vào startup.json"""
    try:
        data = {}
        if os.path.exists(STARTUP_FILE):
            with open(STARTUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        data["auto_close_popup"] = enabled
        
        with open(STARTUP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Error saving auto close popup setting: {e}")

def load_show_on_startup():
    if os.path.exists(STARTUP_FILE):
        try:
            with open(STARTUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("show_on_startup", True))
        except Exception:
            pass
    return True

def set_startup_windows(enable):
    # Chỉ hỗ trợ Windows
    if not sys.platform.startswith("win"):
        return
    # Đường dẫn file thực thi (hoặc script)
    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    # Đường dẫn shortcut trong thư mục Startup
    startup_dir = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
    shortcut_path = os.path.join(startup_dir, "ITM Translate.lnk")

    if enable:
        try:
            # Tạo shortcut bằng win32com (yêu cầu pywin32)
            import pythoncom
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.IconLocation = exe_path
            shortcut.save()
        except Exception as e:
            print("Không thể tạo shortcut khởi động cùng Windows:", e)
    else:
        try:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
        except Exception as e:
            print("Không thể xóa shortcut khởi động cùng Windows:", e)

def set_floating_button_enabled(enabled):
    """Callback để bật/tắt chức năng floating button từ GUI"""
    global mouse_listener
    if enabled:
        # Bật mouse listener nếu chưa có
        if mouse_listener is None or not mouse_listener.running:
            start_mouse_listener()
    else:
        # Tắt mouse listener nếu đang chạy
        if mouse_listener is not None and mouse_listener.running:
            mouse_listener.stop()
            mouse_listener = None
        # Ẩn floating button nếu đang hiển thị
        hide_floating_button()

# Định nghĩa các phím tắt (mặc định, có thể cập nhật từ GUI)
default_hotkeys = {
    '<ctrl>+q': on_activate_translate,
    '<ctrl>+d': on_activate_replace
}
# Load hotkeys từ file
user_hotkeys = load_hotkeys()
hotkeys = {}
action_map = {
    'translate_popup': on_activate_translate,
    'replace_translate': on_activate_replace,
    'translate_popup2': on_activate_translate2,
    'replace_translate2': on_activate_replace2
}
for action, hotkey in user_hotkeys.items():
    if hotkey and action in action_map:
        hotkeys[hotkey] = action_map[action]
if not hotkeys:
    hotkeys = default_hotkeys.copy()

class MultiHotKey:
    def __init__(self, hotkey_map):
        self.set_hotkeys(hotkey_map)
    def set_hotkeys(self, hotkey_map):
        self.hotkeys = [(frozenset(keyboard.HotKey.parse(k)), v) for k, v in hotkey_map.items()]
        self._pressed = set()
        self._active = set()
    def reset_state(self):
        self._pressed.clear()
        self._active.clear()
    def press(self, key):
        self._pressed.add(key)
        for combo, callback in self.hotkeys:
            if combo <= self._pressed and combo not in self._active:
                self._active.add(combo)
                callback()
    def release(self, key):
        self._pressed.discard(key)
        for combo in list(self._active):
            if not combo <= self._pressed:
                self._active.discard(combo)
    def _run_and_reset(self, combo, callback):
        try:
            callback()
        finally:
            self._active.discard(combo)
    def update_hotkeys(self, new_hotkey_map):
        self.set_hotkeys(new_hotkey_map)
        self.reset_state()

multi_hotkey = MultiHotKey(hotkeys)

def update_ITM_TRANSLATE_KEY(new_key):
    os.environ["ITM_TRANSLATE_KEY"] = new_key
    save_ITM_TRANSLATE_KEY(new_key)

def load_hotkey_actions_from_file():
    if os.path.exists(HOTKEYS_FILE):
        try:
            with open(HOTKEYS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                mapped = {}
                for action, hotkey in data.items():
                    if action in action_map and hotkey:
                        mapped[hotkey] = action_map[action]
                if mapped:
                    multi_hotkey.update_hotkeys(mapped)
        except Exception:
            pass

def update_hotkeys_from_gui(new_hotkeys, app=None):
    mapped = {}
    for action, hotkey in new_hotkeys.items():
        if hotkey and action in action_map:
            mapped[hotkey] = action_map[action]
    if mapped:
        multi_hotkey.update_hotkeys(mapped)
        save_hotkeys(new_hotkeys)
    # Cập nhật lại biến ngôn ngữ toàn cục ngay lập tức
    for k in ['Ngon_ngu_dau_tien', 'Ngon_ngu_thu_2', 'Ngon_ngu_thu_3', 'Nhom2_Ngon_ngu_dau_tien', 'Nhom2_Ngon_ngu_thu_2', 'Nhom2_Ngon_ngu_thu_3']:
        if k in new_hotkeys:
            global_language_settings[k] = new_hotkeys[k]
    load_hotkey_actions_from_file()
    # Không cần khởi động lại listener
    if app is not None:
        app.set_initial_settings(new_hotkeys, load_ITM_TRANSLATE_KEY(), load_startup_enabled(), load_show_on_startup(), load_floating_button_enabled(), load_auto_close_popup())

# Khởi tạo listener một lần duy nhất
listener = keyboard.Listener()
listener.on_press = for_canonical(listener, lambda key, *args: multi_hotkey.press(key))
listener.on_release = for_canonical(listener, lambda key, *args: multi_hotkey.release(key))
listener.start()

root = Window(themename="flatly")
# Đặt icon cho cửa sổ chính (nên làm ngay sau khi tạo root)
try:
    import os
    icon_path_ico = os.path.join(os.path.dirname(__file__), "Resource", "icon.ico")
    icon_path_png = os.path.join(os.path.dirname(__file__), "Resource", "icon.png")
    if os.path.exists(icon_path_ico):
        root.iconbitmap(icon_path_ico)
    elif os.path.exists(icon_path_png):
        from tkinter import PhotoImage
        try:
            from PIL import Image, ImageTk
            img = Image.open(icon_path_png)
            tk_icon = ImageTk.PhotoImage(img)
        except Exception:
            tk_icon = PhotoImage(file=icon_path_png)
        root.iconphoto(True, tk_icon)
except Exception:
    pass
show_on_startup = load_show_on_startup()
startup_enabled = load_startup_enabled()
floating_button_enabled = load_floating_button_enabled()
auto_close_popup = load_auto_close_popup()
if startup_enabled and not show_on_startup:
    root.withdraw()
app = MainGUI(root)
app.set_hotkey_manager(multi_hotkey)
app.set_hotkey_updater(update_hotkeys_from_gui)
app.set_initial_settings(user_hotkeys, "", startup_enabled, show_on_startup, floating_button_enabled, auto_close_popup)
app.set_startup_callback(set_startup_windows)
app.set_floating_button_callback(set_floating_button_enabled)

# Khởi động mouse listener cho floating button feature (nếu được bật)
if floating_button_enabled:
    mouse_listener.start()
    print("🖱️ Mouse listener started for floating translate button")
else:
    print("🖱️ Mouse listener disabled by user settings")

# Print API key status on startup
try:
    from core.api_key_manager import api_key_manager
    key_count = api_key_manager.get_key_count()
    active_key = api_key_manager.get_active_key()
    provider_info = api_key_manager.get_provider_info()
    
    print(f"🚀 ITM Translate started with {key_count} API key(s)")
    if active_key:
        print(f"🎯 Active: {provider_info['name']} ({provider_info['provider'].title()}) - Key: {provider_info['key_preview']}")
        if provider_info['model'] != "auto":
            print(f"🤖 Model: {provider_info['model']}")
    else:
        print("⚠️ No active API key found")
except Exception as e:
    print(f"❌ Error checking API keys: {e}")

tray = create_tray_icon(root, app)
check_queue()

# Cleanup function
def cleanup_on_exit():
    """Cleanup khi thoát chương trình"""
    try:
        if mouse_listener:
            mouse_listener.stop()
        if listener:
            listener.stop()
        hide_floating_button()
    except:
        pass

# Register cleanup
atexit.register(cleanup_on_exit)

root.mainloop()
# KHÔNG join listener, KHÔNG dùng with để tránh lỗi thread với Tkinter/ttkbootstrap