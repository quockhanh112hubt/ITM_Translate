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
        self.initial_hotkeys = None
        self.initial_api_key = None
        self.create_tabs()
    def set_hotkey_manager(self, manager):
        self.hotkey_manager = manager
    def set_api_key_updater(self, updater):
        self.api_key_updater = updater
    def set_hotkey_updater(self, updater):
        self.hotkey_updater = updater
    def set_initial_settings(self, hotkeys_dict, api_key):
        self.initial_hotkeys = hotkeys_dict
        self.initial_api_key = api_key
    def create_tabs(self):
        from tkinter import ttk
        tab_control = ttk.Notebook(self.root)
        self.settings_tab = ttk.Frame(tab_control)
        tab_control.add(self.settings_tab, text='Cài đặt')
        tab_control.pack(expand=1, fill='both')
        self.create_settings_tab()
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
        tk.Label(self.settings_tab, text='GEMINI_API_KEY:', font=('Segoe UI', 12, 'bold')).pack(pady=(20, 5))
        self.api_key_entry = tk.Entry(self.settings_tab, width=50, show='*')
        if self.initial_api_key:
            self.api_key_entry.insert(0, self.initial_api_key)
        self.api_key_entry.pack()
        # Nút lưu
        tk.Button(self.settings_tab, text='Lưu', command=self.save_settings).pack(pady=15)
    def save_settings(self):
        new_hotkeys = {action: entry.get() for action, entry in self.entries.items()}
        if hasattr(self, 'hotkey_updater') and self.hotkey_updater:
            self.hotkey_updater(new_hotkeys)
        api_key = self.api_key_entry.get()
        if api_key and hasattr(self, 'api_key_updater') and self.api_key_updater:
            self.api_key_updater(api_key)
        messagebox.showinfo('Lưu thành công', 'Đã lưu cài đặt mới!')
