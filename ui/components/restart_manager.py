"""
Restart Manager Component
Quản lý việc restart ứng dụng ITM Translate
"""
import os
import sys
import time
import ctypes
import subprocess


class RestartManager:
    """Quản lý việc restart ứng dụng"""
    
    def restart_with_batch(self):
        """Tạo restart.bat, chạy với quyền Admin và thoát ứng dụng"""
        try:
            # Bước 1: Tạo restart.bat
            self._create_restart_batch()
            
            # Bước 2: Chạy restart.bat với quyền Admin
            self._run_restart_batch_with_admin()
            
            # Bước 3: Thoát hoàn toàn ứng dụng hiện tại
            self._exit_application()
            
        except Exception as e:
            print(f"❌ Error in restart process: {e}")
            # Fallback: thoát đơn giản
            self._exit_application()
    
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
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
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
                app_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            batch_path = os.path.join(app_dir, "restart.bat")
            
            if not os.path.exists(batch_path):
                raise Exception(f"Restart batch file not found: {batch_path}")
            
            print(f"🚀 Running restart.bat with admin privileges...")
            
            # Chạy với quyền Admin bằng ShellExecute
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
            print("🔄 Exiting current application...")
            
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
        time.sleep(0.5)
        
        # Thoát hoàn toàn
        import tkinter as tk
        # Tìm root window và destroy
        for widget in tk._default_root.winfo_children() if tk._default_root else []:
            if isinstance(widget, tk.Tk):
                widget.destroy()
        os._exit(0)
