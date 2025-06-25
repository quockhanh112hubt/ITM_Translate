import tkinter as tk
from tkinter import messagebox
import json
import os

class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('ITM Translate')
        self.root.geometry('480x320')
        self.hotkey_manager = None
        self.api_key_updater = None
        self.hotkey_updater = None
        self.startup_callback = None
        self.initial_hotkeys = None
        self.initial_api_key = None
        self.initial_startup = False
    def set_hotkey_manager(self, manager):
        self.hotkey_manager = manager
    def set_api_key_updater(self, updater):
        self.api_key_updater = updater
    def set_hotkey_updater(self, updater):
        self.hotkey_updater = updater
    def set_startup_callback(self, callback):
        self.startup_callback = callback
    def set_initial_settings(self, hotkeys_dict, api_key, startup_enabled=False):
        self.initial_hotkeys = hotkeys_dict
        self.initial_api_key = api_key
        self.initial_startup = startup_enabled
        self.create_tabs()
    def create_tabs(self):
        from tkinter import ttk
        tab_control = ttk.Notebook(self.root)
        self.settings_tab = ttk.Frame(tab_control)
        self.advanced_tab = ttk.Frame(tab_control)
        tab_control.add(self.settings_tab, text='Cài Đặt')
        tab_control.add(self.advanced_tab, text='Nâng Cao')
        tab_control.pack(expand=1, fill='both')
        self.create_settings_tab()
        self.create_advanced_tab()
    def create_settings_tab(self):
        tk.Label(self.settings_tab, text='Cài đặt phím tắt:', font=('Segoe UI', 12, 'bold')).pack(pady=10)
        self.entries = {}
        # Các trường nhập hotkey
        frame = tk.Frame(self.settings_tab)
        frame.pack(pady=5)
        tk.Label(frame, text='Dịch popup:').grid(row=0, column=0, sticky='e')
        self.entries['translate_popup'] = tk.Entry(frame, width=20)
        self.entries['translate_popup'].insert(0, self.initial_hotkeys.get('translate_popup', '<ctrl>+q') if self.initial_hotkeys else '<ctrl>+q')
        self.entries['translate_popup'].grid(row=0, column=1)
        tk.Label(frame, text='Dịch & thay thế:').grid(row=1, column=0, sticky='e')
        self.entries['replace_translate'] = tk.Entry(frame, width=20)
        self.entries['replace_translate'].insert(0, self.initial_hotkeys.get('replace_translate', '<ctrl>+d') if self.initial_hotkeys else '<ctrl>+d')
        self.entries['replace_translate'].grid(row=1, column=1)
        # Trường nhập GEMINI_API_KEY
        tk.Label(self.settings_tab, text='ITM_TRANSLATE_KEY:', font=('Segoe UI', 12, 'bold')).pack(pady=(20, 5))
        self.api_key_entry = tk.Entry(self.settings_tab, width=50, show='*')
        if self.initial_api_key:
            self.api_key_entry.insert(0, self.initial_api_key)
        self.api_key_entry.pack()
        # Nút lưu
        tk.Button(self.settings_tab, text='Lưu cấu hình', command=self.save_settings).pack(pady=15)
    def create_advanced_tab(self):
        # Khởi động cùng Windows
        self.startup_var = tk.BooleanVar(value=self.initial_startup)
        tk.Checkbutton(
            self.advanced_tab,
            text="Khởi động cùng Windows",
            variable=self.startup_var,
            command=self.on_startup_toggle
        ).pack(anchor='w', padx=20, pady=(20, 5))
        # Hướng dẫn sử dụng
        tk.Button(self.advanced_tab, text="Hướng dẫn sử dụng", command=self.show_help).pack(fill='x', padx=20, pady=5)
        # Thông tin về chương trình
        tk.Button(self.advanced_tab, text="Thông tin về chương trình", command=self.show_about).pack(fill='x', padx=20, pady=5)
        # Nút cập nhật chương trình (chưa xử lý logic)
        tk.Button(self.advanced_tab, text="Cập nhật chương trình", command=self.update_program).pack(fill='x', padx=20, pady=5)
    def on_startup_toggle(self):
        enabled = self.startup_var.get()
        # Lưu trạng thái vào file (để nhớ khi khởi động lại)
        try:
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({"startup": enabled}, f)
        except Exception:
            pass
        # Gọi callback để main.py xử lý shortcut
        if self.startup_callback:
            self.startup_callback(enabled)
    def show_help(self):
        messagebox.showinfo("Hướng dẫn sử dụng", "1. Chọn đoạn văn bản cần dịch.\n2. Nhấn phím tắt để dịch hoặc thay thế.\n3. Có thể thay đổi phím tắt và API key trong tab Cài Đặt.")
    def show_about(self):
        messagebox.showinfo("Thông tin", "ITM Translate\nPhiên bản 1.0\nTác giả: KhanhIT ITM Team\nGithub: github.com/ITM_Translate")
    def update_program(self):
        messagebox.showinfo("Cập nhật", "Chức năng cập nhật sẽ được bổ sung sau.")
    def save_settings(self):
        new_hotkeys = {action: entry.get() for action, entry in self.entries.items()}
        if hasattr(self, 'hotkey_updater') and self.hotkey_updater:
            self.hotkey_updater(new_hotkeys)
        api_key = self.api_key_entry.get()
        if api_key and hasattr(self, 'api_key_updater') and self.api_key_updater:
            self.api_key_updater(api_key)
        messagebox.showinfo('Lưu thành công', 'Đã lưu cài đặt mới!')
