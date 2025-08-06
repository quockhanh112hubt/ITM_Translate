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
from core.i18n import get_language_manager, _
import ssl
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class Updater:
    def __init__(self, current_version="1.0.0"):
        self.current_version = current_version
        self.config = self._load_config()
        self.update_server_url = self.config.get("update_server", {}).get("api_url", 
                                                "https://api.github.com/repos/quockhanh112hubt/ITM_Translate/releases/latest")
        self.download_url = None
        self.new_version = None
        self.temp_dir = None
        # Create SSL-aware session
        self.session = self._create_ssl_session()
        # Debug logging for v1.0.8
        print(f"🔄 Updater v1.0.8 initialized - Enhanced update mechanism with SSL handling")
    
    def _create_ssl_session(self):
        """Tạo requests session với SSL handling cho môi trường corporate"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],  # Updated parameter name
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Check config for SSL verification override FIRST
        disable_ssl = self.config.get("update_server", {}).get("disable_ssl_verification", False)
        if disable_ssl:
            session.verify = False
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            print("⚠️ SSL verification disabled by config (temporary for corporate environment)")
            return session
        
        # Try to handle corporate SSL certificates if SSL not disabled
        try:
            # Method 1: Try with system certificates first
            session.verify = True
            print("🔒 Using system default SSL verification")
            
            # Method 2: Check for custom certificate bundle
            custom_cert_paths = [
                # Common corporate certificate locations
                "C:\\Program Files\\Custom Certificates\\ca-bundle.crt",
                os.path.join(os.environ.get('REQUESTS_CA_BUNDLE', ''), 'ca-bundle.crt') if os.environ.get('REQUESTS_CA_BUNDLE') else None,
                os.path.join(os.path.dirname(__file__), '..', 'certificates', 'ca-bundle.crt'),
            ]
            
            for cert_path in custom_cert_paths:
                if cert_path and os.path.exists(cert_path):
                    session.verify = cert_path
                    print(f"🔒 Using custom certificate bundle: {cert_path}")
                    break
            
            # Method 3: Create custom CA bundle with Fortinet certificates
            fortinet_bundle = self._create_fortinet_ca_bundle()
            if fortinet_bundle and os.path.exists(fortinet_bundle):
                session.verify = fortinet_bundle
                print(f"🔒 Using Fortinet CA bundle: {fortinet_bundle}")
            
        except Exception as e:
            print(f"⚠️ SSL setup warning: {e}")
            # Fallback to system default SSL verification
            session.verify = True
            print("🔒 Falling back to system SSL verification")
        
        return session
    
    def _create_fortinet_ca_bundle(self):
        """Tạo CA bundle bao gồm system certs + Fortinet certs"""
        try:
            # Try to get system CA bundle
            system_ca_bundle = None
            
            # Method 1: Try certifi (if available)
            try:
                import certifi
                system_ca_bundle = certifi.where()
                print(f"🔒 Using certifi CA bundle: {system_ca_bundle}")
            except ImportError:
                print("ℹ️ Certifi not available, using fallback methods")
            
            # Method 2: Try requests' built-in CA bundle
            if not system_ca_bundle:
                try:
                    import requests.certs
                    system_ca_bundle = requests.certs.where()
                    print(f"🔒 Using requests CA bundle: {system_ca_bundle}")
                    
                    # Verify bundle exists (critical for EXE builds)
                    if not os.path.exists(system_ca_bundle):
                        print(f"⚠️ Requests bundle not found at: {system_ca_bundle}")
                        system_ca_bundle = None
                        
                except (ImportError, AttributeError):
                    print("ℹ️ Requests CA bundle not available")
            
            # Method 3: System default paths (fallback for EXE builds)
            if not system_ca_bundle:
                common_ca_paths = [
                    "C:\\Program Files\\Common Files\\SSL\\certs\\ca-bundle.crt",
                    "C:\\Windows\\System32\\curl-ca-bundle.crt",
                    "/etc/ssl/certs/ca-certificates.crt",  # Linux
                    "/etc/pki/tls/certs/ca-bundle.crt",   # Red Hat
                ]
                for path in common_ca_paths:
                    if os.path.exists(path):
                        system_ca_bundle = path
                        print(f"🔒 Using system CA bundle: {system_ca_bundle}")
                        break
            
            # Create temp CA bundle file in proper temp directory for EXE builds
            if getattr(sys, 'frozen', False):
                # Running as EXE - use system temp directory
                temp_dir = tempfile.gettempdir()
            else:
                # Running as script - use current directory temp
                temp_dir = tempfile.gettempdir()
                
            temp_ca_bundle = os.path.join(temp_dir, "itm_ca_bundle.pem")
            
            # Copy system CA bundle if available
            if system_ca_bundle and os.path.exists(system_ca_bundle):
                try:
                    shutil.copy2(system_ca_bundle, temp_ca_bundle)
                    print(f"📋 Copied system CA bundle to temp file")
                except Exception as e:
                    print(f"⚠️ Could not copy system CA bundle: {e}")
                    # Create minimal bundle if copy fails
                    with open(temp_ca_bundle, 'w', encoding='utf-8') as f:
                        f.write("# ITM Translate Custom CA Bundle\n")
                    print(f"📋 Created minimal CA bundle")
            else:
                # Create empty bundle file
                with open(temp_ca_bundle, 'w', encoding='utf-8') as f:
                    f.write("# ITM Translate Custom CA Bundle\n")
                print(f"📋 Created empty CA bundle (no system bundle found)")
            
            # Look for Fortinet certificates in common locations
            fortinet_cert_paths = []
            
            # Check Downloads folder
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            if os.path.exists(downloads_folder):
                for root, dirs, files in os.walk(downloads_folder):
                    for file in files:
                        if file.startswith("Fortinet_CA_SSL") and file.endswith(".cer"):
                            fortinet_cert_paths.append(os.path.join(root, file))
            
            # Check common certificate folders (including EXE directory)
            cert_folders = [
                "C:\\certificates",
                "C:\\Program Files\\certificates",
                os.path.join(os.path.dirname(__file__), "..", "certificates"),
            ]
            
            # For EXE builds, also check directory where EXE is located
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                cert_folders.append(os.path.join(exe_dir, "certificates"))
                cert_folders.append(exe_dir)  # Also check EXE directory directly
            
            for folder in cert_folders:
                if os.path.exists(folder):
                    for file in os.listdir(folder):
                        if file.startswith("Fortinet_CA_SSL") and file.endswith(".cer"):
                            cert_path = os.path.join(folder, file)
                            if cert_path not in fortinet_cert_paths:  # Avoid duplicates
                                fortinet_cert_paths.append(cert_path)
            
            # Add Fortinet certificates to bundle
            if fortinet_cert_paths:
                with open(temp_ca_bundle, 'a', encoding='utf-8') as bundle_file:
                    bundle_file.write("\n# Fortinet Corporate Certificates\n")
                    for cert_path in fortinet_cert_paths:
                        try:
                            with open(cert_path, 'r', encoding='utf-8') as cert_file:
                                cert_content = cert_file.read()
                                bundle_file.write(f"\n# {os.path.basename(cert_path)}\n")
                                bundle_file.write(cert_content)
                                bundle_file.write("\n")
                                print(f"📜 Added Fortinet cert: {os.path.basename(cert_path)}")
                        except Exception as e:
                            print(f"⚠️ Could not read cert {cert_path}: {e}")
                
                return temp_ca_bundle
            else:
                # No Fortinet certs found, but still return the bundle if we have system certs
                if system_ca_bundle and os.path.exists(system_ca_bundle):
                    return temp_ca_bundle
            
        except Exception as e:
            print(f"⚠️ Could not create Fortinet CA bundle: {e}")
            # Add debug info for EXE builds
            if getattr(sys, 'frozen', False):
                print(f"🔧 Running as EXE from: {sys.executable}")
                print(f"🔧 Temp directory: {tempfile.gettempdir()}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def setup_fortinet_certificates(self):
        """Setup Fortinet certificates for corporate environments"""
        try:
            # Create certificates directory if not exists
            cert_dir = os.path.join(os.path.dirname(__file__), "..", "certificates")
            os.makedirs(cert_dir, exist_ok=True)
            
            # Look for Fortinet certificates in Downloads
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            fortinet_certs_found = []
            
            if os.path.exists(downloads_folder):
                for root, dirs, files in os.walk(downloads_folder):
                    for file in files:
                        if file.startswith("Fortinet_CA_SSL") and file.endswith(".cer"):
                            source_path = os.path.join(root, file)
                            dest_path = os.path.join(cert_dir, file)
                            
                            try:
                                shutil.copy2(source_path, dest_path)
                                fortinet_certs_found.append(file)
                                print(f"📜 Copied Fortinet cert: {file}")
                            except Exception as e:
                                print(f"⚠️ Could not copy {file}: {e}")
            
            if fortinet_certs_found:
                print(f"✅ Setup {len(fortinet_certs_found)} Fortinet certificates")
                return True
            else:
                print("ℹ️ No Fortinet certificates found in Downloads folder")
                return False
                
        except Exception as e:
            print(f"⚠️ Error setting up Fortinet certificates: {e}")
            return False
    
    def cleanup_temp_files(self):
        """Clean up temporary files including CA bundles"""
        try:
            # Clean up temp CA bundle
            temp_ca_bundle = os.path.join(tempfile.gettempdir(), "itm_ca_bundle.pem")
            if os.path.exists(temp_ca_bundle):
                os.remove(temp_ca_bundle)
                print("🗑️ Cleaned up temporary CA bundle")
            
            # Clean up temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                print("🗑️ Cleaned up temp download directory")
                
        except Exception as e:
            print(f"⚠️ Error cleaning up temp files: {e}")
    
    def cleanup_ca_bundle_on_exit(self):
        """Cleanup CA bundle when app exits - call this explicitly"""
        try:
            temp_ca_bundle = os.path.join(tempfile.gettempdir(), "itm_ca_bundle.pem")
            if os.path.exists(temp_ca_bundle):
                os.remove(temp_ca_bundle)
                print("🗑️ Cleaned up CA bundle on app exit")
        except Exception as e:
            print(f"⚠️ Error cleaning up CA bundle: {e}")
    
    def show_certificate_help_dialog(self, parent=None):
        """Show help dialog for SSL certificate issues"""
        try:
            help_window = tk.Toplevel(parent)
            help_window.title("🔒 Hướng dẫn khắc phục lỗi SSL Certificate")
            help_window.geometry("650x600")
            help_window.resizable(False, False)
            
            if parent:
                help_window.transient(parent)
                help_window.grab_set()
            
            # Center window
            help_window.update_idletasks()
            x = (help_window.winfo_screenwidth() // 2) - (325)
            y = (help_window.winfo_screenheight() // 2) - (300)
            help_window.geometry(f"650x600+{x}+{y}")
            
            # Main frame
            main_frame = ttk.Frame(help_window, padding=20)
            main_frame.pack(fill='both', expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, 
                                  text="🔒 Lỗi SSL Certificate - Môi trường Corporate", 
                                  font=('Segoe UI', 14, 'bold'))
            title_label.pack(anchor='w', pady=(0, 15))
            
            # Help text
            help_text = """🚨 Lỗi này xảy ra khi máy tính có Fortinet firewall/proxy với custom SSL certificates.

📋 TÌNH TRẠNG HIỆN TẠI:
✅ Đã tìm thấy Fortinet certificates trong Downloads
❌ Certificates thiếu Authority Key Identifier (vấn đề phổ biến)

🔧 GIẢI PHÁP KHUYẾN NGHỊ (theo thứ tự ưu tiên):

🥇 CÁCH 1: Yêu cầu IT cung cấp COMPLETE certificate chain:
   • Root CA certificate
   • Intermediate CA certificates  
   • All certificates với proper Authority Key Identifier
   • Format: PEM (.pem) thay vì DER (.cer)

🥈 CÁCH 2: Request IT whitelist GitHub domains:
   • github.com
   • api.github.com
   • *.githubusercontent.com
   • objects.githubusercontent.com

🥉 CÁCH 3: TEMPORARY SSL bypass (chỉ để update):
   • Click nút "🔧 Enable Temporary SSL Bypass" bên dưới
   • Chỉ sử dụng trong mạng corporate an toàn
   • Tự động tắt sau khi update xong

🏆 CÁCH 4: Manual update:
   • Mở browser → github.com/quockhanh112hubt/ITM_Translate/releases
   • Download file .exe mới nhất
   • Thay thế file cũ

💡 LƯU Ý: SSL bypass chỉ nên dùng tạm thời trong môi trường corporate được IT quản lý."""
            
            # Text widget with scrollbar
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill='both', expand=True, pady=(0, 15))
            
            text_widget = tk.Text(text_frame, wrap='word', font=('Segoe UI', 10),
                                bg='#f8f9fa', fg='#2c3e50', height=18)
            scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.insert('1.0', help_text)
            text_widget.config(state='disabled')
            
            text_widget.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill='x')
            
            def setup_certs():
                """Auto setup certificates if found"""
                if self.setup_fortinet_certificates():
                    messagebox.showinfo("✅ Thành công", 
                                      "Đã tìm thấy và setup Fortinet certificates!\nHãy thử lại update.")
                else:
                    messagebox.showwarning("⚠️ Không tìm thấy", 
                                         "Không tìm thấy chứng chỉ Fortinet trong Downloads.\nHãy copy các file .cer vào Downloads và thử lại.")
            
            def enable_ssl_bypass():
                """Enable temporary SSL bypass for update"""
                result = messagebox.askquestion("⚠️ Xác nhận SSL Bypass", 
                    "Bạn có muốn TEMPORARILY disable SSL verification để update?\n\n" +
                    "🔴 CHỈ sử dụng trong mạng corporate an toàn!\n" +
                    "🔴 Sẽ tự động tắt sau khi update xong!\n\n" +
                    "Tiếp tục?", icon='warning')
                
                if result == 'yes':
                    try:
                        # Temporarily enable SSL bypass in config
                        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
                        if os.path.exists(config_file):
                            with open(config_file, 'r', encoding='utf-8') as f:
                                config = json.load(f)
                            
                            config.setdefault("update_server", {})["disable_ssl_verification"] = True
                            
                            with open(config_file, 'w', encoding='utf-8') as f:
                                json.dump(config, f, ensure_ascii=False, indent=4)
                            
                            messagebox.showinfo("✅ SSL Bypass Enabled", 
                                              "SSL verification đã tạm thời tắt!\n\n" +
                                              "Hãy thử update ngay bây giờ.\n" +
                                              "SSL verification sẽ được bật lại tự động sau khi update.")
                            help_window.destroy()
                        else:
                            messagebox.showerror("❌ Lỗi", "Không tìm thấy file config.json")
                    except Exception as e:
                        messagebox.showerror("❌ Lỗi", f"Không thể enable SSL bypass: {e}")
            
            def open_manual_download():
                """Open GitHub releases page for manual download"""
                import webbrowser
                webbrowser.open("https://github.com/quockhanh112hubt/ITM_Translate/releases")
                messagebox.showinfo("🌐 Manual Download", 
                                  "Đã mở trang GitHub releases trong browser.\n" +
                                  "Download file .exe mới nhất và thay thế file cũ.")
            
            # Button row 1
            button_frame1 = ttk.Frame(button_frame)
            button_frame1.pack(fill='x', pady=(0, 5))
            
            ttk.Button(button_frame1, text="🔧 Auto Setup Certificates", 
                      command=setup_certs).pack(side='left', padx=(0, 10))
            
            ttk.Button(button_frame1, text="⚠️ Enable Temporary SSL Bypass", 
                      command=enable_ssl_bypass).pack(side='left', padx=(0, 10))
            
            # Button row 2  
            button_frame2 = ttk.Frame(button_frame)
            button_frame2.pack(fill='x')
            
            ttk.Button(button_frame2, text="🌐 Manual Download", 
                      command=open_manual_download).pack(side='left', padx=(0, 10))
            
            ttk.Button(button_frame2, text="❌ Đóng", 
                      command=help_window.destroy).pack(side='left')
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị hướng dẫn: {e}")
    
    def __del__(self):
        """Cleanup when updater is destroyed"""
        try:
            # Only cleanup temp download directory, NOT the CA bundle during active use
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
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
        """Kiểm tra version mới từ server với SSL handling"""
        try:
            print(f"🔍 Checking for updates at: {self.update_server_url}")  # Debug log
            
            # Chuẩn bị headers cho GitHub API
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'ITM-Translate-Updater'
            }
            
            # Thêm GitHub token nếu có (cho private repos)
            github_token = self.config.get("update_server", {}).get("github_token")
            if github_token:
                headers['Authorization'] = f'token {github_token}'
                print("🔑 Using GitHub token for private repository")
            
            # Use SSL-aware session instead of requests.get
            response = self.session.get(self.update_server_url, headers=headers, timeout=15)
            
            print(f"📡 Response status: {response.status_code}")  # Debug log
            
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
                    return False, self.current_version, _("already_latest_version")
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
        
        except requests.exceptions.SSLError as e:
            # Specific handling for SSL errors
            error_msg = str(e)
            if "CERTIFICATE_VERIFY_FAILED" in error_msg:
                return False, None, (
                    f"🔒 Lỗi chứng chỉ SSL - Môi trường corporate firewall detected!\n\n"
                    f"Giải pháp:\n"
                    f"1. Tải các chứng chỉ Fortinet từ IT department\n"
                    f"2. Đặt các file .cer vào thư mục Downloads\n"
                    f"3. Thử lại update\n\n"
                    f"Hoặc liên hệ IT để config proxy/firewall cho phép GitHub access.\n\n"
                    f"Chi tiết lỗi: {error_msg}"
                )
            else:
                return False, None, f"🔒 Lỗi SSL: {error_msg}"
        
        except requests.RequestException as e:
            # Fallback: kiểm tra bằng cách khác hoặc thông báo offline
            error_msg = str(e)
            if "github.com" in error_msg:
                return False, None, f"Không thể kết nối đến GitHub.\nKiểm tra kết nối internet hoặc GitHub có bị chặn.\nLỗi: {error_msg}"
            return False, None, f"Lỗi kết nối: {error_msg}"
        except Exception as e:
            return False, None, f"{_('update_check_error')} {str(e)}"
    
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
        """Download file cập nhật với SSL handling"""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="itm_update_")
            file_name = os.path.basename(self.download_url)
            temp_file_path = os.path.join(self.temp_dir, file_name)
            
            print(f"📥 Downloading update: {self.download_url}")
            
            # Use SSL-aware session for download
            response = self.session.get(self.download_url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            last_progress = 0
            
            print(f"📦 File size: {total_size / (1024*1024):.1f} MB")
            
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
            
            print(f"✅ Download completed: {temp_file_path}")
            return temp_file_path
            
        except requests.exceptions.SSLError as e:
            # Cleanup temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            raise Exception(f"🔒 SSL Error during download: Môi trường corporate firewall detected. Liên hệ IT để config proxy/certificate. Chi tiết: {str(e)}")
            
        except Exception as e:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            raise e
    
    def apply_update(self, downloaded_file_path):
        """Áp dụng cập nhật một cách an toàn với SSL restore logic"""
        try:
            # Auto-restore SSL verification if it was temporarily disabled
            self._restore_ssl_verification_if_temp_disabled()
            
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
            print("🔒 SSL verification restored to secure defaults")
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
    
    def _restore_ssl_verification_if_temp_disabled(self):
        """Restore SSL verification if it was temporarily disabled for update"""
        try:
            config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Check if SSL was temporarily disabled
                if config.get("update_server", {}).get("disable_ssl_verification", False):
                    print("🔒 Restoring SSL verification after successful update...")
                    
                    # Re-enable SSL verification
                    config.setdefault("update_server", {})["disable_ssl_verification"] = False
                    
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    
                    print("✅ SSL verification restored to secure defaults")
                    
        except Exception as e:
            print(f"⚠️ Could not restore SSL verification setting: {e}")
    
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
        self.dialog.title(_("update_check_title"))
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
            title_label = tk.Label(main_frame, text=_("update_available_title"), 
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
                                   _("update_note"),
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
    """Kiểm tra cập nhật async với SSL error handling"""
    def check_updates():
        updater = Updater()
        updater.current_version = updater.get_current_version()
        
        try:
            has_update, version, message = updater.check_for_updates()
            
            # Show dialog in main thread
            if has_update or show_no_update:
                parent_window.after(0, lambda: UpdateDialog(parent_window, updater, has_update, version, message))
                
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's an SSL certificate error
            if "CERTIFICATE_VERIFY_FAILED" in error_msg or "SSL" in error_msg:
                def show_ssl_help():
                    # Show certificate help dialog
                    updater.show_certificate_help_dialog(parent_window)
                
                parent_window.after(0, show_ssl_help)
            else:
                # Show generic error
                parent_window.after(0, lambda: messagebox.showerror(
                    "Lỗi cập nhật", 
                    f"Không thể kiểm tra cập nhật:\n{error_msg}"
                ))
    
    threading.Thread(target=check_updates, daemon=True).start()