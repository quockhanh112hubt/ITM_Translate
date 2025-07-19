"""
About Dialog Component - ITM Translate
Hiển thị thông tin về chương trình
"""

import tkinter as tk
import webbrowser
import json
import os


class AboutDialog:
    """Component quản lý hộp thoại About với thông tin chi tiết về chương trình"""
    
    def __init__(self, parent_root):
        """
        Khởi tạo About Dialog
        
        Args:
            parent_root: Root window của ứng dụng chính
        """
        self.parent_root = parent_root
        self.about_window = None
    
    def show(self):
        """Hiển thị hộp thoại About"""
        # Đọc thông tin version
        version_info, build_info, release_date = self._get_version_info()
        
        # Beautiful modern about window with light theme
        self.about_window = tk.Toplevel(self.parent_root)
        self.about_window.title("About ITM Translate v" + version_info)
        self.about_window.geometry("800x650")
        self.about_window.resizable(True, True)
        self.about_window.transient(self.parent_root)
        self.about_window.grab_set()
        
        # Modern light theme configuration
        self.about_window.configure(bg='#ffffff')
        
        # Center the dialog
        self.about_window.update_idletasks()
        x = (self.about_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.about_window.winfo_screenheight() // 2) - (650 // 2)
        self.about_window.geometry(f"800x650+{x}+{y}")
        
        self._create_header(version_info)
        self._create_content(version_info, build_info, release_date)
        self._create_buttons(version_info, build_info)
    
    def _get_version_info(self):
        """Đọc thông tin version từ file"""
        version_info = "1.0.0"
        build_info = "unknown"
        release_date = "unknown"
        
        try:
            version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "version.json")
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version_info = data.get('version', '1.0.0')
                    build_info = data.get('build', 'unknown')
                    release_date = data.get('release_date', 'unknown')
        except Exception:
            pass
        
        return version_info, build_info, release_date
    
    def _create_header(self, version_info):
        """Tạo header cho dialog"""
        # Create beautiful gradient header with blue theme
        header_frame = tk.Frame(self.about_window, bg='#4285f4', height=100)
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
    
    def _create_content(self, version_info, build_info, release_date):
        """Tạo nội dung about"""
        # Main frame with clean light theme
        main_frame = tk.Frame(self.about_window, bg='white')
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Text widget with beautiful light theme and modern scrollbar
        text_frame = tk.Frame(main_frame, bg='white')
        text_frame.pack(fill='both', expand=True)
        
        self.text_widget = tk.Text(text_frame, wrap='word', font=('Segoe UI', 11), 
                             bg='#fafafa', fg='#333333', padx=25, pady=20,
                             selectbackground='#4285f4', selectforeground='white',
                             insertbackground='#4285f4', relief='solid', borderwidth=1)
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=self.text_widget.yview,
                                bg='#f0f0f0', troughcolor='#fafafa', 
                                activebackground='#4285f4',
                                relief='flat', borderwidth=0, width=14)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Insert about content
        self._insert_about_content(version_info, build_info, release_date)
        
        self.text_widget.config(state='disabled')
        
        # Store main_frame reference for button creation
        self.main_frame = main_frame
    
    def _insert_about_content(self, version_info, build_info, release_date):
        """Chèn nội dung about vào text widget"""
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
├─ Cập nhật tự động/thủ công dựa trên phiên bản mới nhất
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
        
        # Insert content với màu sắc sinh động cho cả icon và text
        lines = about_text.split('\n')
        for line in lines:
            if line.startswith('🌐') and 'ITM Translate' in line:
                self.text_widget.insert('end', line + '\n', 'title')
            elif line.startswith('━━━'):
                self.text_widget.insert('end', line + '\n', 'separator')
            elif line.startswith('🚀') or line.startswith('📋') or line.startswith('⭐') or line.startswith('🔧') or line.startswith('🔄') or line.startswith('📊') or line.startswith('👥') or line.startswith('🏢') or line.startswith('🎯'):
                self.text_widget.insert('end', line + '\n', 'header')
            elif '•' in line and any(emoji in line for emoji in ['🎯', '⚡', '🔄', '🧠', '🎨', '🌍']):
                self.text_widget.insert('end', line + '\n', 'feature_blue')
            elif '•' in line and any(emoji in line for emoji in ['🤖', '🔍', '📝', '🎛️', '💾', '🔒']):
                self.text_widget.insert('end', line + '\n', 'feature_green')
            elif '•' in line and any(emoji in line for emoji in ['🖥️', '🔧', '📊', '🛡️', '📦']):
                self.text_widget.insert('end', line + '\n', 'feature_orange')
            elif '•' in line and any(emoji in line for emoji in ['✨']):
                self.text_widget.insert('end', line + '\n', 'feature_purple')
            elif '•' in line:
                self.text_widget.insert('end', line + '\n', 'normal')
            elif line.startswith('├─') or line.startswith('└─'):
                self.text_widget.insert('end', line + '\n', 'tree_info')
            elif line.startswith('© 2025'):
                self.text_widget.insert('end', line + '\n', 'copyright')
            else:
                self.text_widget.insert('end', line + '\n', 'normal')
        
        self._configure_text_tags()
    
    def _configure_text_tags(self):
        """Cấu hình các text tag với màu sắc đẹp"""
        self.text_widget.tag_configure("title", font=('Segoe UI', 16, 'bold'), foreground='#1a73e8')
        self.text_widget.tag_configure("header", font=('Segoe UI', 13, 'bold'), foreground='#4285f4')
        self.text_widget.tag_configure("separator", font=('Segoe UI', 10), foreground='#9aa0a6')
        self.text_widget.tag_configure("feature_blue", font=('Segoe UI', 11), foreground='#1976d2')
        self.text_widget.tag_configure("feature_green", font=('Segoe UI', 11), foreground='#388e3c')
        self.text_widget.tag_configure("feature_orange", font=('Segoe UI', 11), foreground='#f57c00')
        self.text_widget.tag_configure("feature_purple", font=('Segoe UI', 11), foreground='#7b1fa2')
        self.text_widget.tag_configure("tree_info", font=('Consolas', 10), foreground='#5f6368')
        self.text_widget.tag_configure("copyright", font=('Segoe UI', 9, 'italic'), foreground='#9aa0a6')
        self.text_widget.tag_configure("normal", font=('Segoe UI', 11), foreground='#555555')
    
    def _create_buttons(self, version_info, build_info):
        """Tạo các nút action cho dialog"""
        # Beautiful button frame with clean design
        btn_frame = tk.Frame(self.main_frame, bg='white', height=70)
        btn_frame.pack(fill='x', pady=(20, 0))
        btn_frame.pack_propagate(False)
        
        # Beautiful modern buttons with Google Material Design style
        github_btn = tk.Button(btn_frame, text="🌐 GitHub Repository", command=self._open_github,
                 font=('Segoe UI', 11, 'bold'), bg='#4285f4', fg='white', 
                 padx=30, pady=15, relief='flat', cursor='hand2',
                 activebackground='#3367d6', activeforeground='white')
        github_btn.pack(side='left', padx=(0, 15))
        
        copy_btn = tk.Button(btn_frame, text="📋 Copy Version Info", command=lambda: self._copy_version_info(version_info, build_info),
                 font=('Segoe UI', 11, 'bold'), bg='#34a853', fg='white', 
                 padx=30, pady=15, relief='flat', cursor='hand2',
                 activebackground='#2d7d32', activeforeground='white')
        copy_btn.pack(side='left', padx=(0, 15))
        
        close_btn = tk.Button(btn_frame, text="✕ Close", command=self.about_window.destroy, 
                 font=('Segoe UI', 11, 'bold'), bg='#f1f3f4', fg='#5f6368', 
                 padx=35, pady=15, relief='flat', cursor='hand2',
                 activebackground='#e8eaed', activeforeground='#202124')
        close_btn.pack(side='right')
    
    def _copy_version_info(self, version_info, build_info):
        """Copy version info to clipboard"""
        self.about_window.clipboard_clear()
        self.about_window.clipboard_append(f"ITM Translate v{version_info} (Build: {build_info})")
        tk.messagebox.showinfo("✅ Đã sao chép", "Thông tin phiên bản đã được sao chép vào clipboard!")
    
    def _open_github(self):
        """Open GitHub repository"""
        webbrowser.open('https://github.com/quockhanh112hubt/ITM_Translate')
