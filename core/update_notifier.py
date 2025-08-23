"""
Update Notifier Service - ITM Translate
Dịch vụ kiểm tra cập nhật tự động và thông báo cho UI
"""

import threading
import time
import json
from datetime import datetime, timedelta
from core.updater import Updater
from core.i18n import get_language_manager, _

class UpdateNotifier:
    """Dịch vụ kiểm tra và thông báo cập nhật tự động"""
    
    def __init__(self, check_interval_hours=6):
        """
        Khởi tạo UpdateNotifier
        
        Args:
            check_interval_hours: Thời gian giữa các lần check (giờ)
        """
        self.check_interval = check_interval_hours * 3600  # Convert to seconds
        self.current_version = self._get_current_version()
        self.updater = Updater(self.current_version)
        
        # Update status
        self.has_update = False
        self.new_version = None
        self.last_check_time = None
        
        # Callbacks cho UI update
        self.update_callbacks = []
        
        # Background thread
        self.check_thread = None
        self.stop_flag = threading.Event()
        
        print(f"🔔 UpdateNotifier initialized - Current version: {self.current_version}")
    
    def _get_current_version(self):
        """Lấy version hiện tại từ version.json"""
        try:
            # Debug: Check working directory and file paths
            import os
            current_dir = os.getcwd()
            version_file = "version.json"
            version_file_abs = os.path.abspath(version_file)
            
            print(f"🔍 [VERSION] Working dir: {current_dir}")
            print(f"🔍 [VERSION] Version file: {version_file_abs}")
            print(f"🔍 [VERSION] File exists: {os.path.exists(version_file)}")
            
            with open(version_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                version = data.get("version", "1.0.0")
                print(f"🔍 [VERSION] Read version: {version}")
                return version
        except Exception as e:
            print(f"❌ [VERSION] Error reading version: {e}")
            return "1.0.0"
    
    def register_callback(self, callback):
        """
        Đăng ký callback để nhận thông báo khi có update
        
        Args:
            callback: Function(has_update, new_version) được gọi khi status thay đổi
        """
        if callback not in self.update_callbacks:
            self.update_callbacks.append(callback)
    
    def unregister_callback(self, callback):
        """Hủy đăng ký callback"""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
    
    def _notify_callbacks(self):
        """Thông báo cho tất cả callbacks về update status"""
        for callback in self.update_callbacks:
            try:
                callback(self.has_update, self.new_version)
            except Exception as e:
                print(f"❌ Error in update callback: {e}")
    
    def start_background_check(self):
        """Bắt đầu kiểm tra update trong background"""
        if self.check_thread and self.check_thread.is_alive():
            return
        
        self.stop_flag.clear()
        self.check_thread = threading.Thread(target=self._background_check_loop, daemon=True)
        self.check_thread.start()
        print("🚀 Background update checker started")
        
        # Force refresh UI ngay lập tức để đảm bảo UI sync với trạng thái thực tế
        self._notify_callbacks()
    
    def stop_background_check(self):
        """Dừng background check"""
        self.stop_flag.set()
        if self.check_thread and self.check_thread.is_alive():
            self.check_thread.join(timeout=5)
        print("⏹️ Background update checker stopped")
    
    def _background_check_loop(self):
        """Loop chính cho background checking"""
        # Check ngay lập tức khi start
        self.check_for_updates_silent()
        
        while not self.stop_flag.is_set():
            # Wait với check mỗi 30 giây để có thể stop nhanh
            for _ in range(int(self.check_interval / 30)):
                if self.stop_flag.wait(30):
                    return
            
            # Check for updates
            if not self.stop_flag.is_set():
                self.check_for_updates_silent()
    
    def check_for_updates_silent(self):
        """Kiểm tra update silent (không hiển thị dialog)"""
        try:
            print(f"🔍 Checking for updates (silent) - Current: {self.current_version}")
            
            has_update, new_version, message = self.updater.check_for_updates()
            
            # Debug version comparison
            print(f"🔍 [DEBUG] Current version: '{self.current_version}'")
            print(f"🔍 [DEBUG] Latest version: '{new_version}'")
            print(f"🔍 [DEBUG] Has update: {has_update}")
            
            # Update internal state
            old_has_update = self.has_update
            self.has_update = has_update
            self.new_version = new_version if has_update else None
            self.last_check_time = datetime.now()
            
            # Notify callbacks if status changed OR on first check (để force refresh UI)
            if old_has_update != has_update or not hasattr(self, '_first_check_done'):
                print(f"📢 Update status changed: {has_update} (Version: {new_version})")
                self._notify_callbacks()
                self._first_check_done = True
            
            return has_update, new_version, message
            
        except Exception as e:
            print(f"❌ Error checking for updates: {e}")
            return False, None, str(e)
    
    def force_check_now(self):
        """Ép buộc check update ngay lập tức"""
        # Reload current version từ file
        self.current_version = self._get_current_version()
        self.updater.current_version = self.current_version
        
        return self.check_for_updates_silent()
    
    def get_update_status(self):
        """
        Lấy trạng thái update hiện tại
        
        Returns:
            tuple: (has_update, new_version, last_check_time)
        """
        return self.has_update, self.new_version, self.last_check_time
    
    def get_update_indicator_text(self, base_text):
        """
        Lấy text hiển thị với indicator update nếu có
        
        Args:
            base_text: Text gốc (ví dụ: "Nâng cao", "Kiểm tra cập nhật")
        
        Returns:
            str: Text với indicator nếu có update ("Nâng cao (1)", "Kiểm tra cập nhật (1)")
        """
        if self.has_update:
            return f"{base_text} (1)"
        return base_text
    
    def reset_update_status(self):
        """Reset update status (gọi sau khi user đã update)"""
        old_has_update = self.has_update
        self.has_update = False
        self.new_version = None
        
        # Notify callbacks if status changed
        if old_has_update:
            print("🔄 Update status reset")
            self._notify_callbacks()

# Global instance để sử dụng trong toàn bộ app
_update_notifier_instance = None

def get_update_notifier():
    """Lấy global instance của UpdateNotifier"""
    global _update_notifier_instance
    if _update_notifier_instance is None:
        _update_notifier_instance = UpdateNotifier(check_interval_hours=6)
    return _update_notifier_instance

def start_update_monitoring():
    """Bắt đầu monitoring update (gọi từ main app)"""
    notifier = get_update_notifier()
    notifier.start_background_check()
    return notifier

def stop_update_monitoring():
    """Dừng monitoring update (gọi khi app đóng)"""
    global _update_notifier_instance
    if _update_notifier_instance:
        _update_notifier_instance.stop_background_check()
