import tkinter as tk
from tkinter import messagebox
import json
import os

class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('ITM Translate')
        self.root.geometry('480x320')
        self.hotkey_manager = None  # Sẽ được gán từ main.py
        self.create_tabs()
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
        tk.Label(self.settings_tab, text=' Dịch popup: "<ctrl>+q" \n Dịch & thay thế: "<ctrl>+d"', font=('Segoe UI', 12, 'bold')).pack(pady=10)

        # sửa hotkeys từ file JSON sau


    def save_settings(self):
        new_hotkeys = {action: entry.get() for action, entry in self.entries.items()}
        # save_hotkeys(new_hotkeys)
        if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
            self.hotkey_manager.update_hotkeys(new_hotkeys)
        messagebox.showinfo('Lưu thành công', 'Đã lưu phím tắt mới!')
