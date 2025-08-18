import tkinter as tk
import threading
import time
import math
import os
import json
from core.api_key_manager import api_key_manager

# Import language config with fallback
try:
    from core.language_config import get_main_languages, map_language_to_code
    LANGUAGE_CONFIG_AVAILABLE = True
except ImportError:
    LANGUAGE_CONFIG_AVAILABLE = False
    print("Warning: Language config module not available, using fallback")

def get_app_version():
    """Đọc version từ file version.json"""
    try:
        # Thử đọc từ thư mục gốc trước
        version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.json")
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', '1.0.0')
        
        # Thử đọc từ core/version.json
        core_version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "core", "version.json")
        if os.path.exists(core_version_file):
            with open(core_version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', '1.0.0')
    except Exception:
        pass
    return '1.0.0'

def get_smart_popup_position(master, popup_width, popup_height, mouse_x=None, mouse_y=None):
    """
    Calculate smart popup position to keep it visible on screen
    
    Args:
        master: Parent window
        popup_width: Width of popup
        popup_height: Height of popup
        mouse_x, mouse_y: Mouse position (if None, will get current position)
    
    Returns:
        tuple: (x, y) position for popup
    """
    try:
        # Get screen dimensions
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        
        # Get mouse position if not provided
        if mouse_x is None:
            mouse_x = master.winfo_pointerx()
        if mouse_y is None:
            mouse_y = master.winfo_pointery()
        
        # Default offset from mouse cursor
        offset_x = 20
        offset_y = 20
        
        # Calculate initial position
        x = mouse_x + offset_x
        y = mouse_y + offset_y
        
        # Adjust if popup would go off-screen (right edge)
        if x + popup_width > screen_width:
            x = mouse_x - popup_width - offset_x  # Position to the left of cursor
            
        # Adjust if popup would go off-screen (bottom edge)
        if y + popup_height > screen_height:
            y = mouse_y - popup_height - offset_y  # Position above cursor
            
        # Ensure popup doesn't go off-screen (left edge)
        if x < 0:
            x = 10  # Small margin from left edge
            
        # Ensure popup doesn't go off-screen (top edge)
        if y < 0:
            y = 10  # Small margin from top edge
            
        # Final boundary check
        x = max(10, min(x, screen_width - popup_width - 10))
        y = max(10, min(y, screen_height - popup_height - 10))
        
        print(f"🎯 [POPUP] Smart positioning: mouse({mouse_x},{mouse_y}) → popup({x},{y}) size({popup_width}x{popup_height}) screen({screen_width}x{screen_height})")
        
        return x, y
        
    except Exception as e:
        print(f"❌ [POPUP] Error calculating smart position: {e}")
        # Fallback to simple positioning
        return mouse_x or 100, mouse_y or 100

def apply_text_formatting(text_widget, text):
    """
    Apply beautiful text formatting with colors and styles
    
    Temporarily disabled to avoid regex issues. Just insert plain text.
    """
    import re
    
    # Configure text formatting tags
    text_widget.tag_configure("bold", font=('Segoe UI', 12, 'bold'))
    text_widget.tag_configure("italic", font=('Segoe UI', 12, 'italic'))
    text_widget.tag_configure("bracket_bold", font=('Segoe UI', 12, 'bold'), foreground='#2c3e50')
    text_widget.tag_configure("tag_blue", foreground='#3498db', font=('Segoe UI', 12, 'bold'))
    text_widget.tag_configure("link_blue", foreground='#2980b9', underline=True, font=('Segoe UI', 12))
    text_widget.tag_configure("email_blue", foreground='#2980b9', underline=True)
    text_widget.tag_configure("time_green", foreground='#27ae60', font=('Segoe UI', 12, 'bold'))
    text_widget.tag_configure("number_orange", foreground='#27ae60', font=('Segoe UI', 12, 'bold'))
    text_widget.tag_configure("keyword_purple", foreground='#8e44ad', font=('Segoe UI', 12, 'bold'))
    text_widget.tag_configure("highlight_yellow", background='#fff3cd', foreground='#856404')
    
    # Insert text only once
    text_widget.insert('1.0', text)
    
    # Apply formatting patterns using Python regex instead of tkinter search
    patterns = [
        # @tags -> Blue bold (support Unicode characters for international names)
        (r'@[\w\u00C0-\u017F\u1EA0-\u1EF9\uAC00-\uD7AF\u4E00-\u9FFF]+', 'tag_blue'),
        
        # [text in brackets] -> Bold dark blue
        (r'\[[^\]]+\]', 'bracket_bold'),
        
        # URLs (http/https/ftp) - simplified
        (r'https://[^ \t\n\r<>"]+', 'link_blue'),
        (r'http://[^ \t\n\r<>"]+', 'link_blue'),
        (r'ftp://[^ \t\n\r<>"]+', 'link_blue'),
        
        # Email addresses - simplified
        (r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', 'email_blue'),
        
        # Time stamps [HH:MM] or (HH:MM) - simplified
        (r'\[[0-9]{1,2}:[0-9]{2}\]', 'time_green'),
        (r'\([0-9]{1,2}:[0-9]{2}\)', 'time_green'),
        (r'[0-9]{1,2}:[0-9]{2} *AM', 'time_green'),
        (r'[0-9]{1,2}:[0-9]{2} *PM', 'time_green'),
        
        # **bold** markdown style - simplified
        (r'\*\*[^*]+\*\*', 'bold'),
        
        # Keywords - simplified
        (r'ERROR', 'keyword_purple'),
        (r'FAILED', 'keyword_purple'),
        (r'SUCCESS', 'keyword_purple'),
        (r'WARNING', 'keyword_purple'),
        (r'INFO', 'keyword_purple'),
        (r'DEBUG', 'keyword_purple'),
        (r'CRITICAL', 'keyword_purple'),
        
        # Highlighted text with ==text== - simplified
        (r'==[^=]+==', 'highlight_yellow'),
        
        # Numbers - simplified (put at end to avoid overriding other patterns)
        (r'\b[0-9]+\.[0-9]+\b', 'number_orange'),
        (r'\b[0-9]+\b', 'number_orange'),
    ]
    
    # Apply each pattern using Python regex
    for pattern, tag in patterns:
        try:
            for match in re.finditer(pattern, text):
                start_pos = f"1.0+{match.start()}c"
                end_pos = f"1.0+{match.end()}c"
                text_widget.tag_add(tag, start_pos, end_pos)
        except Exception as e:
            print(f"❌ Error applying pattern {pattern}: {e}")
            continue
    
    # Make links clickable (optional enhancement)
    def make_links_clickable():
        """Make URL and email links clickable"""
        import webbrowser
        
        def open_link(event):
            # Get the text at click position
            index = text_widget.index("@%s,%s" % (event.x, event.y))
            tags = text_widget.tag_names(index)
            
            print(f"🔍 [CLICK] Clicked at {index}, tags: {tags}")
            
            if 'link_blue' in tags or 'email_blue' in tags:
                # Find the range of the link
                for tag in ['link_blue', 'email_blue']:
                    if tag in tags:
                        ranges = text_widget.tag_ranges(tag)
                        for i in range(0, len(ranges), 2):
                            start, end = ranges[i], ranges[i+1]
                            if text_widget.compare(start, '<=', index) and text_widget.compare(index, '<', end):
                                url = text_widget.get(start, end)
                                print(f"🔗 [CLICK] Found URL: '{url}'")
                                
                                if url.startswith('@'):
                                    return  # Don't open @tags
                                    
                                # Prepare URL for opening
                                if not url.startswith(('http://', 'https://', 'ftp://')):
                                    if '@' in url:
                                        url = f'mailto:{url}'
                                    else:
                                        url = f'https://{url}'
                                        
                                try:
                                    webbrowser.open(url)
                                    print(f"✅ [POPUP] Opened link: {url}")
                                except Exception as e:
                                    print(f"❌ [POPUP] Failed to open link: {e}")
                                return
        
        def on_motion(event):
            """Change cursor when hovering over links"""
            index = text_widget.index("@%s,%s" % (event.x, event.y))
            tags = text_widget.tag_names(index)
            
            if 'link_blue' in tags or 'email_blue' in tags:
                text_widget.config(cursor='hand2')
            else:
                text_widget.config(cursor='')
        
        # Bind click events
        text_widget.bind('<Button-1>', open_link)
        text_widget.bind('<Motion>', on_motion)
        
        # Also bind additional events for better UX
        text_widget.bind('<Control-Button-1>', open_link)
        text_widget.bind('<Double-Button-1>', open_link)
    
    # Enable clickable links
    make_links_clickable()
    
    print(f"🎨 [POPUP] Applied text formatting with {len(patterns)} pattern rules")
    """Lấy version hiện tại từ file version.json"""
    try:
        # Thử đọc từ core/version.json trước
        core_version_file = os.path.join(os.path.dirname(__file__), "..", "core", "version.json")
        if os.path.exists(core_version_file):
            with open(core_version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', '1.0.0')
        
        # Fallback: đọc từ version.json gốc
        version_file = os.path.join(os.path.dirname(__file__), "..", "version.json")
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', '1.0.0')
    except Exception:
        pass
    return '1.0.0'

def show_loading_popup(root=None):
    # Hiện popup nhỏ với hiệu ứng loading spinner dots hiện đại - independent
    loading_win = tk.Toplevel()
    loading_win.overrideredirect(True)
    loading_win.attributes('-topmost', True)
    
    # Smart positioning for loading popup
    size = 40
    x, y = get_smart_popup_position(loading_win, size, size)
    loading_win.geometry(f"{size}x{size}+{x}+{y}")

    canvas = tk.Canvas(loading_win, width=size, height=size, bg='white', highlightthickness=0)
    canvas.pack(fill='both', expand=True)

    # Làm nền cửa sổ trong suốt (chỉ Windows)
    try:
        loading_win.wm_attributes('-transparentcolor', 'white')
    except tk.TclError:
        # Nếu không hỗ trợ, có thể dùng alpha cho toàn bộ cửa sổ
        loading_win.attributes('-alpha', 0.92)

    num_dots = 8
    radius = 12
    dot_radius = 3
    dots = []
    center = size // 2

    # Tạo các chấm tròn
    for i in range(num_dots):
        angle = 2 * math.pi * i / num_dots
        x0 = center + radius * math.cos(angle) - dot_radius
        y0 = center + radius * math.sin(angle) - dot_radius
        x1 = center + radius * math.cos(angle) + dot_radius
        y1 = center + radius * math.sin(angle) + dot_radius
        dot = canvas.create_oval(x0, y0, x1, y1, fill='#1e90ff', outline='', stipple='gray50')
        dots.append(dot)

    loading_win._running = True
    def animate(frame=0):
        if getattr(loading_win, "_running", True):
            for i, dot in enumerate(dots):
                # Tạo hiệu ứng mờ dần cho các chấm
                alpha = (i - frame) % num_dots
                alpha = 0.3 + 0.7 * (1 - alpha / (num_dots-1))  # alpha giảm dần
                color = "#1e90ff"
                # Đổi màu theo alpha (giả lập bằng thay đổi độ sáng)
                r, g, b = 30, 144, 255
                r = int(r + (255 - r) * (1 - alpha))
                g = int(g + (255 - g) * (1 - alpha))
                b = int(b + (255 - b) * (1 - alpha))
                hex_color = f'#{r:02x}{g:02x}{b:02x}'
                canvas.itemconfig(dot, fill=hex_color)
            loading_win.after(60, animate, (frame + 1) % num_dots)
    animate()
    return loading_win

def show_popup(text, master=None, source_lang=None, target_lang=None, version=None, auto_close_enabled=True, original_text=None):
    # Create independent popup window (not tied to master)
    win = tk.Toplevel()
    win.withdraw()
    win.title('ITM Translate')
    # Create independent popup window (not tied to master)
    win = tk.Toplevel()
    win.withdraw()
    win.title('ITM Translate')
    
    # Build title with language settings from configuration
    title = 'ITM Translate'
    provider_info = api_key_manager.get_provider_info()
    
    if version:
        title += f' v{version}'
    
    # SIMPLIFIED: Use fixed language display from settings
    if LANGUAGE_CONFIG_AVAILABLE:
        try:
            main_languages = get_main_languages()
            
            # Display format: "Any Language → Primary → Secondary"  
            title += f' *** Auto → {main_languages["source"]} → {main_languages["target"]} ***'
            
            # Add provider and model info
            provider_name = provider_info['provider'].title()
            model_name = provider_info['model']
            key_preview = provider_info['key_preview']
            
            title += f' {provider_name}'
            if model_name != "auto":
                title += f' ({model_name})'
            title += f' - API: {key_preview}'
            
        except Exception as e:
            print(f"Warning: Could not get language config for popup title: {e}")
            # Fallback to basic title if language config fails
            provider_name = provider_info['provider'].title()
            title += f' *** {provider_name} ***'
    else:
        # Fallback when language config module is not available
        provider_name = provider_info['provider'].title()
        model_name = provider_info['model'] 
        key_preview = provider_info['key_preview']
        
        title += f' *** Auto → Vietnamese → English *** {provider_name}'
        if model_name != "auto":
            title += f' ({model_name})'
        title += f' - API: {key_preview}'
    
    win.title(title)
    win.attributes('-topmost', True)
    # Đặt icon cho popup nếu có icon.ico
    try:
        import os
        icon_path_ico = os.path.join(os.path.dirname(__file__), "..", "Resource", "icon.ico")
        icon_path_ico = os.path.abspath(icon_path_ico)
        if os.path.exists(icon_path_ico):
            win.iconbitmap(icon_path_ico)
    except Exception:
        pass
    # Remove transient to make popup independent
    # win.transient(master)  # Commented out to make popup independent
    # Tạo frame với màu nền nhẹ, viền bo tròn
    frame = tk.Frame(win, bg='#f8f9fa', bd=2, relief='groove')
    frame.pack(fill='both', expand=True, padx=10, pady=10)
    # Đặt width cố định cho Text widget để text tự động xuống dòng
    max_chars_per_line = 70
    # Tính số dòng thực tế dựa trên số ký tự mỗi dòng (wrap word)
    import textwrap
    wrapped_lines = []
    for line in text.splitlines() or ['']:
        wrapped_lines.extend(textwrap.wrap(line, width=max_chars_per_line) or [''])
    num_lines = len(wrapped_lines)
    height_lines = min(max(num_lines, 2), 20)  # min 2, max 20 dòng
    text_widget = tk.Text(
        frame,
        wrap='word',
        bg='#f8f9fa',
        fg='#2c3e50',  # Darker text for better contrast
        font=('Segoe UI', 12),
        width=max_chars_per_line,
        height=height_lines+2,  # Increase height by +2 for better spacing
        borderwidth=0,
        highlightthickness=0,
        selectbackground='#3498db',  # Nice blue selection
        selectforeground='white'
    )
    
    # Apply beautiful text formatting instead of plain insert
    apply_text_formatting(text_widget, text)
    
    text_widget.pack(fill='both', expand=True, padx=0, pady=0)  # No padding at all for tight fit
    text_widget.config(state='normal')
    
    # ===== FOOTER SECTION =====
    # Add a subtle separator line above footer
    separator = tk.Frame(frame, bg='#ced4da', height=1)
    separator.pack(fill='x', side='bottom', padx=0, pady=0)
    
    # Create a footer frame at the bottom with distinct styling
    footer_frame = tk.Frame(frame, bg='#dee2e6', relief='flat', bd=0, height=45)
    footer_frame.pack(fill='x', side='bottom', padx=0, pady=0)
    footer_frame.pack_propagate(False)  # Prevent frame from shrinking
    
    # Get all available API keys for comparison buttons
    all_keys = api_key_manager.get_all_keys()
    print(f"🔑 [POPUP] Found {len(all_keys)} API keys for comparison buttons")
    
    # Create footer content with buttons and info
    footer_content_frame = tk.Frame(footer_frame, bg='#dee2e6')
    footer_content_frame.pack(fill='both', expand=True, padx=5, pady=2)
    print(f"🔑 [POPUP] Found {len(all_keys)} API keys for comparison buttons")
    
    if len(all_keys) > 1:  # Only show buttons if multiple providers available
        # Left side: buttons, Right side: info text
        # Buttons container (left side)
        buttons_container = tk.Frame(footer_content_frame, bg='#dee2e6')
        buttons_container.pack(side='left', fill='y')
        
        # Info text (right side)
        info_label = tk.Label(
            footer_content_frame,
            text=f"ITM Translate v{get_app_version()} - Quick Translate",
            bg='#dee2e6',
            fg='#495057',
            font=('Segoe UI', 8, 'italic'),
            anchor='e'
        )
        info_label.pack(side='right', fill='y', pady=3)
        
        # Store original text for comparison
        original_text_for_comparison = original_text if original_text is not None else text
        
        # Function to handle provider button clicks
        def on_provider_button_click(provider_name):
            """Handle click on provider comparison button"""
            def handler():
                try:
                    print(f"🔄 [UI] Comparing with {provider_name}...")
                    
                    # Import here to avoid circular import
                    from core.translator import translate_with_specific_provider
                    
                    # Show loading state
                    text_widget.config(state='normal')
                    text_widget.delete(1.0, tk.END)
                    text_widget.insert(1.0, f"🔄 Translating with {provider_name}...")
                    text_widget.config(state='disabled')
                    text_widget.update()
                    
                    # Get target languages from window title or use defaults
                    # Extract from title: "*** source → target ***"
                    title_text = win.title()
                    if "→" in title_text:
                        try:
                            lang_part = title_text.split("***")[1].strip()
                            source_lang, target_lang = lang_part.split("→")
                            source_lang = source_lang.strip()
                            target_lang = target_lang.strip()
                        except:
                            source_lang, target_lang = "English", "Vietnamese"
                    else:
                        source_lang, target_lang = "English", "Vietnamese"
                    
                    # Convert display names to internal format
                    lang_mapping = {
                        "Auto": "english", "English": "english", "Vietnamese": "vietnamese",
                        "Korean": "korean", "Japanese": "japanese", "Chinese": "chinese"
                    }
                    
                    ngon_ngu_thu_2 = lang_mapping.get(target_lang, "vietnamese")
                    ngon_ngu_thu_3 = lang_mapping.get(source_lang, "english")
                    
                    # SIMPLIFIED: Call translation with specific provider (uses config languages)
                    result = translate_with_specific_provider(
                        original_text_for_comparison, 
                        provider_name
                    )
                    
                    # Handle tuple result (translated_text, detected_lang, target_lang)
                    if isinstance(result, tuple) and len(result) == 3:
                        translated_text, detected_lang, target_lang = result
                        
                        # Update popup with new result
                        text_widget.config(state='normal')
                        text_widget.delete(1.0, tk.END)
                        apply_text_formatting(text_widget, translated_text)
                        text_widget.config(state='disabled')
                        
                        # Update title with actual language info
                        from ui.popup import get_app_version
                        version = get_app_version()
                        
                        # Create title with actual detected and target languages
                        title_prefix = f'ITM Translate v{version}' if version else 'ITM Translate'
                        language_info = f"{detected_lang} → {target_lang}"
                        new_title = f"{title_prefix} *** {language_info} *** - {provider_name}"
                        
                    else:
                        # Handle error message (string)
                        text_widget.config(state='normal')
                        text_widget.delete(1.0, tk.END)
                        text_widget.insert(1.0, str(result))
                        text_widget.config(state='disabled')
                        
                        # Keep original title format for errors
                        current_title = win.title()
                        if " - " in current_title:
                            base_title = current_title.split(" - ")[0]
                        else:
                            base_title = current_title
                        new_title = f"{base_title} - {provider_name}"
                    
                    # Set the new title
                    win.title(new_title)
                    
                    print(f"✅ [UI] Updated popup with {provider_name} result")
                    
                except Exception as e:
                    print(f"❌ [UI] Error with {provider_name}: {e}")
                    text_widget.config(state='normal')
                    text_widget.delete(1.0, tk.END)
                    text_widget.insert(1.0, f"❌ Error with {provider_name}: {str(e)}")
                    text_widget.config(state='disabled')
            
            return handler
        
        # Create buttons for each provider (excluding current active one)
        current_active = api_key_manager.get_active_key()
        button_count = 0
        
        for key_info in all_keys:
            # Skip if this is the currently active provider 
            if current_active and key_info.name == current_active.name:
                continue
                
            # Create button
            btn = tk.Button(
                buttons_container,
                text=key_info.name,
                command=on_provider_button_click(key_info.name),
                bg='#6c757d',
                fg='white',
                font=('Segoe UI', 9),
                relief='flat',
                padx=12,
                pady=4,
                cursor='hand2'
            )
            
            # Pack with minimal spacing
            btn.pack(side='left', padx=(0, 4), pady=1)
            button_count += 1
            
            # Limit to 5 buttons per row to avoid overcrowding
            if button_count >= 5:
                break
    else:
        # If only one provider, just show info text
        info_label = tk.Label(
            footer_content_frame,
            text=f"ITM Translate v{get_app_version()}",
            bg='#dee2e6',
            fg='#495057',
            font=('Segoe UI', 8, 'italic')
        )
        info_label.pack(pady=3)
    
    win.update_idletasks()
    # Đặt width/height cố định dựa trên widget
    req_width = text_widget.winfo_reqwidth()
    req_height = text_widget.winfo_reqheight()
    
    # Add extra height for buttons and footer if they exist
    extra_height = 80 if len(all_keys) > 1 else 25  # Footer always adds some height
    
    width = req_width + 20
    height = req_height + 25 + extra_height  # Moderate base height with footer
    text_widget.config(state='disabled')
    
    # Combined click handler for both link opening and text selection
    def on_click(event):
        # Check if clicking on a link first
        index = text_widget.index("@%s,%s" % (event.x, event.y))
        tags = text_widget.tag_names(index)
        
        print(f"🔍 [CLICK] Clicked at {index}, tags: {tags}")
        
        if 'link_blue' in tags or 'email_blue' in tags:
            # Handle link click - don't enable editing
            import webbrowser
            
            for tag in ['link_blue', 'email_blue']:
                if tag in tags:
                    ranges = text_widget.tag_ranges(tag)
                    for i in range(0, len(ranges), 2):
                        start, end = ranges[i], ranges[i+1]
                        if text_widget.compare(start, '<=', index) and text_widget.compare(index, '<', end):
                            url = text_widget.get(start, end)
                            print(f"🔗 [CLICK] Found URL: '{url}'")
                            
                            if url.startswith('@'):
                                return  # Don't open @tags
                                
                            # Prepare URL for opening
                            if not url.startswith(('http://', 'https://', 'ftp://')):
                                if '@' in url:
                                    url = f'mailto:{url}'
                                else:
                                    url = f'https://{url}'
                                    
                            try:
                                webbrowser.open(url)
                                print(f"✅ [POPUP] Opened link: {url}")
                            except Exception as e:
                                print(f"❌ [POPUP] Failed to open link: {e}")
                            return  # Don't enable text editing after opening link
        
        # If not clicking on a link, temporarily enable selection but prevent editing
        text_widget.config(state='normal')
        # Schedule to disable editing after a brief moment to allow selection
        text_widget.after(10, lambda: text_widget.config(state='disabled'))
    
    def on_motion(event):
        """Change cursor when hovering over links"""
        index = text_widget.index("@%s,%s" % (event.x, event.y))
        tags = text_widget.tag_names(index)
        
        if 'link_blue' in tags or 'email_blue' in tags:
            text_widget.config(cursor='hand2')
        else:
            text_widget.config(cursor='')
            
    def on_key_press(event):
        """Prevent all text editing via keyboard"""
        # Allow selection keys but block editing keys
        allowed_keys = {'Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Prior', 'Next', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R'}
        if event.keysym not in allowed_keys and not (event.state & 0x4):  # Not Ctrl key combination
            return 'break'  # Block the key press
    
    def on_selection_change(event):
        """Keep text widget disabled after selection"""
        text_widget.after(50, lambda: text_widget.config(state='disabled'))
        
    # Bind events
    text_widget.bind('<Button-1>', on_click)
    text_widget.bind('<Motion>', on_motion)
    text_widget.bind('<KeyPress>', on_key_press)
    text_widget.bind('<ButtonRelease-1>', on_selection_change)
    
    # Smart popup positioning (independent of master window)
    x, y = get_smart_popup_position(win, width, height)
    win.geometry(f"{width}x{height}+{x}+{y}")
    
    # Chỉ đóng tự động khi auto_close_enabled=True
    if auto_close_enabled:
        def on_popup_focus_out(event):
            # Nếu focus ra ngoài cửa sổ popup (không phải text_widget)
            if win.focus_get() not in (text_widget, win):
                win.destroy()
        win.bind('<FocusOut>', on_popup_focus_out)
    
    win.deiconify()
    win.lift()
