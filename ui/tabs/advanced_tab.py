"""
Advanced Tab Component - ITM Translate
Quản lý tab Advanced với các tùy chọn nâng cao của ứng dụng
"""

import tkinter as tk
import json
import threading
from tkinter import messagebox
from core.i18n import get_language_manager, _


class AdvancedTab:
    """Component quản lý tab Advanced với các tùy chọn nâng cao"""
    
    def __init__(self, parent_frame, main_gui_instance):
        """
        Khởi tạo Advanced Tab component
        
        Args:
            parent_frame: Frame cha để chứa tab
            main_gui_instance: Instance của MainGUI để access các method và callback
        """
        self.frame = parent_frame
        self.main_gui = main_gui_instance
        
        # Initialize language manager
        self.language_manager = get_language_manager()
        
        # Initialize variables
        self.startup_var = None
        self.show_on_startup_var = None
        self.floating_button_enabled = None
        
        self._create_advanced_tab_ui()
    
    def _create_advanced_tab_ui(self):
        """Tạo giao diện cho Advanced tab"""
        # Khởi động cùng Windows
        self.startup_var = tk.BooleanVar(value=getattr(self.main_gui, 'initial_startup', False))
        startup_check = tk.Checkbutton(
            self.frame,
            text=_('startup_with_windows'),
            variable=self.startup_var,
            command=self.on_startup_toggle
        )
        startup_check.pack(anchor='w', padx=20, pady=(20, 5))
        
        # Bật hộp thoại khi khởi động
        self.show_on_startup_var = tk.BooleanVar(value=getattr(self.main_gui, 'initial_show_on_startup', True))
        show_on_startup_check = tk.Checkbutton(
            self.frame,
            text=_('show_window_startup'),
            variable=self.show_on_startup_var,
            command=self.on_show_on_startup_toggle
        )
        show_on_startup_check.pack(anchor='w', padx=20, pady=(0, 5))
        
        # Phát hiện văn bản tô đen
        self.floating_button_enabled = tk.BooleanVar(value=getattr(self.main_gui, 'initial_floating_button', True))
        floating_button_check = tk.Checkbutton(
            self.frame,
            text="Phát hiện văn bản tô đen (hiển thị nút DỊCH khi chọn text)",
            variable=self.floating_button_enabled,
            command=self.on_floating_button_toggle
        )
        floating_button_check.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Hướng dẫn sử dụng
        help_btn = tk.Button(
            self.frame, 
            text="Hướng dẫn sử dụng", 
            command=self._show_help
        )
        help_btn.pack(fill='x', padx=20, pady=5)
        
        # Thông tin về chương trình
        about_btn = tk.Button(
            self.frame, 
            text="Thông tin về chương trình", 
            command=self._show_about
        )
        about_btn.pack(fill='x', padx=20, pady=5)
        
        # Nút cập nhật chương trình
        update_btn = tk.Button(
            self.frame, 
            text="Cập nhật chương trình", 
            command=self._update_program
        )
        update_btn.pack(fill='x', padx=20, pady=5)
    
    def on_startup_toggle(self):
        """Xử lý khi toggle startup setting"""
        enabled = self.startup_var.get()
        
        # Lưu trạng thái vào file
        try:
            show_on_startup = self.show_on_startup_var.get() if self.show_on_startup_var else True
            floating_button = self.floating_button_enabled.get() if self.floating_button_enabled else True
            
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({
                    "startup": enabled, 
                    "show_on_startup": show_on_startup, 
                    "floating_button": floating_button
                }, f)
        except Exception:
            pass
        
        # Gọi callback để main.py xử lý shortcut
        if hasattr(self.main_gui, 'startup_callback') and self.main_gui.startup_callback:
            self.main_gui.startup_callback(enabled)
    
    def on_show_on_startup_toggle(self):
        """Xử lý khi toggle show on startup setting"""
        try:
            startup = self.startup_var.get() if self.startup_var else False
            show_on_startup = self.show_on_startup_var.get()
            floating_button = self.floating_button_enabled.get() if self.floating_button_enabled else True
            
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({
                    "startup": startup, 
                    "show_on_startup": show_on_startup, 
                    "floating_button": floating_button
                }, f)
        except Exception:
            pass
    
    def on_floating_button_toggle(self):
        """Xử lý khi toggle floating button setting"""
        try:
            startup = self.startup_var.get() if self.startup_var else False
            show_on_startup = self.show_on_startup_var.get() if self.show_on_startup_var else True
            floating_button = self.floating_button_enabled.get()
            
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({
                    "startup": startup, 
                    "show_on_startup": show_on_startup, 
                    "floating_button": floating_button
                }, f)
        except Exception:
            pass
        
        # Gọi callback để main.py xử lý floating button
        if hasattr(self.main_gui, 'floating_button_callback') and self.main_gui.floating_button_callback:
            self.main_gui.floating_button_callback(floating_button)
    
    def _show_help(self):
        """Delegate to main GUI's show_help method"""
        if hasattr(self.main_gui, 'show_help'):
            self.main_gui.show_help()
    
    def _show_about(self):
        """Delegate to main GUI's show_about method"""
        if hasattr(self.main_gui, 'show_about'):
            self.main_gui.show_about()
    
    def _update_program(self):
        """Delegate to main GUI's update_program method"""
        if hasattr(self.main_gui, 'update_program'):
            self.main_gui.update_program()
    
    def get_show_on_startup(self):
        """Trả về trạng thái show_on_startup"""
        return self.show_on_startup_var.get() if self.show_on_startup_var else True
    
    def get_floating_button_enabled(self):
        """Trả về trạng thái floating_button_enabled"""
        return self.floating_button_enabled.get() if self.floating_button_enabled else True
    
    def set_floating_button_callback(self, callback):
        """Set callback cho floating button từ main GUI"""
        # Lưu callback vào main_gui instance để component có thể access
        self.main_gui.floating_button_callback = callback
