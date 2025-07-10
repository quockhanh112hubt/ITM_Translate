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
                                                "https://api.github.com/repos/quockhanh112hubt/ITM_Translate/releases/latest")
        self.download_url = None
        self.new_version = None
        self.temp_dir = None
        # Debug logging for v1.0.8
        print(f"🔄 Updater v1.0.8 initialized - Enhanced update mechanism")
    
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
            print(f"Checking for updates at: {self.update_server_url}")  # Debug log
            
            # Chuẩn bị headers cho GitHub API
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'ITM-Translate-Updater'
            }
            
            # Thêm GitHub token nếu có (cho private repos)
            github_token = self.config.get("update_server", {}).get("github_token")
            if github_token:
                headers['Authorization'] = f'token {github_token}'
                print("Using GitHub token for private repository")
            
            # Thử với GitHub API
            response = requests.get(self.update_server_url, headers=headers, timeout=10)
            
            print(f"Response status: {response.status_code}")  # Debug log
            
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
            elif response.status_code == 404:
                # Repository không tồn tại hoặc không có quyền truy cập
                if github_token:
                    return False, None, f"Repository private không tìm thấy hoặc token không hợp lệ.\nKiểm tra lại GitHub token và quyền truy cập.\nURL: {self.update_server_url}"
                else:
                    return False, None, f"Repository không tồn tại hoặc là private.\nNếu repository là private, cần thêm GitHub token vào config.json.\nURL: {self.update_server_url}"
            elif response.status_code == 401:
                return False, None, f"GitHub token không hợp lệ hoặc hết hạn.\nVui lòng tạo token mới với quyền 'repo' access."
            else:
                return False, None, f"Không thể kết nối server cập nhật (HTTP {response.status_code})"
        except requests.RequestException as e:
            # Fallback: kiểm tra bằng cách khác hoặc thông báo offline
            error_msg = str(e)
            if "github.com" in error_msg:
                return False, None, f"Không thể kết nối đến GitHub.\nKiểm tra kết nối internet hoặc GitHub có bị chặn.\nLỗi: {error_msg}"
            return False, None, f"Lỗi kết nối: {error_msg}"
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
            last_progress = 0
            
            with open(temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            # Chỉ update UI khi progress thay đổi đáng kể (mỗi 1%)
                            if progress - last_progress >= 1.0:
                                progress_callback(progress)
                                last_progress = progress
            
            # Đảm bảo progress cuối cùng là 100%
            if progress_callback:
                progress_callback(100.0)
            
            return temp_file_path
        except Exception as e:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            raise e
    
    def apply_update(self, downloaded_file_path):
        """Áp dụng cập nhật một cách an toàn"""
        try:
            current_exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            current_dir = os.path.dirname(current_exe_path)
            backup_path = current_exe_path + ".backup"
            new_exe_path = current_exe_path + ".new"
            
            print(f"Applying update: {downloaded_file_path} -> {new_exe_path}")
            
            # Copy file mới với tên tạm thời (.new)
            shutil.copy2(downloaded_file_path, new_exe_path)
            print(f"Copied to: {new_exe_path}")
            
            # Tạo backup file hiện tại (nếu tồn tại)
            if os.path.exists(current_exe_path):
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                shutil.copy2(current_exe_path, backup_path)
                print(f"Backup created: {backup_path}")
            
            # Cleanup temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                print("Temp directory cleaned up")
            
            print("Apply update completed successfully")
            return True
            
        except Exception as e:
            print(f"Error in apply_update: {e}")
            # Cleanup if failed
            if os.path.exists(new_exe_path):
                try:
                    os.remove(new_exe_path)
                    print(f"Cleaned up failed update file: {new_exe_path}")
                except Exception:
                    pass
            raise e
    
    def restart_application(self):
        """Khởi động lại ứng dụng với file mới - Cải thiện an toàn hơn"""
        try:
            current_exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            new_exe_path = current_exe_path + ".new"
            backup_path = current_exe_path + ".backup"
            
            if getattr(sys, 'frozen', False):  # Chỉ cho executable
                # Approach: Dùng batch script đơn giản và tin cậy hơn
                batch_script = f'''@echo off
echo Starting ITM Translate update process...
timeout /t 3 /nobreak >nul

set "current_exe={current_exe_path}"
set "new_exe={new_exe_path}"
set "backup_exe={backup_path}"
set "app_dir={os.path.dirname(current_exe_path)}"

cd /d "%app_dir%"

echo Checking for new version file...
if not exist "%new_exe%" (
    echo ERROR: New version file not found!
    pause
    exit /b 1
)

echo Creating backup...
if exist "%current_exe%" (
    if exist "%backup_exe%" del "%backup_exe%" >nul 2>&1
    move "%current_exe%" "%backup_exe%" >nul 2>&1
)

echo Installing new version...
move "%new_exe%" "%current_exe%" >nul 2>&1

if not exist "%current_exe%" (
    echo ERROR: Failed to install new version!
    if exist "%backup_exe%" (
        echo Restoring backup...
        move "%backup_exe%" "%current_exe%" >nul 2>&1
    )
    pause
    exit /b 1
)

echo Starting new version...
start "" "%current_exe%"

echo Waiting for app to start...
timeout /t 3 /nobreak >nul

echo Cleaning up...
if exist "%backup_exe%" del "%backup_exe%" >nul 2>&1
if exist "%~f0" del "%~f0" >nul 2>&1

exit
'''
                
                # Tạo batch script
                batch_path = os.path.join(os.path.dirname(current_exe_path), "update_restart.bat")
                print(f"Creating batch script at: {batch_path}")  # Debug log
                
                with open(batch_path, 'w', encoding='utf-8') as f:
                    f.write(batch_script)
                
                print(f"Batch script created successfully")  # Debug log
                
                # Đảm bảo file batch có thể thực thi
                import stat
                os.chmod(batch_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
                
                print(f"Starting batch script: {batch_path}")  # Debug log
                
                # Chạy batch script với nhiều phương pháp fallback
                try:
                    # Phương pháp 1: subprocess.Popen với shell=True
                    process = subprocess.Popen(
                        [batch_path], 
                        shell=True, 
                        cwd=os.path.dirname(current_exe_path),
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    print(f"Batch process started with PID: {process.pid}")
                except Exception as e1:
                    print(f"Method 1 failed: {e1}")
                    try:
                        # Phương pháp 2: os.system
                        import threading
                        def run_batch():
                            os.system(f'start /min "" "{batch_path}"')
                        
                        thread = threading.Thread(target=run_batch, daemon=True)
                        thread.start()
                        print("Batch script started via os.system")
                    except Exception as e2:
                        print(f"Method 2 failed: {e2}")
                        # Phương pháp 3: subprocess.call với cmd
                        try:
                            subprocess.Popen(
                                ['cmd', '/c', 'start', '/min', batch_path],
                                cwd=os.path.dirname(current_exe_path),
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                            )
                            print("Batch script started via cmd")
                        except Exception as e3:
                            print(f"All methods failed: {e1}, {e2}, {e3}")
                            raise e3
                
            else:
                # Cho development mode - sử dụng python script đơn giản
                python_script = f'''
import os
import sys
import time
import subprocess
import shutil

time.sleep(2)
os.chdir(r"{os.path.dirname(current_exe_path)}")
subprocess.Popen([sys.executable, r"{current_exe_path}"])
'''
                script_path = os.path.join(os.path.dirname(current_exe_path), "dev_restart.py")
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(python_script)
                
                subprocess.Popen([sys.executable, script_path], 
                               cwd=os.path.dirname(current_exe_path))
            
            print("Exiting current application...")
            # Đợi một chút để batch script khởi động
            import time
            time.sleep(1)
            
            # Thoát ngay lập tức
            sys.exit(0)
            
        except Exception as e:
            print(f"Error in restart_application: {e}")
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
        self.dialog.geometry("500x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"500x500+{x}+{y}")
        
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
            self.button_frame = tk.Frame(main_frame)
            self.button_frame.pack(fill='x')
            
            self.update_btn = tk.Button(self.button_frame, text="Cập nhật ngay", 
                                 command=self.start_update, font=('Segoe UI', 10),
                                 bg='#2e7d32', fg='white', padx=20)
            self.update_btn.pack(side='right', padx=(10, 0))
            
            self.cancel_btn = tk.Button(self.button_frame, text="Để sau", 
                                 command=self.dialog.destroy, font=('Segoe UI', 10),
                                 padx=20)
            self.cancel_btn.pack(side='right')
            
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
        
        # Ẩn cả hai nút "Cập nhật ngay" và "Để sau"
        self.update_btn.pack_forget()
        self.cancel_btn.pack_forget()
        
        # Start download in background thread
        threading.Thread(target=self._download_and_update, daemon=True).start()
    
    def _download_and_update(self):
        """Download và cập nhật (chạy trong background thread)"""
        try:
            # Download
            self.dialog.after(0, lambda: self.status_label.config(text="Đang tải xuống..."))
            downloaded_file = self.updater.download_update(self._update_progress)
            
            # Apply update - Thêm thông báo progress chi tiết hơn
            self.dialog.after(0, lambda: (
                self.status_label.config(text="Đang chuẩn bị cài đặt..."),
                self.progress_var.set(95)
            ))
            
            # Thêm small delay để UI update
            import time
            time.sleep(0.5)
            
            self.dialog.after(0, lambda: (
                self.status_label.config(text="Đang sao chép file..."),
                self.progress_var.set(98)
            ))
            
            self.updater.apply_update(downloaded_file)
            
            self.dialog.after(0, lambda: (
                self.status_label.config(text="Hoàn tất!"),
                self.progress_var.set(100)
            ))
            
            # Success
            self.dialog.after(0, self._update_success)
            
        except Exception as e:
            self.dialog.after(0, lambda: self._update_error(str(e)))
    
    def _update_progress(self, progress):
        """Cập nhật progress bar một cách an toàn"""
        try:
            self.dialog.after(0, lambda: self.progress_var.set(progress))
        except Exception:
            # Bỏ qua nếu dialog đã bị đóng
            pass
    
    def _update_success(self):
        """Xử lý khi cập nhật thành công"""
        try:
            self.status_label.config(text="Cập nhật thành công! Sẵn sàng khởi động lại...")
            
            # Đợi 1 giây để user thấy message
            self.dialog.after(1000, self._show_restart_dialog)
        except Exception as e:
            print(f"Error in _update_success: {e}")
            # Fallback: hiện message ngay lập tức
            self._show_restart_dialog()
    
    def _show_restart_dialog(self):
        """Hiển thị dialog khởi động lại"""
        result = messagebox.askyesnocancel("Cập nhật thành công", 
                                         "Cập nhật đã hoàn tất!\n\n" +
                                         "Chọn cách khởi động lại:\n" +
                                         "• YES: Tự động khởi động lại (thử nghiệm)\n" +
                                         "• NO: Khởi động thủ công (khuyến nghị)\n" +
                                         "• CANCEL: Tiếp tục với phiên bản cũ\n\n" +
                                         "Lưu ý: Nếu YES gặp lỗi DLL, hãy chọn NO và làm thủ công.",
                                         parent=self.dialog)
        if result is True:  # YES - Auto restart (experimental)
            try:
                self.updater.restart_application()
            except Exception as e:
                error_detail = str(e)
                if "pydantic" in error_detail.lower() or "module" in error_detail.lower():
                    messagebox.showerror("Lỗi khởi động lại", 
                                       f"Khởi động tự động thất bại do lỗi dependencies:\n{error_detail}\n\n" +
                                       "GIẢI PHÁP:\n" +
                                       "1. Thoát chương trình hoàn toàn (Alt+F4)\n" +
                                       "2. Restart máy tính (khuyến nghị)\n" +
                                       "3. Chạy lại ITM_Translate.exe\n" +
                                       "4. Nếu vẫn lỗi, download lại từ GitHub\n\n" +
                                       "Lỗi này thường do PyInstaller bundling issue.",
                                       parent=self.dialog)
                else:
                    messagebox.showerror("Lỗi khởi động lại", 
                                       f"Khởi động tự động thất bại:\n{error_detail}\n\n" +
                                       "Hãy làm theo hướng dẫn thủ công:\n" +
                                       "1. Thoát chương trình (Alt+F4)\n" +
                                       "2. Vào thư mục chương trình\n" +
                                       "3. Xóa file .backup nếu có\n" +
                                       "4. Chạy ITM_Translate.exe\n\n" +
                                       "Nếu vẫn lỗi DLL, restart máy tính và thử lại.",
                                       parent=self.dialog)
        elif result is False:  # NO - Manual restart (recommended)
            self._show_manual_restart_instructions()
        # result is None (CANCEL) - Do nothing, keep current version
    
    def _show_manual_restart_instructions(self):
        """Hiển thị hướng dẫn khởi động thủ công chi tiết"""
        instructions = """✅ CẬP NHẬT HOÀN TẤT - Hướng dẫn khởi động thủ công

🔧 BƯỚC 1: Thoát chương trình
• Nhấn Alt+F4 hoặc đóng tất cả cửa sổ ITM Translate
• Đảm bảo không còn process nào đang chạy

📁 BƯỚC 2: Vào thư mục chương trình
• Mở thư mục chứa file ITM_Translate.exe
• Bạn sẽ thấy các file: .exe, .new, .backup

🔄 BƯỚC 3: Thực hiện cập nhật
• Xóa file ITM_Translate.exe (file cũ)
• Đổi tên ITM_Translate.exe.new thành ITM_Translate.exe
• Xóa file .backup (nếu có)

🚀 BƯỚC 4: Khởi động lại
• KHUYẾN NGHỊ: Restart máy tính trước
• Chạy file ITM_Translate.exe mới
• Kiểm tra version trong settings

⚠️ NẾU GẶP LỖI "No module named 'pydantic_core'":
• Đây là lỗi PyInstaller bundling
• PHẢI restart máy tính
• Chạy với quyền Administrator
• Tạm thời disable antivirus
• Nếu vẫn lỗi: download lại từ GitHub releases

⚠️ NẾU GẶP LỗI "Failed to load Python DLL":
• Restart máy tính (bắt buộc)
• Chạy với quyền Administrator
• Kiểm tra antivirus không block file

Bạn có muốn mở thư mục chương trình không?"""
        
        response = messagebox.askyesno("Hướng dẫn cập nhật thủ công", instructions, parent=self.dialog)
        if response:
            # Mở thư mục chứa executable
            current_exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            folder_path = os.path.dirname(current_exe_path)
            try:
                os.startfile(folder_path)
            except Exception:
                pass
        
        self.dialog.destroy()
    
    def _update_error(self, error_msg):
        """Xử lý khi cập nhật lỗi"""
        self.status_label.config(text=f"Lỗi: {error_msg}")
        
        # Hiển thị lại các nút để người dùng có thể thử lại hoặc hủy
        self.update_btn.pack(side='right', padx=(10, 0))
        self.cancel_btn.pack(side='right')
        
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
