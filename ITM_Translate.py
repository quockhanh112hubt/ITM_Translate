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

def on_activate_translate():
    loading = show_loading_popup(root)
    try:
        kb.press(Key.ctrl)
        kb.press('c')
        kb.release('c')
        kb.release(Key.ctrl)
        time.sleep(0.15)  # Đợi clipboard cập nhật
        selected_text = get_clipboard()
        if selected_text.strip():
            translated = translate_text(selected_text)
            # Kiểm tra lỗi 429
            if isinstance(translated, str) and "429" in translated and "quota" in translated:
                translated = "Lỗi dịch 429: Key của bạn đã hết hạn sử dụng, vui lòng liên hệ Admin để nhận key mới!."
            if loading and loading.winfo_exists():
                loading._running = False
                loading.destroy()
            show_popup(translated)
        else:
            if loading and loading.winfo_exists():
                loading._running = False
                loading.destroy()
    finally:
        restore_system_cursor()

def on_activate_replace():
    loading = show_loading_popup(root)
    try:
        kb.press(Key.ctrl)
        kb.press('c')
        kb.release('c')
        kb.release(Key.ctrl)
        time.sleep(0.15)
        selected_text = get_clipboard()
        if selected_text.strip():
            translated = translate_text(selected_text)
            # Kiểm tra lỗi 429
            if isinstance(translated, str) and "429" in translated and "quota" in translated:
                translated = "Lỗi dịch 429: Key của bạn đã hết hạn sử dụng, vui lòng liên hệ Admin để nhận key mới!."
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
                from ui.popup import show_popup
                show_popup('Không thể thay thế văn bản tự động. Vị trí dán không cho phép.')
        else:
            if loading and loading.winfo_exists():
                loading._running = False
                loading.destroy()
    finally:
        restore_system_cursor()

def for_canonical(f):
    return lambda k: f(l.canonical(k))

HOTKEYS_FILE = "hotkeys.json"
ENV_FILE = ".env"
STARTUP_FILE = "startup.json"

def load_hotkeys():
    if os.path.exists(HOTKEYS_FILE):
        try:
            with open(HOTKEYS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception:
            pass
    return {
        "translate_popup": "<ctrl>+q",
        "replace_translate": "<ctrl>+d"
    }

def save_hotkeys(hotkeys_dict):
    with open(HOTKEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(hotkeys_dict, f, ensure_ascii=False, indent=2)

def load_gemini_api_key():
    # Ưu tiên biến môi trường, sau đó đọc từ file .env
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("GEMINI_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return ""

def save_gemini_api_key(new_key):
    # Ghi đè hoặc thêm vào file .env
    lines = []
    found = False
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("GEMINI_API_KEY="):
                    lines.append(f"GEMINI_API_KEY={new_key}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"GEMINI_API_KEY={new_key}\n")
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
    'replace_translate': on_activate_replace
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
    def press(self, key):
        self._pressed.add(key)
        for combo, callback in self.hotkeys:
            if combo <= self._pressed and combo not in self._active:
                self._active.add(combo)
                threading.Thread(target=self._run_and_reset, args=(combo, callback)).start()
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
        # new_hotkey_map: dict {hotkey_str: callback}
        self.set_hotkeys(new_hotkey_map)

multi_hotkey = MultiHotKey(hotkeys)

def update_gemini_api_key(new_key):
    os.environ["GEMINI_API_KEY"] = new_key
    save_gemini_api_key(new_key)

def update_hotkeys_from_gui(new_hotkeys):
    # new_hotkeys: dict {action: hotkey_str}
    mapped = {}
    for action, hotkey in new_hotkeys.items():
        if hotkey and action in action_map:
            mapped[hotkey] = action_map[action]
    if mapped:
        multi_hotkey.update_hotkeys(mapped)
        save_hotkeys(new_hotkeys)

with keyboard.Listener(
        on_press=for_canonical(multi_hotkey.press),
        on_release=for_canonical(multi_hotkey.release)) as l:
    root = tk.Tk()
    # Đặt icon cho cửa sổ chính
    try:
        import os
        from tkinter import PhotoImage
        icon_path = os.path.join(os.path.dirname(__file__), "Resource", "icon.png")
        if os.path.exists(icon_path):
            try:
                # Nếu icon.png là PNG, dùng PIL để chuyển sang PhotoImage
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                tk_icon = ImageTk.PhotoImage(img)
            except Exception:
                # Nếu không có PIL, thử dùng trực tiếp PhotoImage (chỉ hỗ trợ PNG trên một số hệ)
                tk_icon = PhotoImage(file=icon_path)
            root.iconphoto(True, tk_icon)
    except Exception:
        pass
    # --- Đọc trạng thái show_on_startup ---
    show_on_startup = load_show_on_startup()
    # Nếu đang khởi động cùng Windows và show_on_startup là False thì ẩn giao diện
    startup_enabled = load_startup_enabled()
    if startup_enabled and not show_on_startup:
        root.withdraw()
    app = MainGUI(root)
    app.set_hotkey_manager(multi_hotkey)
    app.set_api_key_updater(update_gemini_api_key)
    app.set_hotkey_updater(update_hotkeys_from_gui)
    # Truyền giá trị hotkeys, api_key, startup, show_on_startup cho GUI hiển thị
    app.set_initial_settings(user_hotkeys, load_gemini_api_key(), startup_enabled, show_on_startup)
    # Callback khi bật/tắt khởi động cùng Windows
    app.set_startup_callback(set_startup_windows)
    tray = create_tray_icon(root, app)
    root.mainloop()
    l.join()
    app.set_initial_settings(user_hotkeys, load_gemini_api_key(), load_startup_enabled())
    # Callback khi bật/tắt khởi động cùng Windows
    app.set_startup_callback(set_startup_windows)
    tray = create_tray_icon(root, app)
    root.mainloop()
    l.join()
