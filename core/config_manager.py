"""
Config Manager - ITM Translate
Quản lý các cài đặt từ config.json và runtime settings
"""

import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    """Quản lý cài đặt ứng dụng"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self._config = {}
        self._runtime_settings = {}
        self.load_config()
    
    def load_config(self):
        """Load config từ file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                print(f"📁 [CONFIG] Loaded configuration from {self.config_file}")
            else:
                print(f"⚠️ [CONFIG] Config file not found: {self.config_file}, using defaults")
                self._set_default_config()
        except Exception as e:
            print(f"❌ [CONFIG] Error loading config: {e}")
            self._set_default_config()
    
    def save_config(self):
        """Save config to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            print(f"💾 [CONFIG] Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ [CONFIG] Error saving config: {e}")
            return False
    
    def _set_default_config(self):
        """Set default configuration values"""
        self._config = {
            "timeouts": {
                "floating_button_screenshot_timeout": 15,
                "translation_retry_timeout": 10,
                "api_validation_timeout": 30,
                "model_switching_delay": 10
            },
            "app_info": {
                "name": "ITM Translate",
                "author": "KhanhIT ITM Team",
                "company": "ITM Semiconductor Vietnam Company Limited"
            }
        }
    
    def get(self, key: str, default=None) -> Any:
        """Get config value với dot notation (vd: 'timeouts.floating_button_screenshot_timeout')"""
        try:
            keys = key.split('.')
            value = self._config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set config value với dot notation"""
        try:
            keys = key.split('.')
            config = self._config
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the final value
            config[keys[-1]] = value
            return True
        except Exception as e:
            print(f"❌ [CONFIG] Error setting {key}: {e}")
            return False
    
    def get_timeout_config(self) -> Dict[str, int]:
        """Get all timeout configurations"""
        return self.get('timeouts', {
            "floating_button_screenshot_timeout": 15,
            "translation_retry_timeout": 10,
            "api_validation_timeout": 30,
            "model_switching_delay": 10
        })
    
    def set_timeout_config(self, timeout_settings: Dict[str, int]) -> bool:
        """Set timeout configurations"""
        try:
            if 'timeouts' not in self._config:
                self._config['timeouts'] = {}
            
            for key, value in timeout_settings.items():
                if isinstance(value, int) and value > 0:
                    self._config['timeouts'][key] = value
                else:
                    print(f"⚠️ [CONFIG] Invalid timeout value for {key}: {value}")
            
            return self.save_config()
        except Exception as e:
            print(f"❌ [CONFIG] Error setting timeout config: {e}")
            return False
    
    # Convenience methods for specific timeouts
    def get_floating_button_timeout(self) -> int:
        """Get floating button screenshot timeout"""
        return self.get('timeouts.floating_button_screenshot_timeout', 15)
    
    def get_translation_retry_timeout(self) -> int:
        """Get translation retry timeout"""
        return self.get('timeouts.translation_retry_timeout', 10)
    
    def get_api_validation_timeout(self) -> int:
        """Get API validation timeout"""
        return self.get('timeouts.api_validation_timeout', 30)
    
    def get_model_switching_delay(self) -> int:
        """Get model switching delay"""
        return self.get('timeouts.model_switching_delay', 10)
    
    def set_floating_button_timeout(self, seconds: int) -> bool:
        """Set floating button screenshot timeout"""
        return self.set('timeouts.floating_button_screenshot_timeout', seconds) and self.save_config()
    
    def set_translation_retry_timeout(self, seconds: int) -> bool:
        """Set translation retry timeout"""
        return self.set('timeouts.translation_retry_timeout', seconds) and self.save_config()
    
    def set_api_validation_timeout(self, seconds: int) -> bool:
        """Set API validation timeout"""
        return self.set('timeouts.api_validation_timeout', seconds) and self.save_config()
    
    def set_model_switching_delay(self, seconds: int) -> bool:
        """Set model switching delay"""
        return self.set('timeouts.model_switching_delay', seconds) and self.save_config()

# Global instance
config_manager = ConfigManager()
