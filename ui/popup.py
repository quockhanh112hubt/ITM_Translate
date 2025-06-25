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

def show_popup(text):
    def popup():
        root = tk.Tk()
        root.title('ITM Translate')
        root.attributes('-topmost', True)
        # Tạo frame với màu nền nhẹ, viền bo tròn
        frame = tk.Frame(root, bg='#f8f9fa', bd=2, relief='groove')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        # Label nội dung dịch với font hiện đại, padding, màu chữ tối
        label = tk.Label(
            frame,
            text=text,
            wraplength=500,
            justify='left',
            bg='#f8f9fa',
            fg='#222',
            font=('Segoe UI', 12),
            anchor='w',
            padx=16,
            pady=12
        )
        label.pack(fill='both', expand=True)
        # Tính toán kích thước phù hợp
        root.update_idletasks()
        width = min(max(label.winfo_reqwidth() + 40, 320), 600)
        height = min(label.winfo_reqheight() + 40, 1200)
        x = root.winfo_pointerx()
        y = root.winfo_pointery()
        root.geometry(f"{width}x{height}+{x}+{y}")

        # Đóng khi click ra ngoài
        def on_focus_out(event):
            root.destroy()
        root.bind('<FocusOut>', on_focus_out)

        root.mainloop()
    threading.Thread(target=popup).start()
