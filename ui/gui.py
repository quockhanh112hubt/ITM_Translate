import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import json
import os
import sys
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import keyboard
import threading
import subprocess


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

class MainGUI:
    def __init__(self, root):
        self.root = root
        # Đọc version và set title với version
        app_version = get_app_version()
        self.root.title(f'ITM Translate v{app_version}')
        self.root.geometry('1050x420')
        self.hotkey_manager = None
        self.hotkey_updater = None
        self.startup_callback = None
        self.initial_hotkeys = None
        self.initial_api_key = None
        self.initial_startup = False
        self.initial_show_on_startup = True
    def set_hotkey_manager(self, manager):
        self.hotkey_manager = manager
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
            'Ngon_ngu_dau_tien': hotkeys_dict.get('Ngon_ngu_dau_tien', 'Any Language'),
            'Ngon_ngu_thu_2': hotkeys_dict.get('Ngon_ngu_thu_2', 'Tiếng Việt'),
            'Ngon_ngu_thu_3': hotkeys_dict.get('Ngon_ngu_thu_3', 'English'),
            'Nhom2_Ngon_ngu_dau_tien': hotkeys_dict.get('Nhom2_Ngon_ngu_dau_tien', 'Any Language'),
            'Nhom2_Ngon_ngu_thu_2': hotkeys_dict.get('Nhom2_Ngon_ngu_thu_2', 'Tiếng Việt'),
            'Nhom2_Ngon_ngu_thu_3': hotkeys_dict.get('Nhom2_Ngon_ngu_thu_3', 'English'),
        }
        self.create_tabs()
    def create_tabs(self):
        # Footer đẹp: trái là label, phải là 2 nút sát mép phải
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(side='bottom', fill='x', pady=(0, 8), padx=8)
        # Label bên trái
        left_label = ttk.Label(footer_frame, text="Powered by ITM Semiconductor Vietnam Company Limited - KhanhIT IT Team. Copyright © 2025 all rights reserved.", font=("Segoe UI", 9, "italic"), bootstyle=SECONDARY)
        left_label.pack(side='left', anchor='w', padx=(4,0))
        # Frame phải chứa 2 nút, căn phải, dịch vào một chút
        right_btn_frame = ttk.Frame(footer_frame)
        right_btn_frame.pack(side='right', anchor='e', padx=(0, 24), pady=(8, 2))
        def on_cancel():
            self.root.withdraw()
        ttk.Button(right_btn_frame, text='Lưu cấu hình', style='Custom.TButton', command=self.save_settings, bootstyle=PRIMARY).pack(side='left', padx=(0,8))
        ttk.Button(right_btn_frame, text='Huỷ bỏ', style='Custom.TButton', command=on_cancel, bootstyle=SECONDARY).pack(side='left')
        
        # Tạo notebook sau footer để footer luôn ở dưới cùng
        self.tab_control = ttk.Notebook(self.root, bootstyle=PRIMARY)
        self.settings_tab = ttk.Frame(self.tab_control)
        self.api_key_tab = ttk.Frame(self.tab_control)
        self.advanced_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.settings_tab, text='Cài Đặt')
        self.tab_control.add(self.api_key_tab, text='Quản lý API KEY')
        self.tab_control.add(self.advanced_tab, text='Nâng Cao')
        
        # Bind sự kiện chuyển tab để tự động điều chỉnh kích thước
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        self.tab_control.pack(expand=1, fill='both')
        self.create_settings_tab()
        self.create_api_key_tab()
        self.create_advanced_tab()

    def on_tab_changed(self, event):
        """Xử lý sự kiện chuyển tab và tự động điều chỉnh kích thước cửa sổ"""
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        # Điều chỉnh kích thước cửa sổ theo tab được chọn
        if tab_text == "Cài Đặt":
            # Tab Cài Đặt: kích thước mặc định hoặc mở rộng nếu có Group 2
            if hasattr(self, 'group2_visible') and self.group2_visible:
                self.root.geometry('1050x650')
            else:
                self.root.geometry('1050x420')
        elif tab_text == "Quản lý API KEY":
            # Tab API Key: cần không gian lớn hơn cho danh sách keys và controls
            self.root.geometry('1050x1010')
            # Tự động làm mới danh sách API keys khi chuyển sang tab này
            try:
                if hasattr(self, 'refresh_api_keys'):
                    self.refresh_api_keys()
            except Exception as e:
                print(f"Warning: Could not auto-refresh API keys: {e}")
        elif tab_text == "Nâng Cao":
            # Tab Nâng Cao: kích thước nhỏ gọn
            self.root.geometry('1050x350')
        
        # Đảm bảo cửa sổ được cập nhật
        self.root.update_idletasks()

    def create_settings_tab(self):
        style = ttk.Style()
        style.theme_use('flatly')
        title = ttk.Label(self.settings_tab, text='Cài đặt phím tắt & ngôn ngữ', font=('Segoe UI', 18, 'bold'), bootstyle=PRIMARY)
        title.pack(pady=(18, 18))
        self.entries = {}
        self.lang_selects = {}
        lang_list = [
            '',
            'English',
            'Tiếng Việt',
            '한국어',
            '中文',
            '日本語',
            'Français',
            'Deutsch',
            'Русский',
            'Español',
            'ไทย',
        ]
        # Khai báo lại modifiers, main_keys, split_hotkey
        modifiers = ['<none>', '<ctrl>', '<alt>', '<shift>']
        main_keys = [''] + [chr(i) for i in range(65, 91)] + [str(i) for i in range(0, 10)]  # '', A-Z, 0-9
        def split_hotkey(hotkey):
            parts = hotkey.split('+')
            modifiers = ['<ctrl>', '<alt>', '<shift>']
            mods = [p for p in parts if p in modifiers]
            non_mods = [p for p in parts if p not in modifiers]
            if len(mods) == 0:
                return '<none>', '<none>', non_mods[0] if non_mods else ''
            elif len(mods) == 1:
                return mods[0], '<none>', non_mods[0] if non_mods else ''
            elif len(mods) == 2:
                return mods[0], mods[1], non_mods[0] if non_mods else ''
            else:
                return mods[0], mods[1], non_mods[0] if non_mods else ''
        # --- Nhóm 1 ---
        group1 = ttk.Labelframe(self.settings_tab, text='Tuỳ chọn mặc định:', bootstyle=INFO)
        group1.pack(padx=40, pady=(16, 20), fill='x', ipadx=10, ipady=10)
        for i in range(8):
            group1.columnconfigure(i, weight=1)
        ttk.Label(group1, text='Ngôn ngữ đầu tiên sẽ được dịch tới ngôn ngữ thứ 2, ngôn ngữ thứ 2 sẽ được dịch tới ngôn ngữ thứ 3.', font=('Segoe UI', 9, 'italic'), bootstyle=SECONDARY).grid(row=0, column=0, columnspan=8, sticky='w', padx=8, pady=(10,6))
        # Tiêu đề các cột
        ttk.Label(group1, text='Phím tắt:', font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='e', padx=(8,2), pady=(8,4))
        ttk.Label(group1, text='Modifier 1').grid(row=1, column=1, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group1, text='Modifier 2').grid(row=1, column=2, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group1, text='Phím chính').grid(row=1, column=3, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group1, text='Ngôn ngữ đầu tiên:').grid(row=1, column=4, sticky='n', padx=(18,2), pady=(8,4))
        ttk.Label(group1, text='Ngôn ngữ thứ 2:').grid(row=1, column=5, sticky='n', padx=(8,2), pady=(8,4))
        ttk.Label(group1, text='Ngôn ngữ thứ 3:').grid(row=1, column=6, sticky='n', padx=(8,2), pady=(8,4))
        # Dịch popup
        ttk.Label(group1, text='Dịch popup').grid(row=2, column=0, sticky='e', padx=(8,2), pady=8)
        mod1, mod2, key = split_hotkey(self.initial_hotkeys.get('translate_popup', '<ctrl>+q'))
        self.entries['translate_popup_mod1'] = ttk.Combobox(group1, values=modifiers, width=7, state='readonly')
        self.entries['translate_popup_mod1'].set(mod1)
        self.entries['translate_popup_mod1'].grid(row=2, column=1, padx=2, pady=8)
        self.entries['translate_popup_mod2'] = ttk.Combobox(group1, values=modifiers, width=7, state='readonly')
        self.entries['translate_popup_mod2'].set(mod2)
        self.entries['translate_popup_mod2'].grid(row=2, column=2, padx=2, pady=8)
        self.entries['translate_popup_key'] = ttk.Combobox(group1, values=main_keys, width=7, state='readonly')
        self.entries['translate_popup_key'].set(key.upper())
        self.entries['translate_popup_key'].grid(row=2, column=3, padx=2, pady=8)
        self.lang_selects['Ngon_ngu_dau_tien'] = ttk.Combobox(group1, values=lang_list+['Any Language'], width=15, state='readonly')
        self.lang_selects['Ngon_ngu_dau_tien'].set(self.initial_langs.get('Ngon_ngu_dau_tien', 'Any Language'))
        self.lang_selects['Ngon_ngu_dau_tien'].grid(row=2, column=4, padx=2, pady=8)
        self.lang_selects['Ngon_ngu_thu_2'] = ttk.Combobox(group1, values=lang_list, width=15, state='readonly')
        self.lang_selects['Ngon_ngu_thu_2'].set(self.initial_langs.get('Ngon_ngu_thu_2', 'Tiếng Việt'))
        self.lang_selects['Ngon_ngu_thu_2'].grid(row=2, column=5, padx=2, pady=8)
        self.lang_selects['Ngon_ngu_thu_3'] = ttk.Combobox(group1, values=lang_list, width=15, state='readonly')
        self.lang_selects['Ngon_ngu_thu_3'].set(self.initial_langs.get('Ngon_ngu_thu_3', 'English'))
        self.lang_selects['Ngon_ngu_thu_3'].grid(row=2, column=6, padx=2, pady=8)
        # Dịch & thay thế
        ttk.Label(group1, text='Dịch & thay thế').grid(row=3, column=0, sticky='e', padx=(8,2), pady=8)
        mod1, mod2, key = split_hotkey(self.initial_hotkeys.get('replace_translate', '<ctrl>+d'))
        self.entries['replace_translate_mod1'] = ttk.Combobox(group1, values=modifiers, width=7, state='readonly')
        self.entries['replace_translate_mod1'].set(mod1)
        self.entries['replace_translate_mod1'].grid(row=3, column=1, padx=2, pady=8)
        self.entries['replace_translate_mod2'] = ttk.Combobox(group1, values=modifiers, width=7, state='readonly')
        self.entries['replace_translate_mod2'].set(mod2)
        self.entries['replace_translate_mod2'].grid(row=3, column=2, padx=2, pady=8)
        self.entries['replace_translate_key'] = ttk.Combobox(group1, values=main_keys, width=7, state='readonly')
        self.entries['replace_translate_key'].set(key.upper())
        self.entries['replace_translate_key'].grid(row=3, column=3, padx=2, pady=8)

        # --- Nhóm 2 ---
        self.group2_visible = False
        def toggle_group2():
            if self.group2_visible:
                group2.pack_forget()
                toggle_btn.config(text='Hiện Tuỳ chọn tuỳ chỉnh')
                self.root.geometry('1050x420')
                self.group2_visible = False
            else:
                group2.pack(padx=40, pady=(12, 18), fill='x', ipadx=10, ipady=10)
                toggle_btn.config(text='Ẩn Tuỳ chọn tuỳ chỉnh')
                self.root.geometry('1050x650')
                self.group2_visible = True
        toggle_btn = ttk.Button(self.settings_tab, text='Hiện Tuỳ chọn tuỳ chỉnh', command=toggle_group2, bootstyle=SECONDARY)
        toggle_btn.pack(pady=(0, 2))
        group2 = ttk.Labelframe(self.settings_tab, text='Tuỳ chọn tuỳ chỉnh:', bootstyle=INFO)
        for i in range(8):
            group2.columnconfigure(i, weight=1)
        ttk.Label(group2, text='Ngôn ngữ đầu tiên sẽ được dịch tới ngôn ngữ thứ 2, ngôn ngữ thứ 2 sẽ được dịch tới ngôn ngữ thứ 3.', font=('Segoe UI', 9, 'italic'), bootstyle=SECONDARY).grid(row=0, column=0, columnspan=8, sticky='w', padx=8, pady=(10,6))
        # Tiêu đề các cột
        ttk.Label(group2, text='Phím tắt:', font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='e', padx=(8,2), pady=(8,4))
        ttk.Label(group2, text='Modifier 1').grid(row=1, column=1, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group2, text='Modifier 2').grid(row=1, column=2, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group2, text='Phím chính').grid(row=1, column=3, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group2, text='Ngôn ngữ đầu tiên:').grid(row=1, column=4, sticky='n', padx=(18,2), pady=(8,4))
        ttk.Label(group2, text='Ngôn ngữ thứ 2:').grid(row=1, column=5, sticky='n', padx=(8,2), pady=(8,4))
        ttk.Label(group2, text='Ngôn ngữ thứ 3:').grid(row=1, column=6, sticky='n', padx=(8,2), pady=(8,4))
        # Dịch popup 2
        ttk.Label(group2, text='Dịch popup').grid(row=2, column=0, sticky='e', padx=(8,2), pady=8)
        mod1, mod2, key = split_hotkey(self.initial_hotkeys.get('translate_popup2', '<ctrl>+1'))
        self.entries['translate_popup2_mod1'] = ttk.Combobox(group2, values=modifiers, width=7, state='readonly')
        self.entries['translate_popup2_mod1'].set(mod1)
        self.entries['translate_popup2_mod1'].grid(row=2, column=1, padx=2, pady=8)
        self.entries['translate_popup2_mod2'] = ttk.Combobox(group2, values=modifiers, width=7, state='readonly')
        self.entries['translate_popup2_mod2'].set(mod2)
        self.entries['translate_popup2_mod2'].grid(row=2, column=2, padx=2, pady=8)
        self.entries['translate_popup2_key'] = ttk.Combobox(group2, values=main_keys, width=7, state='readonly')
        self.entries['translate_popup2_key'].set(key.upper())
        self.entries['translate_popup2_key'].grid(row=2, column=3, padx=2, pady=8)
        self.lang_selects['Nhom2_Ngon_ngu_dau_tien'] = ttk.Combobox(group2, values=lang_list+['Any Language'], width=15, state='readonly')
        self.lang_selects['Nhom2_Ngon_ngu_dau_tien'].set(self.initial_langs.get('Nhom2_Ngon_ngu_dau_tien', 'Any Language'))
        self.lang_selects['Nhom2_Ngon_ngu_dau_tien'].grid(row=2, column=4, padx=2, pady=8)
        self.lang_selects['Nhom2_Ngon_ngu_thu_2'] = ttk.Combobox(group2, values=lang_list, width=15, state='readonly')
        self.lang_selects['Nhom2_Ngon_ngu_thu_2'].set(self.initial_langs.get('Nhom2_Ngon_ngu_thu_2', 'Tiếng Việt'))
        self.lang_selects['Nhom2_Ngon_ngu_thu_2'].grid(row=2, column=5, padx=2, pady=8)
        self.lang_selects['Nhom2_Ngon_ngu_thu_3'] = ttk.Combobox(group2, values=lang_list, width=15, state='readonly')
        self.lang_selects['Nhom2_Ngon_ngu_thu_3'].set(self.initial_langs.get('Nhom2_Ngon_ngu_thu_3', 'English'))
        self.lang_selects['Nhom2_Ngon_ngu_thu_3'].grid(row=2, column=6, padx=2, pady=8)
        # Dịch & thay thế 2
        ttk.Label(group2, text='Dịch & thay thế').grid(row=3, column=0, sticky='e', padx=(8,2), pady=8)
        mod1, mod2, key = split_hotkey(self.initial_hotkeys.get('replace_translate2', '<ctrl>+2'))
        self.entries['replace_translate2_mod1'] = ttk.Combobox(group2, values=modifiers, width=7, state='readonly')
        self.entries['replace_translate2_mod1'].set(mod1)
        self.entries['replace_translate2_mod1'].grid(row=3, column=1, padx=2, pady=8)
        self.entries['replace_translate2_mod2'] = ttk.Combobox(group2, values=modifiers, width=7, state='readonly')
        self.entries['replace_translate2_mod2'].set(mod2)
        self.entries['replace_translate2_mod2'].grid(row=3, column=2, padx=2, pady=8)
        self.entries['replace_translate2_key'] = ttk.Combobox(group2, values=main_keys, width=7, state='readonly')
        self.entries['replace_translate2_key'].set(key.upper())
        self.entries['replace_translate2_key'].grid(row=3, column=3, padx=2, pady=8)


    def create_api_key_tab(self):
        """Tạo tab quản lý API KEY với hỗ trợ multiple providers"""
        from core.api_key_manager import api_key_manager, AIProvider
        
        # Title
        title_frame = ttk.Frame(self.api_key_tab)
        title_frame.pack(pady=(20, 10), fill='x')
        
        title = ttk.Label(title_frame, text='Quản lý API KEY & AI Providers', 
                         font=('Segoe UI', 18, 'bold'), bootstyle=PRIMARY)
        title.pack()
        
        subtitle = ttk.Label(title_frame, 
                           text='Quản lý API keys từ nhiều providers khác nhau. Hệ thống sẽ tự động failover khi gặp lỗi.',
                           font=('Segoe UI', 10), bootstyle=SECONDARY)
        subtitle.pack(pady=(5, 0))
        
        # Main content frame
        main_frame = ttk.Frame(self.api_key_tab)
        main_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Left side - Key list
        left_frame = ttk.LabelFrame(main_frame, text='Danh sách API Keys & Providers', bootstyle=INFO)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Key listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for better display of provider info
        columns = ('Provider', 'Model', 'Name', 'Status', 'Key')
        self.api_key_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=10)
        
        # Configure columns
        self.api_key_tree.heading('#0', text='Active')
        self.api_key_tree.heading('Provider', text='Provider')
        self.api_key_tree.heading('Model', text='Model')
        self.api_key_tree.heading('Name', text='Name')
        self.api_key_tree.heading('Status', text='Status')
        self.api_key_tree.heading('Key', text='API Key')
        
        self.api_key_tree.column('#0', width=60)
        self.api_key_tree.column('Provider', width=80)
        self.api_key_tree.column('Model', width=100)
        self.api_key_tree.column('Name', width=120)
        self.api_key_tree.column('Status', width=80)
        self.api_key_tree.column('Key', width=200)
        
        # Scrollbar for treeview
        scrollbar_keys = ttk.Scrollbar(list_frame, orient='vertical', command=self.api_key_tree.yview)
        self.api_key_tree.configure(yscrollcommand=scrollbar_keys.set)
        
        self.api_key_tree.pack(side='left', fill='both', expand=True)
        scrollbar_keys.pack(side='right', fill='y')
        
        # Key status frame
        status_frame = ttk.Frame(left_frame)
        status_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.key_status_label = ttk.Label(status_frame, text='', font=('Segoe UI', 9))
        self.key_status_label.pack()
        
        # Right side - Controls
        right_frame = ttk.LabelFrame(main_frame, text='Thao tác', bootstyle=INFO)
        right_frame.pack(side='right', fill='y', padx=(10, 0))
        
        # Add key section
        add_frame = ttk.Frame(right_frame)
        add_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(add_frame, text='Thêm API Key mới:', font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        # Provider selection
        provider_frame = ttk.Frame(add_frame)
        provider_frame.pack(fill='x', pady=(5, 5))
        
        ttk.Label(provider_frame, text='Provider:').pack(anchor='w')
        self.provider_var = tk.StringVar(value='gemini')
        provider_combo = ttk.Combobox(provider_frame, textvariable=self.provider_var, 
                                    values=['gemini', 'chatgpt', 'copilot', 'deepseek', 'claude'],
                                    state='readonly', width=37)
        provider_combo.pack(fill='x')
        
        # Bind provider change to update model list
        provider_combo.bind('<<ComboboxSelected>>', self.on_provider_changed)
        
        # Model selection - now as dropdown
        model_frame = ttk.Frame(add_frame)
        model_frame.pack(fill='x', pady=(5, 5))
        
        ttk.Label(model_frame, text='Model:').pack(anchor='w')
        self.model_var = tk.StringVar(value='auto')
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                       state='readonly', width=37)
        self.model_combo.pack(fill='x')
        
        # Add tooltip for model info
        self.create_model_tooltip()
        
        # Initialize model list for default provider
        self.update_model_list()
        
        # Name
        name_frame = ttk.Frame(add_frame)
        name_frame.pack(fill='x', pady=(5, 5))
        
        ttk.Label(name_frame, text='Tên (tùy chọn):').pack(anchor='w')
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=40)
        name_entry.pack(fill='x')
        
        # API Key input
        key_frame = ttk.Frame(add_frame)
        key_frame.pack(fill='x', pady=(5, 10))
        
        ttk.Label(key_frame, text='API Key:').pack(anchor='w')
        self.new_key_entry = ttk.Entry(key_frame, width=40, show='*')
        self.new_key_entry.pack(fill='x')
        
        add_btn = ttk.Button(add_frame, text='➕ Thêm Key', command=self.add_api_key, 
                           bootstyle=SUCCESS)
        add_btn.pack(fill='x', pady=(5, 0))
        
        # Control buttons
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill='x', padx=10, pady=(20, 10))
        
        ttk.Label(control_frame, text='Quản lý Keys:', font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        set_active_btn = ttk.Button(control_frame, text='🎯 Đặt làm Active', 
                                  command=self.set_active_key, bootstyle=PRIMARY)
        set_active_btn.pack(fill='x', pady=(5, 5))
        
        edit_btn = ttk.Button(control_frame, text='✏️ Chỉnh sửa', 
                            command=self.edit_api_key, bootstyle=INFO)
        edit_btn.pack(fill='x', pady=(0, 5))
        
        remove_btn = ttk.Button(control_frame, text='🗑️ Xóa Key', 
                              command=self.remove_api_key, bootstyle=DANGER)
        remove_btn.pack(fill='x', pady=(0, 5))
        
        refresh_btn = ttk.Button(control_frame, text='🔄 Làm mới', 
                               command=self.refresh_api_keys, bootstyle=SECONDARY)
        refresh_btn.pack(fill='x')
        
        # Provider priority section
        priority_frame = ttk.Frame(right_frame)
        priority_frame.pack(fill='x', padx=10, pady=(20, 10))
        
        ttk.Label(priority_frame, text='Ưu tiên Providers:', font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        self.priority_listbox = tk.Listbox(priority_frame, height=5, font=('Segoe UI', 9))
        self.priority_listbox.pack(fill='x', pady=(5, 5))
        
        priority_btn_frame = ttk.Frame(priority_frame)
        priority_btn_frame.pack(fill='x')
        
        up_btn = ttk.Button(priority_btn_frame, text='↑', command=self.move_priority_up, width=3)
        up_btn.pack(side='left', padx=(0, 5))
        
        down_btn = ttk.Button(priority_btn_frame, text='↓', command=self.move_priority_down, width=3)
        down_btn.pack(side='left')
        
        # Info section
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill='x', padx=10, pady=(20, 10))
        
        ttk.Label(info_frame, text='💡 Thông tin:', font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        info_text = """• Hỗ trợ Gemini, ChatGPT, GitHub Copilot, DeepSeek, Claude
• Auto failover khi provider gặp lỗi
• Model 'auto' = model mặc định của provider
• Thứ tự ưu tiên quyết định failover order"""
        
        info_label = ttk.Label(info_frame, text=info_text, 
                             font=('Segoe UI', 9), bootstyle=SECONDARY,
                             wraplength=250, justify='left')
        info_label.pack(anchor='w', pady=(5, 0))
        
        # Load and display keys
        self.refresh_api_keys()
    
    def on_provider_changed(self, event=None):
        """Xử lý khi provider thay đổi - cập nhật danh sách model"""
        self.update_model_list()
    
    def create_model_tooltip(self):
        """Tạo tooltip hiển thị thông tin model"""
        try:
            from core.provider_models import get_model_description
            
            def show_tooltip(event):
                model = self.model_var.get()
                description = get_model_description(model)
                
                # Create tooltip window
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                tooltip.configure(bg="lightyellow")
                
                label = tk.Label(tooltip, text=description, 
                               bg="lightyellow", fg="black",
                               font=("Segoe UI", 9),
                               wraplength=300, justify="left")
                label.pack()
                
                # Auto hide after 3 seconds
                tooltip.after(3000, tooltip.destroy)
                
                # Store tooltip reference to destroy on mouse leave
                self.model_combo.tooltip = tooltip
            
            def hide_tooltip(event):
                if hasattr(self.model_combo, 'tooltip'):
                    self.model_combo.tooltip.destroy()
                    delattr(self.model_combo, 'tooltip')
            
            # Bind events
            self.model_combo.bind('<Enter>', show_tooltip)
            self.model_combo.bind('<Leave>', hide_tooltip)
            
        except ImportError:
            # No tooltip if provider_models not available
            pass
    
    def update_model_list(self):
        """Cập nhật danh sách model dựa vào provider được chọn"""
        try:
            from core.provider_models import get_models_for_provider
            
            provider = self.provider_var.get()
            models = get_models_for_provider(provider)
            
            # Update combobox values
            self.model_combo['values'] = models
            
            # Set default value if current value is not in new list
            current_model = self.model_var.get()
            if current_model not in models:
                self.model_var.set('auto')
                
        except ImportError:
            # Fallback if provider_models module not available
            self.model_combo['values'] = ['auto']
            self.model_var.set('auto')
    
    def add_api_key(self):
        """Thêm API key mới với validation đầy đủ"""
        from core.api_key_manager import api_key_manager, AIProvider
        from core.api_key_validator import APIKeyValidator, get_validation_message
        import threading
        
        new_key = self.new_key_entry.get().strip()
        provider_str = self.provider_var.get()
        model = self.model_var.get().strip()
        name = self.name_var.get().strip()
        
        if not new_key:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập API key!")
            return
        
        if not model:
            model = "auto"
        
        # Disable add button during validation
        add_btn = None
        for widget in self.api_key_tab.winfo_children():
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if hasattr(child, 'winfo_children'):
                        for subchild in child.winfo_children():
                            if isinstance(subchild, ttk.Button) and "Thêm Key" in str(subchild.cget('text')):
                                add_btn = subchild
                                break
        
        if add_btn:
            add_btn.config(text="🔄 Đang kiểm tra...", state='disabled')
        
        def validate_and_add():
            """Validate API key trong background thread"""
            try:
                # Validate API key
                result, message = APIKeyValidator.validate_api_key(provider_str, new_key, model)
                validation_info = get_validation_message(result, message)
                
                def show_result():
                    """Hiển thị kết quả validation trong main thread"""
                    # Restore button
                    if add_btn:
                        add_btn.config(text="➕ Thêm Key", state='normal')
                    
                    # Show validation result
                    if validation_info["type"] == "success":
                        # API key valid - proceed to add
                        proceed = messagebox.askquestion(
                            validation_info["title"],
                            validation_info["message"] + "\n\nBạn có muốn lưu API key này không?",
                            icon='question'
                        )
                        
                        if proceed == 'yes':
                            self._save_api_key(new_key, provider_str, model, name)
                    
                    elif validation_info["type"] == "warning":
                        # API key có issue nhưng có thể save
                        proceed = messagebox.askyesno(
                            validation_info["title"],
                            validation_info["message"] + "\n\nBạn vẫn muốn lưu API key này không?",
                            icon='warning'
                        )
                        
                        if proceed:
                            self._save_api_key(new_key, provider_str, model, name)
                    
                    else:
                        # API key invalid - không save
                        messagebox.showerror(
                            validation_info["title"],
                            validation_info["message"]
                        )
                
                # Switch back to main thread
                self.root.after(0, show_result)
                
            except Exception as e:
                def show_error():
                    if add_btn:
                        add_btn.config(text="➕ Thêm Key", state='normal')
                    messagebox.showerror("Lỗi", f"Không thể kiểm tra API key: {str(e)}")
                
                self.root.after(0, show_error)
        
        # Start validation in background
        threading.Thread(target=validate_and_add, daemon=True).start()
    
    def _save_api_key(self, new_key: str, provider_str: str, model: str, name: str):
        """Helper method để save API key sau khi đã validate"""
        from core.api_key_manager import api_key_manager, AIProvider
        
        try:
            provider = AIProvider(provider_str)
            
            if api_key_manager.add_key(new_key, provider, model, name):
                messagebox.showinfo("✅ Thành công!", 
                    f"Đã thêm API key {provider_str.upper()} mới!\n\n"
                    f"📋 Provider: {provider_str.title()}\n"
                    f"🤖 Model: {model}\n"
                    f"📝 Tên: {name or f'{provider_str.title()} Key'}")
                
                # Clear form
                self.new_key_entry.delete(0, 'end')
                self.model_var.set('auto')
                self.name_var.set('')
                self.refresh_api_keys()
            else:
                messagebox.showerror("Lỗi", "API key đã tồn tại trong hệ thống!")
                
        except ValueError:
            messagebox.showerror("Lỗi", f"Provider '{provider_str}' không được hỗ trợ!")
    
    def remove_api_key(self):
        """Xóa API key đã chọn"""
        from core.api_key_manager import api_key_manager
        
        selection = self.api_key_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn key cần xóa!")
            return
        
        # Get item data
        item = selection[0]
        index = self.api_key_tree.index(item)
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa API key này?"):
            if api_key_manager.remove_key(index):
                messagebox.showinfo("Thành công", "Đã xóa API key!")
                self.refresh_api_keys()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa API key!")
    
    def set_active_key(self):
        """Đặt key được chọn làm active"""
        from core.api_key_manager import api_key_manager
        
        selection = self.api_key_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn key cần đặt active!")
            return
        
        item = selection[0]
        index = self.api_key_tree.index(item)
        
        if api_key_manager.set_active_index(index):
            messagebox.showinfo("Thành công", "Đã đặt key làm active!")
            self.refresh_api_keys()
        else:
            messagebox.showerror("Lỗi", "Không thể đặt key này làm active!")
    
    def edit_api_key(self):
        """Chỉnh sửa thông tin API key"""
        from core.api_key_manager import api_key_manager, AIProvider
        
        selection = self.api_key_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn key cần chỉnh sửa!")
            return
        
        item = selection[0]
        index = self.api_key_tree.index(item)
        
        try:
            key_info = api_key_manager.keys[index]
            
            # Create edit dialog
            edit_win = tk.Toplevel(self.root)
            edit_win.title("Chỉnh sửa API Key")
            edit_win.geometry("400x300")
            edit_win.transient(self.root)
            edit_win.grab_set()
            
            # Center the window
            edit_win.update_idletasks()
            x = (edit_win.winfo_screenwidth() // 2) - (400 // 2)
            y = (edit_win.winfo_screenheight() // 2) - (300 // 2)
            edit_win.geometry(f"400x300+{x}+{y}")
            
            # Form fields
            main_frame = ttk.Frame(edit_win, padding=20)
            main_frame.pack(fill='both', expand=True)
            
            # Provider
            ttk.Label(main_frame, text='Provider:').grid(row=0, column=0, sticky='w', pady=5)
            provider_var = tk.StringVar(value=key_info.provider.value)
            provider_combo = ttk.Combobox(main_frame, textvariable=provider_var, 
                                        values=['gemini', 'chatgpt', 'copilot', 'deepseek', 'claude'],
                                        state='readonly', width=30)
            provider_combo.grid(row=0, column=1, sticky='ew', pady=5, padx=(10,0))
            
            # Model - now as dropdown
            ttk.Label(main_frame, text='Model:').grid(row=1, column=0, sticky='w', pady=5)
            model_var = tk.StringVar(value=key_info.model)
            model_combo = ttk.Combobox(main_frame, textvariable=model_var, 
                                     state='readonly', width=30)
            model_combo.grid(row=1, column=1, sticky='ew', pady=5, padx=(10,0))
            
            # Update model list based on provider
            def update_edit_model_list():
                try:
                    from core.provider_models import get_models_for_provider
                    provider = provider_var.get()
                    models = get_models_for_provider(provider)
                    model_combo['values'] = models
                    if model_var.get() not in models:
                        model_var.set('auto')
                except ImportError:
                    model_combo['values'] = ['auto']
                    model_var.set('auto')
            
            # Initialize model list and bind provider change
            update_edit_model_list()
            provider_combo.bind('<<ComboboxSelected>>', lambda e: update_edit_model_list())
            
            # Name
            ttk.Label(main_frame, text='Tên:').grid(row=2, column=0, sticky='w', pady=5)
            name_var = tk.StringVar(value=key_info.name)
            name_entry = ttk.Entry(main_frame, textvariable=name_var, width=33)
            name_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(10,0))
            
            # API Key (masked)
            ttk.Label(main_frame, text='API Key:').grid(row=3, column=0, sticky='w', pady=5)
            key_var = tk.StringVar(value=key_info.key)
            key_entry = ttk.Entry(main_frame, textvariable=key_var, show='*', width=33)
            key_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=(10,0))
            
            # Status
            ttk.Label(main_frame, text='Trạng thái:').grid(row=4, column=0, sticky='w', pady=5)
            status_var = tk.BooleanVar(value=key_info.is_active)
            status_check = ttk.Checkbutton(main_frame, text='Hoạt động', variable=status_var)
            status_check.grid(row=4, column=1, sticky='w', pady=5, padx=(10,0))
            
            main_frame.columnconfigure(1, weight=1)
            
            # Buttons
            btn_frame = ttk.Frame(main_frame)
            btn_frame.grid(row=5, column=0, columnspan=2, pady=20, sticky='ew')
            
            def save_changes():
                try:
                    new_provider = AIProvider(provider_var.get())
                    new_model = model_var.get().strip() or "auto"
                    new_name = name_var.get().strip()
                    new_key = key_var.get().strip()
                    new_status = status_var.get()
                    
                    if not new_key:
                        messagebox.showwarning("Cảnh báo", "API key không được để trống!")
                        return
                    
                    # Update key info
                    key_info.provider = new_provider
                    key_info.model = new_model
                    key_info.name = new_name or f"{new_provider.value.title()} Key {index + 1}"
                    key_info.key = new_key
                    key_info.is_active = new_status
                    
                    # Reset failures if reactivated
                    if new_status and key_info.failed_count > 0:
                        key_info.failed_count = 0
                        key_info.last_error = ""
                    
                    api_key_manager.save_keys()
                    messagebox.showinfo("Thành công", "Đã cập nhật API key!")
                    edit_win.destroy()
                    self.refresh_api_keys()
                    
                except ValueError:
                    messagebox.showerror("Lỗi", "Provider không hợp lệ!")
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể cập nhật: {e}")
            
            save_btn = ttk.Button(btn_frame, text='Lưu', command=save_changes, bootstyle=SUCCESS)
            save_btn.pack(side='left', padx=(0, 10))
            
            cancel_btn = ttk.Button(btn_frame, text='Hủy', command=edit_win.destroy, bootstyle=SECONDARY)
            cancel_btn.pack(side='left')
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở form chỉnh sửa: {e}")
    
    def refresh_api_keys(self):
        """Làm mới danh sách API keys"""
        from core.api_key_manager import api_key_manager
        
        # Clear treeview
        for item in self.api_key_tree.get_children():
            self.api_key_tree.delete(item)
        
        # Load keys
        keys = api_key_manager.get_all_keys()
        active_index = api_key_manager.active_index
        
        for i, key_info in enumerate(keys):
            # Create display values
            is_active = "✅" if i == active_index else ""
            provider = key_info.provider.value.title()
            model = key_info.model
            name = key_info.name or f"{provider} Key {i+1}"
            
            # Status with failure info
            if not key_info.is_active:
                status = "❌ Disabled"
            elif key_info.failed_count > 0:
                status = f"⚠️ Failed({key_info.failed_count})"
            else:
                status = "✅ OK"
            
            # Masked key
            masked_key = f"...{key_info.key[-8:]}" if len(key_info.key) > 8 else key_info.key
            
            # Insert into tree
            self.api_key_tree.insert('', 'end', text=is_active,
                                   values=(provider, model, name, status, masked_key))
        
        # Update status
        if keys:
            active_key = api_key_manager.get_active_key()
            if active_key:
                provider_info = api_key_manager.get_provider_info()
                status_text = f"Đang sử dụng: {provider_info['name']} ({provider_info['provider'].title()}) - {len(keys)} key(s) total"
            else:
                status_text = f"Không có key active - {len(keys)} key(s) total"
        else:
            status_text = "Chưa có API key nào"
        
        self.key_status_label.config(text=status_text)
        
        # Update priority list
        if hasattr(self, 'priority_listbox'):
            self.priority_listbox.delete(0, 'end')
            for provider in api_key_manager.provider_priority:
                self.priority_listbox.insert('end', provider.value.title())
    
    def move_priority_up(self):
        """Di chuyển provider lên trên trong danh sách ưu tiên"""
        from core.api_key_manager import api_key_manager
        
        selection = self.priority_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        index = selection[0]
        priorities = api_key_manager.provider_priority.copy()
        
        # Swap
        priorities[index], priorities[index-1] = priorities[index-1], priorities[index]
        
        api_key_manager.set_provider_priority(priorities)
        self.refresh_api_keys()
        self.priority_listbox.selection_set(index-1)
    
    def move_priority_down(self):
        """Di chuyển provider xuống dưới trong danh sách ưu tiên"""
        from core.api_key_manager import api_key_manager
        
        selection = self.priority_listbox.curselection()
        if not selection or selection[0] >= len(api_key_manager.provider_priority) - 1:
            return
        
        index = selection[0]
        priorities = api_key_manager.provider_priority.copy()
        
        # Swap
        priorities[index], priorities[index+1] = priorities[index+1], priorities[index]
        
        api_key_manager.set_provider_priority(priorities)
        self.refresh_api_keys()
        self.priority_listbox.selection_set(index+1)

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
        # Beautiful modern help window with light theme
        help_window = tk.Toplevel(self.root)
        help_window.title("🌟 ITM Translate - User Guide")
        help_window.geometry("950x900")
        help_window.resizable(True, True)
        help_window.transient(self.root)
        help_window.grab_set()
        help_window.configure(bg='#ffffff')  # Clean white background
        
        # Center the dialog
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (help_window.winfo_screenheight() // 2) - (700 // 2)
        help_window.geometry(f"950x900+{x}+{y}")
        
        # Header frame with beautiful blue gradient
        header_frame = tk.Frame(help_window, bg='#4285f4', height=90)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Header title with modern styling
        header_label = tk.Label(header_frame, 
                               text="📚 ITM TRANSLATE USER GUIDE", 
                               font=('Segoe UI', 20, 'bold'), 
                               fg='white', bg='#4285f4')
        header_label.pack(pady=(20, 5))
        
        # Subtitle
        subtitle_label = tk.Label(header_frame, 
                                 text="Complete Guide for Professional AI Translation", 
                                 font=('Segoe UI', 11), 
                                 fg='#e8f0fe', bg='#4285f4')
        subtitle_label.pack()
        
        # Main content frame with clean styling
        main_frame = tk.Frame(help_window, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Text widget with beautiful light theme
        text_frame = tk.Frame(main_frame, bg='white')
        text_frame.pack(fill='both', expand=True)
        
        text_widget = tk.Text(text_frame, wrap='word', 
                             font=('Segoe UI', 11), 
                             bg='#fafafa', fg='#333333', 
                             padx=30, pady=25,
                             selectbackground='#4285f4', selectforeground='white',
                             insertbackground='#4285f4',
                             relief='solid',
                             borderwidth=1)
        
        # Beautiful scrollbar styling
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview,
                                bg='#f0f0f0', troughcolor='#fafafa', 
                                activebackground='#4285f4',
                                relief='flat', borderwidth=0, width=14)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        help_content = """
🔧 A. CÀI ĐẶT VÀ CẤU HÌNH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 LƯU Ý QUAN TRỌNG: Bạn cần có mã API Gemini để sử dụng ITM Translate. Dưới đây là hướng dẫn chi tiết:

Bước 1: Truy cập Google AI Studio
• Mở trình duyệt và truy cập: https://aistudio.google.com/
• Đảm bảo bạn đã đăng nhập bằng tài khoản Google

Bước 2: Truy cập mục API Keys
• Tìm mục “Get API key” trong menu hoặc bảng điều khiển
• Nhấn “Create API key” hoặc “Get API key”

Bước 3: Tạo khoá API mới
• Nhấn “Create API key in new project” (khuyến nghị)
• Hoặc chọn một project Google Cloud sẵn có
• Đặt tên cho project, ví dụ: “ITM Translate”

Bước 4: Sao chép khoá API của bạn
• Sau khi tạo, sao chép khoá API (bắt đầu bằng “AIza...”)
• ⚠️ LƯU Ý QUAN TRỌNG: Lưu trữ khóa cẩn thận – không chia sẻ công khai
• Ví dụ khóa: AIzaSyD...abcd123

Bước 5: Cấu hình trong ITM Translate
• Mở ITM Translate → Vào tab “Nâng Cao”
• Dán khoá vào trường "ITM_TRANSLATE_KEY"
• Nhấn “Lưu cấu hình” để lưu lại

💡 LƯU Ý VỀ CHI PHÍ: API Gemini có giới hạn miễn phí
• 15 yêu cầu mỗi phút với gói miễn phí
• 1 triệu token mỗi tháng miễn phí
• Phù hợp cho nhu cầu cá nhân và công việc

💡 CẤU HÌNH PHÍM TẮT & NGÔN NGỮ
Nhóm mặc định:
• Dịch popup: Ctrl+Q (mặc định)
• Dịch thay thế: Ctrl+D (mặc định)

Nhóm tùy chỉnh:
• Dịch popup 2: Ctrl+1 (mặc định)
• Dịch thay thế 2: Ctrl+2 (mặc định)

💡 LƯU Ý VỀ PHÍM TẮT: 
• Phím tắt có thể bị trùng với ứng dụng khác. Nên chọn phím tắt ít xung đột nhất
• Hỗ trợ phím Ctrl, Alt, Shift kết hợp với phím chính. Ví dụ: Ctrl+Alt+T, Shift+F1, Ctrl+Shift+Q
• Không hỗ trợ phím tắt đơn giản như F1, F2...
• Không hỗ trợ phím tắt có ký tự đặc biệt (ví dụ: @, #, $, v.v.)
• Nên tránh phím tắt trùng với các ứng dụng khác. Nếu gặp lỗi, hãy thử đổi phím tắt khác


🚀 B. CÁCH SỬ DỤNG ITM TRANSLATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 QUY TRÌNH DỊCH CƠ BẢN:
Bước 1: Chọn văn bản
• Bôi đen đoạn văn bản trong bất kỳ ứng dụng nào (Word, Chrome, Notepad, v.v.)
• Hoạt động với email, tài liệu, trang web, ứng dụng chat...

Bước 2: Dùng phím tắt
• Dịch POPUP: Nhấn phím tắt đã cấu hình (mặc định: Ctrl+Q)
• Dịch THAY THẾ: Nhấn phím tắt đã cấu hình (mặc định: Ctrl+D)

Bước 3: Xem kết quả
• Chế độ Popup: Hiển thị kết quả dịch trong cửa sổ nổi
• Chế độ Thay thế: Văn bản được thay bằng bản dịch

🎯 TÍNH NĂNG THÔNG MINH:
• Tự động nhận diện ngôn ngữ (kể cả khi có nhiều ngôn ngữ pha trộn)
• Giữ nguyên định dạng văn bản và ngữ cảnh
• Popup hiển thị thông tin ngôn ngữ ở tiêu đề
• Dùng Ctrl+C để sao chép kết quả


⭐ C. TÍNH NĂNG NÂNG CAO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 NHẬN DIỆN NGÔN NGỮ BẰNG AI:
• Tự động phát hiện ngôn ngữ gốc
• Xử lý thông minh văn bản pha trộn
• Hiển thị “Nhiều ngôn ngữ → Ngôn ngữ đích”

🎨 NHÓM NGÔN NGỮ KÉP:
• Hai nhóm phím tắt độc lập
• Mỗi nhóm dùng cặp ngôn ngữ khác nhau
• Ví dụ ứng dụng:

Nhóm 1: Dùng trong công việc (Anh ↔ Việt)

Nhóm 2: Dùng học tập (Hàn ↔ Việt)


⚡ D. MẸO TỐI ƯU HIỆU NĂNG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 MẸO SỬ DỤNG TỐT HƠN:
• Giữ khoá API an toàn, không chia sẻ
• Dùng “Any Language” để tăng hiệu quả phát hiện ngôn ngữ
• Đóng popup bằng cách click ra ngoài hoặc làm mất focus
• Chế độ thay thế hoạt động tốt nhất với đoạn văn bản ngắn

🔧 XỬ LÝ SỰ CỐ:
• Nếu dịch thất bại: Kiểm tra kết nối mạng và khóa API
• Nếu phím tắt không hoạt động: Khởi động lại ứng dụng hoặc kiểm tra xung đột
• Nếu không hiện popup: Kiểm tra lại đoạn văn đã chọn
• Với văn bản pha ngôn ngữ: Dùng chế độ tự động phát hiện


🌍 E. CÁC NGÔN NGỮ HỖ TRỢ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 DANH SÁCH NGÔN NGỮ:
• English (Tiếng Anh)
• Tiếng Việt (Vietnamese)
• 한국어 (Tiếng Hàn)
• 中文 (Tiếng Trung)
• 日本語 (Tiếng Nhật)
• Français (Tiếng Pháp)
• Deutsch (Tiếng Đức)
• Русский (Tiếng Nga)
• Español (Tiếng Tây Ban Nha)
• ไทย (Tiếng Thái)
• + Hỗ trợ tự động nhận diện hơn 100 ngôn ngữ qua AI Gemini


📞 F. HỖ TRỢ & LIÊN HỆ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏢 Công ty TNHH ITM Semiconductor Việt Nam
📧 Liên hệ: Đội IT ITM
🌐 GitHub: github.com/quockhanh112hubt/ITM_Translate
🔄 Cập nhật: Vào tab “Nâng Cao” → chọn “Cập nhật chương trình”

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 TĂNG NĂNG SUẤT LÀM VIỆC VỚI DỊCH THUẬT THÔNG MINH
Sẵn sàng để dịch cả thế giới chỉ với một cú nhấn!"""
        
        # Insert content với màu sắc đẹp mắt cho cả icon và text
        lines = help_content.split('\n')
        for line in lines:
            if line.startswith('🌟'):
                text_widget.insert('end', line + '\n', 'title')
            elif line.startswith('━━━'):
                text_widget.insert('end', line + '\n', 'separator')
            elif line.startswith('📋') or line.startswith('🔧') or line.startswith('🚀') or line.startswith('⭐') or line.startswith('🛠️') or line.startswith('⚡') or line.startswith('🌍') or line.startswith('📞'):
                text_widget.insert('end', line + '\n', 'header')
            elif line.startswith('🚨') or line.startswith('⚠️'):
                text_widget.insert('end', line + '\n', 'warning')
            elif line.startswith('💡'):
                text_widget.insert('end', line + '\n', 'highlight')
            elif line.startswith('1️⃣') or line.startswith('2️⃣') or line.startswith('Bước'):
                text_widget.insert('end', line + '\n', 'step')
            elif '•' in line and any(emoji in line for emoji in ['🎯', '🔑', '⚡', '📋', '⚙️', '🌐', '🖥️']):
                text_widget.insert('end', line + '\n', 'emoji_blue')
            elif '•' in line and any(emoji in line for emoji in ['🧠', '📝', '🔍', '✨', '🎨']):
                text_widget.insert('end', line + '\n', 'emoji_green')
            elif '•' in line and any(emoji in line for emoji in ['🔧', '📊', '🔒', '🎛️']):
                text_widget.insert('end', line + '\n', 'emoji_orange')
            elif '•' in line and any(emoji in line for emoji in ['🔄', '🇺🇸', '🇻🇳', '🇰🇷', '🇨🇳', '🇯🇵', '🇫🇷', '🇩🇪', '🇷🇺', '🇪🇸', '🇹🇭']):
                text_widget.insert('end', line + '\n', 'emoji_purple')
            elif '•' in line:
                text_widget.insert('end', line + '\n', 'subheader')
            else:
                text_widget.insert('end', line + '\n', 'normal')
        
        # Configure colorful text tags với màu sắc rõ ràng (không có background)
        text_widget.tag_configure("title", font=('Segoe UI', 16, 'bold'), foreground='#1a73e8')
        text_widget.tag_configure("header", font=('Segoe UI', 14, 'bold'), foreground='#4285f4')
        text_widget.tag_configure("separator", font=('Segoe UI', 10), foreground='#9aa0a6')
        text_widget.tag_configure("subheader", font=('Segoe UI', 12, 'bold'), foreground='#34a853')
        text_widget.tag_configure("warning", font=('Segoe UI', 11, 'bold'), foreground='#ea4335')
        text_widget.tag_configure("highlight", font=('Segoe UI', 11, 'bold'), foreground='#9c27b0')
        text_widget.tag_configure("step", font=('Segoe UI', 11, 'bold'), foreground='#ff9800')
        text_widget.tag_configure("emoji_blue", font=('Segoe UI', 11), foreground='#1976d2')
        text_widget.tag_configure("emoji_green", font=('Segoe UI', 11), foreground='#388e3c')
        text_widget.tag_configure("emoji_orange", font=('Segoe UI', 11), foreground='#f57c00')
        text_widget.tag_configure("emoji_purple", font=('Segoe UI', 11), foreground='#7b1fa2')
        text_widget.tag_configure("normal", font=('Segoe UI', 11), foreground='#555555')
        
        text_widget.config(state='disabled')
        
        # Beautiful button frame with clean design
        btn_frame = tk.Frame(main_frame, bg='white', height=70)
        btn_frame.pack(fill='x', pady=(20, 0))
        btn_frame.pack_propagate(False)
        
        # Buttons with beautiful modern styling
        def open_gemini_studio():
            import webbrowser
            webbrowser.open('https://aistudio.google.com/')
        
        def copy_guide():
            help_window.clipboard_clear()
            help_window.clipboard_append(help_content)
            tk.messagebox.showinfo("✅ Đã sao chép", "Hướng dẫn đã được sao chép vào clipboard!")
        
        # Beautiful modern buttons inspired by Google Material Design
        open_btn = tk.Button(btn_frame, text="🌐 Open Google AI Studio", command=open_gemini_studio,
                 font=('Segoe UI', 11, 'bold'), bg='#4285f4', fg='white', 
                 padx=35, pady=15, relief='flat', cursor='hand2',
                 activebackground='#3367d6', activeforeground='white')
        open_btn.pack(side='left', padx=(0, 15))
        
        copy_btn = tk.Button(btn_frame, text="📋 Copy User Guide", command=copy_guide,
                 font=('Segoe UI', 11, 'bold'), bg='#34a853', fg='white', 
                 padx=35, pady=15, relief='flat', cursor='hand2',
                 activebackground='#2d7d32', activeforeground='white')
        copy_btn.pack(side='left', padx=(0, 15))
        
        close_btn = tk.Button(btn_frame, text="✕ Close", command=help_window.destroy, 
                 font=('Segoe UI', 11, 'bold'), bg='#f1f3f4', fg='#5f6368', 
                 padx=40, pady=15, relief='flat', cursor='hand2',
                 activebackground='#e8eaed', activeforeground='#202124')
        close_btn.pack(side='right')
    def show_about(self):
        # Đọc version chi tiết từ file version.json
        version_info = "1.0.0"
        build_info = "unknown"
        release_date = "unknown"
        try:
            version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.json")
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version_info = data.get('version', '1.0.0')
                    build_info = data.get('build', 'unknown')
                    release_date = data.get('release_date', 'unknown')
        except Exception:
            pass
        
        about_text = f"""
🚀 TRÌNH QUẢN LÝ DỊCH THUẬT THÔNG MINH
Công cụ dịch thuật chuyên nghiệp sử dụng AI dành cho Windows

📋 CÁC TÍNH NĂNG CHÍNH:
├─ Chọn và dịch văn bản thông minh
├─ Dịch nhanh tức thì bằng phím tắt
├─ Thay thế văn bản theo thời gian thực
├─ Tự động nhận diện ngôn ngữ bằng AI (Hỗ trợ ngôn ngữ pha trộn)
├─ Nhóm ngôn ngữ kép với phím tắt tuỳ chỉnh
└─ Hỗ trợ hơn 10 ngôn ngữ (Anh, Việt, Hàn, Trung, Nhật, Pháp, Đức, Nga, Tây Ban Nha, Thái...)

⭐ TÍNH NĂNG NÂNG CAO:
├─ Tích hợp AI Gemini cho kết quả dịch chính xác
├─ Tự động phát hiện ngôn ngữ gốc
├─ Dịch theo ngữ cảnh (Giữ nguyên ý nghĩa và giọng điệu)
├─ Tuỳ chỉnh phím tắt linh hoạt (Kết hợp Ctrl/Alt/Shift)
├─ Ghi nhớ thiết lập và sao lưu tự động
└─ Quản lý khóa API an toàn

🔧 TÍCH HỢP HỆ THỐNG:
├─ Tự khởi động cùng Windows
├─ Chạy nền trong khay hệ thống
├─ Tối ưu hiệu suất sử dụng bộ nhớ
├─ Hỗ trợ phím tắt toàn cục (Dùng được trong mọi ứng dụng)
└─ Bảo vệ khỏi khởi động nhiều phiên bản

🔄 HỆ THỐNG CẬP NHẬT:
├─ Cập nhật tự động/thủ công dựa trên phiên bản mới nhất
├─ Cập nhật nền yên lặng với quyền quản trị viên
├─ Cơ chế cập nhật dựa trên kết nối GitHub
└─ Di chuyển phiên bản mượt mà

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 THÔNG TIN PHIÊN BẢN:
├─ Phiên bản: {version_info}
├─ Bản dựng: {build_info}
├─ Ngày phát hành: {release_date}
└─ Kiến trúc: Windows x64

👥 ĐỘI NGŨ PHÁT TRIỂN:
├─ Lập trình viên: KhanhIT – Nhóm ITM
├─ Tích hợp AI: Sử dụng API Gemini
├─ Thiết kế UI/UX: Giao diện hiện đại với Bootstrap
└─ Đảm bảo chất lượng: Kiểm thử chuẩn doanh nghiệp

🏢 CÔNG TY:
Công ty TNHH ITM Semiconductor Việt Nam
🌐 GitHub: github.com/quockhanh112hubt/ITM_Translate
📧 Hỗ trợ: Liên hệ đội IT ITM Việt Nam, 2025

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 MỤC TIÊU ỨNG DỤNG
Tăng hiệu suất làm việc của bạn với công cụ dịch thuật thông minh ngay trong tầm tay

© 2025 Công ty TNHH ITM Semiconductor Việt Nam. Bảo lưu mọi quyền."""
        
        # Beautiful modern about window with light theme
        about_window = tk.Toplevel(self.root)
        about_window.title("About ITM Translate v" + version_info)
        about_window.geometry("800x650")
        about_window.resizable(True, True)
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Modern light theme configuration
        about_window.configure(bg='#ffffff')
        
        # Center the dialog
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (about_window.winfo_screenheight() // 2) - (650 // 2)
        about_window.geometry(f"800x650+{x}+{y}")
        
        # Create beautiful gradient header with blue theme
        header_frame = tk.Frame(about_window, bg='#4285f4', height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Header content with professional styling
        header_label = tk.Label(header_frame, text="🌟 ITM TRANSLATE", 
                               font=('Segoe UI', 22, 'bold'), 
                               bg='#4285f4', fg='white')
        header_label.pack(pady=(15, 5))
        
        version_label = tk.Label(header_frame, text=f"Professional AI Translation Suite v{version_info}", 
                                font=('Segoe UI', 12), 
                                bg='#4285f4', fg='#e8f0fe')
        version_label.pack()
        
        # Main frame with clean light theme
        main_frame = tk.Frame(about_window, bg='white')
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Text widget with beautiful light theme and modern scrollbar
        text_frame = tk.Frame(main_frame, bg='white')
        text_frame.pack(fill='both', expand=True)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Segoe UI', 11), 
                             bg='#fafafa', fg='#333333', padx=25, pady=20,
                             selectbackground='#4285f4', selectforeground='white',
                             insertbackground='#4285f4', relief='solid', borderwidth=1)
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview,
                                bg='#f0f0f0', troughcolor='#fafafa', 
                                activebackground='#4285f4',
                                relief='flat', borderwidth=0, width=14)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Configure text tags for beautiful formatting
        text_widget.tag_configure("header", font=('Segoe UI', 14, 'bold'), foreground='#4285f4')
        text_widget.tag_configure("subheader", font=('Segoe UI', 12, 'bold'), foreground='#34a853')
        text_widget.tag_configure("emoji", font=('Segoe UI', 12))
        text_widget.tag_configure("version", font=('Consolas', 11), foreground='#ea4335')
        text_widget.tag_configure("highlight", background='#e8f0fe', foreground='#1a73e8')
        
        # Insert content với màu sắc sinh động cho cả icon và text
        lines = about_text.split('\n')
        for line in lines:
            if line.startswith('🌐') and 'ITM Translate' in line:
                text_widget.insert('end', line + '\n', 'title')
            elif line.startswith('━━━'):
                text_widget.insert('end', line + '\n', 'separator')
            elif line.startswith('🚀') or line.startswith('📋') or line.startswith('⭐') or line.startswith('🔧') or line.startswith('🔄') or line.startswith('📊') or line.startswith('👥') or line.startswith('🏢') or line.startswith('🎯'):
                text_widget.insert('end', line + '\n', 'header')
            elif '•' in line and any(emoji in line for emoji in ['🎯', '⚡', '🔄', '🧠', '🎨', '🌍']):
                text_widget.insert('end', line + '\n', 'feature_blue')
            elif '•' in line and any(emoji in line for emoji in ['🤖', '🔍', '📝', '🎛️', '💾', '🔒']):
                text_widget.insert('end', line + '\n', 'feature_green')
            elif '•' in line and any(emoji in line for emoji in ['🖥️', '🔧', '📊', '🛡️', '📦']):
                text_widget.insert('end', line + '\n', 'feature_orange')
            elif '•' in line and any(emoji in line for emoji in ['✨']):
                text_widget.insert('end', line + '\n', 'feature_purple')
            elif '•' in line:
                text_widget.insert('end', line + '\n', 'normal')
            elif line.startswith('├─') or line.startswith('└─'):
                text_widget.insert('end', line + '\n', 'tree_info')
            elif line.startswith('© 2025'):
                text_widget.insert('end', line + '\n', 'copyright')
            else:
                text_widget.insert('end', line + '\n', 'normal')
        
        # Configure colorful text tags chỉ với màu sắc (không có background)
        text_widget.tag_configure("title", font=('Segoe UI', 16, 'bold'), foreground='#1a73e8')
        text_widget.tag_configure("header", font=('Segoe UI', 13, 'bold'), foreground='#4285f4')
        text_widget.tag_configure("separator", font=('Segoe UI', 10), foreground='#9aa0a6')
        text_widget.tag_configure("feature_blue", font=('Segoe UI', 11), foreground='#1976d2')
        text_widget.tag_configure("feature_green", font=('Segoe UI', 11), foreground='#388e3c')
        text_widget.tag_configure("feature_orange", font=('Segoe UI', 11), foreground='#f57c00')
        text_widget.tag_configure("feature_purple", font=('Segoe UI', 11), foreground='#7b1fa2')
        text_widget.tag_configure("tree_info", font=('Consolas', 10), foreground='#5f6368')
        text_widget.tag_configure("copyright", font=('Segoe UI', 9, 'italic'), foreground='#9aa0a6')
        text_widget.tag_configure("normal", font=('Segoe UI', 11), foreground='#555555')
        
        text_widget.config(state='disabled')
        
        # Beautiful button frame with clean design
        btn_frame = tk.Frame(main_frame, bg='white', height=70)
        btn_frame.pack(fill='x', pady=(20, 0))
        btn_frame.pack_propagate(False)
        
        # Copy info button with beautiful styling
        def copy_version_info():
            about_window.clipboard_clear()
            about_window.clipboard_append(f"ITM Translate v{version_info} (Build: {build_info})")
            tk.messagebox.showinfo("✅ Đã sao chép", "Thông tin phiên bản đã được sao chép vào clipboard!")
        
        def open_github():
            import webbrowser
            webbrowser.open('https://github.com/quockhanh112hubt/ITM_Translate')
        
        # Beautiful modern buttons with Google Material Design style
        github_btn = tk.Button(btn_frame, text="🌐 GitHub Repository", command=open_github,
                 font=('Segoe UI', 11, 'bold'), bg='#4285f4', fg='white', 
                 padx=30, pady=15, relief='flat', cursor='hand2',
                 activebackground='#3367d6', activeforeground='white')
        github_btn.pack(side='left', padx=(0, 15))
        
        copy_btn = tk.Button(btn_frame, text="📋 Copy Version Info", command=copy_version_info,
                 font=('Segoe UI', 11, 'bold'), bg='#34a853', fg='white', 
                 padx=30, pady=15, relief='flat', cursor='hand2',
                 activebackground='#2d7d32', activeforeground='white')
        copy_btn.pack(side='left', padx=(0, 15))
        
        close_btn = tk.Button(btn_frame, text="✕ Close", command=about_window.destroy, 
                 font=('Segoe UI', 11, 'bold'), bg='#f1f3f4', fg='#5f6368', 
                 padx=35, pady=15, relief='flat', cursor='hand2',
                 activebackground='#e8eaed', activeforeground='#202124')
        close_btn.pack(side='right')
    def update_program(self):
        # Hiển thị loading popup
        loading_popup = None
        try:
            from ui.popup import show_loading_popup
            loading_popup = show_loading_popup(self.root)
        except Exception:
            pass
        
        def check_update_worker():
            try:
                from core.updater import check_for_updates_async
                
                # Close loading popup
                if loading_popup:
                    self.root.after(0, loading_popup.destroy)
                
                # Show update dialog
                check_for_updates_async(self.root, show_no_update=True)
                
            except ImportError:
                if loading_popup:
                    self.root.after(0, loading_popup.destroy)
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể tải module cập nhật. Vui lòng kiểm tra kết nối mạng."))
            except Exception as e:
                if loading_popup:
                    self.root.after(0, loading_popup.destroy)
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi kiểm tra cập nhật: {str(e)}"))
        
        # Run check in background thread
        threading.Thread(target=check_update_worker, daemon=True).start()
    def save_settings(self):
        def join_hotkey(mod1, mod2, key):
            mods = []
            if mod1 != '<none>':
                mods.append(mod1)
            if mod2 != '<none>' and mod2 != mod1:
                mods.append(mod2)
            if key == '' or key == '<none>':
                return '+'.join(mods)
            return '+'.join(mods + [key.lower()])
        # Lấy giá trị các phím tắt
        combos = [
            (self.entries['translate_popup_mod1'].get(), self.entries['translate_popup_mod2'].get(), self.entries['translate_popup_key'].get()),
            (self.entries['replace_translate_mod1'].get(), self.entries['replace_translate_mod2'].get(), self.entries['replace_translate_key'].get()),
            (self.entries['translate_popup2_mod1'].get(), self.entries['translate_popup2_mod2'].get(), self.entries['translate_popup2_key'].get()),
            (self.entries['replace_translate2_mod1'].get(), self.entries['replace_translate2_mod2'].get(), self.entries['replace_translate2_key'].get()),
        ]
        group1_langs = [self.lang_selects['Ngon_ngu_dau_tien'].get(), self.lang_selects['Ngon_ngu_thu_2'].get(), self.lang_selects['Ngon_ngu_thu_3'].get()]
        group2_langs = [self.lang_selects['Nhom2_Ngon_ngu_dau_tien'].get(), self.lang_selects['Nhom2_Ngon_ngu_thu_2'].get(), self.lang_selects['Nhom2_Ngon_ngu_thu_3'].get()]
        lang_groups = [group1_langs, group2_langs]
        group_names = ['Tuỳ chọn mặc định', 'Tuỳ chọn tuỳ chỉnh']
        # 1. Kiểm tra ngôn ngữ
        def check_lang_group(group_langs, group_name):
            filled = [l for l in group_langs if l != '']
            if 0 < len(filled) < 3:
                messagebox.showerror("Lỗi cấu hình", f"Bạn phải chọn đủ 3 ngôn ngữ cho {group_name}!")
                return False
            if len(set(group_langs)) < 3 and len(filled) == 3:
                messagebox.showerror("Lỗi cấu hình", f"Ba ngôn ngữ trong {group_name} không được trùng nhau!")
                return False
            return True
        # 2. Kiểm tra phím tắt
        def check_hotkey(mod1, mod2, key):
            # Không cho phép Modifier 1 và Modifier 2 giống nhau (trừ khi đều là <none>)
            if mod1 != '<none>' and mod1 == mod2:
                return False, "Phím tắt Modifier 1 và Modifier 2 không được giống nhau!"
            values = [mod1, mod2, key]
            none_count = sum([v == '<none>' or v == '' for v in values])
            if none_count >= 2 and not all(v == '<none>' or v == '' for v in values):
                return False, "Phím tắt không hợp lệ!"
            return True, None
        # 3. Kiểm tra chung: tất cả Modifier là <none>, phím chính là '' và cả 3 ngôn ngữ là '' thì cho lưu bình thường
        all_none = all((m1 == '<none>' or m1 == '') and (m2 == '<none>' or m2 == '') and (k == '' or k == '<none>') for m1, m2, k in combos)
        all_langs_empty = all(all(l == '' for l in group) for group in lang_groups)
        if all_none and all_langs_empty:
            pass  # Cho lưu bình thường
        else:
            # Kiểm tra từng tổ hợp phím tắt
            for idx, (mod1, mod2, key) in enumerate(combos):
                valid, msg = check_hotkey(mod1, mod2, key)
                if not valid:
                    messagebox.showerror("Lỗi cấu hình", msg)
                    return
            # Kiểm tra trùng phím tắt (bất kể thứ tự modifier)
            def normalize_hotkey(mod1, mod2, key):
                if all(v == '<none>' or v == '' for v in [mod1, mod2, key]):
                    return '__empty__'
                mods = []
                if mod1 != '<none>':
                    mods.append(mod1)
                if mod2 != '<none>' and mod2 != mod1:
                    mods.append(mod2)
                mods = sorted(mods)
                return '+'.join(mods + [key.lower()])
            normalized_hotkey_strs = [normalize_hotkey(*c) for c in combos]
            # Loại bỏ các tổ hợp rỗng khỏi kiểm tra trùng lặp
            filtered_hotkeys = [h for h in normalized_hotkey_strs if h != '__empty__']
            if len(set(filtered_hotkeys)) < len(filtered_hotkeys):
                messagebox.showerror("Lỗi cấu hình", "Các tổ hợp phím tắt không được trùng nhau!")
                return
            # Kiểm tra ngôn ngữ từng group
            for group_langs, group_name in zip(lang_groups, group_names):
                if not check_lang_group(group_langs, group_name):
                    return
            # Nếu phím tắt hợp lệ nhưng có bất kỳ ngôn ngữ nào là '' (và không phải cả 3 đều là '') thì không cho lưu, báo rõ group_name
            for group_langs, group_name in zip(lang_groups, group_names):
                empty_count = sum([l == '' for l in group_langs])
                if 0 < empty_count < 3:
                    messagebox.showerror("Lỗi cấu hình", f"Chưa chọn ngôn ngữ trong {group_name}")
                    return
            # Nếu phím tắt là hợp lệ, nhưng chưa chọn đủ ngôn ngữ (kể cả 3 ngôn ngữ đều rỗng), thì báo lỗi rõ group_name
            for group_idx, (group_langs, group_name) in enumerate(zip(lang_groups, group_names)):
                # Lấy 2 hotkey của group này
                hotkey1 = combos[group_idx * 2]
                hotkey2 = combos[group_idx * 2 + 1]
                # Nếu bất kỳ hotkey nào trong group này không rỗng hoàn toàn
                for mod1, mod2, key in [hotkey1, hotkey2]:
                    if not (mod1 == '<none>' and mod2 == '<none>' and (key == '' or key == '<none>')):
                        if any(l == '' for l in group_langs):
                            messagebox.showerror("Lỗi cấu hình", f"Chưa chọn ngôn ngữ trong {group_name}")
                            return
            # Nếu ngôn ngữ hợp lệ, thì phải có ít nhất 2 trong 3 phím tắt không phải là '' hoặc <none>
            for idx, (mod1, mod2, key) in enumerate(combos):
                group_langs = lang_groups[idx // 2]  # 2 hotkey đầu là group1, 2 hotkey sau là group2
                if not all(l == '' for l in group_langs):
                    count_non_empty = sum([1 for v in [mod1, mod2, key] if v != '' and v != '<none>'])
                    if count_non_empty < 2:
                        messagebox.showerror("Lỗi cấu hình", "Chưa chọn phím tắt hợp lệ")
                        return
        # Nếu qua hết kiểm tra thì lưu
        new_hotkeys = {
            'translate_popup': join_hotkey(self.entries['translate_popup_mod1'].get(), self.entries['translate_popup_mod2'].get(), self.entries['translate_popup_key'].get()),
            'replace_translate': join_hotkey(self.entries['replace_translate_mod1'].get(), self.entries['replace_translate_mod2'].get(), self.entries['replace_translate_key'].get()),
            'translate_popup2': join_hotkey(self.entries['translate_popup2_mod1'].get(), self.entries['translate_popup2_mod2'].get(), self.entries['translate_popup2_key'].get()),
            'replace_translate2': join_hotkey(self.entries['replace_translate2_mod1'].get(), self.entries['replace_translate2_mod2'].get(), self.entries['replace_translate2_key'].get()),
        }
        new_langs = {
            'Ngon_ngu_dau_tien': self.lang_selects['Ngon_ngu_dau_tien'].get(),
            'Ngon_ngu_thu_2': self.lang_selects['Ngon_ngu_thu_2'].get(),
            'Ngon_ngu_thu_3': self.lang_selects['Ngon_ngu_thu_3'].get(),
            'Nhom2_Ngon_ngu_dau_tien': self.lang_selects['Nhom2_Ngon_ngu_dau_tien'].get(),
            'Nhom2_Ngon_ngu_thu_2': self.lang_selects['Nhom2_Ngon_ngu_thu_2'].get(),
            'Nhom2_Ngon_ngu_thu_3': self.lang_selects['Nhom2_Ngon_ngu_thu_3'].get(),
        }
        config = {**new_hotkeys, **new_langs}
        # So sánh phím tắt mới với ban đầu
        hotkey_keys = ['translate_popup', 'replace_translate', 'translate_popup2', 'replace_translate2']
        changed = False
        if self.initial_hotkeys:
            for k in hotkey_keys:
                if self.initial_hotkeys.get(k, '') != new_hotkeys.get(k, ''):
                    changed = True
                    break
        else:
            changed = True
        with open('hotkeys.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        if changed:
            if messagebox.askokcancel("Thông báo", "Phím tắt đã được thay đổi, hãy khởi động lại chương trình để áp dụng"):
                self._restart_with_batch()
            else:
                return
        else:
            messagebox.showinfo("Thông báo", "Cấu hình đã được lưu thành công.")
        self.initial_hotkeys = new_hotkeys
    def load_settings(self):
        # Đọc hotkeys từ file
        if os.path.exists("hotkeys.json"):
            try:
                with open("hotkeys.json", "r", encoding="utf-8") as f:
                    hotkeys = json.load(f)
                    self.initial_hotkeys = hotkeys
            except Exception:
                pass
        # Đọc api key từ file
        if os.path.exists("apikey.txt"):
            try:
                with open("apikey.txt", "r", encoding="utf-8") as f:
                    api_key = f.read().strip()
                    self.initial_api_key = api_key
            except Exception:
                pass
    def run_hotkey_manager(self):
        if self.hotkey_manager:
            self.hotkey_manager.run()
    def stop_hotkey_manager(self):
        if self.hotkey_manager:
            self.hotkey_manager.stop()
    def restart_hotkey_manager(self):
        if self.hotkey_manager:
            self.hotkey_manager.restart()
    def add_hotkey(self, hotkey, callback):
        if self.hotkey_manager:
            self.hotkey_manager.add_hotkey(hotkey, callback)
    def remove_hotkey(self, hotkey):
        if self.hotkey_manager:
            self.hotkey_manager.remove_hotkey(hotkey)
    def trigger_hotkey(self, hotkey):
        if self.hotkey_manager:
            self.hotkey_manager.trigger_hotkey(hotkey)
    def on_translate_popup(self):
        print("Translate popup triggered")
    def on_replace_translate(self):
        print("Replace translate triggered")
    def on_translate_popup2(self):
        print("Translate popup 2 triggered")
    def on_replace_translate2(self):
        print("Replace translate 2 triggered")
    def _restart_with_batch(self):
        """Tạo restart.bat, chạy với quyền Admin và thoát ứng dụng"""
        try:
            # Bước 1: Tạo restart.bat
            self._create_restart_batch()
            
            # Bước 2: Chạy restart.bat với quyền Admin
            self._run_restart_batch_with_admin()
            
            # Bước 3: Thoát hoàn toàn ứng dụng hiện tại
            self._exit_application()
            
        except Exception as e:
            print(f"❌ Error in restart process: {e}")
            # Fallback: thoát đơn giản
            self._exit_application()
    
    def _create_restart_batch(self):
        """Tạo restart.bat file"""
        try:
            # Xác định đường dẫn executable hiện tại
            if getattr(sys, 'frozen', False):
                # Executable mode
                current_exe = sys.executable
                app_dir = os.path.dirname(current_exe)
                exe_name = os.path.basename(current_exe)
            else:
                # Development mode - tìm ITM_Translate.py
                current_dir = os.path.dirname(os.path.dirname(__file__))
                main_script = os.path.join(current_dir, "ITM_Translate.py")
                if os.path.exists(main_script):
                    current_exe = f'"{sys.executable}" "{main_script}"'
                    app_dir = current_dir
                    exe_name = "python.exe"
                else:
                    raise Exception("ITM_Translate.py not found")
            
            # Tạo restart.bat
            batch_path = os.path.join(app_dir, "restart.bat")
            
            if getattr(sys, 'frozen', False):
                # Executable mode batch content
                batch_content = f'''@echo off
title ITM Translate - Restart Process
echo [INFO] ITM Translate restart process started...

REM Wait for current application to close
echo [INFO] Waiting for application to close...
timeout /t 3 /nobreak >nul

REM Check if application is still running and wait
:wait_close
tasklist /FI "IMAGENAME eq {exe_name}" 2>NUL | find /I /N "{exe_name}" >NUL
if "%ERRORLEVEL%"=="0" (
    echo [WAIT] Application still running, waiting...
    timeout /t 2 /nobreak >nul
    goto wait_close
)

echo [INFO] Application closed successfully
echo [INFO] Starting ITM Translate...

REM Start new application
cd /d "{app_dir}"
start "" "{current_exe}"

if "%ERRORLEVEL%"=="0" (
    echo [SUCCESS] ITM Translate restarted successfully
) else (
    echo [ERROR] Failed to restart ITM Translate
)

REM Self-delete this batch file
echo [INFO] Cleaning up restart batch file...
(goto) 2>nul & del "%~f0"
'''
            else:
                # Development mode batch content
                batch_content = f'''@echo off
title ITM Translate - Restart Process (Development)
echo [INFO] ITM Translate restart process started (Development Mode)...

REM Wait for current application to close
echo [INFO] Waiting for application to close...
timeout /t 3 /nobreak >nul

REM Check if Python process is still running and wait
:wait_close
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "ITM_Translate" >NUL
if "%ERRORLEVEL%"=="0" (
    echo [WAIT] Python process still running, waiting...
    timeout /t 2 /nobreak >nul
    goto wait_close
)

echo [INFO] Application closed successfully
echo [INFO] Starting ITM Translate (Development mode)...

REM Start new application
cd /d "{app_dir}"
{current_exe}

if "%ERRORLEVEL%"=="0" (
    echo [SUCCESS] ITM Translate restarted successfully
) else (
    echo [ERROR] Failed to restart ITM Translate
)

REM Self-delete this batch file
echo [INFO] Cleaning up restart batch file...
timeout /t 2 /nobreak >nul
del "%~f0"
'''
            
            # Ghi file batch
            with open(batch_path, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            print(f"✅ Restart batch file created: {batch_path}")
            return batch_path
            
        except Exception as e:
            print(f"❌ Failed to create restart batch file: {e}")
            raise e
    
    def _run_restart_batch_with_admin(self):
        """Chạy restart.bat với quyền Admin"""
        try:
            # Xác định đường dẫn
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.dirname(__file__))
            
            batch_path = os.path.join(app_dir, "restart.bat")
            
            if not os.path.exists(batch_path):
                raise Exception(f"Restart batch file not found: {batch_path}")
            
            print(f"🚀 Running restart.bat with admin privileges...")
            
            # Chạy với quyền Admin bằng ShellExecute
            import ctypes
            result = ctypes.windll.shell32.ShellExecuteW(
                None,        # hwnd
                "runas",     # lpVerb (run as administrator) 
                batch_path,  # lpFile
                None,        # lpParameters
                app_dir,     # lpDirectory
                0            # nShowCmd (SW_HIDE)
            )
            
            if result > 32:
                print(f"✅ Restart batch launched with admin privileges (result: {result})")
            else:
                print(f"⚠️ Admin launch may have failed (result: {result}), trying fallback...")
                # Fallback: chạy không cần admin
                subprocess.Popen(
                    [batch_path],
                    cwd=app_dir,
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                print("✅ Restart batch launched without admin privileges")
                
        except Exception as e:
            print(f"❌ Failed to run restart batch: {e}")
            raise e
    
    def _exit_application(self):
        """Thoát hoàn toàn ứng dụng hiện tại"""
        try:
            print("� Exiting current application...")
            
            # Dọn dẹp tray icon nếu có
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.stop()
        except Exception:
            pass
        
        try:
            # Release lock file
            from core.lockfile import release_lock
            release_lock()
        except Exception:
            pass
        
        # Delay nhỏ để batch file kịp khởi động
        import time
        time.sleep(0.5)
        
        # Thoát hoàn toàn
        self.root.destroy()
        os._exit(0)
