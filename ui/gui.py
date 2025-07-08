import tkinter as tk
from tkinter import messagebox
import json
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import keyboard
import threading

class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('ITM Translate')
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
        messagebox.showinfo("Hướng dẫn sử dụng", "1. Chọn đoạn văn bản cần dịch.\n2. Nhấn phím tắt để dịch hoặc thay thế.\n3. Có thể thay đổi phím tắt và API key trong tab Cài Đặt.")
    def show_about(self):
        # Đọc version từ file version.json
        version_info = "1.0.0"
        try:
            import json
            import os
            version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.json")
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version_info = f"v{data.get('version', '1.0.0')} (Build {data.get('build', 'unknown')})"
        except Exception:
            pass
        
        messagebox.showinfo("Thông tin", 
                          f"ITM Translate\n"
                          f"Phiên bản: {version_info}\n"
                          f"🔄 Update Test Version - Enhanced Features\n"
                          f"Tác giả: KhanhIT ITM Team\n"
                          f"Github: github.com/ITM_Translate\n\n"
                          f"✨ New in this version:\n"
                          f"• Improved update mechanism\n"
                          f"• Enhanced error handling\n"
                          f"• Better user experience\n\n"
                          f"Powered by ITM Semiconductor Vietnam Company Limited\n"
                          f"Copyright © 2025 all rights reserved.")
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
