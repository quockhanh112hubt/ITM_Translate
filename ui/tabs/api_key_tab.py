"""
API Key Tab Component - ITM Translate
Quản lý tab API Key với tất cả chức năng quản lý API keys
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ttkbootstrap import SUCCESS, SECONDARY, INFO, DANGER, PRIMARY
from core.i18n import get_language_manager, _


class ApiKeyTab:
    """Component quản lý tab API Key với chức năng quản lý API keys"""
    
    def __init__(self, parent_frame, main_gui_instance):
        """
        Khởi tạo API Key Tab component
        
                                         text=_('edit_api_key'), 
                                  font=('Segoe UI', 12, 'bold')rgs:
            parent_frame: Frame cha để chứa tab
            main_gui_instance: Instance của MainGUI để access các method và callback
        """
        self.frame = parent_frame
        self.main_gui = main_gui_instance
        
        # Initialize language manager
        self.language_manager = get_language_manager()
        
        # Initialize UI elements
        self.api_key_tree = None
        self.new_key_entry = None
        self.provider_var = None
        self.model_var = None
        self.name_var = None
        self.key_status_label = None
        self.priority_listbox = None
        
        self._create_api_key_tab_ui()
    
    def _create_api_key_tab_ui(self):
        """Tạo giao diện cho API Key tab với design đẹp như ban đầu"""
        # Title và subtitle
        title = ttk.Label(self.frame, text=_('api_keys_title'), 
                         font=('Segoe UI', 16, 'bold'))
        title.pack(pady=(20, 5))
        
        subtitle = ttk.Label(self.frame, text=_('api_keys_subtitle'), 
                            font=('Segoe UI', 9), bootstyle=SECONDARY)
        subtitle.pack(pady=(0, 20))
        
        # Main content frame
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Left side - Key list  
        left_frame = ttk.LabelFrame(main_frame, text=_('api_keys_list'), bootstyle=INFO)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right side - Controls
        right_frame = ttk.LabelFrame(main_frame, text=_('actions'), bootstyle=INFO)
        right_frame.pack(side='right', fill='y', padx=(10, 0))
        
        # Create left side content
        self._create_keys_list_section(left_frame)
        
        # Create right side content 
        self._create_add_key_section(right_frame)
        self._create_control_buttons(right_frame)
        self._create_priority_section(right_frame)
        self._create_info_section(right_frame)
        
        # Load initial data
        self.refresh_api_keys()
    
    def _create_add_key_section(self, parent):
        """Tạo section thêm API key mới với style đẹp"""
        # Add key section - more compact layout
        add_frame = ttk.Frame(parent)
        add_frame.pack(fill='x', padx=10, pady=8)
        
        ttk.Label(add_frame, text=_('add_new_api_key'), font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        # Provider and Model in horizontal layout
        provider_model_frame = ttk.Frame(add_frame)
        provider_model_frame.pack(fill='x', pady=(5, 3))
        
        # Provider column
        provider_col = ttk.Frame(provider_model_frame)
        provider_col.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ttk.Label(provider_col, text=_('provider'), font=('Segoe UI', 9)).pack(anchor='w')
        self.provider_var = tk.StringVar(value='gemini')
        provider_combo = ttk.Combobox(provider_col, textvariable=self.provider_var, 
                                    values=['gemini', 'chatgpt', 'copilot', 'deepseek', 'claude'],
                                    state='readonly', width=18, font=('Segoe UI', 9))
        provider_combo.pack(fill='x')
        
        # Model column
        model_col = ttk.Frame(provider_model_frame)
        model_col.pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        ttk.Label(model_col, text=_('model'), font=('Segoe UI', 9)).pack(anchor='w')
        self.model_var = tk.StringVar(value='auto')
        self.model_combo = ttk.Combobox(model_col, textvariable=self.model_var, 
                                       state='readonly', width=18, font=('Segoe UI', 9))
        self.model_combo.pack(fill='x')
        
        # Bind provider change to update model list
        provider_combo.bind('<<ComboboxSelected>>', self.on_provider_changed)
        
        # Add tooltip for model info
        self.create_model_tooltip()
        
        # Initialize model list for default provider
        self.update_model_list()
        
        # Name and API Key in compact vertical layout
        name_frame = ttk.Frame(add_frame)
        name_frame.pack(fill='x', pady=(3, 3))
        
        ttk.Label(name_frame, text=_('name_optional'), font=('Segoe UI', 9)).pack(anchor='w')
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=35, font=('Segoe UI', 9))
        name_entry.pack(fill='x')
        
        # API Key input
        key_frame = ttk.Frame(add_frame)
        key_frame.pack(fill='x', pady=(3, 8))
        
        ttk.Label(key_frame, text=_('api_key'), font=('Segoe UI', 9)).pack(anchor='w')
        self.new_key_entry = ttk.Entry(key_frame, width=35, show='*', font=('Segoe UI', 9))
        self.new_key_entry.pack(fill='x')
        
        add_btn = ttk.Button(add_frame, text=_('add_key'), command=self.add_api_key, 
                           bootstyle=SUCCESS)
        add_btn.pack(fill='x', pady=(3, 0))
    
    def _create_keys_list_section(self, parent):
        """Tạo section danh sách API keys với style đẹp"""
        # Key listbox with scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for better display of provider info with Excel-like styling
        columns = ('Provider', 'Model', 'Name', 'Status', 'Key')
        self.api_key_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=10)
        
        # Configure Excel-like styling
        style = ttk.Style()
        style.configure("Treeview", 
                       background="white",
                       foreground="black",
                       rowheight=25,
                       fieldbackground="white",
                       borderwidth=1,
                       relief="solid")
        style.configure("Treeview.Heading", 
                       background="#f0f0f0",
                       foreground="black",
                       borderwidth=1,
                       relief="solid",
                       font=('Segoe UI', 9, 'bold'))
        
        # Configure column headers
        self.api_key_tree.heading('#0', text=_('active'))
        self.api_key_tree.heading('Provider', text=_('provider'))
        self.api_key_tree.heading('Model', text=_('model'))
        self.api_key_tree.heading('Name', text=_('name'))
        self.api_key_tree.heading('Status', text=_('status'))
        self.api_key_tree.heading('Key', text=_('api_key'))
        
        # Auto-sizing columns with minimum widths
        self.api_key_tree.column('#0', width=60, minwidth=50, anchor='center')
        self.api_key_tree.column('Provider', width=100, minwidth=80, anchor='center')
        self.api_key_tree.column('Model', width=150, minwidth=120, anchor='w')
        self.api_key_tree.column('Name', width=140, minwidth=100, anchor='w')
        self.api_key_tree.column('Status', width=100, minwidth=80, anchor='center')
        self.api_key_tree.column('Key', width=180, minwidth=150, anchor='w')
        
        # Add alternating row colors for better readability
        self.api_key_tree.tag_configure('oddrow', background='#f9f9f9')
        self.api_key_tree.tag_configure('evenrow', background='white')
        
        # Scrollbar for treeview
        scrollbar_keys = ttk.Scrollbar(list_frame, orient='vertical', command=self.api_key_tree.yview)
        self.api_key_tree.configure(yscrollcommand=scrollbar_keys.set)
        
        self.api_key_tree.pack(side='left', fill='both', expand=True)
        scrollbar_keys.pack(side='right', fill='y')
        
        # Key status frame
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.key_status_label = ttk.Label(status_frame, text='', font=('Segoe UI', 9))
        self.key_status_label.pack()
    
    def _create_control_buttons(self, parent):
        """Tạo control buttons với style đẹp"""
        # Control buttons - arranged in compact grid layout
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill='x', padx=10, pady=(15, 8))
        
        ttk.Label(control_frame, text=_('manage_keys'), font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        # Create grid for buttons - 2 columns
        btn_grid = ttk.Frame(control_frame)
        btn_grid.pack(fill='x', pady=(5, 0))
        
        # Configure grid columns
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)
        
        set_active_btn = ttk.Button(btn_grid, text=_('set_active'), 
                                  command=self.set_active_key, bootstyle=PRIMARY)
        set_active_btn.grid(row=0, column=0, sticky='ew', padx=(0, 3), pady=2)
        
        edit_btn = ttk.Button(btn_grid, text=_('edit'), 
                            command=self.edit_api_key, bootstyle=INFO)
        edit_btn.grid(row=0, column=1, sticky='ew', padx=(3, 0), pady=2)
        
        remove_btn = ttk.Button(btn_grid, text=_('remove'), 
                              command=self.remove_api_key, bootstyle=DANGER)
        remove_btn.grid(row=1, column=0, sticky='ew', padx=(0, 3), pady=2)
        
        refresh_btn = ttk.Button(btn_grid, text=_('refresh'), 
                               command=self.refresh_api_keys, bootstyle=SECONDARY)
        refresh_btn.grid(row=1, column=1, sticky='ew', padx=(3, 0), pady=2)
    
    def _create_priority_section(self, parent):
        """Tạo section quản lý priority với style đẹp"""
        # Provider priority section - more compact
        priority_frame = ttk.Frame(parent)
        priority_frame.pack(fill='x', padx=10, pady=(10, 8))
        
        ttk.Label(priority_frame, text=_('priority_providers'), font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        # Priority controls in horizontal layout
        priority_content = ttk.Frame(priority_frame)
        priority_content.pack(fill='x', pady=(5, 0))
        
        self.priority_listbox = tk.Listbox(priority_content, height=4, font=('Segoe UI', 9))
        self.priority_listbox.pack(side='left', fill='both', expand=True)
        
        priority_btn_frame = ttk.Frame(priority_content)
        priority_btn_frame.pack(side='right', fill='y', padx=(5, 0))
        
        up_btn = ttk.Button(priority_btn_frame, text='↑', command=self.move_priority_up, width=3)
        up_btn.pack(pady=(0, 3))
        
        down_btn = ttk.Button(priority_btn_frame, text='↓', command=self.move_priority_down, width=3)
        down_btn.pack()
    
    def _create_info_section(self, parent):
        """Tạo info section với style đẹp"""
        # Info section - more compact
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill='x', padx=10, pady=(10, 10))
        
        ttk.Label(info_frame, text=_('information'), font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        info_text = _('info_text')
        
        info_label = ttk.Label(info_frame, text=info_text, 
                             font=('Segoe UI', 8), bootstyle=SECONDARY,
                             wraplength=240, justify='left')
        info_label.pack(anchor='w', pady=(3, 0))
    
    def on_provider_changed(self, event=None):
        """Xử lý khi thay đổi provider"""
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
        """Cập nhật danh sách models dựa trên provider"""
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
            messagebox.showwarning(_('warning'), _('please_enter_api_key'))
            return
        
        if not model:
            model = "auto"
        
        # Disable add button during validation
        add_btn = None
        for widget in self.frame.winfo_children():
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if hasattr(child, 'winfo_children'):
                        for subchild in child.winfo_children():
                            if isinstance(subchild, ttk.Button) and "Thêm Key" in str(subchild.cget('text')):
                                add_btn = subchild
                                break
        
        if add_btn:
            add_btn.config(text=_('checking'), state='disabled')
        
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
                        add_btn.config(text=_('add_key'), state='normal')
                    
                    # Show validation result
                    if validation_info["type"] == "success":
                        # API key valid - proceed to add
                        proceed = messagebox.askquestion(
                            validation_info["title"],
                            validation_info["message"] + f"\n\n{_('confirm_save_api_key')}",
                            icon='question'
                        )
                        
                        if proceed == 'yes':
                            self._save_api_key(new_key, provider_str, model, name)
                    
                    elif validation_info["type"] == "warning":
                        # API key có issue nhưng có thể save
                        proceed = messagebox.askyesno(
                            validation_info["title"],
                            validation_info["message"] + f"\n\n{_('confirm_save_still')}",
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
                self.frame.after(0, show_result)
                
            except Exception as e:
                def show_error():
                    if add_btn:
                        add_btn.config(text=_('add_key'), state='normal')
                    messagebox.showerror(_('error'), f"{_('cannot_check_api_key')} {str(e)}")
                
                self.frame.after(0, show_error)
        
        # Start validation in background
        threading.Thread(target=validate_and_add, daemon=True).start()
    
    def _save_api_key(self, new_key: str, provider_str: str, model: str, name: str):
        """Helper method để save API key sau khi đã validate"""
        from core.api_key_manager import api_key_manager, AIProvider
        
        try:
            provider = AIProvider(provider_str)
            
            if api_key_manager.add_key(new_key, provider, model, name):
                messagebox.showinfo(f"✅ {_('success')}!", 
                    _('added_api_key_success').format(
                        provider=provider_str.upper(),
                        provider_title=provider_str.title(),
                        model=model,
                        name=name or f'{provider_str.title()} Key'
                    ))
                
                # Clear form
                self.new_key_entry.delete(0, 'end')
                self.model_var.set('auto')
                self.name_var.set('')
                self.refresh_api_keys()
            else:
                messagebox.showerror(_('error'), _('api_key_exists'))
                
        except ValueError:
            messagebox.showerror(_('error'), _('provider_not_supported').format(provider=provider_str))
    
    def remove_api_key(self):
        """Xóa API key đã chọn"""
        from core.api_key_manager import api_key_manager
        
        selection = self.api_key_tree.selection()
        if not selection:
            messagebox.showwarning(_('warning'), _('please_select_api_key_to_delete'))
            return
        
        # Get item data
        item = selection[0]
        index = self.api_key_tree.index(item)
        
        if messagebox.askyesno(_('confirm'), _('confirm_delete_api_key')):
            if api_key_manager.remove_key(index):
                self.refresh_api_keys()
                messagebox.showinfo(_('success'), _('api_key_deleted'))
            else:
                messagebox.showerror(_('error'), _('cannot_delete_api_key'))
    
    def set_active_key(self):
        """Đặt key được chọn làm active"""
        from core.api_key_manager import api_key_manager
        
        selection = self.api_key_tree.selection()
        if not selection:
            messagebox.showwarning(_('warning'), _('please_select_api_key_to_activate'))
            return
        
        item = selection[0]
        index = self.api_key_tree.index(item)
        
        if api_key_manager.set_active_index(index):
            self.refresh_api_keys()
            messagebox.showinfo(_('success'), _('api_key_activated'))
        else:
            messagebox.showerror(_('error'), _('cannot_activate_api_key'))
    
    def edit_api_key(self):
        """Chỉnh sửa thông tin API key"""
        from core.api_key_manager import api_key_manager, AIProvider
        
        selection = self.api_key_tree.selection()
        if not selection:
            messagebox.showwarning(_('warning'), _('please_select_api_key_to_edit'))
            return
        
        item = selection[0]
        index = self.api_key_tree.index(item)
        
        try:
            # Get key info from manager
            keys = api_key_manager.get_all_keys()
            if index >= len(keys):
                messagebox.showerror(_('error'), _('cannot_get_api_key_info'))
                return
            
            key_info = keys[index]
            
            # Create edit window đơn giản hơn để tránh lỗi
            edit_win = tk.Toplevel()
            edit_win.title(_('edit_api_key'))
            edit_win.geometry("500x450")
            edit_win.resizable(False, False)
            edit_win.transient(self.main_gui.root)
            edit_win.grab_set()
            
            # Center window
            edit_win.update_idletasks()
            x = (edit_win.winfo_screenwidth() // 2) - (250)
            y = (edit_win.winfo_screenheight() // 2) - (225)
            edit_win.geometry(f"500x450+{x}+{y}")
            
            # Main frame
            main_frame = ttk.Frame(edit_win, padding=20)
            main_frame.pack(fill='both', expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, 
                                  text="🔧 Chỉnh sửa API Key", 
                                  font=('Segoe UI', 14, 'bold'))
            title_label.pack(anchor='w', pady=(0, 15))
            
            # Form fields
            # Provider
            ttk.Label(main_frame, text=_('provider'), font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(5, 2))
            provider_var = tk.StringVar(value=key_info.provider.value)
            provider_combo = ttk.Combobox(main_frame, textvariable=provider_var, 
                                        values=['gemini', 'chatgpt', 'copilot', 'deepseek', 'claude'],
                                        state='readonly', width=50)
            provider_combo.pack(fill='x', pady=(0, 10))
            
            # Model
            ttk.Label(main_frame, text='Model:', font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(5, 2))
            model_var = tk.StringVar(value=key_info.model)
            model_combo = ttk.Combobox(main_frame, textvariable=model_var, 
                                     state='readonly', width=50)
            model_combo.pack(fill='x', pady=(0, 10))
            
            # Name
            ttk.Label(main_frame, text='Tên:', font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(5, 2))
            name_var = tk.StringVar(value=key_info.name or "")
            name_entry = ttk.Entry(main_frame, textvariable=name_var, width=50)
            name_entry.pack(fill='x', pady=(0, 10))
            
            # API Key
            ttk.Label(main_frame, text='API Key:', font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(5, 2))
            key_var = tk.StringVar(value=key_info.key)
            key_entry = ttk.Entry(main_frame, textvariable=key_var, show='*', width=50)
            key_entry.pack(fill='x', pady=(0, 10))
            
            # Status
            status_var = tk.BooleanVar(value=key_info.is_active)
            status_check = ttk.Checkbutton(main_frame, text=_('active_status'), variable=status_var)
            status_check.pack(anchor='w', pady=10)
            
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
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill='x', pady=(20, 0))
            
            def save_changes():
                try:
                    new_provider = AIProvider(provider_var.get())
                    new_model = model_var.get().strip() or "auto"
                    new_name = name_var.get().strip()
                    new_key = key_var.get().strip()
                    new_status = status_var.get()
                    
                    # Validate inputs
                    if not new_key:
                        messagebox.showwarning(_('warning'), _('api_key_empty'))
                        return
                    
                    if len(new_key) < 10:
                        messagebox.showwarning(_('warning'), _('api_key_too_short'))
                        return
                    
                    # Disable save button during validation
                    save_btn.configure(state='disabled', text=_('checking'))
                    cancel_btn.configure(state='disabled')
                    
                    def validate_and_save():
                        """Validate API key trong background thread"""
                        try:
                            # Only validate if key or provider changed
                            key_changed = new_key != key_info.key
                            provider_changed = new_provider != key_info.provider
                            
                            if key_changed or provider_changed:
                                from core.api_key_validator import APIKeyValidator, get_validation_message
                                
                                # Validate new API key
                                result, message = APIKeyValidator.validate_api_key(new_provider.value, new_key, new_model)
                                validation_info = get_validation_message(result, message)
                                
                                def handle_validation_result():
                                    """Handle validation result in main thread"""
                                    # Re-enable buttons
                                    save_btn.configure(state='normal', text='💾 Lưu')
                                    cancel_btn.configure(state='normal')
                                    
                                    if validation_info["type"] == "success":
                                        # API key valid - proceed to save
                                        proceed = messagebox.askquestion(
                                            _('validation_success'),
                                            f"{validation_info['message']}\n\n{_('confirm_save_changes')}",
                                            icon='question'
                                        )
                                        
                                        if proceed == 'yes':
                                            perform_save()
                                    
                                    elif validation_info["type"] == "warning":
                                        # API key có issue nhưng có thể save
                                        proceed = messagebox.askyesno(
                                            validation_info["title"],
                                            f"{validation_info['message']}\n\n{_('confirm_save_changes_anyway')}",
                                            icon='warning'
                                        )
                                        
                                        if proceed:
                                            perform_save()
                                    
                                    else:
                                        # API key invalid - không save
                                        messagebox.showerror(
                                            validation_info["title"],
                                            f"{validation_info['message']}\n\n{_('check_api_key_again')}"
                                        )
                                
                                # Schedule validation result handling in main thread
                                edit_win.after(0, handle_validation_result)
                            else:
                                # No validation needed, just save
                                def just_save():
                                    save_btn.configure(state='normal', text='💾 Lưu')
                                    cancel_btn.configure(state='normal')
                                    perform_save()
                                
                                edit_win.after(0, just_save)
                                
                        except Exception as e:
                            def show_validation_error():
                                save_btn.configure(state='normal', text='💾 Lưu')
                                cancel_btn.configure(state='normal')
                                messagebox.showerror(_('validation_error_title'), f"{_('cannot_check_api_key_validation')} {str(e)}")
                            
                            edit_win.after(0, show_validation_error)
                    
                    def perform_save():
                        """Actually save the changes after validation"""
                        try:
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
                            messagebox.showinfo(f"✅ {_('success')}", _('api_key_updated_success'))
                            edit_win.destroy()
                            self.refresh_api_keys()
                            
                        except Exception as e:
                            messagebox.showerror(_('error'), f"{_('cannot_save_changes')} {e}")
                    
                    # Start validation in background
                    import threading
                    threading.Thread(target=validate_and_save, daemon=True).start()
                    
                except ValueError:
                    messagebox.showerror(_('error'), _('invalid_provider'))
                except Exception as e:
                    messagebox.showerror(_('error'), f"{_('cannot_update')} {e}")
            
            # Buttons
            save_btn = ttk.Button(button_frame, text='💾 Lưu', command=save_changes)
            save_btn.pack(side='left', padx=(0, 10))
            
            cancel_btn = ttk.Button(button_frame, text='❌ Hủy', command=edit_win.destroy)
            cancel_btn.pack(side='left')
            
        except Exception as e:
            messagebox.showerror(_('error'), f"{_('cannot_open_edit_form')} {e}")
    
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
                status = _('status_disabled')
            elif key_info.failed_count > 0:
                status = f"{_('status_error')} {key_info.failed_count}"
            else:
                status = _('status_active')
            
            # Masked key
            masked_key = f"...{key_info.key[-8:]}" if len(key_info.key) > 8 else key_info.key
            
            # Apply alternating row colors
            row_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Insert into tree with alternating colors
            item = self.api_key_tree.insert('', 'end', text=is_active,
                                           values=(provider, model, name, status, masked_key),
                                           tags=(row_tag,))
        
        # Auto-resize columns based on content
        self._auto_resize_columns()
        
        # Update status
        if keys:
            active_key = api_key_manager.get_active_key()
            if active_key:
                status_text = f"{_('key_active_status')} {active_key.provider.value.title()} - {active_key.model}"
            else:
                status_text = _('no_active_key')
        else:
            status_text = _('no_api_keys')
        
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
    
    def _auto_resize_columns(self):
        """Tự động điều chỉnh kích thước cột dựa trên nội dung"""
        try:
            # Dictionary to store max width for each column
            column_widths = {}
            
            # Get all column identifiers
            all_columns = ['#0'] + list(self.api_key_tree['columns'])
            
            # Initialize with header widths
            for col in all_columns:
                if col == '#0':
                    header_text = 'Active'
                else:
                    header_text = self.api_key_tree.heading(col)['text']
                # Calculate header width (approximate)
                column_widths[col] = max(len(header_text) * 8, 50)
            
            # Check all items in the tree
            for item in self.api_key_tree.get_children():
                # Get the text for #0 column
                text_0 = self.api_key_tree.item(item, 'text')
                column_widths['#0'] = max(column_widths['#0'], len(str(text_0)) * 8 + 20)
                
                # Get values for other columns
                values = self.api_key_tree.item(item, 'values')
                for i, value in enumerate(values):
                    col = self.api_key_tree['columns'][i]
                    # Calculate width based on content (approximate pixel width)
                    content_width = len(str(value)) * 8 + 20  # 8 pixels per char + padding
                    column_widths[col] = max(column_widths[col], content_width)
            
            # Apply the calculated widths with reasonable limits
            for col, width in column_widths.items():
                # Set minimum and maximum widths
                min_width = 60
                max_width = 250
                
                # Special cases for specific columns
                if col == '#0':
                    min_width = 50
                    max_width = 80
                elif col == 'Provider':
                    min_width = 80
                    max_width = 120
                elif col == 'Model':
                    min_width = 120
                    max_width = 200
                elif col == 'Name':
                    min_width = 100
                    max_width = 180
                elif col == 'Status':
                    min_width = 80
                    max_width = 120
                elif col == 'Key':
                    min_width = 150
                    max_width = 200
                
                # Apply the width within limits
                final_width = max(min_width, min(width, max_width))
                self.api_key_tree.column(col, width=final_width)
                
        except Exception as e:
            print(f"Error in auto-resize columns: {e}")
    
    def refresh_language(self):
        """Refresh UI text when language changes"""
        # Không cần rebuild vì GUI đã recreate tabs rồi
        pass
