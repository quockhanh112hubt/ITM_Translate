import tkinter as tk
from tkinter import messagebox
import json
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import keyboard
import threading

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
            'Ngon_ngu_dau_tien': hotkeys_dict.get('Ngon_ngu_dau_tien', 'Any Language'),
            'Ngon_ngu_thu_2': hotkeys_dict.get('Ngon_ngu_thu_2', 'Tiếng Việt'),
            'Ngon_ngu_thu_3': hotkeys_dict.get('Ngon_ngu_thu_3', 'English'),
            'Nhom2_Ngon_ngu_dau_tien': hotkeys_dict.get('Nhom2_Ngon_ngu_dau_tien', 'Any Language'),
            'Nhom2_Ngon_ngu_thu_2': hotkeys_dict.get('Nhom2_Ngon_ngu_thu_2', 'Tiếng Việt'),
            'Nhom2_Ngon_ngu_thu_3': hotkeys_dict.get('Nhom2_Ngon_ngu_thu_3', 'English'),
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
        # Thêm phần nhập ITM_TRANSLATE_KEY vào đầu tab Nâng Cao
        ttk.Label(self.advanced_tab, text='ITM_TRANSLATE_KEY:', font=('Segoe UI', 12, 'bold'), bootstyle=PRIMARY).pack(pady=(18, 5))
        self.api_key_entry = ttk.Entry(self.advanced_tab, width=50, show='*')
        if self.initial_api_key:
            self.api_key_entry.insert(0, self.initial_api_key)
        self.api_key_entry.pack()

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
        # Tạo dialog custom với scroll để hiển thị hướng dẫn chi tiết
        help_window = tk.Toplevel(self.root)
        help_window.title("ITM Translate - User Guide")
        help_window.geometry("900x700")
        help_window.resizable(True, True)
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center the dialog
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (help_window.winfo_screenheight() // 2) - (700 // 2)
        help_window.geometry(f"900x700+{x}+{y}")
        
        # Main frame with scrollbar
        main_frame = tk.Frame(help_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Text widget with scrollbar
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill='both', expand=True)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Segoe UI', 10), 
                             bg='#f8f9fa', fg='#2c3e50', padx=20, pady=20,
                             selectbackground='#3498db', selectforeground='white')
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        help_content = """🌟 ITM TRANSLATE - COMPREHENSIVE USER GUIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 QUICK START GUIDE

🔧 1. SETUP & CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ GET GEMINI API KEY (Required for Translation)
   
   Step 1: Visit Google AI Studio
   • Open your web browser and go to: https://aistudio.google.com/
   • Make sure you're signed in with your Google account
   
   Step 2: Access API Keys Section
   • Look for "Get API key" in the navigation menu or dashboard
   • Click on "Create API key" or "Get API key"
   
   Step 3: Create New API Key
   • Click "Create API key in new project" (recommended)
   • Or select an existing Google Cloud project if you have one
   • Give your project a descriptive name (e.g., "ITM Translate")
   
   Step 4: Copy Your API Key
   • Once created, copy the API key (starts with "AIza...")
   • ⚠️ IMPORTANT: Store this key securely - don't share it publicly
   • The key will look like: AIzaSyD...abcd123 (example)
   
   Step 5: Configure in ITM Translate
   • Open ITM Translate → Go to "Nâng Cao" tab
   • Paste your API key in the "ITM_TRANSLATE_KEY" field
   • Click "Lưu cấu hình" to save
   
   💡 BILLING NOTE: Gemini API has generous free usage limits
   • 15 requests per minute for free tier
   • 1 million tokens per month free
   • Perfect for personal/professional translation needs

2️⃣ CONFIGURE HOTKEYS & LANGUAGES
   
   Default Group (Tuỳ chọn mặc định):
   • Popup Translation: Ctrl+Q (default)
   • Replace Translation: Ctrl+D (default)
   
   Custom Group (Tuỳ chọn tuỳ chỉnh):
   • Popup Translation 2: Ctrl+1 (default)
   • Replace Translation 2: Ctrl+2 (default)
   
   Language Configuration:
   • Language 1 → Language 2 → Language 3 (circular translation)
   • "Any Language" = Auto-detect source language
   • Example: Any Language → Tiếng Việt → English

🚀 2. HOW TO USE ITM TRANSLATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 BASIC TRANSLATION WORKFLOW:

   Step 1: Select Text
   • Highlight any text in ANY application (Word, Chrome, Notepad, etc.)
   • Works with emails, documents, websites, chat applications
   
   Step 2: Use Hotkey
   • For POPUP translation: Press your configured hotkey (default: Ctrl+Q)
   • For REPLACE translation: Press your configured hotkey (default: Ctrl+D)
   
   Step 3: View Results
   • Popup mode: Translation appears in a popup window
   • Replace mode: Selected text is replaced with translation
   
   🎯 SMART FEATURES:
   • Auto-detects source language (works with mixed languages!)
   • Preserves text formatting and context
   • Popup shows language detection info in title
   • Copy translation results with Ctrl+C

⭐ 3. ADVANCED FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 AI-POWERED LANGUAGE DETECTION:
   • Automatically detects source language
   • Handles mixed-language content intelligently
   • Shows "Multi language → Target" for complex content
   
🎨 DUAL LANGUAGE GROUPS:
   • Two independent hotkey groups
   • Different language combinations per group
   • Example Use Cases:
     - Group 1: Work languages (EN ↔ VI)
     - Group 2: Study languages (KR ↔ VI)
   
🎛️ FLEXIBLE HOTKEY SYSTEM:
   • Supports Ctrl, Alt, Shift modifiers
   • Combine up to 2 modifiers + main key
   • Works globally in any application
   • Examples: Ctrl+Alt+T, Shift+F1, Ctrl+Shift+Q

🔄 CIRCULAR TRANSLATION:
   Language 1 → Language 2 → Language 3 → Language 1
   • Press same hotkey multiple times to cycle through languages
   • Perfect for multilingual workflows

🛠️ 4. SYSTEM INTEGRATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖥️ WINDOWS STARTUP:
   • Enable "Khởi động cùng Windows" in Advanced tab
   • ITM Translate runs in system tray
   • Always ready for instant translation

🔧 SYSTEM TRAY OPERATION:
   • Runs silently in background
   • Right-click tray icon for options
   • Left-click to show/hide settings window

🔄 AUTO-UPDATE SYSTEM:
   • Automatic update notifications
   • One-click update with admin privileges
   • Silent background installation

⚡ 5. PERFORMANCE TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 OPTIMIZATION TIPS:
   • Keep API key secure and don't share
   • Use "Any Language" for auto-detection efficiency
   • Close popup by clicking outside or losing focus
   • Replace mode works best with short text selections
   
🔧 TROUBLESHOOTING:
   • If translation fails: Check internet connection and API key
   • If hotkeys don't work: Restart application or check conflicts
   • If popup doesn't appear: Ensure text is properly selected
   • For mixed languages: Use auto-detect source language

🌍 6. SUPPORTED LANGUAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 FULL LANGUAGE SUPPORT:
   • English (English)
   • Tiếng Việt (Vietnamese)
   • 한국어 (Korean)
   • 中文 (Chinese)
   • 日本語 (Japanese)
   • Français (French)
   • Deutsch (German)
   • Русский (Russian)
   • Español (Spanish)
   • ไทย (Thai)
   • + Auto-detect for 100+ languages via Gemini AI

📞 7. SUPPORT & CONTACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏢 ITM Semiconductor Vietnam Company Limited
📧 Contact: ITM IT Team
🌐 GitHub: github.com/quockhanh112hubt/ITM_Translate
🔄 Updates: Check "Cập nhật chương trình" in Advanced tab

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ENHANCE YOUR PRODUCTIVITY WITH INTELLIGENT TRANSLATION
Ready to translate the world at your fingertips!"""
        
        # Insert content
        text_widget.insert('1.0', help_content)
        text_widget.config(state='disabled')
        
        # Button frame
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(15, 0))
        
        # Buttons
        def open_gemini_studio():
            import webbrowser
            webbrowser.open('https://aistudio.google.com/')
        
        def copy_guide():
            help_window.clipboard_clear()
            help_window.clipboard_append(help_content)
            tk.messagebox.showinfo("Copied", "User guide copied to clipboard!")
        
        tk.Button(btn_frame, text="🌐 Open Google AI Studio", command=open_gemini_studio,
                 font=('Segoe UI', 10), bg='#4285f4', fg='white', padx=20, pady=8).pack(side='left')
        
        tk.Button(btn_frame, text="📋 Copy Guide", command=copy_guide,
                 font=('Segoe UI', 10), bg='#95a5a6', fg='white', padx=20, pady=8).pack(side='left', padx=(10, 0))
        
        tk.Button(btn_frame, text="✕ Close", command=help_window.destroy, 
                 font=('Segoe UI', 10), bg='#e74c3c', fg='white', padx=30, pady=8).pack(side='right')
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
        
        about_text = f"""🌐 ITM Translate v{version_info}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 INTELLIGENT TRANSLATION MANAGER
Professional AI-Powered Translation Tool for Windows

📋 CORE FEATURES:
• 🎯 Smart Text Selection & Translation
• ⚡ Instant Popup Translation with Hotkeys  
• 🔄 Real-time Text Replacement
• 🧠 AI-Powered Language Detection (Mixed Language Support)
• 🎨 Dual Language Groups with Custom Hotkeys
• 🌍 Support 10+ Languages (EN, VI, KR, CN, JP, FR, DE, RU, ES, TH)

⭐ ADVANCED CAPABILITIES:
• 🤖 Gemini AI Integration for Accurate Translation
• 🔍 Automatic Language Detection (Auto-detect source language)
• 📝 Context-Aware Translation (Preserves meaning & tone)
• 🎛️ Flexible Hotkey Configuration (Ctrl/Alt/Shift combinations)
• 💾 Persistent Settings & Auto-backup
• 🔒 Secure API Key Management

🛠️ SYSTEM INTEGRATION:
• 🖥️ Windows Startup Integration
• 🔧 System Tray Background Operation
• 📊 Memory-efficient Performance
• 🎯 Global Hotkey Support (Works in any application)
• 🔒 Single Instance Protection

🔄 UPDATE SYSTEM:
• ✨ Intelligent Auto-Update with GitHub Integration
• 🛡️ Silent Background Updates with Admin Privileges
• 📦 Windows Batch-based Update Mechanism
• 🔄 Seamless Version Migration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 VERSION INFORMATION:
├─ Version: {version_info}
├─ Build: {build_info} 
├─ Release Date: {release_date}
└─ Architecture: Windows x64

👥 DEVELOPMENT TEAM:
├─ Lead Developer: KhanhIT ITM Team
├─ AI Integration: Gemini API Implementation
├─ UI/UX Design: Modern Bootstrap Theme
└─ Quality Assurance: Enterprise-grade Testing

🏢 COMPANY:
ITM Semiconductor Vietnam Company Limited
🌐 GitHub: github.com/quockhanh112hubt/ITM_Translate
📧 Support: Contact ITM IT Team
� Vietnam, 2025

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 DESIGNED FOR PROFESSIONALS
Enhance your productivity with intelligent translation at your fingertips

© 2025 ITM Semiconductor Vietnam Co., Ltd. All rights reserved."""
        
        # Tạo dialog custom với scroll để hiển thị đẹp
        about_window = tk.Toplevel(self.root)
        about_window.title("About ITM Translate")
        about_window.geometry("800x600")
        about_window.resizable(True, True)
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Center the dialog
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (about_window.winfo_screenheight() // 2) - (600 // 2)
        about_window.geometry(f"800x600+{x}+{y}")
        
        # Main frame with scrollbar
        main_frame = tk.Frame(about_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Text widget with scrollbar
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill='both', expand=True)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Consolas', 10), 
                             bg='#f8f9fa', fg='#2c3e50', padx=15, pady=15,
                             selectbackground='#3498db', selectforeground='white')
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Insert content
        text_widget.insert('1.0', about_text)
        text_widget.config(state='disabled')
        
        # Button frame
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(15, 0))
        
        tk.Button(btn_frame, text="Close", command=about_window.destroy, 
                 font=('Segoe UI', 10), bg='#3498db', fg='white', padx=30, pady=8).pack(side='right')
        
        # Copy info button
        def copy_version_info():
            about_window.clipboard_clear()
            about_window.clipboard_append(f"ITM Translate v{version_info} (Build: {build_info})")
            tk.messagebox.showinfo("Copied", "Version information copied to clipboard!")
        
        tk.Button(btn_frame, text="Copy Version", command=copy_version_info,
                 font=('Segoe UI', 10), bg='#95a5a6', fg='white', padx=20, pady=8).pack(side='right', padx=(0, 10))
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
        api_key = self.api_key_entry.get()
        if self.api_key_updater:
            self.api_key_updater(api_key)
        if changed:
            if messagebox.askokcancel("Thông báo", "Phím tắt đã được thay đổi, hãy khởi động lại chương trình để áp dụng"):
                try:
                    # Nếu có icon tray, dừng nó
                    if hasattr(self, 'tray_icon') and self.tray_icon:
                        self.tray_icon.stop()
                except Exception:
                    pass
                try:
                    from core.lockfile import release_lock
                    release_lock()
                except Exception:
                    pass
                self.root.destroy()
                import os
                os._exit(0)   
            else:
                return
        else:
            messagebox.showinfo("Thông báo", "Cấu hình đã được lưu thành công.")
        self.initial_hotkeys = new_hotkeys
        self.initial_api_key = api_key
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
