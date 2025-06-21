import tkinter as tk
import threading

def show_popup(text):
    def popup():
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes('-topmost', True)
        root.geometry(f"400x100+{root.winfo_pointerx()}+{root.winfo_pointery()}")
        label = tk.Label(root, text=text, wraplength=380, justify='left', bg='yellow', font=('Arial', 12))
        label.pack(fill='both', expand=True)
        # Tự động đóng sau 10 giây
        root.after(10000, root.destroy)
        root.mainloop()
    threading.Thread(target=popup).start()
