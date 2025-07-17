import json
import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class AIProvider(Enum):
    GEMINI = "gemini"
    CHATGPT = "chatgpt"
    DEEPSEEK = "deepseek"
    CLAUDE = "claude"
    COPILOT = "copilot"

@dataclass
class APIKeyInfo:
    """Thông tin chi tiết về một API key"""
    key: str
    provider: AIProvider
    model: str = "auto"  # "auto" means use default model for provider
    name: str = ""  # User-friendly name
    is_active: bool = True
    failed_count: int = 0
    last_error: str = ""

class APIKeyManager:
    def __init__(self, keys_file="api_keys.json"):
        self.keys_file = keys_file
        self.keys: List[APIKeyInfo] = []
        self.active_index = 0
        self.provider_priority = [AIProvider.GEMINI, AIProvider.CHATGPT, AIProvider.COPILOT, AIProvider.DEEPSEEK, AIProvider.CLAUDE]
        self.load_keys()
    
    def load_keys(self):
        """Đọc danh sách API keys từ file"""
        try:
            if os.path.exists(self.keys_file):
                with open(self.keys_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Load new format (with provider info)
                    if isinstance(data.get('keys'), list) and data['keys'] and isinstance(data['keys'][0], dict):
                        self.keys = []
                        for key_data in data['keys']:
                            try:
                                provider = AIProvider(key_data.get('provider', 'gemini'))
                                key_info = APIKeyInfo(
                                    key=key_data['key'],
                                    provider=provider,
                                    model=key_data.get('model', 'auto'),
                                    name=key_data.get('name', ''),
                                    is_active=key_data.get('is_active', True),
                                    failed_count=key_data.get('failed_count', 0),
                                    last_error=key_data.get('last_error', '')
                                )
                                self.keys.append(key_info)
                            except (ValueError, KeyError) as e:
                                print(f"Invalid key data: {key_data}, error: {e}")
                                
                    # Load old format (plain string keys) - auto-migrate to Gemini
                    else:
                        old_keys = data.get('keys', [])
                        self.keys = []
                        for key_str in old_keys:
                            key_info = APIKeyInfo(
                                key=key_str,
                                provider=AIProvider.GEMINI,
                                model='auto',
                                name=f"Gemini Key {len(self.keys) + 1}"
                            )
                            self.keys.append(key_info)
                    
                    self.active_index = data.get('active_index', 0)
                    loaded_priority = data.get('provider_priority', [p.value for p in self.provider_priority])
                    self.provider_priority = [AIProvider(p) for p in loaded_priority]
                    
                    # Ensure all providers are in priority list (for backward compatibility)
                    all_providers = set(AIProvider)
                    current_priority_set = set(self.provider_priority)
                    missing_providers = all_providers - current_priority_set
                    
                    # Add missing providers to priority list
                    if missing_providers:
                        self.provider_priority.extend(list(missing_providers))
                        # Save updated priority
                        self.save_keys()
                    
                    # Validate active_index
                    if self.active_index >= len(self.keys):
                        self.active_index = 0
                        
                    # Save migrated data
                    if not isinstance(data.get('keys'), list) or not data['keys'] or not isinstance(data['keys'][0], dict):
                        self.save_keys()
            else:
                # Migration: check for old single key in .env file
                old_key = self._load_old_single_key()
                if old_key:
                    key_info = APIKeyInfo(
                        key=old_key,
                        provider=AIProvider.GEMINI,
                        model='auto',
                        name="Migrated Gemini Key"
                    )
                    self.keys = [key_info]
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
            # Convert APIKeyInfo objects to dict
            keys_data = []
            for key_info in self.keys:
                keys_data.append({
                    'key': key_info.key,
                    'provider': key_info.provider.value,
                    'model': key_info.model,
                    'name': key_info.name,
                    'is_active': key_info.is_active,
                    'failed_count': key_info.failed_count,
                    'last_error': key_info.last_error
                })
                
            data = {
                'keys': keys_data,
                'active_index': self.active_index,
                'provider_priority': [p.value for p in self.provider_priority]
            }
            with open(self.keys_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving API keys: {e}")
    
    def add_key(self, new_key: str, provider: AIProvider, model: str = "auto", name: str = "") -> bool:
        """Thêm API key mới"""
        if new_key and new_key.strip():
            key = new_key.strip()
            # Check if key already exists
            if any(k.key == key and k.provider == provider for k in self.keys):
                return False
                
            if not name:
                provider_count = sum(1 for k in self.keys if k.provider == provider)
                name = f"{provider.value.title()} Key {provider_count + 1}"
                
            key_info = APIKeyInfo(
                key=key,
                provider=provider,
                model=model,
                name=name
            )
            self.keys.append(key_info)
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
    
    def get_active_key(self) -> Optional[APIKeyInfo]:
        """Lấy API key đang active"""
        if 0 <= self.active_index < len(self.keys):
            return self.keys[self.active_index]
        return None
    
    def get_active_key_string(self) -> Optional[str]:
        """Lấy API key string đang active (for backward compatibility)"""
        active_key = self.get_active_key()
        return active_key.key if active_key else None
    
    def get_all_keys(self) -> List[APIKeyInfo]:
        """Lấy tất cả API keys"""
        return self.keys.copy()
    
    def get_keys_by_provider(self, provider: AIProvider) -> List[APIKeyInfo]:
        """Lấy tất cả keys theo provider"""
        return [k for k in self.keys if k.provider == provider and k.is_active]
    
    def set_active_index(self, index: int) -> bool:
        """Đặt index của key active"""
        if 0 <= index < len(self.keys):
            self.active_index = index
            self.save_keys()
            return True
        return False
    
    def rotate_to_next_key(self) -> Optional[APIKeyInfo]:
        """Chuyển sang key tiếp theo (rotation)"""
        if len(self.keys) <= 1:
            return self.get_active_key()
        
        self.active_index = (self.active_index + 1) % len(self.keys)
        self.save_keys()
        return self.get_active_key()
    
    def find_next_working_key(self, exclude_current=True) -> Optional[APIKeyInfo]:
        """Tìm key tiếp theo có thể hoạt động (theo priority và provider)"""
        if not self.keys:
            return None
            
        current_key = self.get_active_key()
        
        # Try same provider first (if not excluding current)
        if current_key and not exclude_current:
            same_provider_keys = [k for k in self.keys if k.provider == current_key.provider and k.is_active and k.failed_count < 3]
            if same_provider_keys:
                return same_provider_keys[0]
        
        # Try other providers by priority
        for provider in self.provider_priority:
            provider_keys = [k for k in self.keys if k.provider == provider and k.is_active and k.failed_count < 3]
            if provider_keys:
                # Find index and set as active
                for i, key in enumerate(self.keys):
                    if key == provider_keys[0]:
                        self.active_index = i
                        self.save_keys()
                        return key
        
        return None
    
    def mark_key_failed(self, key_info: APIKeyInfo, error_msg: str = ""):
        """Đánh dấu key bị lỗi"""
        for key in self.keys:
            if key.key == key_info.key and key.provider == key_info.provider:
                key.failed_count += 1
                key.last_error = error_msg
                if key.failed_count >= 3:
                    key.is_active = False
                self.save_keys()
                break
    
    def reset_key_failures(self, key_info: APIKeyInfo):
        """Reset lỗi cho key (khi hoạt động lại)"""
        for key in self.keys:
            if key.key == key_info.key and key.provider == key_info.provider:
                key.failed_count = 0
                key.last_error = ""
                key.is_active = True
                self.save_keys()
                break
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Lấy thông tin về provider hiện tại"""
        active_key = self.get_active_key()
        if not active_key:
            return {"provider": "none", "model": "none", "name": "No API Key"}
        
        return {
            "provider": active_key.provider.value,
            "model": active_key.model,
            "name": active_key.name,
            "key_preview": f"...{active_key.key[-8:]}" if len(active_key.key) > 8 else active_key.key
        }
    
    def set_provider_priority(self, priorities: List[AIProvider]):
        """Đặt thứ tự ưu tiên provider"""
        self.provider_priority = priorities
        self.save_keys()
    
    def get_available_providers(self) -> List[AIProvider]:
        """Lấy danh sách providers có sẵn"""
        return list(set(k.provider for k in self.keys if k.is_active))
    
    def get_key_count(self) -> int:
        """Lấy số lượng keys"""
        return len(self.keys)
    
    def is_valid_index(self, index: int) -> bool:
        """Kiểm tra index có hợp lệ không"""
        return 0 <= index < len(self.keys)

# Global instance for easy access
api_key_manager = APIKeyManager()
