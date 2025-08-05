import tkinter as tk
import threading
import time
import math
import os
import json
from core.api_key_manager import api_key_manager

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
    text_widget.tag_configure("number_orange", foreground='#e67e22', font=('Segoe UI', 12, 'bold'))
    text_widget.tag_configure("keyword_purple", foreground='#8e44ad', font=('Segoe UI', 12, 'bold'))
    text_widget.tag_configure("highlight_yellow", background='#fff3cd', foreground='#856404')
    
    # Insert text only once
    text_widget.insert('1.0', text)
    
    # Apply formatting patterns
    patterns = [
        # [text in brackets] -> Bold dark blue
        (r'\[[^\]]+\]', 'bracket_bold'),
        
        # @tags -> Blue bold
        (r'@[A-Za-z0-9_]+', 'tag_blue'),
        
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
        
        # Numbers - simplified
        (r'[0-9]+\.[0-9]+', 'number_orange'),
        (r'[0-9]+', 'number_orange'),
        
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
        (r'==[^=]+=+', 'highlight_yellow'),
    ]
    
    # Apply each pattern
    for pattern, tag in patterns:
        start = '1.0'
        while True:
            match_start = text_widget.search(pattern, start, tk.END, regexp=True)
            if not match_start:
                break
            
            # Calculate match end
            match_text = text_widget.get(match_start, f"{match_start} lineend")
            match = re.search(pattern, match_text)
            if match:
                match_length = len(match.group(0))
                match_end = f"{match_start}+{match_length}c"
                
                # Apply tag to the match
                text_widget.tag_add(tag, match_start, match_end)
                
                # For **bold** pattern, remove the ** and just keep the text bold
                if pattern == r'\*\*([^*]+)\*\*' and match.group(1):
                    # Replace **text** with just text, but keep it bold
                    text_widget.delete(match_start, match_end)
                    text_widget.insert(match_start, match.group(1))
                    new_end = f"{match_start}+{len(match.group(1))}c"
                    text_widget.tag_add(tag, match_start, new_end)
                    start = new_end
                elif pattern == r'==([^=]+)==' and match.group(1):
                    # Replace ==text== with just text, but keep it highlighted
                    text_widget.delete(match_start, match_end)
                    text_widget.insert(match_start, match.group(1))
                    new_end = f"{match_start}+{len(match.group(1))}c"
                    text_widget.tag_add(tag, match_start, new_end)
                    start = new_end
                else:
                    start = match_end
            else:
                break
    
    # Make links clickable (optional enhancement)
    def make_links_clickable():
        """Make URL and email links clickable"""
        import webbrowser
        
        def open_link(event):
            # Get the text at click position
            index = text_widget.index("@%s,%s" % (event.x, event.y))
            tags = text_widget.tag_names(index)
            
            if 'link_blue' in tags or 'email_blue' in tags:
                # Find the range of the link
                for tag in ['link_blue', 'email_blue']:
                    if tag in tags:
                        ranges = text_widget.tag_ranges(tag)
                        for i in range(0, len(ranges), 2):
                            start, end = ranges[i], ranges[i+1]
                            if text_widget.compare(start, '<=', index) and text_widget.compare(index, '<', end):
                                url = text_widget.get(start, end)
                                if url.startswith('@'):
                                    return  # Don't open @tags
                                if not url.startswith(('http://', 'https://', 'ftp://')):
                                    if '@' in url:
                                        url = f'mailto:{url}'
                                    else:
                                        url = f'http://{url}'
                                try:
                                    webbrowser.open(url)
                                    print(f"🔗 [POPUP] Opened link: {url}")
                                except Exception as e:
                                    print(f"❌ [POPUP] Failed to open link: {e}")
                                return
        
        text_widget.bind('<Button-1>', open_link, add='+')
        text_widget.bind('<Control-Button-1>', open_link, add='+')
    
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

def show_loading_popup(root):
    # Hiện popup nhỏ với hiệu ứng loading spinner dots hiện đại
    loading_win = tk.Toplevel(root)
    loading_win.overrideredirect(True)
    loading_win.attributes('-topmost', True)
    
    # Smart positioning for loading popup
    size = 40
    x, y = get_smart_popup_position(root, size, size)
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

def show_popup(text, master=None, source_lang=None, target_lang=None, version=None, auto_close_enabled=True):
    if master is None:
        master = tk._default_root
    
    # Tạo title với thông tin chi tiết
    title = 'ITM Translate'
    provider_info = api_key_manager.get_provider_info()
    
    if version:
        title += f' v{version}'
    
    if source_lang and target_lang:
        # Handle special cases
        if source_lang.lower() == "mixed":
            source_display = "Multi language"
        else:
            source_display = source_lang.replace('Any Language', 'Auto').replace('Tiếng ', '')
        
        target_display = target_lang.replace('Tiếng ', '')
        
        # Add provider and model info
        provider_name = provider_info['provider'].title()
        model_name = provider_info['model']
        key_preview = provider_info['key_preview']
        
        title += f' *** {source_display} → {target_display} *** {provider_name}'
        if model_name != "auto":
            title += f' ({model_name})'
        title += f' - API: {key_preview}'
    
    win = tk.Toplevel(master)
    win.withdraw()
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
    win.transient(master)
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
        height=height_lines+1,
        borderwidth=0,
        highlightthickness=0,
        selectbackground='#3498db',  # Nice blue selection
        selectforeground='white'
    )
    
    # Apply beautiful text formatting instead of plain insert
    apply_text_formatting(text_widget, text)
    
    text_widget.pack(fill='both', expand=True, padx=0, pady=0)
    text_widget.config(state='normal')
    win.update_idletasks()
    # Đặt width/height cố định dựa trên widget
    req_width = text_widget.winfo_reqwidth()
    req_height = text_widget.winfo_reqheight()
    width = req_width + 20
    height = req_height + 20
    text_widget.config(state='disabled')
    # Cho phép select/copy, không đóng khi click vào text
    def enable_select(event):
        text_widget.config(state='normal')
    def disable_edit(event):
        text_widget.config(state='disabled')
    text_widget.bind('<Button-1>', enable_select)
    text_widget.bind('<KeyRelease>', disable_edit)
    text_widget.bind('<FocusOut>', disable_edit)
    
    # Smart popup positioning
    x, y = get_smart_popup_position(master, width, height)
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
