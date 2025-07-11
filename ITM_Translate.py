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
                # Get translation with actual language info
                translated, actual_source, actual_target = translate_text(
                    selected_text, 
                    global_language_settings['Ngon_ngu_dau_tien'], 
                    global_language_settings['Ngon_ngu_thu_2'], 
                    global_language_settings['Ngon_ngu_thu_3'],
                    return_language_info=True
                )
                
                # Kiểm tra lỗi 429
                if isinstance(translated, str) and "429" in translated and "quota" in translated:
                    translated = "Lỗi dịch 429: Key của bạn đã hết hạn sử dụng, vui lòng liên hệ Admin để nhận key mới!."
                # Kiểm tra lỗi 400
                if isinstance(translated, str) and "400" in translated and "key not valid" in translated:
                    translated = "Lỗi 400: Key của bạn không chính xác, vui lòng liên hệ Admin để nhận key sử dụng!."
                
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
                              version=version)
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
                # For replace function, we don't need language info, just use old method for compatibility
                translated = translate_text(selected_text, global_language_settings['Ngon_ngu_dau_tien'], global_language_settings['Ngon_ngu_thu_2'], global_language_settings['Ngon_ngu_thu_3'])
                # Kiểm tra lỗi 429
                if isinstance(translated, str) and "429" in translated and "quota" in translated:
                    translated = "Lỗi dịch 429: Key của bạn đã hết hạn sử dụng, vui lòng liên hệ Admin để nhận key mới!."
                # Kiểm tra lỗi 400
                if isinstance(translated, str) and "400" in translated and "key not valid" in translated:
                    translated = "Lỗi 400: Key của bạn không chính xác, vui lòng liên hệ Admin để nhận key sử dụng!."
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
                                      master=root, version=version)
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
                # Get translation with actual language info for Group 2
                translated, actual_source, actual_target = translate_text(
                    selected_text, 
                    global_language_settings['Nhom2_Ngon_ngu_dau_tien'], 
                    global_language_settings['Nhom2_Ngon_ngu_thu_2'], 
                    global_language_settings['Nhom2_Ngon_ngu_thu_3'],
                    return_language_info=True
                )
                
                if isinstance(translated, str) and "429" in translated and "quota" in translated:
                    translated = "Lỗi dịch 429: Key của bạn đã hết hạn sử dụng, vui lòng liên hệ Admin để nhận key mới!."
                if isinstance(translated, str) and "400" in translated and "key not valid" in translated:
                    translated = "Lỗi 400: Key của bạn không chính xác, vui lòng liên hệ Admin để nhận key sử dụng!."
                
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
                              version=version)
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
                # For replace function Group 2, use old method for compatibility  
                translated = translate_text(selected_text, global_language_settings['Nhom2_Ngon_ngu_dau_tien'], global_language_settings['Nhom2_Ngon_ngu_thu_2'], global_language_settings['Nhom2_Ngon_ngu_thu_3'])
                if isinstance(translated, str) and "429" in translated and "quota" in translated:
                    translated = "Lỗi dịch 429: Key của bạn đã hết hạn sử dụng, vui lòng liên hệ Admin để nhận key mới!."
                if isinstance(translated, str) and "400" in translated and "key not valid" in translated:
                    translated = "Lỗi 400: Key của bạn không chính xác, vui lòng liên hệ Admin để nhận key sử dụng!."
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
                                      master=root, version=version)
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
        app.set_initial_settings(new_hotkeys, load_ITM_TRANSLATE_KEY(), load_startup_enabled(), load_show_on_startup())

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
if startup_enabled and not show_on_startup:
    root.withdraw()
app = MainGUI(root)
app.set_hotkey_manager(multi_hotkey)
app.set_api_key_updater(update_ITM_TRANSLATE_KEY)
app.set_hotkey_updater(update_hotkeys_from_gui)
app.set_initial_settings(user_hotkeys, load_ITM_TRANSLATE_KEY(), startup_enabled, show_on_startup)
app.set_startup_callback(set_startup_windows)
tray = create_tray_icon(root, app)
check_queue()
root.mainloop()
# KHÔNG join listener, KHÔNG dùng with để tránh lỗi thread với Tkinter/ttkbootstrap