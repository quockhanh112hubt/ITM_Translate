"""
Hệ thống đa ngôn ngữ (i18n) cho ITM Translate
"""
import json
import os

# File lưu trữ ngôn ngữ đã chọn
LANGUAGE_CONFIG_FILE = "language.json"

# Dictionary chứa tất cả text cần dịch
TRANSLATIONS = {
    "vi": {
        # Window title
        "app_title": "ITM Translate v1.2.3",
        
        # Tab names
        "tab_settings": "Cài đặt",
        "tab_api_keys": "Quản lý API KEY",
        "tab_advanced": "Nâng Cao",
        
        # Settings tab
        "settings_title": "Cài đặt phím tắt & ngôn ngữ",
        "auto_choose_hint": "Tùy chọn mặc định. Ngôn ngữ đầu tiên sẽ được dịch tới ngôn ngữ thứ 2. Ngôn ngữ thứ 2 sẽ được dịch tới ngôn ngữ thứ 3",
        "shortcuts_group1": "Phím tắt",
        "modifier1": "Modifier 1",
        "modifier2": "Modifier 2",
        "main_key": "Phím chính",
        "popup_translate": "Dịch popup",
        "replace_translate": "Dịch & thay thế",
        "first_language": "Ngôn ngữ đầu tiên:",
        "second_language": "Ngôn ngữ thứ 2:",
        "third_language": "Ngôn ngữ thứ 3:",
        "shortcuts_group2": "Phím tắt nhóm 2:",
        "group2_first_language": "Ngôn ngữ đầu tiên:",
        "group2_second_language": "Ngôn ngữ thứ 2:",
        "group2_third_language": "Ngôn ngữ thứ 3:",
        "auto_save_option": "Hiện tùy chọn tự chỉnh",
        "save_close_settings": "Lưu & Khép Cửa Sổ Cài Đặt",
        "cancel": "Hủy bỏ",
        
        # API Keys tab
        "api_keys_title": "Quản lý API Keys",
        "add_key": "Thêm API Key",
        "edit_key": "Chỉnh sửa",
        "delete_key": "Xóa",
        "set_active": "Đặt làm chính",
        "key_name": "Tên",
        "provider": "Nhà cung cấp",
        "key_preview": "Key Preview",
        "model": "Model",
        "status": "Trạng thái",
        "active": "Đang dùng",
        "inactive": "Không dùng",
        
        # Add/Edit API Key dialog
        "add_api_key": "Thêm API Key mới",
        "edit_api_key": "Chỉnh sửa API Key",
        "key_name_label": "Tên Key:",
        "key_name_placeholder": "Ví dụ: OpenAI chính, Claude backup...",
        "provider_label": "Nhà cung cấp:",
        "api_key_label": "API Key:",
        "api_key_placeholder": "Nhập API key của bạn...",
        "model_label": "Model:",
        "auto_model": "Tự động",
        "test_key": "Kiểm tra",
        "save": "Lưu",
        "cancel": "Hủy",
        
        # Advanced tab
        "advanced_title": "Các tùy chọn nâng cao",
        "startup_group": "Khởi động",
        "startup_with_windows": "Khởi động cùng Windows",
        "show_window_startup": "Hiển thị cửa sổ khi khởi động",
        "features_group": "Tính năng",
        "floating_translate_button": "Nút dịch nổi (xuất hiện khi chọn text)",
        "about_group": "Thông tin",
        "usage_guide": "Hướng dẫn sử dụng",
        "app_info": "Thông tin chương trình",
        "check_updates": "Kiểm tra cập nhật",
        
        # Messages and dialogs
        "restart_required": "Cần khởi động lại",
        "restart_message": "Một số thay đổi cần khởi động lại ứng dụng để có hiệu lực. Bạn có muốn khởi động lại ngay không?",
        "restart_now": "Khởi động lại",
        "restart_later": "Để sau",
        "validation_error": "Lỗi xác thực",
        "key_name_required": "Vui lòng nhập tên cho API key",
        "provider_required": "Vui lòng chọn nhà cung cấp",
        "api_key_required": "Vui lòng nhập API key",
        "delete_confirm": "Xác nhận xóa",
        "delete_key_message": "Bạn có chắc chắn muốn xóa API key này?",
        "yes": "Có",
        "no": "Không",
        "testing_key": "Đang kiểm tra...",
        "test_success": "Kiểm tra thành công!",
        "test_failed": "Kiểm tra thất bại: ",
        "duplicate_name": "Tên API key đã tồn tại",
        "invalid_hotkey": "Phím tắt không hợp lệ",
        "hotkey_exists": "Phím tắt đã được sử dụng",
        
        # Popup and floating button
        "translate_button": "🌐 Dịch",
        "loading": "Đang dịch...",
        "translation_failed": "Dịch thất bại",
        "no_text_selected": "Không có text được chọn",
        "replace_failed": "Không thể thay thế văn bản tự động. Vị trí dán không cho phép.",
        
        # Language names
        "any_language": "Any Language",
        "vietnamese": "Tiếng Việt", 
        "english": "English",
        "japanese": "日本語",
        "korean": "한국어",
        "chinese_simplified": "中文(简体)",
        "chinese_traditional": "中文(繁體)",
        "french": "Français",
        "german": "Deutsch",
        "spanish": "Español",
        "italian": "Italiano",
        "portuguese": "Português",
        "russian": "Русский",
        "arabic": "العربية",
        "thai": "ไทย",
        "indonesian": "Bahasa Indonesia",
    },
    
    "en": {
        # Window title
        "app_title": "ITM Translate v1.2.3",
        
        # Tab names
        "tab_settings": "Settings",
        "tab_api_keys": "API KEY Management",
        "tab_advanced": "Advanced",
        
        # Settings tab
        "settings_title": "Hotkey & Language Settings",
        "auto_choose_hint": "Default option. First language will be translated to second language. Second language will be translated to third language",
        "shortcuts_group1": "Shortcuts",
        "modifier1": "Modifier 1",
        "modifier2": "Modifier 2", 
        "main_key": "Main Key",
        "popup_translate": "Popup translate",
        "replace_translate": "Translate & replace",
        "first_language": "First language:",
        "second_language": "Second language:",
        "third_language": "Third language:",
        "shortcuts_group2": "Group 2 shortcuts:",
        "group2_first_language": "First language:",
        "group2_second_language": "Second language:",
        "group2_third_language": "Third language:",
        "auto_save_option": "Show auto-save option",
        "save_close_settings": "Save & Close Settings",
        "cancel": "Cancel",
        
        # API Keys tab
        "api_keys_title": "API Keys Management",
        "add_key": "Add API Key",
        "edit_key": "Edit",
        "delete_key": "Delete",
        "set_active": "Set Active",
        "key_name": "Name",
        "provider": "Provider",
        "key_preview": "Key Preview",
        "model": "Model",
        "status": "Status",
        "active": "Active",
        "inactive": "Inactive",
        
        # Add/Edit API Key dialog
        "add_api_key": "Add New API Key",
        "edit_api_key": "Edit API Key",
        "key_name_label": "Key Name:",
        "key_name_placeholder": "e.g., OpenAI main, Claude backup...",
        "provider_label": "Provider:",
        "api_key_label": "API Key:",
        "api_key_placeholder": "Enter your API key...",
        "model_label": "Model:",
        "auto_model": "Auto",
        "test_key": "Test",
        "save": "Save",
        "cancel": "Cancel",
        
        # Advanced tab
        "advanced_title": "Advanced Options",
        "startup_group": "Startup",
        "startup_with_windows": "Start with Windows",
        "show_window_startup": "Show window on startup",
        "features_group": "Features",
        "floating_translate_button": "Floating translate button (appears when selecting text)",
        "about_group": "About",
        "usage_guide": "Usage Guide",
        "app_info": "App Information",
        "check_updates": "Check for Updates",
        
        # Messages and dialogs
        "restart_required": "Restart Required",
        "restart_message": "Some changes require restarting the application to take effect. Would you like to restart now?",
        "restart_now": "Restart Now",
        "restart_later": "Later",
        "validation_error": "Validation Error",
        "key_name_required": "Please enter a name for the API key",
        "provider_required": "Please select a provider",
        "api_key_required": "Please enter an API key",
        "delete_confirm": "Confirm Delete",
        "delete_key_message": "Are you sure you want to delete this API key?",
        "yes": "Yes",
        "no": "No",
        "testing_key": "Testing...",
        "test_success": "Test successful!",
        "test_failed": "Test failed: ",
        "duplicate_name": "API key name already exists",
        "invalid_hotkey": "Invalid hotkey",
        "hotkey_exists": "Hotkey already in use",
        
        # Popup and floating button
        "translate_button": "🌐 Translate",
        "loading": "Translating...",
        "translation_failed": "Translation failed",
        "no_text_selected": "No text selected",
        "replace_failed": "Cannot automatically replace text. Paste location does not allow.",
        
        # Language names
        "any_language": "Any Language",
        "vietnamese": "Vietnamese",
        "english": "English",
        "japanese": "Japanese",
        "korean": "Korean", 
        "chinese_simplified": "Chinese (Simplified)",
        "chinese_traditional": "Chinese (Traditional)",
        "french": "French",
        "german": "German",
        "spanish": "Spanish",
        "italian": "Italian",
        "portuguese": "Portuguese",
        "russian": "Russian",
        "arabic": "Arabic",
        "thai": "Thai",
        "indonesian": "Indonesian",
    }
}

class LanguageManager:
    def __init__(self):
        self.current_language = "vi"  # Mặc định tiếng Việt
        self.load_language_preference()
        
    def load_language_preference(self):
        """Load ngôn ngữ đã chọn từ file"""
        if os.path.exists(LANGUAGE_CONFIG_FILE):
            try:
                with open(LANGUAGE_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_language = data.get("language", "vi")
            except Exception:
                self.current_language = "vi"
    
    def save_language_preference(self, language):
        """Lưu ngôn ngữ đã chọn vào file"""
        try:
            with open(LANGUAGE_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"language": language}, f, ensure_ascii=False, indent=2)
            self.current_language = language
        except Exception as e:
            print(f"Error saving language preference: {e}")
    
    def get_text(self, key, language=None):
        """Lấy text đã dịch theo ngôn ngữ hiện tại"""
        if language is None:
            language = self.current_language
        
        if language not in TRANSLATIONS:
            language = "vi"  # Fallback to Vietnamese
            
        return TRANSLATIONS[language].get(key, key)
    
    def get_current_language(self):
        """Lấy ngôn ngữ hiện tại"""
        return self.current_language
    
    def set_language(self, language):
        """Đặt ngôn ngữ mới"""
        if language in TRANSLATIONS:
            self.save_language_preference(language)
            return True
        return False
    
    def get_available_languages(self):
        """Lấy danh sách ngôn ngữ có sẵn"""
        return list(TRANSLATIONS.keys())

# Global language manager instance
language_manager = LanguageManager()

def _(key, language=None):
    """Hàm shortcut để lấy text đã dịch"""
    return language_manager.get_text(key, language)

def get_language_manager():
    """Lấy instance của language manager"""
    return language_manager
