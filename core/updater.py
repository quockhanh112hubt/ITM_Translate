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
            
            # Tạo update.bat file
            self.create_update_batch_file(current_exe_path, current_dir)
            
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
    
    def create_update_batch_file(self, current_exe_path, app_dir):
        """Tạo file update.bat để thực hiện cập nhật"""
        try:
            batch_file_path = os.path.join(app_dir, "update.bat")
            current_exe_name = os.path.basename(current_exe_path)
            new_exe_name = current_exe_name + ".new"
            
            # Tạo nội dung batch file
            batch_content = f'''@echo off
title ITM Translate Auto Update

REM Change to application directory
cd /d "{app_dir}"

REM Wait for main application to close completely
timeout /t 3 /nobreak >nul 2>&1

REM Verify files exist
if not exist "{new_exe_name}" (
    exit /b 1
)

REM Perform update steps
REM Step 1: Remove old executable and backup files
if exist "{current_exe_name}" (
    del /f /q "{current_exe_name}" >nul 2>&1
    if exist "{current_exe_name}" (
        exit /b 1
    )
)

REM Also remove old backup file if exists
if exist "{current_exe_name}.backup" (
    del /f /q "{current_exe_name}.backup" >nul 2>&1
)

REM Step 2: Rename new file to main executable
ren "{new_exe_name}" "{current_exe_name}" >nul 2>&1
if not exist "{current_exe_name}" (
    exit /b 1
)

REM Step 3: Launch new application
start "" "{current_exe_name}"

REM Small delay to let application start
timeout /t 2 /nobreak >nul 2>&1

REM Step 4: Self-cleanup
del /f /q "%~f0" >nul 2>&1

exit /b 0
'''
            
            # Ghi file batch
            with open(batch_file_path, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            print(f"✅ Update batch file created: {batch_file_path}")
            return batch_file_path
            
        except Exception as e:
            print(f"❌ Failed to create update batch file: {e}")
            raise e
    
    def restart_application(self):
        """Chạy update.bat với quyền admin và thoát ứng dụng"""
        try:
            current_exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            app_dir = os.path.dirname(current_exe_path)
            batch_file_path = os.path.join(app_dir, "update.bat")
            
            print(f"🔄 Starting batch update process...")
            print(f"📁 App directory: {app_dir}")
            print(f"📄 Batch file: {batch_file_path}")
            
            # Verify batch file exists
            if not os.path.exists(batch_file_path):
                raise Exception(f"Update batch file not found: {batch_file_path}")
            
            print(f"✅ Batch file verified")
            
            if getattr(sys, 'frozen', False):  # Executable mode
                print("🚀 Running update.bat with administrator privileges...")
                
                try:
                    # Method 1: Run batch file with admin privileges using ShellExecute
                    import ctypes
                    
                    # ShellExecute với "runas" để yêu cầu quyền admin
                    result = ctypes.windll.shell32.ShellExecuteW(
                        None,           # hwnd
                        "runas",        # lpVerb (run as administrator)
                        batch_file_path, # lpFile
                        None,           # lpParameters
                        app_dir,        # lpDirectory
                        0               # nShowCmd (SW_HIDE - chạy ẩn)
                    )
                    
                    if result > 32:  # Success
                        print(f"✅ Batch file launched with admin privileges (result: {result})")
                        print("👋 Exiting current application...")
                        
                        # Small delay to ensure batch file starts
                        import time
                        time.sleep(1)
                        
                        # Force exit current process
                        sys.exit(0)
                    else:
                        raise Exception(f"ShellExecute failed with result: {result}")
                        
                except Exception as e:
                    print(f"❌ Admin launch failed: {e}")
                    
                    # Fallback: Try without admin privileges
                    print("🔄 Trying fallback method without admin...")
                    try:
                        subprocess.Popen(
                            [batch_file_path],
                            cwd=app_dir,
                            shell=True,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                        )
                        print("✅ Batch file launched without admin privileges")
                        print("👋 Exiting current application...")
                        
                        import time
                        time.sleep(1)
                        sys.exit(0)
                        
                    except Exception as e2:
                        print(f"❌ Fallback also failed: {e2}")
                        raise e2
                        
            else:
                # Development mode
                print("🛠️ Development mode - running batch file normally...")
                subprocess.Popen([batch_file_path], cwd=app_dir, shell=True,
                               creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
                print("👋 Exiting current application...")
                sys.exit(0)
            
        except Exception as e:
            print(f"💥 Critical error in restart_application: {e}")
            import traceback
            traceback.print_exc()
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
        result = messagebox.askyesno("Cập nhật thành công", 
                                   "Cập nhật đã hoàn tất!\n\n" +
                                   "Khởi động lại ngay để áp dụng phiên bản mới?\n\n" +
                                   "• YES: Khởi động lại ứng dụng ngay\n" +
                                   "• NO: Tiếp tục sử dụng, khởi động lại sau\n\n" +
                                   "Lưu ý: Luôn sử dụng phiên bản mới nhất để đảm bảo có trải nghiệm tốt.\n",
                                   parent=self.dialog)
        if result:  # YES - Restart now
            try:
                self.updater.restart_application()
            except Exception as e:
                error_detail = str(e)
                messagebox.showerror("Lỗi khởi động lại", 
                                   f"Không thể khởi động lại tự động:\n{error_detail}\n\n" +
                                   "Vui lòng thoát ứng dụng và chạy lại thủ công.\n" +
                                   "File cập nhật đã sẵn sàng.",
                                   parent=self.dialog)
        else:  # NO - Close dialog and continue with current version
            self.dialog.destroy()
    
    def _show_manual_restart_instructions(self):
        """Hiển thị hướng dẫn khởi động thủ công chi tiết"""
        instructions = """✅ CẬP NHẬT HOÀN TẤT - Hướng dẫn khởi động thủ công

🔧 CÁCH 1: Sử dụng update.bat (Đơn giản nhất)
• Thoát ITM Translate hoàn toàn (Alt+F4)
• Vào thư mục chứa ITM_Translate.exe
• Click phải vào file "update.bat" → "Run as administrator"
• Đợi script hoàn thành và khởi động lại ứng dụng

� CÁCH 2: Thủ công (Nếu update.bat không hoạt động)
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