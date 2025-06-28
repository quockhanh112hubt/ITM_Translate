import tkinter as tk
from tkinter import messagebox
import json
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('ITM Translate')
        self.root.geometry('850x620')
        self.hotkey_manager = None
        self.api_key_updater = None
        self.hotkey_updater = None
        self.startup_callback = None
        self.initial_hotkeys = None
        self.initial_api_key = None
        self.initial_startup = False
        self.initial_show_on_startup = True
    def set_hotkey_manager(self, manager):
        self.hotkey_manager = manager
    def set_api_key_updater(self, updater):
        self.api_key_updater = updater
    def set_hotkey_updater(self, updater):
        self.hotkey_updater = updater
    def set_startup_callback(self, callback):
        self.startup_callback = callback
    def set_initial_settings(self, hotkeys_dict, api_key, startup_enabled=False, show_on_startup=True):
        self.initial_hotkeys = hotkeys_dict
        self.initial_api_key = api_key
        self.initial_startup = startup_enabled
        self.initial_show_on_startup = show_on_startup
        # Đọc lại ngôn ngữ nếu có
        self.initial_langs = {
            'Ngon_ngu_dau_tien': hotkeys_dict.get('Ngon_ngu_dau_tien', 'Bất kỳ'),
            'Ngon_ngu_thu_2': hotkeys_dict.get('Ngon_ngu_thu_2', 'vi - Tiếng Việt'),
            'Ngon_ngu_thu_3': hotkeys_dict.get('Ngon_ngu_thu_3', 'en - English'),
            'Nhom2_Ngon_ngu_dau_tien': hotkeys_dict.get('Nhom2_Ngon_ngu_dau_tien', 'Bất kỳ'),
            'Nhom2_Ngon_ngu_thu_2': hotkeys_dict.get('Nhom2_Ngon_ngu_thu_2', 'vi - Tiếng Việt'),
            'Nhom2_Ngon_ngu_thu_3': hotkeys_dict.get('Nhom2_Ngon_ngu_thu_3', 'en - English'),
        }
        self.create_tabs()
    def create_tabs(self):
        tab_control = ttk.Notebook(self.root, bootstyle=PRIMARY)
        self.settings_tab = ttk.Frame(tab_control)
        self.advanced_tab = ttk.Frame(tab_control)
        tab_control.add(self.settings_tab, text='Cài Đặt')
        tab_control.add(self.advanced_tab, text='Nâng Cao')
        tab_control.pack(expand=1, fill='both')
        self.create_settings_tab()
        self.create_advanced_tab()
    def create_settings_tab(self):
        style = ttk.Style()
        style.theme_use('flatly')
        title = ttk.Label(self.settings_tab, text='Cài đặt phím tắt & ngôn ngữ', font=('Segoe UI', 18, 'bold'), bootstyle=PRIMARY)
        title.pack(pady=(18, 18))
        self.entries = {}
        self.lang_selects = {}
        lang_list = [
            ('en', 'English'),
            ('vi', 'Tiếng Việt'),
            ('ja', '日本語'),
            ('zh', '中文'),
            ('fr', 'Français'),
            ('de', 'Deutsch'),
            ('ko', '한국어'),
            ('ru', 'Русский'),
            ('es', 'Español'),
            ('th', 'ไทย'),
        ]
        # --- Nhóm 1 ---
        group1 = ttk.Labelframe(self.settings_tab, text='Tuỳ chọn thứ nhất:', bootstyle=INFO)
        group1.pack(padx=24, pady=12, fill='x', ipadx=6, ipady=6)
        for i in range(6):
            group1.columnconfigure(i, weight=1)
        ttk.Label(group1, text='Ngôn ngữ đầu tiên sẽ được dịch tới ngôn ngữ thứ 2, ngôn ngữ thứ 2 sẽ được dịch tới ngôn ngữ thứ 3.', font=('Segoe UI', 9, 'italic'), bootstyle=SECONDARY).grid(row=0, column=0, columnspan=6, sticky='w', padx=8, pady=(6,2))
        ttk.Label(group1, text='Phím tắt:', font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=(8,2), pady=(8,2))
        ttk.Label(group1, text='Dịch popup').grid(row=2, column=0, sticky='e', padx=(8,2), pady=2)
        self.entries['translate_popup'] = ttk.Entry(group1, width=15)
        self.entries['translate_popup'].insert(0, self.initial_hotkeys.get('translate_popup', '<ctrl>+1') if self.initial_hotkeys else '<ctrl>+1')
        self.entries['translate_popup'].grid(row=2, column=1, sticky='w', pady=2)
        ttk.Label(group1, text='Dịch & thay thế').grid(row=3, column=0, sticky='e', padx=(8,2), pady=2)
        self.entries['replace_translate'] = ttk.Entry(group1, width=15)
        self.entries['replace_translate'].insert(0, self.initial_hotkeys.get('replace_translate', '<ctrl>+2') if self.initial_hotkeys else '<ctrl>+2')
        self.entries['replace_translate'].grid(row=3, column=1, sticky='w', pady=2)
        ttk.Label(group1, text='Ngôn ngữ đầu tiên:').grid(row=2, column=2, sticky='e', padx=(18,2), pady=2)
        self.lang_selects['Ngon_ngu_dau_tien'] = ttk.Combobox(group1, values=['Bất kỳ']+[f"{code} - {name}" for code, name in lang_list], width=15, state='readonly')
        self.lang_selects['Ngon_ngu_dau_tien'].set(self.initial_langs.get('Ngon_ngu_dau_tien', 'Bất kỳ'))
        self.lang_selects['Ngon_ngu_dau_tien'].grid(row=2, column=3, sticky='w', pady=2)
        ttk.Label(group1, text='Ngôn ngữ thứ 2:').grid(row=2, column=4, sticky='e', padx=(8,2), pady=2)
        self.lang_selects['Ngon_ngu_thu_2'] = ttk.Combobox(group1, values=[f"{code} - {name}" for code, name in lang_list], width=15, state='readonly')
        self.lang_selects['Ngon_ngu_thu_2'].set(self.initial_langs.get('Ngon_ngu_thu_2', 'vi - Tiếng Việt'))
        self.lang_selects['Ngon_ngu_thu_2'].grid(row=2, column=5, sticky='w', pady=2)
        ttk.Label(group1, text='Ngôn ngữ thứ 3:').grid(row=3, column=2, sticky='e', padx=(18,2), pady=2)
        self.lang_selects['Ngon_ngu_thu_3'] = ttk.Combobox(group1, values=[f"{code} - {name}" for code, name in lang_list], width=15, state='readonly')
        self.lang_selects['Ngon_ngu_thu_3'].set(self.initial_langs.get('Ngon_ngu_thu_3', 'en - English'))
        self.lang_selects['Ngon_ngu_thu_3'].grid(row=3, column=3, sticky='w', pady=2)

        # --- Nhóm 2 ---
        group2 = ttk.Labelframe(self.settings_tab, text='Tuỳ chọn thứ hai:', bootstyle=INFO)
        group2.pack(padx=24, pady=12, fill='x', ipadx=6, ipady=6)
        for i in range(6):
            group2.columnconfigure(i, weight=1)
        ttk.Label(group2, text='Ngôn ngữ đầu tiên sẽ được dịch tới ngôn ngữ thứ 2, ngôn ngữ thứ 2 sẽ được dịch tới ngôn ngữ thứ 3.', font=('Segoe UI', 9, 'italic'), bootstyle=SECONDARY).grid(row=0, column=0, columnspan=6, sticky='w', padx=8, pady=(6,2))
        ttk.Label(group2, text='Phím tắt:', font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=(8,2), pady=(8,2))
        ttk.Label(group2, text='Dịch popup').grid(row=2, column=0, sticky='e', padx=(8,2), pady=2)
        self.entries['translate_popup2'] = ttk.Entry(group2, width=15)
        self.entries['translate_popup2'].insert(0, self.initial_hotkeys.get('translate_popup2', '<ctrl>+q') if self.initial_hotkeys else '<ctrl>+q')
        self.entries['translate_popup2'].grid(row=2, column=1, sticky='w', pady=2)
        ttk.Label(group2, text='Dịch & thay thế').grid(row=3, column=0, sticky='e', padx=(8,2), pady=2)
        self.entries['replace_translate2'] = ttk.Entry(group2, width=15)
        self.entries['replace_translate2'].insert(0, self.initial_hotkeys.get('replace_translate2', '<ctrl>+w') if self.initial_hotkeys else '<ctrl>+w')
        self.entries['replace_translate2'].grid(row=3, column=1, sticky='w', pady=2)
        ttk.Label(group2, text='Ngôn ngữ đầu tiên:').grid(row=2, column=2, sticky='e', padx=(18,2), pady=2)
        self.lang_selects['Nhom2_Ngon_ngu_dau_tien'] = ttk.Combobox(group2, values=['Bất kỳ']+[f"{code} - {name}" for code, name in lang_list], width=15, state='readonly')
        self.lang_selects['Nhom2_Ngon_ngu_dau_tien'].set(self.initial_langs.get('Nhom2_Ngon_ngu_dau_tien', 'Bất kỳ'))
        self.lang_selects['Nhom2_Ngon_ngu_dau_tien'].grid(row=2, column=3, sticky='w', pady=2)
        ttk.Label(group2, text='Ngôn ngữ thứ 2:').grid(row=2, column=4, sticky='e', padx=(8,2), pady=2)
        self.lang_selects['Nhom2_Ngon_ngu_thu_2'] = ttk.Combobox(group2, values=[f"{code} - {name}" for code, name in lang_list], width=15, state='readonly')
        self.lang_selects['Nhom2_Ngon_ngu_thu_2'].set(self.initial_langs.get('Nhom2_Ngon_ngu_thu_2', 'vi - Tiếng Việt'))
        self.lang_selects['Nhom2_Ngon_ngu_thu_2'].grid(row=2, column=5, sticky='w', pady=2)
        ttk.Label(group2, text='Ngôn ngữ thứ 3:').grid(row=3, column=2, sticky='e', padx=(18,2), pady=2)
        self.lang_selects['Nhom2_Ngon_ngu_thu_3'] = ttk.Combobox(group2, values=[f"{code} - {name}" for code, name in lang_list], width=15, state='readonly')
        self.lang_selects['Nhom2_Ngon_ngu_thu_3'].set(self.initial_langs.get('Nhom2_Ngon_ngu_thu_3', 'en - English'))
        self.lang_selects['Nhom2_Ngon_ngu_thu_3'].grid(row=3, column=3, sticky='w', pady=2)

        # Trường nhập ITM_TRANSLATE_KEY
        ttk.Label(self.settings_tab, text='ITM_TRANSLATE_KEY:', font=('Segoe UI', 12, 'bold'), bootstyle=PRIMARY).pack(pady=(28, 5))
        self.api_key_entry = ttk.Entry(self.settings_tab, width=50, show='*')
        if self.initial_api_key:
            self.api_key_entry.insert(0, self.initial_api_key)
        self.api_key_entry.pack()
        ttk.Button(self.settings_tab, text='Lưu cấu hình', style='Custom.TButton', command=self.save_settings, bootstyle=PRIMARY).pack(pady=18)
    def create_advanced_tab(self):
        # Khởi động cùng Windows
        self.startup_var = tk.BooleanVar(value=self.initial_startup)
        tk.Checkbutton(
            self.advanced_tab,
            text="Khởi động cùng Windows",
            variable=self.startup_var,
            command=self.on_startup_toggle
        ).pack(anchor='w', padx=20, pady=(20, 5))
        # Bật hộp thoại khi khởi động
        self.show_on_startup_var = tk.BooleanVar(value=getattr(self, 'initial_show_on_startup', True))
        tk.Checkbutton(
            self.advanced_tab,
            text="Bật hộp thoại này khi khởi động",
            variable=self.show_on_startup_var,
            command=self.on_show_on_startup_toggle
        ).pack(anchor='w', padx=20, pady=(0, 10))
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
            # Đọc trạng thái show_on_startup hiện tại
            show_on_startup = self.show_on_startup_var.get() if hasattr(self, 'show_on_startup_var') else True
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({"startup": enabled, "show_on_startup": show_on_startup}, f)
        except Exception:
            pass
        # Gọi callback để main.py xử lý shortcut
        if self.startup_callback:
            self.startup_callback(enabled)
    def on_show_on_startup_toggle(self):
        # Lưu cả hai trạng thái vào file
        try:
            startup = self.startup_var.get() if hasattr(self, 'startup_var') else False
            show_on_startup = self.show_on_startup_var.get()
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({"startup": startup, "show_on_startup": show_on_startup}, f)
        except Exception:
            pass
    def get_show_on_startup(self):
        return self.show_on_startup_var.get() if hasattr(self, 'show_on_startup_var') else True
    def show_help(self):
        messagebox.showinfo("Hướng dẫn sử dụng", "1. Chọn đoạn văn bản cần dịch.\n2. Nhấn phím tắt để dịch hoặc thay thế.\n3. Có thể thay đổi phím tắt và API key trong tab Cài Đặt.")
    def show_about(self):
        messagebox.showinfo("Thông tin", "ITM Translate\nPhiên bản 1.0\nTác giả: KhanhIT ITM Team\nGithub: github.com/ITM_Translate")
    def update_program(self):
        messagebox.showinfo("Cập nhật", "Chức năng cập nhật sẽ được bổ sung sau.")
    def save_settings(self):
        new_hotkeys = {action: entry.get() for action, entry in self.entries.items()}
        # Lưu lựa chọn ngôn ngữ Nhóm 1
        new_langs = {
            'Ngon_ngu_dau_tien': self.lang_selects['Ngon_ngu_dau_tien'].get(),
            'Ngon_ngu_thu_2': self.lang_selects['Ngon_ngu_thu_2'].get(),
            'Ngon_ngu_thu_3': self.lang_selects['Ngon_ngu_thu_3'].get(),
            # Lưu lựa chọn ngôn ngữ Nhóm 2
            'Nhom2_Ngon_ngu_dau_tien': self.lang_selects['Nhom2_Ngon_ngu_dau_tien'].get(),
            'Nhom2_Ngon_ngu_thu_2': self.lang_selects['Nhom2_Ngon_ngu_thu_2'].get(),
            'Nhom2_Ngon_ngu_thu_3': self.lang_selects['Nhom2_Ngon_ngu_thu_3'].get(),
        }
        config = {**new_hotkeys, **new_langs}
        with open('hotkeys.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        if hasattr(self, 'hotkey_updater') and self.hotkey_updater:
            self.hotkey_updater(config)
        api_key = self.api_key_entry.get()
        if api_key and hasattr(self, 'api_key_updater') and self.api_key_updater:
            self.api_key_updater(api_key)
        messagebox.showinfo('Lưu thành công', 'Đã lưu cài đặt mới!')
