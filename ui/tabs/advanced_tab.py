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
            text=_('floating_translate_button'),
            variable=self.floating_button_enabled,
            command=self.on_floating_button_toggle
        )
        floating_button_check.pack(anchor='w', padx=20, pady=(0, 5))
        
        # Excluded Applications section - đặt ngay cạnh floating button
        self.excluded_frame = tk.LabelFrame(self.frame, text=_('excluded_applications'), padx=10, pady=10)
        self.excluded_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Help text for excluded apps
        self.help_text = tk.Label(
            self.excluded_frame,
            text=_('excluded_apps_help'),
            font=("Arial", 8),
            fg="gray",
            wraplength=500,
            justify='left'
        )
        self.help_text.pack(anchor='w', pady=(0, 5))
        
        # Excluded apps listbox với scrollbar
        listbox_frame = tk.Frame(self.excluded_frame)
        listbox_frame.pack(fill='both', expand=True)
        
        self.excluded_apps_listbox = tk.Listbox(listbox_frame, height=6, selectmode='multiple')
        scrollbar = tk.Scrollbar(listbox_frame, orient='vertical')
        self.excluded_apps_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.excluded_apps_listbox.yview)
        
        self.excluded_apps_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons frame - simplified design
        btn_frame = tk.Frame(self.excluded_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        # Main button - Add running apps
        add_running_btn = tk.Button(btn_frame, text=_('add_running_apps'), command=self._add_running_apps)
        add_running_btn.pack(side='left', padx=(0, 5))
        
        # Remove selected button
        remove_btn = tk.Button(btn_frame, text=_('remove_application'), command=self._remove_excluded_app)
        remove_btn.pack(side='left', padx=(0, 5))
        
        # Clear all button
        clear_btn = tk.Button(btn_frame, text=_('clear_list'), command=self._clear_excluded_list)
        clear_btn.pack(side='left', padx=(0, 5))
        
        # Preset buttons frame
        preset_frame = tk.Frame(self.excluded_frame)
        preset_frame.pack(fill='x', pady=(5, 0))
        
        preset_office_btn = tk.Button(preset_frame, text=_('add_office_apps'), command=self._add_office_preset)
        preset_office_btn.pack(side='left', padx=(0, 5))
        
        preset_dev_btn = tk.Button(preset_frame, text=_('add_dev_apps'), command=self._add_dev_preset)
        preset_dev_btn.pack(side='left', padx=(0, 5))
        
        # Load excluded apps
        self._load_excluded_applications()
        
        # Update excluded frame state based on floating button
        self._update_excluded_frame_state()
        
        # Tự động đóng cửa sổ dịch
        self.auto_close_popup_var = tk.BooleanVar(value=getattr(self.main_gui, 'initial_auto_close_popup', True))
        auto_close_popup_check = tk.Checkbutton(
            self.frame,
            text=_('auto_close_popup'),
            variable=self.auto_close_popup_var,
            command=self.on_auto_close_popup_toggle
        )
        auto_close_popup_check.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Hướng dẫn sử dụng
        help_btn = tk.Button(
            self.frame, 
            text=_('usage_guide'), 
            command=self._show_help
        )
        help_btn.pack(fill='x', padx=20, pady=5)
        
        # Thông tin về chương trình
        about_btn = tk.Button(
            self.frame, 
            text=_('app_info'), 
            command=self._show_about
        )
        about_btn.pack(fill='x', padx=20, pady=5)
        
        # Nút cập nhật chương trình
        update_btn = tk.Button(
            self.frame, 
            text=_('check_updates'), 
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
            auto_close_popup = self.auto_close_popup_var.get() if self.auto_close_popup_var else True
            
            # Get excluded apps
            excluded_apps = []
            if hasattr(self, 'excluded_apps_listbox'):
                for i in range(self.excluded_apps_listbox.size()):
                    excluded_apps.append(self.excluded_apps_listbox.get(i))
            
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({
                    "startup": enabled, 
                    "show_on_startup": show_on_startup, 
                    "floating_button": floating_button,
                    "auto_close_popup": auto_close_popup,
                    "excluded_applications": excluded_apps
                }, f, ensure_ascii=False, indent=2)
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
            auto_close_popup = self.auto_close_popup_var.get() if self.auto_close_popup_var else True
            
            # Get excluded apps
            excluded_apps = []
            if hasattr(self, 'excluded_apps_listbox'):
                for i in range(self.excluded_apps_listbox.size()):
                    excluded_apps.append(self.excluded_apps_listbox.get(i))
            
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({
                    "startup": startup, 
                    "show_on_startup": show_on_startup, 
                    "floating_button": floating_button,
                    "auto_close_popup": auto_close_popup,
                    "excluded_applications": excluded_apps
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def on_floating_button_toggle(self):
        """Xử lý khi toggle floating button setting"""
        try:
            startup = self.startup_var.get() if self.startup_var else False
            show_on_startup = self.show_on_startup_var.get() if self.show_on_startup_var else True
            floating_button = self.floating_button_enabled.get()
            auto_close_popup = self.auto_close_popup_var.get() if self.auto_close_popup_var else True
            
            # Get excluded apps
            excluded_apps = []
            if hasattr(self, 'excluded_apps_listbox'):
                for i in range(self.excluded_apps_listbox.size()):
                    excluded_apps.append(self.excluded_apps_listbox.get(i))
            
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({
                    "startup": startup, 
                    "show_on_startup": show_on_startup, 
                    "floating_button": floating_button,
                    "auto_close_popup": auto_close_popup,
                    "excluded_applications": excluded_apps
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        
        # Gọi callback để main.py xử lý floating button
        if hasattr(self.main_gui, 'floating_button_callback') and self.main_gui.floating_button_callback:
            self.main_gui.floating_button_callback(floating_button)
        
        # Gọi callback để cập nhật tray icon
        if hasattr(self.main_gui, 'tray_update_callback') and self.main_gui.tray_update_callback:
            try:
                self.main_gui.tray_update_callback()
                print(f"🔄 Tray icon updated from Advanced Tab: floating_button = {floating_button}")
            except Exception as e:
                print(f"❌ Error updating tray icon: {e}")
        
        # Update excluded frame state
        self._update_excluded_frame_state()
    
    def on_auto_close_popup_toggle(self):
        """Xử lý khi toggle auto close popup setting"""
        try:
            startup = self.startup_var.get() if self.startup_var else False
            show_on_startup = self.show_on_startup_var.get() if self.show_on_startup_var else True
            floating_button = self.floating_button_enabled.get() if self.floating_button_enabled else True
            auto_close_popup = self.auto_close_popup_var.get()
            
            # Get excluded apps
            excluded_apps = []
            if hasattr(self, 'excluded_apps_listbox'):
                for i in range(self.excluded_apps_listbox.size()):
                    excluded_apps.append(self.excluded_apps_listbox.get(i))
            
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({
                    "startup": startup, 
                    "show_on_startup": show_on_startup, 
                    "floating_button": floating_button,
                    "auto_close_popup": auto_close_popup,
                    "excluded_applications": excluded_apps
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving auto close popup setting: {e}")
        
        # Gọi callback để cập nhật tray icon
        if hasattr(self.main_gui, 'tray_update_callback') and self.main_gui.tray_update_callback:
            try:
                self.main_gui.tray_update_callback()
                print(f"🔄 Tray icon updated from Advanced Tab: auto_close_popup = {auto_close_popup}")
            except Exception as e:
                print(f"❌ Error updating tray icon: {e}")
    
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
    
    def set_tray_update_callback(self, callback):
        """Set callback để cập nhật tray icon từ main GUI"""
        # Lưu callback vào main_gui instance để component có thể access
        self.main_gui.tray_update_callback = callback
    
    def _update_excluded_frame_state(self):
        """Cập nhật trạng thái của excluded frame dựa trên floating button"""
        try:
            floating_enabled = self.floating_button_enabled.get()
            print(f"🔍 [DEBUG] _update_excluded_frame_state called: floating_enabled = {floating_enabled}")
            
            if floating_enabled:
                # Floating button BẬT -> Enable excluded frame (cần thiết lập loại trừ)
                print(f"🔍 [DEBUG] Floating button ON -> Enabling excluded frame")
                self._enable_widget_recursive(self.excluded_frame)
            else:
                # Floating button TẮT -> Disable excluded frame (không cần thiết lập)
                print(f"🔍 [DEBUG] Floating button OFF -> Disabling excluded frame")
                self._disable_widget_recursive(self.excluded_frame)
        except Exception as e:
            print(f"❌ Error updating excluded frame state: {e}")
    
    def _enable_widget_recursive(self, widget):
        """Recursively enable widget and its children"""
        try:
            if hasattr(widget, 'configure'):
                widget.configure(state='normal')
        except:
            pass
        for child in widget.winfo_children():
            self._enable_widget_recursive(child)
    
    def _disable_widget_recursive(self, widget):
        """Recursively disable widget and its children"""
        try:
            if hasattr(widget, 'configure'):
                widget.configure(state='disabled')
        except:
            pass
        for child in widget.winfo_children():
            self._disable_widget_recursive(child)
    
    def _load_excluded_applications(self):
        """Load danh sách ứng dụng bị loại trừ từ file"""
        try:
            with open("startup.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                excluded_apps = data.get("excluded_applications", [])
                
                # Clear current list
                self.excluded_apps_listbox.delete(0, tk.END)
                
                # Add apps to listbox
                for app in excluded_apps:
                    self.excluded_apps_listbox.insert(tk.END, app)
        except Exception:
            # Default excluded apps nếu file không tồn tại
            default_apps = ["excel", "word", "powerpoint", "outlook"]
            for app in default_apps:
                self.excluded_apps_listbox.insert(tk.END, app)
            self._save_excluded_applications()
    
    def _save_excluded_applications(self):
        """Lưu danh sách ứng dụng bị loại trừ vào file"""
        try:
            # Get current settings
            startup = self.startup_var.get() if self.startup_var else False
            show_on_startup = self.show_on_startup_var.get() if self.show_on_startup_var else True
            floating_button = self.floating_button_enabled.get() if self.floating_button_enabled else True
            auto_close_popup = self.auto_close_popup_var.get() if self.auto_close_popup_var else True
            
            # Get excluded apps from listbox
            excluded_apps = []
            for i in range(self.excluded_apps_listbox.size()):
                excluded_apps.append(self.excluded_apps_listbox.get(i))
            
            # Save to file
            with open("startup.json", "w", encoding="utf-8") as f:
                json.dump({
                    "startup": startup,
                    "show_on_startup": show_on_startup,
                    "floating_button": floating_button,
                    "auto_close_popup": auto_close_popup,
                    "excluded_applications": excluded_apps
                }, f, ensure_ascii=False, indent=2)
                
            print(f"💾 Excluded applications saved: {excluded_apps}")
        except Exception as e:
            print(f"❌ Error saving excluded applications: {e}")
    
    def _add_excluded_app(self):
        """Thêm ứng dụng vào danh sách loại trừ"""
        from tkinter.simpledialog import askstring
        
        app_name = askstring(
            _('add_application'),
            _('enter_application_name') + "\n" + 
            _('examples') + ": excel, word, powerpoint, chrome, firefox"
        )
        
        if app_name and app_name.strip():
            app_name = app_name.strip().lower()
            
            # Check if already exists
            current_apps = []
            for i in range(self.excluded_apps_listbox.size()):
                current_apps.append(self.excluded_apps_listbox.get(i))
            
            if app_name not in current_apps:
                self.excluded_apps_listbox.insert(tk.END, app_name)
                self._save_excluded_applications()
                messagebox.showinfo(_('success'), f"'{app_name}' " + _('added_to_excluded_list'))
            else:
                messagebox.showwarning(_('warning'), f"'{app_name}' " + _('already_in_list'))
    
    def _auto_detect_app(self):
        """Tự động phát hiện ứng dụng hiện tại"""
        try:
            import win32gui
            import win32process
            import psutil
            import time
            
            # Show instruction dialog
            result = messagebox.askokcancel(
                _('auto_detect_app'),
                _('auto_detect_instruction')
            )
            
            if not result:
                return
            
            # Hide the main window temporarily
            if hasattr(self.main_gui, 'root'):
                self.main_gui.root.withdraw()
            
            # Wait a moment for user to switch to target app
            time.sleep(2)
            
            # Get active window
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                # Get process ID
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                
                # Get process name
                try:
                    process = psutil.Process(pid)
                    process_name = process.name().lower()
                    
                    # Remove .exe extension if present
                    if process_name.endswith('.exe'):
                        process_name = process_name[:-4]
                    
                    # Show the main window again
                    if hasattr(self.main_gui, 'root'):
                        self.main_gui.root.deiconify()
                        self.main_gui.root.lift()
                        self.main_gui.root.focus_force()
                    
                    # Check if already exists
                    current_apps = []
                    for i in range(self.excluded_apps_listbox.size()):
                        current_apps.append(self.excluded_apps_listbox.get(i))
                    
                    if process_name not in current_apps:
                        # Ask for confirmation
                        confirm_result = messagebox.askyesno(
                            _('confirm_add_app'),
                            f"{_('detected_app')}: '{process_name}'\n{_('add_to_excluded_list')}?"
                        )
                        
                        if confirm_result:
                            self.excluded_apps_listbox.insert(tk.END, process_name)
                            self._save_excluded_applications()
                            messagebox.showinfo(_('success'), f"'{process_name}' " + _('added_to_excluded_list'))
                    else:
                        messagebox.showwarning(_('warning'), f"'{process_name}' " + _('already_in_list'))
                        
                except psutil.NoSuchProcess:
                    # Show the main window again
                    if hasattr(self.main_gui, 'root'):
                        self.main_gui.root.deiconify()
                        self.main_gui.root.lift()
                    messagebox.showerror(_('error'), _('cannot_detect_app'))
            else:
                # Show the main window again
                if hasattr(self.main_gui, 'root'):
                    self.main_gui.root.deiconify()
                    self.main_gui.root.lift()
                messagebox.showerror(_('error'), _('no_active_window'))
                
        except ImportError:
            messagebox.showerror(_('error'), _('missing_dependencies_for_detection'))
        except Exception as e:
            # Show the main window again
            if hasattr(self.main_gui, 'root'):
                self.main_gui.root.deiconify()
                self.main_gui.root.lift()
            messagebox.showerror(_('error'), f"{_('detection_error')}: {str(e)}")
    
    def _add_running_apps(self):
        """Hiển thị danh sách ứng dụng đang chạy với multi-select"""
        try:
            import psutil
            import tkinter.ttk as ttk
            
            # Create new window
            apps_window = tk.Toplevel(self.main_gui.root)
            apps_window.title(_('running_applications'))
            apps_window.geometry("500x400")
            apps_window.resizable(True, True)
            
            # Center the window
            apps_window.transient(self.main_gui.root)
            apps_window.grab_set()
            
            # Create frame for the listbox
            frame = tk.Frame(apps_window)
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Add label
            label = tk.Label(frame, text=_('select_apps_to_add'), font=("Arial", 10, "bold"))
            label.pack(pady=(0, 10))
            
            # Create listbox with scrollbar - EXTENDED for multi-select
            listbox_frame = tk.Frame(frame)
            listbox_frame.pack(fill='both', expand=True)
            
            apps_listbox = tk.Listbox(listbox_frame, selectmode='extended')
            scrollbar_v = tk.Scrollbar(listbox_frame, orient='vertical')
            scrollbar_h = tk.Scrollbar(listbox_frame, orient='horizontal')
            
            apps_listbox.config(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
            scrollbar_v.config(command=apps_listbox.yview)
            scrollbar_h.config(command=apps_listbox.xview)
            
            apps_listbox.pack(side='left', fill='both', expand=True)
            scrollbar_v.pack(side='right', fill='y')
            scrollbar_h.pack(side='bottom', fill='x')
            
            # Get running processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if proc_name.endswith('.exe'):
                        proc_name = proc_name[:-4]
                    
                    # Filter out system processes and duplicates
                    if (proc_name not in ['system', 'registry', 'smss', 'csrss', 'wininit', 'winlogon', 'services', 'lsass', 'svchost', 'dwm'] 
                        and proc_name not in processes):
                        processes.append(proc_name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort and add to listbox
            processes.sort()
            for proc in processes:
                apps_listbox.insert(tk.END, proc)
            
            # Buttons frame
            btn_frame = tk.Frame(frame)
            btn_frame.pack(fill='x', pady=(10, 0))
            
            def add_selected_apps():
                selections = apps_listbox.curselection()
                if selections:
                    # Get current apps to check for duplicates
                    current_apps = []
                    for i in range(self.excluded_apps_listbox.size()):
                        current_apps.append(self.excluded_apps_listbox.get(i))
                    
                    added_apps = []
                    duplicate_apps = []
                    
                    for selection in selections:
                        selected_app = apps_listbox.get(selection)
                        if selected_app not in current_apps:
                            self.excluded_apps_listbox.insert(tk.END, selected_app)
                            added_apps.append(selected_app)
                        else:
                            duplicate_apps.append(selected_app)
                    
                    # Save if any apps were added
                    if added_apps:
                        self._save_excluded_applications()
                        apps_window.destroy()
                        
                        # Show success message
                        if len(added_apps) == 1:
                            messagebox.showinfo(_('success'), f"'{added_apps[0]}' " + _('added_to_excluded_list'))
                        else:
                            messagebox.showinfo(_('success'), f"{len(added_apps)} ứng dụng đã được thêm vào danh sách loại trừ")
                        
                        # Show warning for duplicates if any
                        if duplicate_apps:
                            if len(duplicate_apps) == 1:
                                messagebox.showwarning(_('warning'), f"'{duplicate_apps[0]}' " + _('already_in_list'))
                            else:
                                messagebox.showwarning(_('warning'), f"{len(duplicate_apps)} ứng dụng đã có trong danh sách")
                    else:
                        messagebox.showwarning(_('warning'), _('already_in_list'))
                else:
                    messagebox.showwarning(_('warning'), _('please_select_apps'))
            
            add_btn = tk.Button(btn_frame, text=_('add_selected'), command=add_selected_apps)
            add_btn.pack(side='left', padx=(0, 5))
            
            close_btn = tk.Button(btn_frame, text=_('close'), command=apps_window.destroy)
            close_btn.pack(side='right')
            
        except ImportError:
            messagebox.showerror(_('error'), _('missing_dependencies_for_detection'))
        except Exception as e:
            messagebox.showerror(_('error'), f"{_('error_loading_apps')}: {str(e)}")
    
    def _remove_excluded_app(self):
        """Xóa ứng dụng khỏi danh sách loại trừ (hỗ trợ multi-select)"""
        selection = self.excluded_apps_listbox.curselection()
        if selection:
            # Get selected app names before deletion (reverse order to maintain indices)
            selected_apps = []
            for i in reversed(selection):
                selected_apps.append(self.excluded_apps_listbox.get(i))
                self.excluded_apps_listbox.delete(i)
            
            self._save_excluded_applications()
            
            if len(selected_apps) == 1:
                messagebox.showinfo(_('success'), f"'{selected_apps[0]}' " + _('removed_from_excluded_list'))
            else:
                messagebox.showinfo(_('success'), f"{len(selected_apps)} " + _('apps_removed_from_list'))
        else:
            messagebox.showwarning(_('warning'), _('please_select_app_to_remove'))
    
    def _add_office_preset(self):
        """Thêm preset các ứng dụng Office"""
        office_apps = ["excel", "word", "powerpoint", "outlook", "onenote", "access", "publisher", "visio"]
        
        # Get current apps
        current_apps = []
        for i in range(self.excluded_apps_listbox.size()):
            current_apps.append(self.excluded_apps_listbox.get(i))
        
        added_count = 0
        for app in office_apps:
            if app not in current_apps:
                self.excluded_apps_listbox.insert(tk.END, app)
                added_count += 1
        
        if added_count > 0:
            self._save_excluded_applications()
            messagebox.showinfo(_('success'), f"{added_count} " + _('office_apps_added'))
        else:
            messagebox.showinfo(_('info'), _('all_office_apps_already_added'))
    
    def _add_dev_preset(self):
        """Thêm preset các ứng dụng Development"""
        dev_apps = ["code", "visual studio", "notepad++", "sublime text", "atom", "phpstorm", "intellij", "eclipse"]
        
        # Get current apps
        current_apps = []
        for i in range(self.excluded_apps_listbox.size()):
            current_apps.append(self.excluded_apps_listbox.get(i))
        
        added_count = 0
        for app in dev_apps:
            if app not in current_apps:
                self.excluded_apps_listbox.insert(tk.END, app)
                added_count += 1
        
        if added_count > 0:
            self._save_excluded_applications()
            messagebox.showinfo(_('success'), f"{added_count} " + _('dev_apps_added'))
        else:
            messagebox.showinfo(_('info'), _('all_dev_apps_already_added'))
    
    def _clear_excluded_list(self):
        """Xóa toàn bộ danh sách ứng dụng loại trừ"""
        if self.excluded_apps_listbox.size() == 0:
            messagebox.showinfo(_('info'), _('list_already_empty'))
            return
        
        # Confirm dialog
        if messagebox.askyesno(_('confirm'), _('confirm_clear_list')):
            self.excluded_apps_listbox.delete(0, tk.END)
            self._save_excluded_applications()
            messagebox.showinfo(_('success'), _('list_cleared'))
