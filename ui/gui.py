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
from core.i18n import get_language_manager, _
from ui.components.language_flags import LanguageFlagButtons
from core.update_notifier import get_update_notifier, start_update_monitoring

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
        # Initialize language manager
        self.language_manager = get_language_manager()
        
        # Đọc version và set title với version
        app_version = get_app_version()
        self.root.title(f'ITM Translate v{app_version}')
        self.root.geometry('1070x420')
        self.hotkey_manager = None
        self.hotkey_updater = None
        self.startup_callback = None
        self.initial_hotkeys = None
        self.initial_api_key = None
        self.initial_startup = False
        self.initial_show_on_startup = True
        
        # Initialize language flags
        self.language_flags = None
        
        # Initialize update notifier
        self.update_notifier = get_update_notifier()
        self.update_notifier.register_callback(self._on_update_notification)
        
        # Start update monitoring in background
        start_update_monitoring()
    def set_hotkey_manager(self, manager):
        self.hotkey_manager = manager
    def set_hotkey_updater(self, updater):
        self.hotkey_updater = updater
    def set_startup_callback(self, callback):
        self.startup_callback = callback
    def set_initial_settings(self, hotkeys_dict, api_key, startup_enabled=False, show_on_startup=True, floating_button=False, auto_close_popup=True):
        self.initial_hotkeys = hotkeys_dict
        self.initial_api_key = api_key
        self.initial_startup = startup_enabled
        self.initial_show_on_startup = show_on_startup
        self.initial_floating_button = floating_button
        self.initial_auto_close_popup = auto_close_popup
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
        # Lưu reference đến footer buttons để có thể update text
        self.save_button = ttk.Button(right_btn_frame, text=_('save_close_settings'), style='Custom.TButton', command=self.save_settings, bootstyle=PRIMARY)
        self.save_button.pack(side='left', padx=(0,8))
        self.cancel_button = ttk.Button(right_btn_frame, text=_('cancel'), style='Custom.TButton', command=on_cancel, bootstyle=SECONDARY)
        self.cancel_button.pack(side='left')
        
        # Tạo notebook sau footer để footer luôn ở dưới cùng
        self.tab_control = ttk.Notebook(self.root, bootstyle=PRIMARY)
        self.settings_tab = ttk.Frame(self.tab_control)
        self.api_key_tab = ttk.Frame(self.tab_control)
        self.advanced_tab = ttk.Frame(self.tab_control)
        self.history_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.settings_tab, text=_('tab_settings'))
        self.tab_control.add(self.api_key_tab, text=_('tab_api_keys'))
        self.tab_control.add(self.advanced_tab, text=_('tab_advanced'))
        self.tab_control.add(self.history_tab, text='📚 History')
        
        # Language flags positioned in top-right corner (overlaid on window, near minimize button)
        self.language_flags = LanguageFlagButtons(self.root, on_language_change=self.on_language_change)
        self.language_flags.place(relx=1.0, rely=0.0, anchor='ne', x=0, y=30)
        
        # Bind sự kiện chuyển tab để tự động điều chỉnh kích thước
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        self.tab_control.pack(expand=1, fill='both')
        self.create_settings_tab()
        self.create_api_key_tab()
        self.create_advanced_tab()
        self.create_history_tab()

    def on_tab_changed(self, event):
        """Xử lý sự kiện chuyển tab và tự động điều chỉnh kích thước cửa sổ"""
        selected_tab = event.widget.select()
        tab_index = event.widget.index(selected_tab)
        
        # Điều chỉnh kích thước cửa sổ theo tab được chọn (sử dụng index thay vì text)
        if tab_index == 0:  # Settings tab
            # Tab Cài Đặt: kích thước mặc định hoặc mở rộng nếu có Group 2
            if hasattr(self, 'group2_visible') and self.group2_visible:
                self.root.geometry('1070x650')
            else:
                self.root.geometry('1070x440')
        elif tab_index == 1:  # API Keys tab
            # Tab API Key: cần không gian lớn hơn cho danh sách keys và controls
            self.root.geometry('1070x860')
            # Tự động làm mới danh sách API keys khi chuyển sang tab này
            try:
                if hasattr(self, 'refresh_api_keys'):
                    self.refresh_api_keys()
            except Exception as e:
                print(f"Warning: Could not auto-refresh API keys: {e}")
        elif tab_index == 2:  # Advanced tab
            # Tab Nâng Cao: kích thước nhỏ gọn
            self.root.geometry('1070x800')
        elif tab_index == 3:  # History tab
            # Tab History: cần không gian lớn để hiển thị danh sách history
            self.root.geometry('1070x800')
            # Refresh history when switching to this tab
            try:
                if hasattr(self, 'history_tab_component'):
                    self.history_tab_component.refresh_history()
            except Exception as e:
                print(f"Warning: Could not refresh history: {e}")
        
        # Đảm bảo cửa sổ được cập nhật
        self.root.update_idletasks()

    def create_settings_tab(self):
        """Tạo tab settings sử dụng SettingsTab component"""
        from ui.tabs.settings_tab import SettingsTab
        
        # Tạo SettingsTab component và pass initial_langs
        self.settings_tab_instance = SettingsTab(self.settings_tab, self, self.initial_langs)
        
        # Export các variables để các method khác có thể access
        self.entries = self.settings_tab_instance.entries
        self.lang_selects = self.settings_tab_instance.lang_selects
        self.initial_hotkeys = self.settings_tab_instance.initial_hotkeys

    def create_api_key_tab(self):
        """Tạo tab quản lý API KEY sử dụng ApiKeyTab component"""
        from ui.tabs.api_key_tab import ApiKeyTab
        
        # Tạo ApiKeyTab component
        self.api_key_tab_component = ApiKeyTab(self.api_key_tab, self)
        
        # Export các variables để các method khác có thể access
        self.api_key_tree = self.api_key_tab_component.api_key_tree
        self.new_key_entry = self.api_key_tab_component.new_key_entry
        self.provider_var = self.api_key_tab_component.provider_var
        self.model_var = self.api_key_tab_component.model_var
        self.name_var = self.api_key_tab_component.name_var
        self.key_status_label = self.api_key_tab_component.key_status_label
        self.priority_listbox = self.api_key_tab_component.priority_listbox
    
    # Delegate API key methods to component
    def add_api_key(self):
        """Delegate to API key tab component"""
        self.api_key_tab_component.add_api_key()
    
    def remove_api_key(self):
        """Delegate to API key tab component"""
        self.api_key_tab_component.remove_api_key()
    
    def set_active_key(self):
        """Delegate to API key tab component"""
        self.api_key_tab_component.set_active_key()
    
    def edit_api_key(self):
        """Delegate to API key tab component"""
        self.api_key_tab_component.edit_api_key()
    
    def refresh_api_keys(self):
        """Delegate to API key tab component"""
        self.api_key_tab_component.refresh_api_keys()
    
    def move_priority_up(self):
        """Delegate to API key tab component"""
        self.api_key_tab_component.move_priority_up()
    
    def move_priority_down(self):
        """Delegate to API key tab component"""
        self.api_key_tab_component.move_priority_down()

    def create_advanced_tab(self):
        """Tạo Advanced tab sử dụng AdvancedTab component"""
        from ui.tabs.advanced_tab import AdvancedTab
        
        # Tạo AdvancedTab component và gán các biến để compatibility
        self.advanced_tab_component = AdvancedTab(self.advanced_tab, self)
        
        # Export các variables để các method khác có thể access
        self.startup_var = self.advanced_tab_component.startup_var
        self.show_on_startup_var = self.advanced_tab_component.show_on_startup_var
        self.floating_button_enabled = self.advanced_tab_component.floating_button_enabled
        self.auto_close_popup_var = self.advanced_tab_component.auto_close_popup_var

    def create_history_tab(self):
        """Tạo History tab sử dụng HistoryTab component"""
        from ui.tabs.history_tab import HistoryTab
        
        # Tạo HistoryTab component
        self.history_tab_component = HistoryTab(self.history_tab)

    def on_startup_toggle(self):
        enabled = self.startup_var.get()
        # Lưu trạng thái vào file (để nhớ khi khởi động lại)
        try:
            # Đọc trạng thái show_on_startup và floating_button hiện tại
            show_on_startup = self.show_on_startup_var.get() if hasattr(self, 'show_on_startup_var') else True
            floating_button = self.floating_button_enabled.get() if hasattr(self, 'floating_button_enabled') else True
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({"startup": enabled, "show_on_startup": show_on_startup, "floating_button": floating_button}, f)
        except Exception:
            pass
        # Gọi callback để main.py xử lý shortcut
        if self.startup_callback:
            self.startup_callback(enabled)
    def on_show_on_startup_toggle(self):
        # Lưu cả ba trạng thái vào file
        try:
            startup = self.startup_var.get() if hasattr(self, 'startup_var') else False
            show_on_startup = self.show_on_startup_var.get()
            floating_button = self.floating_button_enabled.get() if hasattr(self, 'floating_button_enabled') else True
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({"startup": startup, "show_on_startup": show_on_startup, "floating_button": floating_button}, f)
        except Exception:
            pass
    def on_floating_button_toggle(self):
        # Lưu cả ba trạng thái vào file
        try:
            startup = self.startup_var.get() if hasattr(self, 'startup_var') else False
            show_on_startup = self.show_on_startup_var.get() if hasattr(self, 'show_on_startup_var') else True
            floating_button = self.floating_button_enabled.get()
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({"startup": startup, "show_on_startup": show_on_startup, "floating_button": floating_button}, f)
        except Exception:
            pass
        # Gọi callback để main.py xử lý floating button
        if hasattr(self, 'floating_button_callback'):
            self.floating_button_callback(floating_button)
    
    def set_floating_button_callback(self, callback):
        self.floating_button_callback = callback
    
    def set_tray_update_callback(self, callback):
        """Set callback để cập nhật tray icon khi settings thay đổi"""
        self.tray_update_callback = callback
        # Cũng set cho advanced tab component nếu đã được khởi tạo
        if hasattr(self, 'advanced_tab_component'):
            self.advanced_tab_component.set_tray_update_callback(callback)
    
    def get_show_on_startup(self):
        return self.show_on_startup_var.get() if hasattr(self, 'show_on_startup_var') else True
    def get_floating_button_enabled(self):
        return self.floating_button_enabled.get() if hasattr(self, 'floating_button_enabled') else True
    
    def show_help(self):
        """Hiển thị dialog Help sử dụng HelpDialog component"""
        from ui.dialogs.help_dialog import HelpDialog
        
        help_dialog = HelpDialog(self.root)
        help_dialog.show()
    
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
├─ Tích hợp AI cho kết quả dịch chính xác
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
    def show_about(self):
        """Hiển thị dialog About sử dụng AboutDialog component"""
        from ui.dialogs.about_dialog import AboutDialog
        
        about_dialog = AboutDialog(self.root)
        about_dialog.show()
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
        """Delegate to Settings tab component"""
        if hasattr(self, 'settings_tab_instance'):
            self.settings_tab_instance.save_settings()
        else:
            messagebox.showerror(_('error'), _('settings_not_initialized'))
    
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
        """Tạo restart.bat, chạy với quyền Admin và thoát ứng dụng sử dụng RestartManager"""
        from ui.components.restart_manager import RestartManager
        
        restart_manager = RestartManager()
        restart_manager.restart_with_batch()
    
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
    
    def on_language_change(self, language):
        """Xử lý thay đổi ngôn ngữ - refresh toàn bộ UI"""
        try:
            print(f"🌐 Language changed to: {language}")
            
            # Update window title
            app_version = get_app_version()
            self.root.title(_(
                "app_title",
                language
            ).replace("v1.2.3", f"v{app_version}"))
            
            # Update tab titles with update indicator
            current_tab_index = self.tab_control.index(self.tab_control.select())
            self.tab_control.tab(0, text=_("tab_settings", language))
            self.tab_control.tab(1, text=_("tab_api_keys", language))
            self.tab_control.tab(2, text=self._get_advanced_tab_title(language))
            
            # Refresh all UI components by recreating them
            self._refresh_all_components(language)
            
            # Restore selected tab
            self.tab_control.select(current_tab_index)
            
        except Exception as e:
            print(f"❌ Error changing language: {e}")
    
    def _refresh_all_components(self, language):
        """Refresh tất cả components với ngôn ngữ mới"""
        try:
            # Clear existing content
            for widget in self.settings_tab.winfo_children():
                widget.destroy()
            for widget in self.api_key_tab.winfo_children():
                widget.destroy()
            for widget in self.advanced_tab.winfo_children():
                widget.destroy()
            
            # Recreate tabs with new language - không cần gọi refresh_language nữa
            self.create_settings_tab()
            self.create_api_key_tab()
            self.create_advanced_tab()
            
            # Update footer buttons - cải thiện logic
            self._update_footer_buttons(language)
            
        except Exception as e:
            print(f"❌ Error refreshing components: {e}")
    
    def _update_footer_buttons(self, language):
        """Cập nhật text cho footer buttons"""
        try:
            # Update footer buttons directly using references
            if hasattr(self, 'save_button'):
                self.save_button.configure(text=_("save_close_settings", language))
            if hasattr(self, 'cancel_button'):
                self.cancel_button.configure(text=_("cancel", language))
        except Exception as e:
            print(f"❌ Error updating footer buttons: {e}")
    
    def _on_update_notification(self, has_update, new_version):
        """Callback khi có update notification từ UpdateNotifier"""
        try:
            # Kiểm tra tab_control đã được khởi tạo chưa
            if not hasattr(self, 'tab_control') or self.tab_control is None:
                print("⚠️ Tab control not ready yet, skipping update notification")
                return
                
            # Update advanced tab title
            current_language = self.language_manager.get_current_language()
            self.tab_control.tab(2, text=self._get_advanced_tab_title(current_language))
            
            if has_update:
                print(f"🎉 Update available: {new_version}")
            else:
                print("✅ No updates available")
                
        except Exception as e:
            print(f"❌ Error handling update notification: {e}")
    
    def _get_advanced_tab_title(self, language=None):
        """Lấy title cho Advanced tab với update indicator nếu có"""
        if language is None:
            language = self.language_manager.get_current_language()
        
        base_title = _("tab_advanced", language)
        return self.update_notifier.get_update_indicator_text(base_title)
    
    def cleanup(self):
        """Cleanup khi đóng app"""
        try:
            # Cleanup advanced tab
            if hasattr(self, 'advanced_tab_component') and hasattr(self.advanced_tab_component, 'cleanup'):
                self.advanced_tab_component.cleanup()
            
            # Unregister update callback
            if self.update_notifier:
                self.update_notifier.unregister_callback(self._on_update_notification)
        except Exception as e:
            print(f"❌ Error cleaning up MainGUI: {e}")
