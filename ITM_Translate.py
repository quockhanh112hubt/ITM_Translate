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
screenshot_mode_keys = set()  # Theo dõi các phím chụp ảnh đang được nhấn
screenshot_mode_active = False  # Trạng thái chế độ chụp ảnh đang hoạt động
screenshot_mode_timer = None  # Timer để tự động tắt chế độ chụp ảnh

def show_floating_translate_button(mouse_x, mouse_y):
    """Hiển thị nút dịch floating cạnh vị trí chuột"""
    global floating_btn, floating_btn_timer
    
    # KIỂM TRA EXCLUSION NGAY ĐẦU
    if is_current_app_excluded():
        print(f"🚫 [FLOATING] Cannot show floating button - current app is excluded")
        return
    
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
            # Kiểm tra nếu đang trong chế độ chụp ảnh
            if screenshot_mode_active or screenshot_mode_keys:
                print(f"📸 [FLOATING] Screenshot mode detected, ignoring mouse drag")
                return
            
            # Kiểm tra nếu ứng dụng hiện tại bị loại trừ
            if is_current_app_excluded():
                return
            
            # Bắt đầu có thể drag (select text)
            mouse_drag_start = (x, y)
            is_dragging = False
        else:
            # Kết thúc click/drag
            if mouse_drag_start and is_dragging and not screenshot_mode_active and not screenshot_mode_keys and not is_current_app_excluded():
                # Đã drag (select text), check clipboard sau một chút
                # Tăng delay để đảm bảo text đã được select hoàn toàn
                root.after(300, lambda: check_for_new_selection(x, y))
            
            mouse_drag_start = None
            is_dragging = False

def on_mouse_move(x, y):
    """Xử lý mouse move events"""
    global mouse_drag_start, is_dragging
    
    if mouse_drag_start and not screenshot_mode_active and not screenshot_mode_keys and not is_current_app_excluded():
        # Tính khoảng cách drag
        dx = abs(x - mouse_drag_start[0])
        dy = abs(y - mouse_drag_start[1])
        
        # Nâng cao threshold và yêu cầu drag đủ xa để có thể là text selection
        # Drag theo chiều ngang (dx) thường là text selection
        # Drag theo chiều dọc (dy) có thể là scroll hoặc drag window
        horizontal_drag = dx > 15  # Tăng từ 10 lên 15 pixels
        meaningful_drag = dx > 8 and dy < 50  # Ưu tiên drag ngang, hạn chế drag dọc quá nhiều
        
        if horizontal_drag or meaningful_drag:
            is_dragging = True

def activate_screenshot_mode(duration_ms=15000):
    """Kích hoạt chế độ chụp ảnh trong khoảng thời gian nhất định"""
    global screenshot_mode_active, screenshot_mode_timer
    
    screenshot_mode_active = True
    print(f"📸 [FLOATING] Screenshot mode activated for {duration_ms}ms")
    
    # Hủy timer cũ nếu có
    if screenshot_mode_timer:
        root.after_cancel(screenshot_mode_timer)
    
    # Đặt timer để tự động tắt
    screenshot_mode_timer = root.after(duration_ms, deactivate_screenshot_mode)

def deactivate_screenshot_mode():
    """Tắt chế độ chụp ảnh"""
    global screenshot_mode_active, screenshot_mode_timer
    
    screenshot_mode_active = False
    if screenshot_mode_timer:
        root.after_cancel(screenshot_mode_timer)
        screenshot_mode_timer = None
    print(f"📸 [FLOATING] Screenshot mode deactivated")

def get_active_window_title():
    """Lấy title của cửa sổ đang active (Windows only)"""
    try:
        if sys.platform.startswith("win"):
            import ctypes
            from ctypes import wintypes
            
            # Get the handle of the foreground window
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            
            # Get the length of the window title
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return ""
            
            # Get the window title
            buffer = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
            
            return buffer.value
    except Exception:
        pass
    return ""

def get_active_window_process_name():
    """Lấy process name của cửa sổ đang active (Windows only)"""
    try:
        if sys.platform.startswith("win"):
            import ctypes
            import psutil
            
            # Get the handle of the foreground window
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            
            # Get process ID
            process_id = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            
            # Get process name
            try:
                process = psutil.Process(process_id.value)
                process_name = process.name().lower()
                if process_name.endswith('.exe'):
                    process_name = process_name[:-4]
                return process_name
            except psutil.NoSuchProcess:
                return ""
    except Exception:
        pass
    return ""

def check_for_new_selection(mouse_x, mouse_y):
    """Kiểm tra xem có text mới được select không"""
    global last_clipboard_text
    
    try:
        # Kiểm tra nếu đang trong chế độ chụp ảnh
        if screenshot_mode_active or screenshot_mode_keys:
            print(f"📸 [FLOATING] Screenshot mode active, skipping text selection check")
            return
        
        # Kiểm tra nếu ứng dụng hiện tại bị loại trừ
        if is_current_app_excluded():
            return
        
        # Tránh trigger khi click vào floating button đang hiển thị
        if floating_btn and floating_btn.winfo_exists():
            try:
                btn_x = floating_btn.winfo_rootx()
                btn_y = floating_btn.winfo_rooty()
                btn_w = floating_btn.winfo_width()
                btn_h = floating_btn.winfo_height()
                
                # Nếu chuột gần floating button, không check selection
                if (btn_x - 50 <= mouse_x <= btn_x + btn_w + 50 and 
                    btn_y - 50 <= mouse_y <= btn_y + btn_h + 50):
                    print(f"🖱️ [FLOATING] Mouse near floating button, skipping")
                    return
            except:
                pass
        
        # Backup clipboard hiện tại để so sánh
        original_clipboard = get_clipboard()
        
        # Delay ngắn trước khi gửi Ctrl+C để tránh conflict với Excel auto-copy
        time.sleep(0.05)
        
        # Copy text đã select (simulate Ctrl+C)
        kb.press(Key.ctrl)
        kb.press('c')
        kb.release('c')
        kb.release(Key.ctrl)
        
        # Đợi clipboard update (tăng delay cho Excel)
        time.sleep(0.15)
        
        current_text = get_clipboard()
        
        # Kiểm tra điều kiện để hiển thị floating button:
        # 1. Clipboard đã thay đổi (có text mới được copy)
        # 2. Text không rỗng và có nội dung thực sự
        # 3. Text khác với lần cuối cùng đã xử lý
        # 4. Text không giống với clipboard ban đầu (tránh trường hợp không có selection)
        clipboard_changed = current_text != original_clipboard
        has_meaningful_text = current_text and current_text.strip() and len(current_text.strip()) > 1
        is_new_text = current_text != last_clipboard_text
        
        # Kiểm tra ứng dụng hiện tại để tránh Excel auto-copy
        active_window = get_active_window_title().lower()
        is_excel_app = any(keyword in active_window for keyword in ['excel', 'microsoft excel', '.xlsx', '.xls'])
        
        # Thêm kiểm tra đặc biệt cho Excel auto-copy
        # Excel thường copy single cell values hoặc short text khi click
        is_excel_auto_copy = False
        if clipboard_changed and current_text and is_excel_app:
            cleaned_text = current_text.strip()
            
            # Excel auto-copy patterns:
            # - Single word/number (no spaces)
            # - Very short text (< 10 chars)
            # - Pure numbers or simple formulas
            # - Single line with common Excel content patterns
            if (len(cleaned_text) < 10 and 
                ('\n' not in cleaned_text) and
                (cleaned_text.replace('.', '').replace(',', '').replace('-', '').isdigit() or  # Numbers
                 len(cleaned_text.split()) <= 2 or  # Max 2 words
                 cleaned_text.startswith('='))):  # Excel formulas
                is_excel_auto_copy = True
                print(f"🖱️ [FLOATING] Detected Excel auto-copy pattern, skipping: '{cleaned_text}'")
        
        # Nếu không phải Excel, cũng check pattern tương tự cho các ứng dụng khác
        elif clipboard_changed and current_text and not is_excel_app:
            cleaned_text = current_text.strip()
            
            # Auto-copy patterns from other apps (Google Sheets, LibreOffice, etc.)
            if (len(cleaned_text) < 8 and 
                ('\n' not in cleaned_text) and
                (cleaned_text.replace('.', '').replace(',', '').replace('-', '').isdigit() or  # Numbers
                 len(cleaned_text.split()) <= 1)):  # Single word
                is_excel_auto_copy = True
                print(f"🖱️ [FLOATING] Detected auto-copy pattern from {active_window}, skipping: '{cleaned_text}'")
        
        if clipboard_changed and has_meaningful_text and is_new_text and not is_excel_auto_copy:
            # Kiểm tra thêm: text không được quá ngắn hoặc chỉ là ký tự đặc biệt
            cleaned_text = current_text.strip()
            
            # Bỏ qua nếu chỉ là 1 ký tự hoặc toàn ký tự đặc biệt/số
            if len(cleaned_text) < 2:
                print(f"🖱️ [FLOATING] Text too short, skipping: '{cleaned_text}'")
                return
                
            # Bỏ qua nếu toàn là ký tự không phải chữ (số, ký tự đặc biệt)
            if not any(c.isalpha() for c in cleaned_text):
                print(f"🖱️ [FLOATING] No alphabetic characters, skipping: '{cleaned_text}'")
                return
            
            # Kiểm tra thêm cho meaningful content (ít nhất 3 từ hoặc 15 ký tự có ý nghĩa)
            word_count = len([w for w in cleaned_text.split() if any(c.isalpha() for c in w)])
            if word_count < 2 and len(cleaned_text) < 15:
                print(f"🖱️ [FLOATING] Not enough meaningful content, skipping: '{cleaned_text}' (words: {word_count})")
                return
            
            # KIỂM TRA CUỐI CÙNG: Ứng dụng hiện tại có bị loại trừ không
            if is_current_app_excluded():
                print(f"🚫 [FLOATING] Current app excluded, not showing floating button")
                return
            
            # Text hợp lệ, cập nhật last_clipboard_text và hiển thị floating button
            last_clipboard_text = current_text
            show_floating_translate_button(mouse_x, mouse_y)
            print(f"🖱️ [FLOATING] New text selected: {current_text[:30]}...")
        else:
            # Debug: in lý do không hiển thị
            if not clipboard_changed:
                print(f"🖱️ [FLOATING] No clipboard change detected")
            elif not has_meaningful_text:
                print(f"🖱️ [FLOATING] No meaningful text: '{current_text}'")
            elif not is_new_text:
                print(f"🖱️ [FLOATING] Already processed this text")
            elif is_excel_auto_copy:
                # Already logged above
                pass
            
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

def load_excluded_applications():
    """Load danh sách ứng dụng bị loại trừ từ startup.json"""
    if os.path.exists(STARTUP_FILE):
        try:
            with open(STARTUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("excluded_applications", ["excel", "word", "powerpoint", "outlook"])
        except Exception:
            pass
    return ["excel", "word", "powerpoint", "outlook"]  # Default excluded apps

def is_current_app_excluded():
    """Kiểm tra xem ứng dụng hiện tại có bị loại trừ không"""
    try:
        # Chỉ lấy process name để kiểm tra, không check window title
        # vì window title có thể chứa đường dẫn file gây nhầm lẫn
        process_name = get_active_window_process_name().lower()
        active_window = get_active_window_title().lower()  # Chỉ để log
        excluded_apps = load_excluded_applications()
        
        for app in excluded_apps:
            app_lower = app.lower()
            # Chỉ kiểm tra process name, không check window title
            if app_lower in process_name:
                print(f"🚫 [FLOATING] Current app excluded - Process: '{process_name}' (matched: {app})")
                return True
        
        return False
    except Exception as e:
        print(f"❌ [FLOATING] Error checking excluded app: {e}")
        return False

def load_floating_button_enabled():
    if os.path.exists(STARTUP_FILE):
        try:
            with open(STARTUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("floating_button", False))  # Mặc định tắt
        except Exception:
            pass
    return False  # Mặc định tắt

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
    """Callback để bật/tắt chức năng floating button từ GUI hoặc tray"""
    global mouse_listener, tray, app
    print(f"🔍 [DEBUG] set_floating_button_enabled called with: enabled = {enabled}")
    
    if enabled:
        # Bật mouse listener nếu chưa có
        if mouse_listener is None or not mouse_listener.running:
            start_mouse_listener()
        print(f"🖱️ Floating button enabled")
    else:
        # Tắt mouse listener nếu đang chạy
        if mouse_listener is not None and mouse_listener.running:
            mouse_listener.stop()
            mouse_listener = None
        # Ẩn floating button nếu đang hiển thị
        hide_floating_button()
        print(f"🖱️ Floating button disabled")
    
    # Cập nhật tray icon nếu có
    if tray and hasattr(tray, 'update_floating_button_state'):
        try:
            tray.update_floating_button_state(enabled)
        except Exception as e:
            print(f"❌ Error updating tray icon: {e}")
    
    # Cập nhật UI trong Advanced tab để ẩn/hiện phần excluded applications
    try:
        print(f"🔍 [DEBUG] Checking app availability: app={app is not None}")
        if app:
            print(f"🔍 [DEBUG] Has advanced_tab_component: {hasattr(app, 'advanced_tab_component')}")
            if hasattr(app, 'advanced_tab_component'):
                print(f"🔍 [DEBUG] advanced_tab_component: {app.advanced_tab_component}")
                
                # CẬP NHẬT CHECKBOX STATE TRƯỚC KHI GỌI _update_excluded_frame_state
                if hasattr(app.advanced_tab_component, 'floating_button_enabled'):
                    app.advanced_tab_component.floating_button_enabled.set(enabled)
                    print(f"🔄 Updated checkbox state to: {enabled}")
                
                print(f"🔍 [DEBUG] Has _update_excluded_frame_state: {hasattr(app.advanced_tab_component, '_update_excluded_frame_state')}")
                if hasattr(app.advanced_tab_component, '_update_excluded_frame_state'):
                    app.advanced_tab_component._update_excluded_frame_state()
                    print(f"🔄 Advanced tab excluded frame state updated")
                else:
                    print(f"❌ Method _update_excluded_frame_state not found")
            else:
                print(f"❌ advanced_tab_component not found")
        else:
            print(f"❌ app is None")
    except Exception as e:
        print(f"❌ Error updating advanced tab excluded frame state: {e}")

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
        # Theo dõi các phím chụp ảnh phổ biến
        self._check_screenshot_keys(key, True)
        
        self._pressed.add(key)
        for combo, callback in self.hotkeys:
            if combo <= self._pressed and combo not in self._active:
                self._active.add(combo)
                callback()
    def release(self, key):
        # Theo dõi các phím chụp ảnh phổ biến
        self._check_screenshot_keys(key, False)
        
        self._pressed.discard(key)
        for combo in list(self._active):
            if not combo <= self._pressed:
                self._active.discard(combo)
    def _check_screenshot_keys(self, key, is_pressed):
        """Theo dõi các tổ hợp phím chụp ảnh phổ biến"""
        global screenshot_mode_keys
        
        if is_pressed:
            # Special handling for Ctrl+Alt+S sequence
            if (keyboard.Key.ctrl in self._pressed and 
                keyboard.Key.alt in self._pressed and 
                key == keyboard.KeyCode.from_char('s')):
                print(f"📸 [FLOATING] Ctrl+Alt+S screenshot sequence detected!")
                activate_screenshot_mode(15000)
                return
                
            # Special handling for Win+Shift+S sequence  
            if (keyboard.Key.cmd in self._pressed and 
                keyboard.Key.shift in self._pressed and 
                key == keyboard.KeyCode.from_char('s')):
                print(f"📸 [FLOATING] Win+Shift+S screenshot sequence detected!")
                activate_screenshot_mode(15000)
                return
                
            # Print Screen variations
            if key == keyboard.Key.print_screen:
                print(f"📸 [FLOATING] Print Screen detected!")
                activate_screenshot_mode(15000)
                return
                
            # ShareX shortcuts
            if (keyboard.Key.ctrl in self._pressed and 
                keyboard.Key.shift in self._pressed and 
                hasattr(key, 'char') and key.char in ['1', '2', '3', '4']):
                print(f"📸 [FLOATING] ShareX shortcut Ctrl+Shift+{key.char} detected!")
                activate_screenshot_mode(15000)
                return
                
        # Keep track of pressed keys for combo detection
        # (Original combo logic as fallback)
        screenshot_combos = [
            frozenset([keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('s')]),
            frozenset([keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char('s')]),
            frozenset([keyboard.Key.print_screen]),
            frozenset([keyboard.Key.alt, keyboard.Key.print_screen]),
            frozenset([keyboard.Key.ctrl, keyboard.Key.print_screen]),
        ]
        
        if is_pressed:
            for combo in screenshot_combos:
                if combo <= self._pressed and combo not in screenshot_mode_keys:
                    screenshot_mode_keys.add(combo)
                    print(f"📸 [FLOATING] Screenshot combo active: {combo}")
        else:
            to_remove = []
            for combo in screenshot_mode_keys:
                if not combo <= self._pressed:
                    to_remove.append(combo)
            for combo in to_remove:
                screenshot_mode_keys.discard(combo)
                print(f"📸 [FLOATING] Screenshot combo released: {combo}")
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

# Tạo callback để cập nhật tray icon từ GUI
def update_tray_icon_from_gui():
    """Callback để cập nhật tray icon khi settings thay đổi từ GUI"""
    try:
        if tray and hasattr(tray, 'update_tray_icon'):
            # Gọi function update_tray_icon của tray
            tray.update_tray_icon()
        else:
            # Nếu không có method update_tray_icon, reload tray state
            import importlib
            import core.tray
            importlib.reload(core.tray)
            print("🔄 Tray icon updated from GUI settings change")
    except Exception as e:
        print(f"❌ Error updating tray icon from GUI: {e}")

# Set callback cho app
app.set_tray_update_callback(update_tray_icon_from_gui)

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