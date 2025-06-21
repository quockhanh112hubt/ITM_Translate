import tkinter as tk
import threading

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
