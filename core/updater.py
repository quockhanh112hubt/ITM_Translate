import os
import sys
import json
import requests
import tempfile
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import zipfile
import shutil
from datetime import datetime

class Updater:
    def __init__(self, current_version="1.0.0"):
        self.current_version = current_version
        self.config = self._load_config()
        self.update_server_url = self.config.get("update_server", {}).get("api_url", 
                                                "https://api.github.com/repos/YOUR_USERNAME/ITM_Translate/releases/latest")
        self.download_url = None
        self.new_version = None
        self.temp_dir = None
    
    def _load_config(self):
        """Đọc config từ file config.json"""
        try:
            config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
        
    def get_current_version(self):
        """Đọc version hiện tại từ file version.json"""
        try:
            version_file = os.path.join(os.path.dirname(__file__), "version.json")
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', '1.0.0')
        except Exception:
            pass
        return '1.0.0'
    
    def check_for_updates(self):
        """Kiểm tra version mới từ server"""
        try:
            # Thử với GitHub API trước
            response = requests.get(self.update_server_url, timeout=10)
            if response.status_code == 200:
                release_data = response.json()
                self.new_version = release_data['tag_name'].lstrip('v')
                
                # Tìm file .exe trong assets
                for asset in release_data.get('assets', []):
                    if asset['name'].endswith('.exe'):
                        self.download_url = asset['browser_download_url']
                        break
                
                if self.download_url and self._compare_versions(self.new_version, self.current_version) > 0:
                    return True, self.new_version, release_data.get('body', 'Cập nhật mới có sẵn')
                else:
                    return False, self.current_version, "Bạn đang sử dụng phiên bản mới nhất"
            else:
                return False, None, f"Không thể kết nối server cập nhật (HTTP {response.status_code})"
        except requests.RequestException as e:
            # Fallback: kiểm tra bằng cách khác hoặc thông báo offline
            if "github.com" in str(e) or "YOUR_USERNAME" in self.update_server_url:
                return False, None, "Chưa cấu hình server cập nhật. Vui lòng liên hệ nhà phát triển."
            return False, None, f"Lỗi kết nối: {str(e)}"
        except Exception as e:
            return False, None, f"Lỗi kiểm tra cập nhật: {str(e)}"
    
    def _compare_versions(self, v1, v2):
        """So sánh 2 version string (1.0.0 format)"""
        try:
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            return 0
        except Exception:
            return 0
    
    def download_update(self, progress_callback=None):
        """Download file cập nhật"""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="itm_update_")
            file_name = os.path.basename(self.download_url)
            temp_file_path = os.path.join(self.temp_dir, file_name)
            
            response = requests.get(self.download_url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            return temp_file_path
        except Exception as e:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            raise e
    
    def apply_update(self, downloaded_file_path):
        """Áp dụng cập nhật"""
        try:
            current_exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            current_dir = os.path.dirname(current_exe_path)
            backup_path = current_exe_path + ".backup"
            
            # Tạo backup file hiện tại
            if os.path.exists(current_exe_path):
                shutil.copy2(current_exe_path, backup_path)
            
            # Copy file mới
            shutil.copy2(downloaded_file_path, current_exe_path)
            
            # Cleanup temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            return True
        except Exception as e:
            # Restore backup if update failed
            if os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, current_exe_path)
                except Exception:
                    pass
            raise e
    
    def restart_application(self):
        """Khởi động lại ứng dụng"""
        try:
            current_exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            subprocess.Popen([current_exe_path], cwd=os.path.dirname(current_exe_path))
            sys.exit(0)
        except Exception as e:
            raise e

class UpdateDialog:
    def __init__(self, parent, updater, has_update=False, new_version="", changelog=""):
        self.updater = updater
        self.parent = parent
        self.dialog = None
        self.progress_var = None
        self.progress_bar = None
        self.status_label = None
        
        self.show_dialog(has_update, new_version, changelog)
    
    def show_dialog(self, has_update, new_version, changelog):
        """Hiển thị dialog cập nhật"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("ITM Translate - Kiểm tra cập nhật")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        if has_update:
            # Update available
            title_label = tk.Label(main_frame, text="🎉 Cập nhật mới có sẵn!", 
                                 font=('Segoe UI', 16, 'bold'), fg='#2e7d32')
            title_label.pack(pady=(0, 10))
            
            version_label = tk.Label(main_frame, 
                                   text=f"Phiên bản hiện tại: {self.updater.current_version}\nPhiên bản mới: {new_version}",
                                   font=('Segoe UI', 11))
            version_label.pack(pady=(0, 15))
            
            # Changelog
            changelog_label = tk.Label(main_frame, text="Nội dung cập nhật:", 
                                     font=('Segoe UI', 12, 'bold'))
            changelog_label.pack(anchor='w', pady=(0, 5))
            
            changelog_frame = tk.Frame(main_frame, relief='sunken', bd=1)
            changelog_frame.pack(fill='both', expand=True, pady=(0, 15))
            
            changelog_text = tk.Text(changelog_frame, wrap='word', font=('Segoe UI', 10),
                                   height=8, state='disabled')
            scrollbar = tk.Scrollbar(changelog_frame, orient='vertical', command=changelog_text.yview)
            changelog_text.configure(yscrollcommand=scrollbar.set)
            
            changelog_text.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            changelog_text.config(state='normal')
            changelog_text.insert('1.0', changelog)
            changelog_text.config(state='disabled')
            
            # Progress bar (hidden initially)
            progress_frame = tk.Frame(main_frame)
            progress_frame.pack(fill='x', pady=(0, 10))
            
            self.progress_var = tk.DoubleVar()
            self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                              maximum=100, length=460)
            
            self.status_label = tk.Label(progress_frame, text="", font=('Segoe UI', 9))
            
            # Buttons
            button_frame = tk.Frame(main_frame)
            button_frame.pack(fill='x')
            
            update_btn = tk.Button(button_frame, text="Cập nhật ngay", 
                                 command=self.start_update, font=('Segoe UI', 10),
                                 bg='#2e7d32', fg='white', padx=20)
            update_btn.pack(side='right', padx=(10, 0))
            
            cancel_btn = tk.Button(button_frame, text="Để sau", 
                                 command=self.dialog.destroy, font=('Segoe UI', 10),
                                 padx=20)
            cancel_btn.pack(side='right')
            
        else:
            # No update available
            title_label = tk.Label(main_frame, text="✅ Đã cập nhật!", 
                                 font=('Segoe UI', 16, 'bold'), fg='#1976d2')
            title_label.pack(pady=(50, 20))
            
            message_label = tk.Label(main_frame, text=changelog, 
                                   font=('Segoe UI', 12), wraplength=400)
            message_label.pack(pady=(0, 50))
            
            ok_btn = tk.Button(main_frame, text="OK", 
                             command=self.dialog.destroy, font=('Segoe UI', 10),
                             bg='#1976d2', fg='white', padx=30)
            ok_btn.pack()
    
    def start_update(self):
        """Bắt đầu quá trình cập nhật"""
        # Show progress UI
        self.progress_bar.pack(fill='x', pady=(0, 5))
        self.status_label.pack()
        
        # Disable update button
        for widget in self.dialog.winfo_children():
            if isinstance(widget, tk.Frame):
                for btn in widget.winfo_children():
                    if isinstance(btn, tk.Button) and btn['text'] == "Cập nhật ngay":
                        btn.config(state='disabled')
        
        # Start download in background thread
        threading.Thread(target=self._download_and_update, daemon=True).start()
    
    def _download_and_update(self):
        """Download và cập nhật (chạy trong background thread)"""
        try:
            # Download
            self.dialog.after(0, lambda: self.status_label.config(text="Đang tải xuống..."))
            downloaded_file = self.updater.download_update(self._update_progress)
            
            # Apply update
            self.dialog.after(0, lambda: (
                self.status_label.config(text="Đang cài đặt..."),
                self.progress_var.set(100)
            ))
            
            self.updater.apply_update(downloaded_file)
            
            # Success
            self.dialog.after(0, self._update_success)
            
        except Exception as e:
            self.dialog.after(0, lambda: self._update_error(str(e)))
    
    def _update_progress(self, progress):
        """Cập nhật progress bar"""
        self.dialog.after(0, lambda: self.progress_var.set(progress))
    
    def _update_success(self):
        """Xử lý khi cập nhật thành công"""
        self.status_label.config(text="Cập nhật thành công!")
        
        result = messagebox.askyesno("Cập nhật thành công", 
                                   "Cập nhật đã hoàn tất.\nBạn có muốn khởi động lại ứng dụng ngay không?",
                                   parent=self.dialog)
        if result:
            self.updater.restart_application()
        else:
            self.dialog.destroy()
    
    def _update_error(self, error_msg):
        """Xử lý khi cập nhật lỗi"""
        self.status_label.config(text=f"Lỗi: {error_msg}")
        messagebox.showerror("Lỗi cập nhật", f"Không thể cập nhật:\n{error_msg}", 
                           parent=self.dialog)

def check_for_updates_async(parent_window, show_no_update=True):
    """Kiểm tra cập nhật async (được gọi từ GUI)"""
    def check_updates():
        updater = Updater()
        updater.current_version = updater.get_current_version()
        
        has_update, version, message = updater.check_for_updates()
        
        # Show dialog in main thread
        if has_update or show_no_update:
            parent_window.after(0, lambda: UpdateDialog(parent_window, updater, has_update, version, message))
    
    threading.Thread(target=check_updates, daemon=True).start()
