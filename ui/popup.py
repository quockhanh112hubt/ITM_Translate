import tkinter as tk
import threading
import time
import math

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

def show_popup(text, master=None):
    if master is None:
        master = tk._default_root
    win = tk.Toplevel(master)
    win.withdraw()
    win.title('ITM Translate')
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
    # Đặt width cho Text widget vừa phải, wrap word
    num_lines = text.count('\n') + 1
    text_widget = tk.Text(
        frame,
        wrap='word',
        bg='#f8f9fa',
        fg='#222',
        font=('Segoe UI', 12),
        height=min(max(num_lines, 2), 20),
        width=50,  # width theo ký tự
        borderwidth=0,
        highlightthickness=0
    )
    text_widget.insert('1.0', text)
    text_widget.pack(fill='both', expand=True, padx=0, pady=0)
    text_widget.config(state='normal')
    win.update_idletasks()
    # Lấy kích thước yêu cầu thực tế
    req_width = text_widget.winfo_reqwidth()
    req_height = text_widget.winfo_reqheight()
    width = min(max(req_width + 20, 320), 600)
    height = min(max(req_height + 20, 60), 1200)
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
