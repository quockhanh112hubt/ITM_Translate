import json
import os
from typing import List, Optional

class APIKeyManager:
    def __init__(self, keys_file="api_keys.json"):
        self.keys_file = keys_file
        self.keys = []
        self.active_index = 0
        self.load_keys()
    
    def load_keys(self):
        """Đọc danh sách API keys từ file"""
        try:
            if os.path.exists(self.keys_file):
                with open(self.keys_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.keys = data.get('keys', [])
                    self.active_index = data.get('active_index', 0)
                    
                    # Validate active_index
                    if self.active_index >= len(self.keys):
                        self.active_index = 0
            else:
                # Migration: check for old single key in .env file
                old_key = self._load_old_single_key()
                if old_key:
                    self.keys = [old_key]
                    self.active_index = 0
                    self.save_keys()
        except Exception as e:
            print(f"Error loading API keys: {e}")
            self.keys = []
            self.active_index = 0
    
    def _load_old_single_key(self) -> Optional[str]:
        """Load old single key from .env file for migration"""
        try:
            # Check environment variable first
            key = os.environ.get("ITM_TRANSLATE_KEY")
            if key:
                return key
                
            # Check .env file
            env_file = ".env"
            if os.path.exists(env_file):
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("ITM_TRANSLATE_KEY="):
                            return line.strip().split("=", 1)[1]
        except Exception:
            pass
        return None
    
    def save_keys(self):
        """Lưu danh sách API keys vào file"""
        try:
            data = {
                'keys': self.keys,
                'active_index': self.active_index
            }
            with open(self.keys_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving API keys: {e}")
    
    def add_key(self, new_key: str) -> bool:
        """Thêm API key mới"""
        if new_key and new_key.strip():
            key = new_key.strip()
            if key not in self.keys:
                self.keys.append(key)
                self.save_keys()
                return True
        return False
    
    def remove_key(self, index: int) -> bool:
        """Xóa API key theo index"""
        if 0 <= index < len(self.keys):
            self.keys.pop(index)
            
            # Adjust active_index if necessary
            if self.active_index >= len(self.keys):
                self.active_index = max(0, len(self.keys) - 1)
            elif self.active_index > index:
                self.active_index -= 1
            
            self.save_keys()
            return True
        return False
    
    def get_active_key(self) -> Optional[str]:
        """Lấy API key đang active"""
        if 0 <= self.active_index < len(self.keys):
            return self.keys[self.active_index]
        return None
    
    def get_all_keys(self) -> List[str]:
        """Lấy tất cả API keys"""
        return self.keys.copy()
    
    def set_active_index(self, index: int) -> bool:
        """Đặt index của key active"""
        if 0 <= index < len(self.keys):
            self.active_index = index
            self.save_keys()
            return True
        return False
    
    def rotate_to_next_key(self) -> Optional[str]:
        """Chuyển sang key tiếp theo (rotation)"""
        if len(self.keys) <= 1:
            return self.get_active_key()
        
        self.active_index = (self.active_index + 1) % len(self.keys)
        self.save_keys()
        return self.get_active_key()
    
    def get_key_count(self) -> int:
        """Lấy số lượng keys"""
        return len(self.keys)
    
    def is_valid_index(self, index: int) -> bool:
        """Kiểm tra index có hợp lệ không"""
        return 0 <= index < len(self.keys)

# Global instance for easy access
api_key_manager = APIKeyManager()
