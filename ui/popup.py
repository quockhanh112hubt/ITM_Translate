import tkinter as tk
import threading
import time
import math
import os
import json

def get_app_version():
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
    x = loading_win.winfo_pointerx()
    y = loading_win.winfo_pointery()
    size = 40
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

def show_popup(text, master=None, source_lang=None, target_lang=None, version=None):
    if master is None:
        master = tk._default_root
    
    # Tạo title với thông tin chi tiết
    title = 'ITM Translate'
    if version:
        title += f' v{version}'
    if source_lang and target_lang:
        # Rút gọn tên ngôn ngữ nếu quá dài
        source_display = source_lang.replace('Any Language', 'Auto').replace('Tiếng ', '')
        target_display = target_lang.replace('Tiếng ', '')
        title += f' - {source_display} → {target_display}'
    
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
        fg='#222',
        font=('Segoe UI', 12),
        width=max_chars_per_line,
        height=height_lines+1,
        borderwidth=0,
        highlightthickness=0
    )
    text_widget.insert('1.0', text)
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
    x = win.winfo_pointerx()
    y = win.winfo_pointery()
    win.geometry(f"{width}x{height}+{x}+{y}")
    # Chỉ đóng khi focus ra ngoài toàn bộ popup
    def on_popup_focus_out(event):
        # Nếu focus ra ngoài cửa sổ popup (không phải text_widget)
        if win.focus_get() not in (text_widget, win):
            win.destroy()
    win.bind('<FocusOut>', on_popup_focus_out)
    win.deiconify()
    win.lift()
