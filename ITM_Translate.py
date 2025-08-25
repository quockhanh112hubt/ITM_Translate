# -*- coding: utf-8 -*-
"""
ITM Translate - Universal Translation Tool
Main application entry point
"""
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
from core.config_manager import config_manager
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

# NEW: Smart selection detection without clipboard interference
last_selection_info = None  # Store selection context for later use

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
                   command=lambda: on_floating_translate_click_v3())
    btn.pack()
    
    # Update to get button size after packing
    floating_btn.update_idletasks()
    btn_width = btn.winfo_reqwidth()
    btn_height = btn.winfo_reqheight()
    
    # Smart positioning for floating button
    from ui.popup import get_smart_popup_position
    x, y = get_smart_popup_position(root, btn_width, btn_height, mouse_x, mouse_y)
    floating_btn.geometry(f'+{x}+{y}')
    
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
    floating_btn_timer = root.after(3000, hide_floating_button)
    
    # DON'T use FocusOut since we don't want to steal focus from user's text selection
    # Instead, button will auto-hide after 5 seconds or when user clicks it
    # This preserves user's ability to Ctrl+C their selected text
    
    # Optional: Add click-outside detection via global mouse listener (already handled in mouse events)

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

def on_floating_translate_click_v3():
    """V3: Handle floating translate click - Use pre-validated text from last_selection_info
    
    Since text was already captured and validated during button show,
    we can directly use it without Ctrl+C again.
    """
    global last_selection_info, last_clipboard_text

    hide_floating_button()  # Hide button first
    
    try:
        # Check if we have pre-validated text from selection detection
        if last_selection_info and last_selection_info.get('validated_text'):
            selected_text = last_selection_info['validated_text']

            # Process translation directly with pre-validated text
            last_clipboard_text = selected_text
            
            # Trigger translate
            action_queue.put(('translate', 'group1'))

        else:
            # Fallback: Try to get text with Ctrl+C (in case validation failed or no stored text)

            # Step 1: Backup user's current clipboard before any modification
            original_clipboard = get_clipboard()

            # Step 2: Use Ctrl+C to get the selected text (since we know there is selection)

            kb.press(Key.ctrl)
            kb.press('c')
            kb.release('c')
            kb.release(Key.ctrl)
            
            # Wait for clipboard update
            time.sleep(0.15)
            
            # Step 3: Get the selected text from clipboard
            selected_text = get_clipboard()
            
            # Step 4: Check if we got valid text
            if selected_text and selected_text.strip() and selected_text != original_clipboard:

                # Process translation
                last_clipboard_text = selected_text
                
                # Trigger translate
                action_queue.put(('translate', 'group1'))

            else:

                # Restore original clipboard if no new text
                if original_clipboard:
                    set_clipboard(original_clipboard)
                
                # Show feedback to user
                from ui.popup import get_app_version
                version = get_app_version()
                show_popup("Không có văn bản nào được chọn để dịch.", 
                          master=root, version=version, auto_close_enabled=True)
        
        # Step 5: Reset selection info
        last_selection_info = None
        
    except Exception as e:
        print(f"❌ [FLOATING V3] Error in floating translate click: {e}")
        # Reset selection info on error
        last_selection_info = None

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
                # Đã drag (select text), check for selection WITHOUT Ctrl+C
                # NEW APPROACH: Show button based on drag pattern, Ctrl+C only when user clicks
                try:
                    import threading
                    # Pass current dragging state to avoid race condition
                    current_dragging = is_dragging
                    # Delay 200ms để đảm bảo text selection hoàn tất
                    threading.Timer(0.2, lambda: check_for_text_selection_v3(x, y, current_dragging)).start()
                except Exception as e:
                    pass
            else:
                pass
                pass
            
            mouse_drag_start = None
            is_dragging = False  # Reset dragging state
            is_dragging = False

def on_mouse_move(x, y):
    """Xử lý mouse move events"""
    global mouse_drag_start, is_dragging
    
    try:
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
    except Exception as e:
        pass

def activate_screenshot_mode(duration_ms=None):
    """Kích hoạt chế độ chụp ảnh trong khoảng thời gian nhất định"""
    global screenshot_mode_active, screenshot_mode_timer
    
    # Get timeout from config if not specified
    if duration_ms is None:
        duration_seconds = config_manager.get_floating_button_timeout()
        duration_ms = duration_seconds * 1000  # Convert to milliseconds
    
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

def check_for_text_selection_v3(mouse_x, mouse_y, was_dragging=None):
    """NEW V3: Smart text selection detection without clipboard interference
    
    Logic:
    1. Check if current app is excluded → Skip if yes
    2. Check if in screenshot mode → Skip if yes  
    3. Apply smart filters (drag pattern, window context, etc.)
    4. Only show floating button if real text selection detected
    5. NO clipboard interference until user clicks "Translate"
    
    Args:
        mouse_x, mouse_y: Mouse position
        was_dragging: Dragging state at the time of call (to avoid race conditions)
    """
    global last_selection_info, is_dragging

    try:
        # Step 1: Check if current app is excluded
        if is_current_app_excluded():
            print(f"� [FLOATING V3] Current app is excluded, skipping")
            return
        
        # Step 2: Check if in screenshot mode
        if screenshot_mode_active or screenshot_mode_keys:
            print(f"📸 [FLOATING V3] Screenshot mode active, skipping")
            return
        
        # Step 3: Only trigger if we detect actual dragging motion (text selection behavior)
        dragging_state = was_dragging if was_dragging is not None else is_dragging
        if not dragging_state:
            return
        
        # Step 4: Avoid triggering near existing floating button
        if floating_btn and floating_btn.winfo_exists():
            try:
                btn_x = floating_btn.winfo_rootx()
                btn_y = floating_btn.winfo_rooty()
                btn_w = floating_btn.winfo_width()
                btn_h = floating_btn.winfo_height()
                
                if (btn_x - 50 <= mouse_x <= btn_x + btn_w + 50 and 
                    btn_y - 50 <= mouse_y <= btn_y + btn_h + 50):

                    return
            except:
                pass
        
        # Step 5: Smart context analysis - NO clipboard interference yet
        context_analysis = analyze_selection_context()
        
        if not context_analysis['likely_text_selection']:

            return
        
        # Step 6: Apply smart filters based on window context and app behavior
        filter_result = apply_smart_filters()
        
        if not filter_result['passed']:

            return
        
        # Step 7: If we reach here, likely a real text selection - VALIDATE TEXT FIRST
        # NEW: Check text content BEFORE showing button to avoid showing unusable button
        print(f"🔍 [FLOATING V3] Pre-validating text selection before showing button...")
        
        # We need to get the actual selected text to validate it
        # This is a lightweight check - we'll do a quick Ctrl+C to peek at the content
        validated_text = None
        try:
            # Backup current clipboard
            temp_clipboard = get_clipboard()
            
            # Quick Ctrl+C to get selected text
            kb.press(Key.ctrl)
            kb.press('c')
            kb.release('c')
            kb.release(Key.ctrl)
            
            # Brief wait for clipboard
            time.sleep(0.1)
            
            # Get the selected text
            peek_text = get_clipboard()
            
            # Restore original clipboard immediately
            if temp_clipboard:
                set_clipboard(temp_clipboard)
            
            # Validate the peeked text
            if peek_text and peek_text.strip() and peek_text != temp_clipboard:
                validation_result = validate_text_content(peek_text)
                
                if not validation_result['is_valid']:
                    print(f"🚫 [FLOATING V3] Text validation failed - NOT showing button: {validation_result['reason']}")
                    return  # Don't show button for invalid text
                
                print(f"✅ [FLOATING V3] Text validation passed - safe to show button: {validation_result['reason']}")
                validated_text = peek_text  # Store the validated text for later use
            else:

                return  # Don't show button if no new text
                
        except Exception as e:
            print(f"❌ [FLOATING V3] Error in pre-validation: {e}")
            # If validation fails, default to showing button (fallback)
        
        # Store context for later use when user clicks translate (INCLUDING the validated text)
        last_selection_info = {
            'mouse_pos': (mouse_x, mouse_y),
            'timestamp': time.time(),
            'active_window': get_active_window_title(),
            'process_name': get_active_window_process_name(),
            'context_analysis': context_analysis,
            'ready_for_translation': True,
            'validated_text': validated_text  # Store the actual text for reuse
        }
        
        print(f"✅ [FLOATING V3] Text selection detected - showing translate button")
        show_floating_translate_button(mouse_x, mouse_y)
        
    except Exception as e:
        print(f"❌ [FLOATING V3] Error in selection detection: {e}")

def analyze_selection_context():
    """Analyze context to determine if this is likely a text selection
    
    Returns:
        dict: {
            'likely_text_selection': bool,
            'reason': str,
            'confidence': float
        }
    """
    try:
        # Get current window and app info
        window_title = get_active_window_title().lower()
        process_name = get_active_window_process_name().lower()
        
        # Check if it's a text-oriented application
        text_apps = [
            'notepad', 'wordpad', 'code', 'sublime', 'atom', 'vim', 'emacs',
            'chrome', 'firefox', 'edge', 'opera', 'browser',
            'word', 'onenote', 'notion', 'obsidian',
            'slack', 'discord', 'telegram', 'whatsapp',
            'cmd', 'powershell', 'terminal', 'git'
        ]
        
        # Check if it's likely a file manager or image viewer
        non_text_apps = [
            'explorer', 'finder', 'nautilus',
            'photoshop', 'gimp', 'paint', 'mspaint',
            'vlc', 'media', 'player', 'spotify',
            'calculator', 'calc'
        ]
        
        confidence = 0.5  # Default confidence
        
        # Boost confidence for text applications
        for app in text_apps:
            if app in process_name or app in window_title:
                confidence += 0.3
                break
        
        # Reduce confidence for non-text applications  
        for app in non_text_apps:
            if app in process_name:
                confidence -= 0.4
                break
        
        # Additional context checks
        if any(ext in window_title for ext in ['.jpg', '.png', '.gif', '.mp4', '.avi', '.pdf']):
            confidence -= 0.2
            reason = "File extension suggests non-text content"
        elif any(keyword in window_title for keyword in ['folder', 'directory', 'file manager']):
            confidence -= 0.3
            reason = "Window suggests file manager context"
        else:
            reason = f"Context analysis for {process_name}"
        
        likely_selection = confidence > 0.4
        
        return {
            'likely_text_selection': likely_selection,
            'reason': reason,
            'confidence': confidence,
            'process_name': process_name,
            'window_title': window_title
        }
        
    except Exception as e:
        print(f"❌ [FLOATING V3] Error in context analysis: {e}")
        return {
            'likely_text_selection': True,  # Default to allowing if error
            'reason': f"Error in analysis: {e}",
            'confidence': 0.5
        }

def validate_text_content(text):
    """Validate if text content is meaningful and suitable for translation
    
    Args:
        text (str): Text to validate
        
    Returns:
        dict: {
            'is_valid': bool,
            'reason': str,
            'confidence': float
        }
    """
    try:
        if not text or not text.strip():
            return {
                'is_valid': False,
                'reason': 'Text is empty or whitespace only',
                'confidence': 0.0
            }
        
        cleaned_text = text.strip()
        
        # Filter 1: Text quá ngắn (< 2 ký tự)
        if len(cleaned_text) < 2:
            return {
                'is_valid': False,
                'reason': f'Text too short: "{cleaned_text}" ({len(cleaned_text)} chars)',
                'confidence': 0.0
            }
        
        # Filter 2: Text chỉ có 1 ký tự
        if len(cleaned_text) == 1:
            return {
                'is_valid': False,
                'reason': f'Single character: "{cleaned_text}"',
                'confidence': 0.0
            }
        
        # Filter 3: Text không có chữ cái (chỉ số và ký tự đặc biệt)
        has_letters = any(c.isalpha() for c in cleaned_text)
        if not has_letters:
            return {
                'is_valid': False,
                'reason': f'No alphabetic characters: "{cleaned_text}"',
                'confidence': 0.0
            }
        
        # Filter 4: Text chỉ toàn số (ngay cả khi có dấu phẩy, chấm)
        numeric_text = cleaned_text.replace(',', '').replace('.', '').replace('-', '').replace('+', '').replace(' ', '')
        if numeric_text.isdigit():
            return {
                'is_valid': False,
                'reason': f'Pure numeric content: "{cleaned_text}"',
                'confidence': 0.0
            }
        
        # Filter 5: File path patterns (C:\, /, file extensions)
        if any(pattern in cleaned_text for pattern in ['C:\\', 'D:\\', 'E:\\', '\\\\', '.exe', '.dll', '.sys']):
            return {
                'is_valid': False,
                'reason': f'File path pattern detected: "{cleaned_text[:30]}..."',
                'confidence': 0.0
            }
        
        # Filter 6: File extensions
        file_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg',
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv',
            '.mp3', '.wav', '.flac', '.aac', '.wma',
            '.zip', '.rar', '.7z', '.tar', '.gz',
            '.exe', '.msi', '.dmg', '.deb', '.rpm',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.csv', '.json', '.xml', '.html', '.css', '.js'
        ]
        
        text_lower = cleaned_text.lower()
        if any(ext in text_lower for ext in file_extensions):
            # Additional check: if it's ONLY filename, reject it
            if len(cleaned_text.split()) <= 2 and any(cleaned_text.lower().endswith(ext) for ext in file_extensions):
                return {
                    'is_valid': False,
                    'reason': f'Filename detected: "{cleaned_text}"',
                    'confidence': 0.0
                }
        
        # Filter 7: Very short text with no meaningful words (< 3 characters and not a word)
        if len(cleaned_text) < 3 and not any(c.isalpha() for c in cleaned_text):
            return {
                'is_valid': False,
                'reason': f'Too short and no letters: "{cleaned_text}"',
                'confidence': 0.0
            }
        
        # Filter 8: Special patterns (URLs, email addresses)
        if 'http://' in text_lower or 'https://' in text_lower or 'www.' in text_lower:
            # URLs might be valid for translation in some cases, but usually not
            word_count = len([w for w in cleaned_text.split() if any(c.isalpha() for c in w)])
            if word_count <= 1:  # If it's just a URL without description
                return {
                    'is_valid': False,
                    'reason': f'URL without meaningful text: "{cleaned_text[:30]}..."',
                    'confidence': 0.2
                }
        
        # Filter 9: Email addresses
        if '@' in cleaned_text and '.' in cleaned_text:
            words = cleaned_text.split()
            if len(words) <= 2 and any('@' in word and '.' in word for word in words):
                return {
                    'is_valid': False,
                    'reason': f'Email address: "{cleaned_text}"',
                    'confidence': 0.1
                }
        
        # Filter 10: Text quá ngắn nhưng có nghĩa - yêu cầu ít nhất 3 ký tự có chữ
        meaningful_chars = sum(1 for c in cleaned_text if c.isalpha())
        if meaningful_chars < 3:
            return {
                'is_valid': False,
                'reason': f'Too few meaningful characters: "{cleaned_text}" ({meaningful_chars} letters)',
                'confidence': 0.3
            }
        
        # Calculate confidence based on text quality
        confidence = 0.5  # Base confidence
        
        # Boost confidence for longer text
        if len(cleaned_text) > 10:
            confidence += 0.2
        if len(cleaned_text) > 20:
            confidence += 0.2
            
        # Boost confidence for multiple words
        word_count = len([w for w in cleaned_text.split() if any(c.isalpha() for c in w)])
        if word_count >= 2:
            confidence += 0.2
        if word_count >= 4:
            confidence += 0.1
            
        # Boost confidence for sentences (punctuation)
        if any(p in cleaned_text for p in ['.', '!', '?', ';', ':']):
            confidence += 0.1
        
        confidence = min(confidence, 1.0)  # Cap at 1.0
        
        return {
            'is_valid': True,
            'reason': f'Valid text content ({word_count} words, {meaningful_chars} letters)',
            'confidence': confidence
        }
        
    except Exception as e:
        print(f"❌ [TEXT_VALIDATION] Error validating text: {e}")
        return {
            'is_valid': True,  # Default to allowing if error
            'reason': f'Validation error: {e}',
            'confidence': 0.5
        }

def apply_smart_filters():
    """Apply smart filters based on app behavior patterns and text content analysis
    
    Returns:
        dict: {
            'passed': bool,
            'reason': str
        }
    """
    try:
        window_title = get_active_window_title().lower()
        process_name = get_active_window_process_name().lower()
        
        # Filter 1: Excel/Spreadsheet auto-selection patterns
        if any(app in process_name for app in ['excel', 'calc', 'sheets']):
            # In spreadsheet apps, many clicks are just cell navigation
            # We'll be more conservative and require longer drags
            return {
                'passed': True,  # Allow but we'll be more careful
                'reason': 'Spreadsheet app - will apply stricter validation'
            }
        
        # Filter 2: File managers and system apps
        if any(app in process_name for app in ['explorer', 'finder', 'nautilus']):
            return {
                'passed': False,
                'reason': 'File manager detected - likely file selection not text'
            }
        
        # Filter 3: Media applications
        if any(app in process_name for app in ['vlc', 'player', 'spotify', 'media']):
            return {
                'passed': False,
                'reason': 'Media application - unlikely to have text selection'
            }
        
        # Filter 4: Image/Design applications
        if any(app in process_name for app in ['photoshop', 'gimp', 'paint', 'image']):
            return {
                'passed': False,
                'reason': 'Image application - likely graphic selection not text'
            }
        
        # Filter 5: Window title patterns that suggest non-text
        if any(pattern in window_title for pattern in [
            'untitled - paint', 'image viewer', 'photo viewer',
            'video player', 'music player'
        ]):
            return {
                'passed': False,
                'reason': 'Window title suggests non-text application'
            }
        
        # NEW: Filter 6: File extension patterns in window title (file/folder selection)
        file_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg',  # Images
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv',            # Videos
            '.mp3', '.wav', '.flac', '.aac', '.wma',                   # Audio
            '.zip', '.rar', '.7z', '.tar', '.gz',                     # Archives
            '.exe', '.msi', '.dmg', '.deb', '.rpm',                   # Executables
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx' # Documents
        ]
        
        if any(ext in window_title for ext in file_extensions):
            return {
                'passed': False,
                'reason': f'File extension detected in title - likely file selection: {window_title}'
            }
        
        # NEW: Filter 7: Folder/directory patterns
        folder_patterns = [
            '\\', '/', 'folder', 'directory', 'downloads', 'documents',
            'desktop', 'pictures', 'music', 'videos', 'c:', 'd:', 'e:'
        ]
        
        if any(pattern in window_title for pattern in folder_patterns):
            # Additional check: if it looks like a file path
            if ('\\' in window_title and len(window_title.split('\\')) > 2) or \
               ('/' in window_title and len(window_title.split('/')) > 2):
                return {
                    'passed': False,
                    'reason': f'File path pattern detected: {window_title}'
                }
        
        # If we reach here, it passed all filters
        return {
            'passed': True,
            'reason': 'Passed all smart filters'
        }
        
    except Exception as e:
        print(f"❌ [FLOATING V3] Error in smart filters: {e}")
        return {
            'passed': True,  # Default to allowing if error
            'reason': f'Filter error: {e}'
        }

def check_for_new_selection_OLD_METHOD(mouse_x, mouse_y):
    """OLD METHOD: Kiểm tra xem có text mới được select không - DEPRECATED
    
    This function is kept for reference but should not be used.
    Use check_for_text_selection_v3() instead for smart context-aware selection detection.
    """
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

        # Nếu không phải Excel, cũng check pattern tương tự cho các ứng dụng khác
        elif clipboard_changed and current_text and not is_excel_app:
            cleaned_text = current_text.strip()
            
            # Auto-copy patterns from other apps (Google Sheets, LibreOffice, etc.)
            if (len(cleaned_text) < 8 and 
                ('\n' not in cleaned_text) and
                (cleaned_text.replace('.', '').replace(',', '').replace('-', '').isdigit() or  # Numbers
                 len(cleaned_text.split()) <= 1)):  # Single word
                is_excel_auto_copy = True

        if clipboard_changed and has_meaningful_text and is_new_text and not is_excel_auto_copy:
            # Kiểm tra thêm: text không được quá ngắn hoặc chỉ là ký tự đặc biệt
            cleaned_text = current_text.strip()
            
            # Bỏ qua nếu chỉ là 1 ký tự hoặc toàn ký tự đặc biệt/số
            if len(cleaned_text) < 2:

                return
                
            # Bỏ qua nếu toàn là ký tự không phải chữ (số, ký tự đặc biệt)
            if not any(c.isalpha() for c in cleaned_text):

                return
            
            # Kiểm tra thêm cho meaningful content (ít nhất 3 từ hoặc 15 ký tự có ý nghĩa)
            word_count = len([w for w in cleaned_text.split() if any(c.isalpha() for c in w)])
            if word_count < 2 and len(cleaned_text) < 15:

                return
            
            # KIỂM TRA CUỐI CÙNG: Ứng dụng hiện tại có bị loại trừ không
            if is_current_app_excluded():
                print(f"🚫 [FLOATING] Current app excluded, not showing floating button")
                return
            
            # Text hợp lệ, cập nhật last_clipboard_text và hiển thị floating button
            last_clipboard_text = current_text
            show_floating_translate_button(mouse_x, mouse_y)

        else:
            # Debug: in lý do không hiển thị
            if not clipboard_changed:
                pass
            elif not has_meaningful_text:
                pass
            elif not is_new_text:
                pass
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
    
    # Timeout mechanism
    translation_completed = threading.Event()
    translation_result = {'translated': None, 'actual_source': None, 'actual_target': None, 'error': None, 'original_text': None}
    
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
                
                try:
                    # Get translation with actual language info and timeout
                    start_time = time.time()
                    translated, actual_source, actual_target = translate_text(
                        selected_text, 
                        global_language_settings['Ngon_ngu_dau_tien'], 
                        global_language_settings['Ngon_ngu_thu_2'], 
                        global_language_settings['Ngon_ngu_thu_3'],
                        return_language_info=True
                    )
                    
                    # Store successful result
                    translation_result['translated'] = translated
                    translation_result['actual_source'] = actual_source
                    translation_result['actual_target'] = actual_target
                    translation_result['original_text'] = selected_text
                    
                    # Log translation time
                    translation_time = time.time() - start_time
                    print(f"⏱️ [GROUP 1] Translation completed in {translation_time:.2f}s")
                    
                except Exception as e:
                    # Store error result
                    translation_result['error'] = str(e)
                    print(f"❌ [GROUP 1] Translation error: {e}")
                
                # Signal completion regardless of success/failure
                translation_completed.set()
            else:
                # No text selected
                translation_completed.set()
        except Exception as e:
            print(f"❌ [GROUP 1] Unexpected error: {e}")
            translation_result['error'] = f"Unexpected error: {e}"
            translation_completed.set()
        finally:
            root.after(0, restore_system_cursor)
    
    # Start translation in background thread
    threading.Thread(target=do_translate, daemon=True).start()
    
    # Wait for completion with timeout
    def check_translation_status():
        if translation_completed.is_set():
            # Translation completed (success or error)
            def show_result():
                if loading and loading.winfo_exists():
                    loading._running = False
                    loading.destroy()
                
                # Check if there was an error
                if translation_result['error']:
                    from ui.popup import get_app_version
                    version = get_app_version()
                    error_msg = f"❌ Lỗi dịch thuật: {translation_result['error']}"
                    show_popup(error_msg, master=root, version=version, auto_close_enabled=load_auto_close_popup())
                    return
                
                # Check if we have translation result
                if translation_result['translated']:
                    translated = translation_result['translated']
                    actual_source = translation_result['actual_source']
                    actual_target = translation_result['actual_target']
                    
                    # Print result info
                    print(f"✨ [GROUP 1] Translation result: {translated[:50]}..." if len(translated) > 50 else f"✨ [GROUP 1] Translation result: {translated}")
                    
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
                              auto_close_enabled=load_auto_close_popup(),
                              original_text=translation_result.get('original_text'))
                else:
                    # No text selected or other issue
                    pass
            
            root.after(0, show_result)
        else:
            # Check timeout (configurable)
            floating_timeout = config_manager.get_floating_button_timeout()
            if hasattr(check_translation_status, 'start_time'):
                elapsed = time.time() - check_translation_status.start_time
                if elapsed >= floating_timeout:  # Configurable timeout
                    print(f"⏰ [GROUP 1] Translation timeout after {elapsed:.1f}s")
                    def show_timeout():
                        if loading and loading.winfo_exists():
                            loading._running = False
                            loading.destroy()
                        from ui.popup import get_app_version
                        version = get_app_version()
                        timeout_msg = "⏰ Hết thời gian chờ dịch. Vui lòng kiểm tra kết nối mạng và thử lại."
                        show_popup(timeout_msg, master=root, version=version, auto_close_enabled=load_auto_close_popup())
                    root.after(0, show_timeout)
                    return
            else:
                # First call, record start time
                check_translation_status.start_time = time.time()
            
            # Continue checking every 100ms
            root.after(100, check_translation_status)
    
    # Start the timeout checker
    root.after(100, check_translation_status)

def _on_activate_replace():
    loading = show_loading_popup(root)
    
    # Timeout mechanism
    translation_completed = threading.Event()
    translation_result = {'translated': None, 'actual_source': None, 'actual_target': None, 'error': None, 'original_text': None}
    
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
                
                try:
                    # Optimized for replace: No language detection needed, direct translation
                    print(f"🔄 [REPLACE] Calling translate_text with return_language_info=False")
                    start_time = time.time()
                    translated = translate_text(
                        selected_text, 
                        global_language_settings['Ngon_ngu_dau_tien'], 
                        global_language_settings['Ngon_ngu_thu_2'], 
                        global_language_settings['Ngon_ngu_thu_3'],
                        return_language_info=False  # Skip language detection for faster performance
                    )
                    print(f"✅ [REPLACE] Got translation result: {translated[:50]}...")
                    
                    # Store successful result (only translated text needed for replace)
                    translation_result['translated'] = translated
                    translation_result['actual_source'] = None  # Not needed for replace
                    translation_result['actual_target'] = None  # Not needed for replace
                    
                    # Log translation time
                    translation_time = time.time() - start_time
                    print(f"⏱️ [GROUP 1 REPLACE] Translation completed in {translation_time:.2f}s")
                    
                except Exception as e:
                    # Store error result
                    translation_result['error'] = str(e)
                    print(f"❌ [GROUP 1 REPLACE] Translation error: {e}")
                
                # Signal completion regardless of success/failure
                translation_completed.set()
            else:
                # No text selected
                translation_completed.set()
        except Exception as e:
            print(f"❌ [GROUP 1 REPLACE] Unexpected error: {e}")
            translation_result['error'] = f"Unexpected error: {e}"
            translation_completed.set()
        finally:
            root.after(0, restore_system_cursor)
    
    # Start translation in background thread
    threading.Thread(target=do_replace, daemon=True).start()
    
    # Wait for completion with timeout
    def check_translation_status():
        if translation_completed.is_set():
            # Translation completed (success or error)
            def handle_result():
                if loading and loading.winfo_exists():
                    loading._running = False
                    loading.destroy()
                
                # Check if there was an error
                if translation_result['error']:
                    from ui.popup import get_app_version
                    version = get_app_version()
                    error_msg = f"❌ Lỗi dịch thuật: {translation_result['error']}"
                    show_popup(error_msg, master=root, version=version, auto_close_enabled=load_auto_close_popup())
                    return
                
                # Check if we have translation result
                if translation_result['translated']:
                    translated = translation_result['translated']
                    
                    # Print result info
                    print(f"✨ [GROUP 1 REPLACE] Translation result: {translated[:50]}..." if len(translated) > 50 else f"✨ [GROUP 1 REPLACE] Translation result: {translated}")
                    
                    # Perform paste operation
                    def do_paste():
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
                    
                    # Execute paste operation
                    do_paste()
                else:
                    # No text selected or other issue
                    pass
            
            root.after(0, handle_result)
        else:
            # Check timeout (configurable)
            floating_timeout = config_manager.get_floating_button_timeout()
            if hasattr(check_translation_status, 'start_time'):
                elapsed = time.time() - check_translation_status.start_time
                if elapsed >= floating_timeout:  # Configurable timeout
                    print(f"⏰ [GROUP 1 REPLACE] Translation timeout after {elapsed:.1f}s")
                    def show_timeout():
                        if loading and loading.winfo_exists():
                            loading._running = False
                            loading.destroy()
                        from ui.popup import get_app_version
                        version = get_app_version()
                        timeout_msg = "⏰ Hết thời gian chờ dịch. Vui lòng kiểm tra kết nối mạng và thử lại."
                        show_popup(timeout_msg, master=root, version=version, auto_close_enabled=load_auto_close_popup())
                    root.after(0, show_timeout)
                    return
            else:
                # First call, record start time
                check_translation_status.start_time = time.time()
            
            # Continue checking every 100ms
            root.after(100, check_translation_status)
    
    # Start the timeout checker
    root.after(100, check_translation_status)

def _on_activate_translate_group2():
    loading = show_loading_popup(root)
    
    # Timeout mechanism
    translation_completed = threading.Event()
    translation_result = {'translated': None, 'actual_source': None, 'actual_target': None, 'error': None}
    
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
                
                try:
                    # Get translation with actual language info for Group 2
                    start_time = time.time()
                    translated, actual_source, actual_target = translate_text(
                        selected_text, 
                        global_language_settings['Nhom2_Ngon_ngu_dau_tien'], 
                        global_language_settings['Nhom2_Ngon_ngu_thu_2'], 
                        global_language_settings['Nhom2_Ngon_ngu_thu_3'],
                        return_language_info=True
                    )
                    
                    # Store successful result
                    translation_result['translated'] = translated
                    translation_result['actual_source'] = actual_source
                    translation_result['actual_target'] = actual_target
                    
                    # Log translation time
                    translation_time = time.time() - start_time
                    print(f"⏱️ [GROUP 2] Translation completed in {translation_time:.2f}s")
                    
                except Exception as e:
                    # Store error result
                    translation_result['error'] = str(e)
                    print(f"❌ [GROUP 2] Translation error: {e}")
                
                # Signal completion regardless of success/failure
                translation_completed.set()
            else:
                # No text selected
                translation_completed.set()
        except Exception as e:
            print(f"❌ [GROUP 2] Unexpected error: {e}")
            translation_result['error'] = f"Unexpected error: {e}"
            translation_completed.set()
        finally:
            root.after(0, restore_system_cursor)
    
    # Start translation in background thread
    threading.Thread(target=do_translate, daemon=True).start()
    
    # Wait for completion with timeout
    def check_translation_status():
        if translation_completed.is_set():
            # Translation completed (success or error)
            def show_result():
                if loading and loading.winfo_exists():
                    loading._running = False
                    loading.destroy()
                
                # Check if there was an error
                if translation_result['error']:
                    from ui.popup import get_app_version
                    version = get_app_version()
                    error_msg = f"❌ Lỗi dịch thuật: {translation_result['error']}"
                    show_popup(error_msg, master=root, version=version, auto_close_enabled=load_auto_close_popup())
                    return
                
                # Check if we have translation result
                if translation_result['translated']:
                    translated = translation_result['translated']
                    actual_source = translation_result['actual_source']
                    actual_target = translation_result['actual_target']
                    
                    # Print result info
                    print(f"✨ [GROUP 2] Translation result: {translated[:50]}..." if len(translated) > 50 else f"✨ [GROUP 2] Translation result: {translated}")
                    
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
                else:
                    # No text selected or other issue
                    pass
            
            root.after(0, show_result)
        else:
            # Check timeout (configurable)
            floating_timeout = config_manager.get_floating_button_timeout()
            if hasattr(check_translation_status, 'start_time'):
                elapsed = time.time() - check_translation_status.start_time
                if elapsed >= floating_timeout:  # Configurable timeout
                    print(f"⏰ [GROUP 2] Translation timeout after {elapsed:.1f}s")
                    def show_timeout():
                        if loading and loading.winfo_exists():
                            loading._running = False
                            loading.destroy()
                        from ui.popup import get_app_version
                        version = get_app_version()
                        timeout_msg = "⏰ Hết thời gian chờ dịch. Vui lòng kiểm tra kết nối mạng và thử lại."
                        show_popup(timeout_msg, master=root, version=version, auto_close_enabled=load_auto_close_popup())
                    root.after(0, show_timeout)
                    return
            else:
                # First call, record start time
                check_translation_status.start_time = time.time()
            
            # Continue checking every 100ms
            root.after(100, check_translation_status)
    
    # Start the timeout checker
    root.after(100, check_translation_status)

def _on_activate_replace_group2():
    loading = show_loading_popup(root)
    
    # Timeout mechanism
    translation_completed = threading.Event()
    translation_result = {'translated': None, 'actual_source': None, 'actual_target': None, 'error': None}
    
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
                
                try:
                    # Optimized for replace: No language detection needed, direct translation  
                    print(f"🔄 [GROUP 2 REPLACE] Calling translate_text with return_language_info=False")
                    start_time = time.time()
                    translated = translate_text(
                        selected_text, 
                        global_language_settings['Nhom2_Ngon_ngu_dau_tien'], 
                        global_language_settings['Nhom2_Ngon_ngu_thu_2'], 
                        global_language_settings['Nhom2_Ngon_ngu_thu_3'],
                        return_language_info=False  # Skip language detection for faster performance
                    )
                    print(f"✅ [GROUP 2 REPLACE] Got translation result: {translated[:50]}...")
                    
                    # Store successful result (only translated text needed for replace)
                    translation_result['translated'] = translated
                    translation_result['actual_source'] = None  # Not needed for replace
                    translation_result['actual_target'] = None  # Not needed for replace
                    
                    # Log translation time
                    translation_time = time.time() - start_time
                    print(f"⏱️ [GROUP 2 REPLACE] Translation completed in {translation_time:.2f}s")
                    
                except Exception as e:
                    # Store error result
                    translation_result['error'] = str(e)
                    print(f"❌ [GROUP 2 REPLACE] Translation error: {e}")
                
                # Signal completion regardless of success/failure
                translation_completed.set()
            else:
                # No text selected
                translation_completed.set()
        except Exception as e:
            print(f"❌ [GROUP 2 REPLACE] Unexpected error: {e}")
            translation_result['error'] = f"Unexpected error: {e}"
            translation_completed.set()
        finally:
            root.after(0, restore_system_cursor)
    
    # Start translation in background thread
    threading.Thread(target=do_replace, daemon=True).start()
    
    # Wait for completion with timeout
    def check_translation_status():
        if translation_completed.is_set():
            # Translation completed (success or error)
            def handle_result():
                if loading and loading.winfo_exists():
                    loading._running = False
                    loading.destroy()
                
                # Check if there was an error
                if translation_result['error']:
                    from ui.popup import get_app_version
                    version = get_app_version()
                    error_msg = f"❌ Lỗi dịch thuật: {translation_result['error']}"
                    show_popup(error_msg, master=root, version=version, auto_close_enabled=load_auto_close_popup())
                    return
                
                # Check if we have translation result
                if translation_result['translated']:
                    translated = translation_result['translated']
                    
                    # Print result info
                    print(f"✨ [GROUP 2 REPLACE] Translation result: {translated[:50]}..." if len(translated) > 50 else f"✨ [GROUP 2 REPLACE] Translation result: {translated}")
                    
                    # Perform paste operation
                    def do_paste():
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
                    
                    # Execute paste operation
                    do_paste()
                else:
                    # No text selected or other issue
                    pass
            
            root.after(0, handle_result)
        else:
            # Check timeout (configurable)
            floating_timeout = config_manager.get_floating_button_timeout()
            if hasattr(check_translation_status, 'start_time'):
                elapsed = time.time() - check_translation_status.start_time
                if elapsed >= floating_timeout:  # Configurable timeout
                    print(f"⏰ [GROUP 2 REPLACE] Translation timeout after {elapsed:.1f}s")
                    def show_timeout():
                        if loading and loading.winfo_exists():
                            loading._running = False
                            loading.destroy()
                        from ui.popup import get_app_version
                        version = get_app_version()
                        timeout_msg = "⏰ Hết thời gian chờ dịch. Vui lòng kiểm tra kết nối mạng và thử lại."
                        show_popup(timeout_msg, master=root, version=version, auto_close_enabled=load_auto_close_popup())
                    root.after(0, show_timeout)
                    return
            else:
                # First call, record start time
                check_translation_status.start_time = time.time()
            
            # Continue checking every 100ms
            root.after(100, check_translation_status)
    
    # Start the timeout checker
    root.after(100, check_translation_status)

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
    
    # Cập nhật UI trong Advanced tab để sync checkbox state và excluded frame
    try:
        if app and hasattr(app, 'advanced_tab_component'):
            # Cập nhật checkbox state trước khi gọi _update_excluded_frame_state
            if hasattr(app.advanced_tab_component, 'floating_button_enabled'):
                app.advanced_tab_component.floating_button_enabled.set(enabled)
            
            if hasattr(app.advanced_tab_component, '_update_excluded_frame_state'):
                app.advanced_tab_component._update_excluded_frame_state()
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
                activate_screenshot_mode()  # Use config default
                return
                
            # Special handling for Win+Shift+S sequence  
            if (keyboard.Key.cmd in self._pressed and 
                keyboard.Key.shift in self._pressed and 
                key == keyboard.KeyCode.from_char('s')):
                print(f"📸 [FLOATING] Win+Shift+S screenshot sequence detected!")
                activate_screenshot_mode()  # Use config default
                return
                
            # Print Screen variations
            if key == keyboard.Key.print_screen:
                print(f"📸 [FLOATING] Print Screen detected!")
                activate_screenshot_mode()  # Use config default
                return
                
            # ShareX shortcuts
            if (keyboard.Key.ctrl in self._pressed and 
                keyboard.Key.shift in self._pressed and 
                hasattr(key, 'char') and key.char in ['1', '2', '3', '4']):
                print(f"📸 [FLOATING] ShareX shortcut Ctrl+Shift+{key.char} detected!")
                activate_screenshot_mode()  # Use config default
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

# Set tray reference vào GUI để có thể update tray icon
app.set_tray_reference(tray)

# Tạo callback để cập nhật tray icon từ GUI
def update_tray_icon_from_gui():
    """Callback để cập nhật tray icon khi settings thay đổi từ GUI"""
    try:
        if tray and hasattr(tray, 'update_tray_icon'):
            # Lấy update status từ update notifier
            try:
                from core.update_notifier import get_update_notifier
                update_notifier = get_update_notifier()
                has_update, _, _ = update_notifier.get_update_status()
            except Exception:
                has_update = False
            
            # Gọi function update_tray_icon của tray với update status
            tray.update_tray_icon(has_update)
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
        
        # Cleanup GUI components
        if 'app' in globals() and hasattr(app, 'cleanup'):
            app.cleanup()
    except:
        pass

# Register cleanup
atexit.register(cleanup_on_exit)

root.mainloop()
# KHÔNG join listener, KHÔNG dùng with để tránh lỗi thread với Tkinter/ttkbootstrap