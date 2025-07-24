"""
Help Dialog Component - ITM Translate
Hiển thị hộp thoại hướng dẫn sử dụng chi tiết
"""

import tkinter as tk
import webbrowser
import os
import sys
from core.i18n import get_language_manager, _


class HelpDialog:
    """Component quản lý hộp thoại Help với hướng dẫn sử dụng chi tiết"""
    
    def __init__(self, parent_root):
        """
        Khởi tạo Help Dialog
        
        Args:
            parent_root: Root window của ứng dụng chính
        """
        self.parent_root = parent_root
        self.help_window = None
    
    def show(self):
        """Hiển thị hộp thoại Help"""
        # Beautiful modern help window with light theme
        self.help_window = tk.Toplevel(self.parent_root)
        self.help_window.title("🌟 ITM Translate - Multi-AI User Guide")
        self.help_window.geometry("950x900")
        self.help_window.resizable(True, True)
        self.help_window.transient(self.parent_root)
        self.help_window.grab_set()
        self.help_window.configure(bg='#ffffff')  # Clean white background
        
        # Center the dialog
        self.help_window.update_idletasks()
        x = (self.help_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.help_window.winfo_screenheight() // 2) - (700 // 2)
        self.help_window.geometry(f"950x900+{x}+{y}")
        
        self._create_header()
        self._create_content()
        self._create_buttons()
    
    def _create_header(self):
        """Tạo header cho dialog"""
        # Header frame with beautiful blue gradient
        header_frame = tk.Frame(self.help_window, bg='#4285f4', height=90)
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
                                 text="Multi-AI Translation Platform - Complete Professional Guide", 
                                 font=('Segoe UI', 11), 
                                 fg='#e8f0fe', bg='#4285f4')
        subtitle_label.pack()
    
    def _create_content(self):
        """Tạo nội dung help"""
        # Main content frame with clean styling
        main_frame = tk.Frame(self.help_window, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Text widget with beautiful light theme
        text_frame = tk.Frame(main_frame, bg='white')
        text_frame.pack(fill='both', expand=True)
        
        self.text_widget = tk.Text(text_frame, wrap='word', 
                             font=('Segoe UI', 11), 
                             bg='#fafafa', fg='#333333', 
                             padx=30, pady=25,
                             selectbackground='#4285f4', selectforeground='white',
                             insertbackground='#4285f4',
                             relief='solid',
                             borderwidth=1)
        
        # Beautiful scrollbar styling
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=self.text_widget.yview,
                                bg='#f0f0f0', troughcolor='#fafafa', 
                                activebackground='#4285f4',
                                relief='flat', borderwidth=0, width=14)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Insert help content
        self._insert_help_content()
        
        self.text_widget.config(state='disabled')
    
    def _insert_help_content(self):
        """Chèn nội dung help vào text widget"""
        help_content = self._get_help_content()
        
        # Insert content với màu sắc đẹp mắt cho cả icon và text
        lines = help_content.split('\n')
        for line in lines:
            if line.startswith('🌟'):
                self.text_widget.insert('end', line + '\n', 'title')
            elif line.startswith('━━━'):
                self.text_widget.insert('end', line + '\n', 'separator')
            elif line.startswith('📋') or line.startswith('🔧') or line.startswith('🚀') or line.startswith('⭐') or line.startswith('🛠️') or line.startswith('🌍') or line.startswith('📞'):
                self.text_widget.insert('end', line + '\n', 'header')
            elif line.startswith('🚨') or line.startswith('⚠️'):
                self.text_widget.insert('end', line + '\n', 'warning')
            elif line.startswith('💡'):
                self.text_widget.insert('end', line + '\n', 'highlight')
            elif line.startswith('Nhóm') or line.startswith('Bước'):
                self.text_widget.insert('end', line + '\n', 'step')
            elif any(line.startswith(prefix) for prefix in ['🤖 1.', '🧠 2.', '🎭 3.', '🐙 4.', '🌊 5.']):
                self.text_widget.insert('end', line + '\n', 'provider_title')
            elif '•' in line and any(emoji in line for emoji in ['🎯', '🔑', '📋', '⚙️', '🌐', '🖥️']):
                self.text_widget.insert('end', line + '\n', 'emoji_blue')
            elif '•' in line and any(emoji in line for emoji in ['🧠', '📝', '🔍', '✨', '🎨']):
                self.text_widget.insert('end', line + '\n', 'emoji_green')
            elif '•' in line and any(emoji in line for emoji in ['🔧', '📊', '🔒', '🎛️']):
                self.text_widget.insert('end', line + '\n', 'emoji_orange')
            elif '•' in line and any(emoji in line for emoji in ['🔄', '🇺🇸', '🇻🇳', '🇰🇷', '🇨🇳', '🇯🇵', '🇫🇷', '🇩🇪', '🇷🇺', '🇪🇸', '🇹🇭']):
                self.text_widget.insert('end', line + '\n', 'emoji_purple')
            elif '•' in line:
                self.text_widget.insert('end', line + '\n', 'subheader')
            else:
                self.text_widget.insert('end', line + '\n', 'normal')
        
        self._configure_text_tags()
    
    def _configure_text_tags(self):
        """Cấu hình các text tag với màu sắc đẹp"""
        self.text_widget.tag_configure("title", font=('Segoe UI', 16, 'bold'), foreground='#1a73e8')
        self.text_widget.tag_configure("header", font=('Segoe UI', 14, 'bold'), foreground='#4285f4')
        self.text_widget.tag_configure("separator", font=('Segoe UI', 10), foreground='#9aa0a6')
        self.text_widget.tag_configure("provider_title", font=('Segoe UI', 13, 'bold'), foreground='#1565c0')
        self.text_widget.tag_configure("subheader", font=('Segoe UI', 12, 'bold'), foreground='#34a853')
        self.text_widget.tag_configure("warning", font=('Segoe UI', 11, 'bold'), foreground='#ea4335')
        self.text_widget.tag_configure("highlight", font=('Segoe UI', 11, 'bold'), foreground='#9c27b0')
        self.text_widget.tag_configure("step", font=('Segoe UI', 11, 'bold'), foreground='#ff9800')
        self.text_widget.tag_configure("emoji_blue", font=('Segoe UI', 11), foreground='#1976d2')
        self.text_widget.tag_configure("emoji_green", font=('Segoe UI', 11), foreground='#388e3c')
        self.text_widget.tag_configure("emoji_orange", font=('Segoe UI', 11), foreground='#f57c00')
        self.text_widget.tag_configure("emoji_purple", font=('Segoe UI', 11), foreground='#7b1fa2')
        self.text_widget.tag_configure("normal", font=('Segoe UI', 11), foreground='#555555')
    
    def _create_buttons(self):
        """Tạo các nút action cho dialog"""
        # Main frame cho buttons
        main_frame = self.help_window.children['!frame2']  # Main content frame
        
        # Beautiful button frame with clean design
        btn_frame = tk.Frame(main_frame, bg='white', height=120)
        btn_frame.pack(fill='x', pady=(20, 0))
        btn_frame.pack_propagate(False)
        
        # First row - AI Provider platforms
        provider_frame = tk.Frame(btn_frame, bg='white')
        provider_frame.pack(fill='x', pady=(0, 10))
        
        # Provider buttons
        self._create_provider_buttons(provider_frame)
        
        # Second row - Actions
        action_frame = tk.Frame(btn_frame, bg='white')
        action_frame.pack(fill='x')
        
        self._create_action_buttons(action_frame)
    
    def _create_provider_buttons(self, parent_frame):
        """Tạo các nút provider"""
        # Gemini button
        gemini_btn = tk.Button(parent_frame, text="🤖 Gemini Studio", command=self._open_gemini_studio,
                 font=('Segoe UI', 10, 'bold'), bg='#4285f4', fg='white', 
                 padx=20, pady=12, relief='flat', cursor='hand2',
                 activebackground='#3367d6', activeforeground='white')
        gemini_btn.pack(side='left', padx=(0, 8))
        
        # OpenAI button
        openai_btn = tk.Button(parent_frame, text="🧠 OpenAI Platform", command=self._open_openai_platform,
                 font=('Segoe UI', 10, 'bold'), bg='#00a67e', fg='white', 
                 padx=20, pady=12, relief='flat', cursor='hand2',
                 activebackground='#008060', activeforeground='white')
        openai_btn.pack(side='left', padx=(0, 8))
        
        # Anthropic button
        anthropic_btn = tk.Button(parent_frame, text="🎭 Claude Console", command=self._open_anthropic_console,
                 font=('Segoe UI', 10, 'bold'), bg='#d97706', fg='white', 
                 padx=20, pady=12, relief='flat', cursor='hand2',
                 activebackground='#b45309', activeforeground='white')
        anthropic_btn.pack(side='left', padx=(0, 8))
        
        # DeepSeek button
        deepseek_btn = tk.Button(parent_frame, text="🌊 DeepSeek Platform", command=self._open_deepseek_platform,
                 font=('Segoe UI', 10, 'bold'), bg='#7c3aed', fg='white', 
                 padx=20, pady=12, relief='flat', cursor='hand2',
                 activebackground='#5b21b6', activeforeground='white')
        deepseek_btn.pack(side='left', padx=(0, 8))
        
        # GitHub Copilot button
        copilot_btn = tk.Button(parent_frame, text="🐙 GitHub Copilot", command=self._open_github_copilot,
                 font=('Segoe UI', 10, 'bold'), bg='#24292e', fg='white', 
                 padx=20, pady=12, relief='flat', cursor='hand2',
                 activebackground='#1b1f23', activeforeground='white')
        copilot_btn.pack(side='left')
    
    def _create_action_buttons(self, parent_frame):
        """Tạo các nút action"""
        copy_btn = tk.Button(parent_frame, text="📋 Copy Multi-AI Guide", command=self._copy_guide,
                 font=('Segoe UI', 11, 'bold'), bg='#34a853', fg='white', 
                 padx=35, pady=15, relief='flat', cursor='hand2',
                 activebackground='#2d7d32', activeforeground='white')
        copy_btn.pack(side='left', padx=(0, 15))
        
        close_btn = tk.Button(parent_frame, text="✕ Close", command=self.help_window.destroy, 
                 font=('Segoe UI', 11, 'bold'), bg='#f1f3f4', fg='#5f6368', 
                 padx=40, pady=15, relief='flat', cursor='hand2',
                 activebackground='#e8eaed', activeforeground='#202124')
        close_btn.pack(side='right')
    
    def _get_help_content(self):
        """Trả về nội dung help"""
        return _("help_content")
    
    # Provider URL opening methods
    def _open_gemini_studio(self):
        webbrowser.open('https://aistudio.google.com/')
    
    def _open_openai_platform(self):
        webbrowser.open('https://platform.openai.com/api-keys')
    
    def _open_anthropic_console(self):
        webbrowser.open('https://console.anthropic.com/')
    
    def _open_deepseek_platform(self):
        webbrowser.open('https://platform.deepseek.com/')
    
    def _open_github_copilot(self):
        webbrowser.open('https://github.com/settings/copilot')
    
    def _copy_guide(self):
        """Copy help content to clipboard"""
        help_content = self._get_help_content()
        self.help_window.clipboard_clear()
        self.help_window.clipboard_append(help_content)
        tk.messagebox.showinfo(_("help_copied"), _("help_copied_message"))
