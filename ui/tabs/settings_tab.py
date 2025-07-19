import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
import os
import sys
from tkinter import messagebox


class SettingsTab:
    """Component quản lý tab Settings với cấu hình hotkey và ngôn ngữ"""
    
    def __init__(self, parent_frame, main_app, initial_langs=None):
        """
        Khởi tạo SettingsTab component
        
        Args:
            parent_frame: Frame cha để chứa settings tab
            main_app: Instance của MainApp để access các method và attributes
            initial_langs: Dict chứa initial language values
        """
        self.parent_frame = parent_frame
        self.main_app = main_app
        self.initial_langs = initial_langs or {}
        self.entries = {}
        self.lang_selects = {}
        self.initial_hotkeys = {}
        
        # Setup UI
        self.setup_settings_ui()
        
        # Load initial settings
        self.load_settings()
    
    def setup_settings_ui(self):
        """Tạo giao diện cho settings tab"""
        # Add title with styling
        style = ttk.Style()
        style.theme_use('flatly')
        title = ttk.Label(self.parent_frame, text='Cài đặt phím tắt & ngôn ngữ', 
                         font=('Segoe UI', 18, 'bold'), bootstyle='primary')
        title.pack(pady=(18, 18))
        
        # Main container with padding
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill='both', expand=True, padx=40, pady=(0, 20))
        
        # Create hotkey section
        self.setup_hotkey_section(main_container)
        
        # Add language selectors to hotkey sections (integrated approach)
        # Note: Language selectors are integrated into hotkey sections for better UX
    
    def setup_hotkey_section(self, parent):
        """Thiết lập phần cấu hình phím tắt với ngôn ngữ tích hợp"""
        # Define modifier và key options theo app gốc
        modifier_options = ['<none>', '<ctrl>', '<alt>', '<shift>']
        main_keys = [''] + [chr(i) for i in range(65, 91)] + [str(i) for i in range(0, 10)]  # '', A-Z, 0-9
        
        # Language options
        lang_options = [
            '', 'English', 'Tiếng Việt', '한국어', '中文', '日本語', 'Français', 
            'Deutsch', 'Русский', 'Español', 'ไทย'
        ]
        
        # Group 1: Tuỳ chọn mặc định
        group1 = ttk.LabelFrame(parent, text="Tuỳ chọn mặc định:", bootstyle='info')
        group1.pack(padx=0, pady=(16, 20), fill='x', ipadx=10, ipady=10)
        
        # Configure grid
        for i in range(8):
            group1.columnconfigure(i, weight=1)
        
        # Description
        ttk.Label(group1, text='Ngôn ngữ đầu tiên sẽ được dịch tới ngôn ngữ thứ 2, ngôn ngữ thứ 2 sẽ được dịch tới ngôn ngữ thứ 3.', 
                 font=('Segoe UI', 9, 'italic'), bootstyle='secondary').grid(row=0, column=0, columnspan=8, sticky='w', padx=8, pady=(10,6))
        
        # Headers
        ttk.Label(group1, text='Phím tắt:', font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='e', padx=(8,2), pady=(8,4))
        ttk.Label(group1, text='Modifier 1').grid(row=1, column=1, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group1, text='Modifier 2').grid(row=1, column=2, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group1, text='Phím chính').grid(row=1, column=3, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group1, text='Ngôn ngữ đầu tiên:').grid(row=1, column=4, sticky='n', padx=(18,2), pady=(8,4))
        ttk.Label(group1, text='Ngôn ngữ thứ 2:').grid(row=1, column=5, sticky='n', padx=(8,2), pady=(8,4))
        ttk.Label(group1, text='Ngôn ngữ thứ 3:').grid(row=1, column=6, sticky='n', padx=(8,2), pady=(8,4))
        
        # Dịch popup row
        ttk.Label(group1, text='Dịch popup').grid(row=2, column=0, sticky='e', padx=(8,2), pady=8)
        self.entries['translate_popup_mod1'] = ttk.Combobox(group1, values=modifier_options, width=7, state='readonly')
        self.entries['translate_popup_mod1'].grid(row=2, column=1, padx=2, pady=8)
        self.entries['translate_popup_mod2'] = ttk.Combobox(group1, values=modifier_options, width=7, state='readonly')
        self.entries['translate_popup_mod2'].grid(row=2, column=2, padx=2, pady=8)
        self.entries['translate_popup_key'] = ttk.Combobox(group1, values=main_keys, width=7, state='readonly')
        self.entries['translate_popup_key'].grid(row=2, column=3, padx=2, pady=8)
        
        # Language selectors for group 1
        self.lang_selects['Ngon_ngu_dau_tien'] = ttk.Combobox(group1, values=lang_options+['Any Language'], width=15, state='readonly')
        self.lang_selects['Ngon_ngu_dau_tien'].grid(row=2, column=4, padx=2, pady=8)
        self.lang_selects['Ngon_ngu_thu_2'] = ttk.Combobox(group1, values=lang_options, width=15, state='readonly')
        self.lang_selects['Ngon_ngu_thu_2'].grid(row=2, column=5, padx=2, pady=8)
        self.lang_selects['Ngon_ngu_thu_3'] = ttk.Combobox(group1, values=lang_options, width=15, state='readonly')
        self.lang_selects['Ngon_ngu_thu_3'].grid(row=2, column=6, padx=2, pady=8)
        
        # Dịch & thay thế row
        ttk.Label(group1, text='Dịch & thay thế').grid(row=3, column=0, sticky='e', padx=(8,2), pady=8)
        self.entries['replace_translate_mod1'] = ttk.Combobox(group1, values=modifier_options, width=7, state='readonly')
        self.entries['replace_translate_mod1'].grid(row=3, column=1, padx=2, pady=8)
        self.entries['replace_translate_mod2'] = ttk.Combobox(group1, values=modifier_options, width=7, state='readonly')
        self.entries['replace_translate_mod2'].grid(row=3, column=2, padx=2, pady=8)
        self.entries['replace_translate_key'] = ttk.Combobox(group1, values=main_keys, width=7, state='readonly')
        self.entries['replace_translate_key'].grid(row=3, column=3, padx=2, pady=8)
        
        # Toggle button for group 2
        self.group2_visible = False
        def toggle_group2():
            if self.group2_visible:
                group2.pack_forget()
                toggle_btn.config(text='Hiện Tuỳ chọn tuỳ chỉnh')
                self.group2_visible = False
                # Điều chỉnh kích thước cửa sổ về nhỏ
                self.main_app.root.geometry('1070x440')
            else:
                group2.pack(padx=0, pady=(12, 18), fill='x', ipadx=10, ipady=10)
                toggle_btn.config(text='Ẩn Tuỳ chọn tuỳ chỉnh')
                self.group2_visible = True
                # Điều chỉnh kích thước cửa sổ về lớn
                self.main_app.root.geometry('1070x650')
            
            # Cập nhật trạng thái trong main app để on_tab_changed biết
            self.main_app.group2_visible = self.group2_visible
        
        toggle_btn = ttk.Button(parent, text='Hiện Tuỳ chọn tuỳ chỉnh', command=toggle_group2, bootstyle='secondary')
        toggle_btn.pack(pady=(0, 2))
        
        # Group 2: Tuỳ chọn tuỳ chỉnh
        group2 = ttk.LabelFrame(parent, text="Tuỳ chọn tuỳ chỉnh:", bootstyle='info')
        
        # Configure grid
        for i in range(8):
            group2.columnconfigure(i, weight=1)
        
        # Description
        ttk.Label(group2, text='Ngôn ngữ đầu tiên sẽ được dịch tới ngôn ngữ thứ 2, ngôn ngữ thứ 2 sẽ được dịch tới ngôn ngữ thứ 3.', 
                 font=('Segoe UI', 9, 'italic'), bootstyle='secondary').grid(row=0, column=0, columnspan=8, sticky='w', padx=8, pady=(10,6))
        
        # Headers
        ttk.Label(group2, text='Phím tắt:', font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='e', padx=(8,2), pady=(8,4))
        ttk.Label(group2, text='Modifier 1').grid(row=1, column=1, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group2, text='Modifier 2').grid(row=1, column=2, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group2, text='Phím chính').grid(row=1, column=3, sticky='n', padx=2, pady=(8,4))
        ttk.Label(group2, text='Ngôn ngữ đầu tiên:').grid(row=1, column=4, sticky='n', padx=(18,2), pady=(8,4))
        ttk.Label(group2, text='Ngôn ngữ thứ 2:').grid(row=1, column=5, sticky='n', padx=(8,2), pady=(8,4))
        ttk.Label(group2, text='Ngôn ngữ thứ 3:').grid(row=1, column=6, sticky='n', padx=(8,2), pady=(8,4))
        
        # Dịch popup 2 row
        ttk.Label(group2, text='Dịch popup').grid(row=2, column=0, sticky='e', padx=(8,2), pady=8)
        self.entries['translate_popup2_mod1'] = ttk.Combobox(group2, values=modifier_options, width=7, state='readonly')
        self.entries['translate_popup2_mod1'].grid(row=2, column=1, padx=2, pady=8)
        self.entries['translate_popup2_mod2'] = ttk.Combobox(group2, values=modifier_options, width=7, state='readonly')
        self.entries['translate_popup2_mod2'].grid(row=2, column=2, padx=2, pady=8)
        self.entries['translate_popup2_key'] = ttk.Combobox(group2, values=main_keys, width=7, state='readonly')
        self.entries['translate_popup2_key'].grid(row=2, column=3, padx=2, pady=8)
        
        # Language selectors for group 2
        self.lang_selects['Nhom2_Ngon_ngu_dau_tien'] = ttk.Combobox(group2, values=lang_options+['Any Language'], width=15, state='readonly')
        self.lang_selects['Nhom2_Ngon_ngu_dau_tien'].grid(row=2, column=4, padx=2, pady=8)
        self.lang_selects['Nhom2_Ngon_ngu_thu_2'] = ttk.Combobox(group2, values=lang_options, width=15, state='readonly')
        self.lang_selects['Nhom2_Ngon_ngu_thu_2'].grid(row=2, column=5, padx=2, pady=8)
        self.lang_selects['Nhom2_Ngon_ngu_thu_3'] = ttk.Combobox(group2, values=lang_options, width=15, state='readonly')
        self.lang_selects['Nhom2_Ngon_ngu_thu_3'].grid(row=2, column=6, padx=2, pady=8)
        
        # Dịch & thay thế 2 row
        ttk.Label(group2, text='Dịch & thay thế').grid(row=3, column=0, sticky='e', padx=(8,2), pady=8)
        self.entries['replace_translate2_mod1'] = ttk.Combobox(group2, values=modifier_options, width=7, state='readonly')
        self.entries['replace_translate2_mod1'].grid(row=3, column=1, padx=2, pady=8)
        self.entries['replace_translate2_mod2'] = ttk.Combobox(group2, values=modifier_options, width=7, state='readonly')
        self.entries['replace_translate2_mod2'].grid(row=3, column=2, padx=2, pady=8)
        self.entries['replace_translate2_key'] = ttk.Combobox(group2, values=main_keys, width=7, state='readonly')
        self.entries['replace_translate2_key'].grid(row=3, column=3, padx=2, pady=8)
    
    def load_settings(self):
        """Load settings từ files"""
        # Load hotkeys
        if os.path.exists("hotkeys.json"):
            try:
                with open("hotkeys.json", "r", encoding="utf-8") as f:
                    hotkeys = json.load(f)
                    self.initial_hotkeys = hotkeys.copy()
                    
                    # Load hotkey values into UI
                    self.load_hotkey_values(hotkeys)
                    
                    # Load language values into UI
                    self.load_language_values(hotkeys)
            except Exception as e:
                print(f"Error loading hotkeys: {e}")
    
    def load_hotkey_values(self, hotkeys):
        """Load hotkey values vào UI components"""
        hotkey_mappings = {
            'translate_popup': ['translate_popup_mod1', 'translate_popup_mod2', 'translate_popup_key'],
            'replace_translate': ['replace_translate_mod1', 'replace_translate_mod2', 'replace_translate_key'],
            'translate_popup2': ['translate_popup2_mod1', 'translate_popup2_mod2', 'translate_popup2_key'],
            'replace_translate2': ['replace_translate2_mod1', 'replace_translate2_mod2', 'replace_translate2_key']
        }
        
        # Default values
        defaults = {
            'translate_popup': '<ctrl>+q',
            'replace_translate': '<ctrl>+d',
            'translate_popup2': '<ctrl>+1',
            'replace_translate2': '<ctrl>+2'
        }
        
        for hotkey_name, entry_names in hotkey_mappings.items():
            hotkey_str = hotkeys.get(hotkey_name, defaults.get(hotkey_name, ''))
            mod1, mod2, key = self.parse_hotkey(hotkey_str)
            
            self.entries[entry_names[0]].set(mod1)
            self.entries[entry_names[1]].set(mod2) 
            self.entries[entry_names[2]].set(key.upper() if key else '')
    
    def load_language_values(self, hotkeys):
        """Load language values vào UI components"""
        # Sử dụng initial_langs nếu có, nếu không thì dùng values từ hotkeys
        for lang_key, combobox in self.lang_selects.items():
            if lang_key in self.initial_langs:
                combobox.set(self.initial_langs[lang_key])
            elif lang_key in hotkeys:
                combobox.set(hotkeys[lang_key])
            else:
                # Default values
                defaults = {
                    'Ngon_ngu_dau_tien': 'Any Language',
                    'Ngon_ngu_thu_2': 'Tiếng Việt', 
                    'Ngon_ngu_thu_3': 'English',
                    'Nhom2_Ngon_ngu_dau_tien': 'Any Language',
                    'Nhom2_Ngon_ngu_thu_2': 'Tiếng Việt',
                    'Nhom2_Ngon_ngu_thu_3': 'English'
                }
                combobox.set(defaults.get(lang_key, ''))
    
    def parse_hotkey(self, hotkey_str):
        """Parse hotkey string thành các component - phù hợp với format gốc"""
        if not hotkey_str or hotkey_str == '':
            return '<none>', '<none>', ''
        
        # Parse theo format của app gốc
        parts = hotkey_str.split('+')
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
    
    def join_hotkey(self, mod1, mod2, key):
        """Join hotkey components thành string - phù hợp với format gốc"""
        mods = []
        if mod1 and mod1 != '<none>':
            mods.append(mod1)
        if mod2 and mod2 != '<none>' and mod2 != mod1:
            mods.append(mod2)
        if key == '' or key == '<none>':
            return '+'.join(mods)
        return '+'.join(mods + [key.lower()])
    
    def validate_hotkey_combination(self, mod1, mod2, key):
        """Validate hotkey combination với logic chi tiết như app gốc"""
        # Nếu tất cả đều empty hoặc <none> thì valid (nghĩa là không có hotkey)
        if (mod1 == '<none>' or mod1 == '') and (mod2 == '<none>' or mod2 == '') and (key == '<none>' or key == ''):
            return True, "__empty__"
        
        # Không cho phép Modifier 1 và Modifier 2 giống nhau (trừ khi đều là <none>)
        if mod1 != '<none>' and mod1 == mod2:
            return False, "Phím tắt Modifier 1 và Modifier 2 không được giống nhau!"
        
        # Đếm số components không rỗng
        values = [mod1, mod2, key]
        none_count = sum([v == '<none>' or v == '' for v in values])
        
        # Nếu có >= 2 values là none/empty và không phải tất cả đều none/empty thì invalid
        if none_count >= 2 and not all(v == '<none>' or v == '' for v in values):
            return False, "Phím tắt không hợp lệ!"
        
        # Nếu không phải empty hoàn toàn, phải có ít nhất 2 trong 3 components
        if none_count < 3:
            non_empty_count = sum([1 for v in values if v != '<none>' and v != ''])
            if non_empty_count < 2:
                return False, "Chưa chọn phím tắt hợp lệ!"
        
        return True, self.join_hotkey(mod1, mod2, key)
    
    def validate_language_group(self, lang_group, group_name):
        """Validate language group với logic chi tiết như app gốc"""
        # Đếm số ngôn ngữ đã chọn
        filled = [l for l in lang_group if l != '']
        empty_count = sum([l == '' for l in lang_group])
        
        # Nếu có 1 hoặc 2 ngôn ngữ trống trong 3 (không phải tất cả trống hoặc tất cả đầy)
        if 0 < empty_count < 3:
            return False, f"Bạn phải chọn đủ 3 ngôn ngữ cho {group_name}!"
        
        # Nếu cả 3 ngôn ngữ đã chọn nhưng có trùng lặp
        if len(filled) == 3 and len(set(lang_group)) < 3:
            return False, f"Ba ngôn ngữ trong {group_name} không được trùng nhau!"
        
        return True, ""
    
    def save_settings(self):
        """Lưu cấu hình settings với validation đầy đủ như app gốc"""
        try:
            # Collect data trước khi validate
            hotkey_data = self.collect_hotkey_data_basic()
            language_data = self.collect_language_data_basic()
            
            if not hotkey_data or not language_data:
                return
            
            # Thực hiện validation tổng thể như app gốc
            if not self.validate_comprehensive_settings(hotkey_data, language_data):
                return
            
            # Combine and save
            config = {**hotkey_data, **language_data}
            
            with open('hotkeys.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # Check if restart is needed
            if self.is_restart_needed(hotkey_data):
                if messagebox.askokcancel("Thông báo", "Phím tắt đã được thay đổi, hãy khởi động lại chương trình để áp dụng"):
                    self.restart_application()
                else:
                    return
            else:
                messagebox.showinfo("Thông báo", "Cấu hình đã được lưu thành công.")
            
            # Update initial hotkeys
            self.initial_hotkeys = hotkey_data.copy()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cấu hình: {str(e)}")
    
    def collect_hotkey_data_basic(self):
        """Collect hotkey data không validate - chỉ thu thập"""
        hotkey_entries = [
            ('translate_popup_mod1', 'translate_popup_mod2', 'translate_popup_key'),
            ('replace_translate_mod1', 'replace_translate_mod2', 'replace_translate_key'),
            ('translate_popup2_mod1', 'translate_popup2_mod2', 'translate_popup2_key'),
            ('replace_translate2_mod1', 'replace_translate2_mod2', 'replace_translate2_key')
        ]
        
        hotkey_combinations = []
        for mod1_key, mod2_key, key_key in hotkey_entries:
            mod1 = self.entries[mod1_key].get()
            mod2 = self.entries[mod2_key].get()
            key = self.entries[key_key].get()
            hotkey_combinations.append((mod1, mod2, key))
        
        # Create hotkey dictionary
        hotkey_names = ['translate_popup', 'replace_translate', 'translate_popup2', 'replace_translate2']
        hotkey_data = {}
        
        for i, name in enumerate(hotkey_names):
            mod1, mod2, key = hotkey_combinations[i]
            hotkey_data[name] = self.join_hotkey(mod1, mod2, key)
        
        return hotkey_data
    
    def collect_language_data_basic(self):
        """Collect language data không validate - chỉ thu thập"""
        language_data = {
            'Ngon_ngu_dau_tien': self.lang_selects['Ngon_ngu_dau_tien'].get(),
            'Ngon_ngu_thu_2': self.lang_selects['Ngon_ngu_thu_2'].get(),
            'Ngon_ngu_thu_3': self.lang_selects['Ngon_ngu_thu_3'].get(),
            'Nhom2_Ngon_ngu_dau_tien': self.lang_selects['Nhom2_Ngon_ngu_dau_tien'].get(),
            'Nhom2_Ngon_ngu_thu_2': self.lang_selects['Nhom2_Ngon_ngu_thu_2'].get(),
            'Nhom2_Ngon_ngu_thu_3': self.lang_selects['Nhom2_Ngon_ngu_thu_3'].get(),
        }
        
        return language_data
    
    def validate_comprehensive_settings(self, hotkey_data, language_data):
        """Validation tổng thể như app gốc"""
        # Collect combinations cho validation
        combos = [
            (self.entries['translate_popup_mod1'].get(), self.entries['translate_popup_mod2'].get(), self.entries['translate_popup_key'].get()),
            (self.entries['replace_translate_mod1'].get(), self.entries['replace_translate_mod2'].get(), self.entries['replace_translate_key'].get()),
            (self.entries['translate_popup2_mod1'].get(), self.entries['translate_popup2_mod2'].get(), self.entries['translate_popup2_key'].get()),
            (self.entries['replace_translate2_mod1'].get(), self.entries['replace_translate2_mod2'].get(), self.entries['replace_translate2_key'].get()),
        ]
        
        # Language groups
        group1_langs = [language_data['Ngon_ngu_dau_tien'], language_data['Ngon_ngu_thu_2'], language_data['Ngon_ngu_thu_3']]
        group2_langs = [language_data['Nhom2_Ngon_ngu_dau_tien'], language_data['Nhom2_Ngon_ngu_thu_2'], language_data['Nhom2_Ngon_ngu_thu_3']]
        lang_groups = [group1_langs, group2_langs]
        group_names = ['Tuỳ chọn mặc định', 'Tuỳ chọn tuỳ chỉnh']
        
        # 1. Kiểm tra tổng thể: nếu tất cả đều rỗng thì cho lưu
        all_hotkeys_empty = all(
            (m1 == '<none>' or m1 == '') and (m2 == '<none>' or m2 == '') and (k == '' or k == '<none>') 
            for m1, m2, k in combos
        )
        all_langs_empty = all(all(l == '' for l in group) for group in lang_groups)
        
        if all_hotkeys_empty and all_langs_empty:
            return True  # Cho lưu bình thường
        
        # 2. Kiểm tra từng tổ hợp phím tắt
        for idx, (mod1, mod2, key) in enumerate(combos):
            is_valid, error_msg = self.validate_hotkey_combination(mod1, mod2, key)
            if not is_valid:
                messagebox.showerror("Lỗi cấu hình", error_msg)
                return False
        
        # 3. Kiểm tra trùng phím tắt (normalize và compare)
        def normalize_hotkey(mod1, mod2, key):
            if all(v == '<none>' or v == '' for v in [mod1, mod2, key]):
                return '__empty__'
            mods = []
            if mod1 != '<none>' and mod1 != '':
                mods.append(mod1)
            if mod2 != '<none>' and mod2 != '' and mod2 != mod1:
                mods.append(mod2)
            mods = sorted(mods)
            key_part = key.lower() if key and key != '<none>' and key != '' else ''
            return '+'.join(mods + ([key_part] if key_part else []))
        
        normalized_hotkeys = [normalize_hotkey(*c) for c in combos]
        filtered_hotkeys = [h for h in normalized_hotkeys if h != '__empty__']
        
        if len(set(filtered_hotkeys)) < len(filtered_hotkeys):
            messagebox.showerror("Lỗi cấu hình", "Các tổ hợp phím tắt không được trùng nhau!")
            return False
        
        # 4. Kiểm tra ngôn ngữ từng group
        for group_langs, group_name in zip(lang_groups, group_names):
            is_valid, error_msg = self.validate_language_group(group_langs, group_name)
            if not is_valid:
                messagebox.showerror("Lỗi cấu hình", error_msg)
                return False
        
        # 5. Kiểm tra logic phức tạp: nếu có hotkey thì phải có ngôn ngữ
        for group_idx, (group_langs, group_name) in enumerate(zip(lang_groups, group_names)):
            # Lấy 2 hotkey của group này
            hotkey1 = combos[group_idx * 2]
            hotkey2 = combos[group_idx * 2 + 1]
            
            # Kiểm tra xem có hotkey nào không rỗng hoàn toàn
            for mod1, mod2, key in [hotkey1, hotkey2]:
                if not (mod1 == '<none>' and mod2 == '<none>' and (key == '' or key == '<none>')):
                    # Có hotkey -> phải có ngôn ngữ đầy đủ
                    if any(l == '' for l in group_langs):
                        messagebox.showerror("Lỗi cấu hình", f"Chưa chọn ngôn ngữ trong {group_name}")
                        return False
        
        # 6. Kiểm tra ngược: nếu có ngôn ngữ thì phải có ít nhất 1 hotkey hợp lệ
        for idx, (mod1, mod2, key) in enumerate(combos):
            group_langs = lang_groups[idx // 2]  # 2 hotkey đầu là group1, 2 hotkey sau là group2
            if not all(l == '' for l in group_langs):
                # Có ngôn ngữ -> phải có hotkey hợp lệ (ít nhất 2/3 components)
                count_non_empty = sum([1 for v in [mod1, mod2, key] if v != '' and v != '<none>'])
                if count_non_empty < 2:
                    messagebox.showerror("Lỗi cấu hình", "Chưa chọn phím tắt hợp lệ")
                    return False
        
        return True
    
    def is_restart_needed(self, new_hotkeys):
        """Kiểm tra có cần restart hay không"""
        if not self.initial_hotkeys:
            return True
        
        hotkey_keys = ['translate_popup', 'replace_translate', 'translate_popup2', 'replace_translate2']
        for key in hotkey_keys:
            if self.initial_hotkeys.get(key, '') != new_hotkeys.get(key, ''):
                return True
        
        return False
    
    def restart_application(self):
        """Restart application"""
        if hasattr(self.main_app, '_restart_with_batch'):
            self.main_app._restart_with_batch()
        else:
            # Fallback restart method
            messagebox.showinfo("Thông báo", "Vui lòng khởi động lại ứng dụng thủ công để áp dụng thay đổi.")
