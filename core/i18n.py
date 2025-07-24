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
        "close": "Đóng",
        "ok": "Đồng ý",
        
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
        "auto_close_popup": "Tự động đóng cửa sổ dịch khi mất focus",
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
        
        # Settings tab translations
        "language_description": "Ngôn ngữ đầu tiên sẽ được dịch tới ngôn ngữ thứ 2, ngôn ngữ thứ 2 sẽ được dịch tới ngôn ngữ thứ 3.",
        "hotkey": "Phím tắt:",
        "main_key": "Phím chính",
        "first_language": "Ngôn ngữ đầu tiên:",
        "second_language": "Ngôn ngữ thứ 2:",
        "third_language": "Ngôn ngữ thứ 3:",
        "translate_popup": "Dịch popup",
        "default_options": "Tuỳ chọn mặc định",
        "custom_options": "Tuỳ chọn tuỳ chỉnh:",
        "show_custom_options": "Hiện Tuỳ chọn tuỳ chỉnh",
        "hide_custom_options": "Ẩn Tuỳ chọn tuỳ chỉnh",
        "not_selected_hotkey": "Chưa chọn phím tắt hợp lệ!",
        "must_select_languages": "Bạn phải chọn đủ 3 ngôn ngữ cho {group_name}!",
        "config_saved": "Cấu hình đã được lưu thành công.",
        "error": "Lỗi",
        "cannot_save_config": "Không thể lưu cấu hình:",
        "config_error": "Lỗi cấu hình",
        "duplicate_hotkeys": "Các tổ hợp phím tắt không được trùng nhau!",
        "notification": "Thông báo",
        "translate_and_replace": "Dịch & thay thế",
        "shortcuts_group1": "Tuỳ chọn mặc định",
        "auto_choose_hint": "Tuỳ chọn mặc định. Ngôn ngữ đầu tiên sẽ được dịch tới ngôn ngữ thứ 2, ngôn ngữ thứ 2 sẽ được dịch tới ngôn ngữ thứ 3",
        "settings_not_initialized": "Settings tab component chưa được khởi tạo",
        "save_close_settings": "Lưu & Đóng Cài Đặt",
        "cancel": "Hủy bỏ",
        
        # API Key tab translations
        "api_keys_subtitle": "Thêm, quản lý và thiết lập ưu tiên các API keys",
        "api_keys_list": "Danh sách API Keys & Providers",
        "actions": "Thao tác",
        "add_new_api_key": "Thêm API Key mới:",
        "provider": "Provider:",
        "model": "Model:",
        "name_optional": "Tên (tùy chọn):",
        "api_key": "API Key:",
        "add_key": "➕ Thêm Key",
        "active": "Active",
        "name": "Name",
        "status": "Status",
        "save_button": "💾 Lưu",
        "cancel_button": "❌ Hủy",
        "edit_api_key_title": "🔧 Chỉnh sửa API Key",
        "name_label": "Tên:",
        "model_label": "Model:",
        "manage_keys": "Quản lý Keys:",
        "set_active": "🎯 Active",
        "edit": "✏️ Sửa",
        "remove": "🗑️ Xóa",
        "refresh": "🔄 Làm mới",
        "priority_providers": "Ưu tiên Providers:",
        "information": "💡 Thông tin:",
        "checking": "🔄 Đang kiểm tra...",
        "edit_api_key": "🔧 Chỉnh sửa API Key",
        "info_text": "• Hỗ trợ 5 Providers: Gemini, ChatGPT, Copilot, DeepSeek, Claude\n• Khi gặp lỗi, hệ thống sẽ tự động chuyển sang key OK tiếp theo\n• Model 'auto' = Model mặc định chương trình tự động nhận diện\n• Thứ tự ưu tiên từ trên xuống, quyết định Provider nào sẽ được sử dụng trước",
        "active_status": "Hoạt động",
        "status_disabled": "❌ Vô hiệu",
        "status_active": "✅ Hoạt động",
        "status_error": "⚠️ Lỗi",
        
        # MessageBox titles and messages
        "warning": "Cảnh báo",
        "error": "Lỗi",
        "success": "Thành công",
        "confirm": "Xác nhận",
        "please_enter_api_key": "Vui lòng nhập API key!",
        "confirm_save_api_key": "Bạn có muốn lưu API key này không?",
        "confirm_save_still": "Bạn vẫn muốn lưu API key này không?",
        "cannot_check_api_key": "Không thể kiểm tra API key:",
        "added_api_key_success": "Đã thêm API key {provider} mới!\n\n📋 Provider: {provider_title}\n🤖 Model: {model}\n📝 Tên: {name}",
        "api_key_exists": "API key đã tồn tại trong hệ thống!",
        "provider_not_supported": "Provider '{provider}' không được hỗ trợ!",
        "please_select_api_key_to_delete": "Vui lòng chọn API key cần xóa!",
        "confirm_delete_api_key": "Bạn có chắc muốn xóa API key này?",
        "api_key_deleted": "API key đã được xóa!",
        "cannot_delete_api_key": "Không thể xóa API key!",
        "please_select_api_key_to_activate": "Vui lòng chọn API key cần đặt active!",
        "api_key_activated": "API key đã được đặt làm active!",
        "cannot_activate_api_key": "Không thể đặt API key này làm active!",
        "please_select_api_key_to_edit": "Vui lòng chọn API key cần chỉnh sửa!",
        "cannot_get_api_key_info": "Không thể lấy thông tin API key!",
        "api_key_empty": "API key không được để trống!",
        "api_key_too_short": "API key quá ngắn! Vui lòng kiểm tra lại.",
        "validation_success": "Xác thực thành công",
        "confirm_save_changes": "Bạn có muốn lưu thay đổi không?",
        "confirm_save_changes_anyway": "Bạn vẫn muốn lưu thay đổi không?",
        "check_api_key_again": "Vui lòng kiểm tra lại API key.",
        "validation_error_title": "Lỗi xác thực",
        "cannot_check_api_key_validation": "Không thể kiểm tra API key:",
        "api_key_updated_success": "API key đã được cập nhật thành công!",
        "cannot_save_changes": "Không thể lưu thay đổi:",
        "invalid_provider": "Provider không hợp lệ!",
        "cannot_update": "Không thể cập nhật:",
        "cannot_open_edit_form": "Không thể mở form chỉnh sửa:",
        "no_active_key": "⚠️ Không có key nào được đặt active",
        "no_api_keys": "Chưa có API key nào",
        "key_active_status": "✅ Key active:",
        
        # API Key Validator messages
        "api_key_empty": "API key không được để trống",
        "gemini_key_format": "Gemini API key phải bắt đầu bằng 'AIza'",
        "gemini_key_short": "Gemini API key quá ngắn (phải >= 30 ký tự)",
        "gemini_key_invalid_chars": "Gemini API key chứa ký tự không hợp lệ",
        "openai_key_format": "OpenAI API key phải bắt đầu bằng 'sk-'",
        "openai_key_short": "OpenAI API key quá ngắn (phải >= 40 ký tự)",
        "openai_key_invalid_chars": "OpenAI API key chứa ký tự không hợp lệ",
        "deepseek_key_format": "DeepSeek API key phải bắt đầu bằng 'sk-'",
        "deepseek_key_short": "DeepSeek API key quá ngắn (phải >= 40 ký tự)",
        "deepseek_key_invalid_chars": "DeepSeek API key chứa ký tự không hợp lệ",
        "claude_key_format": "Claude API key phải bắt đầu bằng 'sk-ant-'",
        "claude_key_short": "Claude API key quá ngắn (phải >= 50 ký tự)",
        "claude_key_invalid_chars": "Claude API key chứa ký tự không hợp lệ",
        "copilot_key_format": "GitHub Copilot chỉ hỗ trợ OpenAI API key (bắt đầu bằng 'sk-'). GitHub tokens không dùng được cho API calls.",
        "provider_not_supported_validator": "Provider '{provider}' không được hỗ trợ",
        "api_key_format_valid": "Định dạng API key hợp lệ",
        "gemini_working": "✅ Gemini API key hoạt động tốt (model: {model})",
        "gemini_empty_response": "❌ Gemini API trả về response rỗng",
        "gemini_missing_library": "❌ Thiếu thư viện google-generativeai",
        "gemini_invalid_key": "❌ Gemini API key không hợp lệ",
        "gemini_quota_exceeded": "❌ Gemini API: Vượt quá quota/rate limit",
        "gemini_timeout": "❌ Gemini API: Timeout - thử lại sau",
        "network_error": "❌ Lỗi kết nối mạng",
        "gemini_error": "❌ Gemini API error: {error}",
        "openai_working": "✅ OpenAI API key hoạt động tốt (model: {model})",
        "openai_invalid_key": "❌ OpenAI API key không hợp lệ",
        "openai_rate_limit": "❌ OpenAI API: Vượt quá rate limit",
        "openai_no_credit": "❌ OpenAI API: Hết credit/quota",
        "openai_error": "❌ OpenAI API error ({status}): {error}",
        "openai_timeout": "❌ OpenAI API: Timeout - thử lại sau",
        "deepseek_working": "✅ DeepSeek API key hoạt động tốt (model: {model})",
        "deepseek_invalid_key": "❌ DeepSeek API key không hợp lệ",
        "deepseek_no_balance": "❌ DeepSeek API: Insufficient Balance (Hết tiền)",
        "deepseek_rate_limit": "❌ DeepSeek API: Vượt quá rate limit",
        "deepseek_error": "❌ DeepSeek API error ({status}): {error}",
        "deepseek_timeout": "❌ DeepSeek API: Timeout - thử lại sau",
        "claude_working": "✅ Claude API key hoạt động tốt (model: {model})",
        "claude_invalid_key": "❌ Claude API key không hợp lệ",
        "claude_rate_limit": "❌ Claude API: Vượt quá rate limit",
        "claude_error": "❌ Claude API error ({status}): {error}",
        "claude_timeout": "❌ Claude API: Timeout - thử lại sau",
        "copilot_working": "✅ GitHub Copilot API key hoạt động tốt (model: {model})",
        "copilot_empty_response": "❌ GitHub Copilot API trả về response rỗng",
        "copilot_missing_library": "❌ Thiếu thư viện openai (pip install openai)",
        "copilot_invalid_key": "❌ GitHub Copilot API key không hợp lệ",
        "copilot_quota_exceeded": "❌ GitHub Copilot: Vượt quá quota hoặc rate limit",
        "copilot_no_credit": "❌ GitHub Copilot: Hết credit hoặc quota",
        "copilot_timeout": "❌ GitHub Copilot API: Timeout - thử lại sau",
        "copilot_error": "❌ GitHub Copilot API error: {error}",
        "unexpected_error": "❌ Lỗi không mong đợi: {error}",
        "validation_success_title": "✅ API Key hợp lệ!",
        "validation_format_error_title": "❌ Định dạng API Key không đúng",
        "validation_format_error_hint": "💡 Kiểm tra lại API key từ provider",
        "validation_invalid_key_title": "❌ API Key không hợp lệ",
        "validation_invalid_key_hint": "💡 Tạo API key mới từ provider",
        "validation_quota_title": "⚠️ Vượt quá giới hạn",
        "validation_quota_hint": "💡 API key hợp lệ nhưng hết quota/credit",
        "validation_network_title": "🌐 Lỗi kết nối",
        "validation_network_hint": "💡 Kiểm tra internet và thử lại",
        "validation_timeout_title": "⏱️ Timeout",
        "validation_timeout_hint": "💡 Server chậm, thử lại sau",
        "validation_provider_error_title": "❌ Lỗi Provider",
        "validation_provider_error_hint": "💡 Liên hệ support nếu lỗi tiếp tục",
        
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
        "close": "Close",
        "ok": "OK",
        
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
        "auto_close_popup": "Auto close translation popup when focus lost",
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
        
        # Settings tab translations
        "language_description": "First language will be translated to second language, second language will be translated to third language.",
        "hotkey": "Hotkey:",
        "main_key": "Main Key",
        "first_language": "First Language:",
        "second_language": "Second Language:",
        "third_language": "Third Language:",
        "translate_popup": "Translate popup",
        "default_options": "Default Options",
        "custom_options": "Custom Options:",
        "show_custom_options": "Show Custom Options",
        "hide_custom_options": "Hide Custom Options",
        "not_selected_hotkey": "No valid hotkey selected!",
        "must_select_languages": "You must select all 3 languages for {group_name}!",
        "config_saved": "Configuration saved successfully.",
        "error": "Error",
        "cannot_save_config": "Cannot save configuration:",
        "config_error": "Configuration Error",
        "duplicate_hotkeys": "Hotkey combinations cannot be duplicated!",
        "notification": "Notification",
        "translate_and_replace": "Translate & Replace",
        "shortcuts_group1": "Default Options",
        "auto_choose_hint": "Default option. First language will be translated to second language. Second language will be translated to third language",
        "settings_not_initialized": "Settings tab component not initialized",
        "save_close_settings": "Save & Close Settings",
        "cancel": "Cancel",
        
        # API Key tab translations
        "api_keys_subtitle": "Add, manage and set priority for API keys",
        "api_keys_list": "API Keys & Providers List",
        "actions": "Actions",
        "add_new_api_key": "Add new API Key:",
        "provider": "Provider:",
        "model": "Model:",
        "name_optional": "Name (optional):",
        "api_key": "API Key:",
        "add_key": "➕ Add Key",
        "active": "Active",
        "name": "Name",
        "status": "Status",
        "save_button": "💾 Save",
        "cancel_button": "❌ Cancel",
        "edit_api_key_title": "🔧 Edit API Key",
        "name_label": "Name:",
        "model_label": "Model:",
        "manage_keys": "Manage Keys:",
        "set_active": "🎯 Active",
        "edit": "✏️ Edit",
        "remove": "🗑️ Remove",
        "refresh": "🔄 Refresh",
        "priority_providers": "Priority Providers:",
        "information": "💡 Information:",
        "checking": "🔄 Checking...",
        "edit_api_key": "🔧 Edit API Key",
        "info_text": "• Supports 5 Providers: Gemini, ChatGPT, Copilot, DeepSeek, Claude\n• When errors occur, system will automatically switch to next OK key\n• Model 'auto' = Default model automatically recognized by program\n• Priority order from top to bottom, determines which Provider will be used first",
        "active_status": "Active",
        "status_disabled": "❌ Disabled",
        "status_active": "✅ Active",
        "status_error": "⚠️ Error",
        
        # MessageBox titles and messages
        "warning": "Warning",
        "error": "Error",
        "success": "Success",
        "confirm": "Confirm",
        "please_enter_api_key": "Please enter API key!",
        "confirm_save_api_key": "Do you want to save this API key?",
        "confirm_save_still": "Do you still want to save this API key?",
        "cannot_check_api_key": "Cannot check API key:",
        "added_api_key_success": "Added new {provider} API key!\n\n📋 Provider: {provider_title}\n🤖 Model: {model}\n📝 Name: {name}",
        "api_key_exists": "API key already exists in the system!",
        "provider_not_supported": "Provider '{provider}' is not supported!",
        "please_select_api_key_to_delete": "Please select an API key to delete!",
        "confirm_delete_api_key": "Are you sure you want to delete this API key?",
        "api_key_deleted": "API key has been deleted!",
        "cannot_delete_api_key": "Cannot delete API key!",
        "please_select_api_key_to_activate": "Please select an API key to set as active!",
        "api_key_activated": "API key has been set as active!",
        "cannot_activate_api_key": "Cannot set this API key as active!",
        "please_select_api_key_to_edit": "Please select an API key to edit!",
        "cannot_get_api_key_info": "Cannot get API key information!",
        "api_key_empty": "API key cannot be empty!",
        "api_key_too_short": "API key is too short! Please check again.",
        "validation_success": "Validation Successful",
        "confirm_save_changes": "Do you want to save the changes?",
        "confirm_save_changes_anyway": "Do you still want to save the changes?",
        "check_api_key_again": "Please check the API key again.",
        "validation_error_title": "Validation Error",
        "cannot_check_api_key_validation": "Cannot check API key:",
        "api_key_updated_success": "API key has been updated successfully!",
        "cannot_save_changes": "Cannot save changes:",
        "invalid_provider": "Invalid provider!",
        "cannot_update": "Cannot update:",
        "cannot_open_edit_form": "Cannot open edit form:",
        "no_active_key": "⚠️ No key is set as active",
        "no_api_keys": "No API keys yet",
        "key_active_status": "✅ Key active:",
        
        # API Key Validator messages
        "api_key_empty": "API key cannot be empty",
        "gemini_key_format": "Gemini API key must start with 'AIza'",
        "gemini_key_short": "Gemini API key too short (must be >= 30 characters)",
        "gemini_key_invalid_chars": "Gemini API key contains invalid characters",
        "openai_key_format": "OpenAI API key must start with 'sk-'",
        "openai_key_short": "OpenAI API key too short (must be >= 40 characters)",
        "openai_key_invalid_chars": "OpenAI API key contains invalid characters",
        "deepseek_key_format": "DeepSeek API key must start with 'sk-'",
        "deepseek_key_short": "DeepSeek API key too short (must be >= 40 characters)",
        "deepseek_key_invalid_chars": "DeepSeek API key contains invalid characters",
        "claude_key_format": "Claude API key must start with 'sk-ant-'",
        "claude_key_short": "Claude API key too short (must be >= 50 characters)",
        "claude_key_invalid_chars": "Claude API key contains invalid characters",
        "copilot_key_format": "GitHub Copilot only supports OpenAI API key (starting with 'sk-'). GitHub tokens cannot be used for API calls.",
        "provider_not_supported_validator": "Provider '{provider}' is not supported",
        "api_key_format_valid": "API key format is valid",
        "gemini_working": "✅ Gemini API key working well (model: {model})",
        "gemini_empty_response": "❌ Gemini API returned empty response",
        "gemini_missing_library": "❌ Missing google-generativeai library",
        "gemini_invalid_key": "❌ Gemini API key is invalid",
        "gemini_quota_exceeded": "❌ Gemini API: Quota/rate limit exceeded",
        "gemini_timeout": "❌ Gemini API: Timeout - try again later",
        "network_error": "❌ Network connection error",
        "gemini_error": "❌ Gemini API error: {error}",
        "openai_working": "✅ OpenAI API key working well (model: {model})",
        "openai_invalid_key": "❌ OpenAI API key is invalid",
        "openai_rate_limit": "❌ OpenAI API: Rate limit exceeded",
        "openai_no_credit": "❌ OpenAI API: Out of credit/quota",
        "openai_error": "❌ OpenAI API error ({status}): {error}",
        "openai_timeout": "❌ OpenAI API: Timeout - try again later",
        "deepseek_working": "✅ DeepSeek API key working well (model: {model})",
        "deepseek_invalid_key": "❌ DeepSeek API key is invalid",
        "deepseek_no_balance": "❌ DeepSeek API: Insufficient Balance (Out of money)",
        "deepseek_rate_limit": "❌ DeepSeek API: Rate limit exceeded",
        "deepseek_error": "❌ DeepSeek API error ({status}): {error}",
        "deepseek_timeout": "❌ DeepSeek API: Timeout - try again later",
        "claude_working": "✅ Claude API key working well (model: {model})",
        "claude_invalid_key": "❌ Claude API key is invalid",
        "claude_rate_limit": "❌ Claude API: Rate limit exceeded",
        "claude_error": "❌ Claude API error ({status}): {error}",
        "claude_timeout": "❌ Claude API: Timeout - try again later",
        "copilot_working": "✅ GitHub Copilot API key working well (model: {model})",
        "copilot_empty_response": "❌ GitHub Copilot API returned empty response",
        "copilot_missing_library": "❌ Missing openai library (pip install openai)",
        "copilot_invalid_key": "❌ GitHub Copilot API key is invalid",
        "copilot_quota_exceeded": "❌ GitHub Copilot: Quota or rate limit exceeded",
        "copilot_no_credit": "❌ GitHub Copilot: Out of credit or quota",
        "copilot_timeout": "❌ GitHub Copilot API: Timeout - try again later",
        "copilot_error": "❌ GitHub Copilot API error: {error}",
        "unexpected_error": "❌ Unexpected error: {error}",
        "validation_success_title": "✅ API Key Valid!",
        "validation_format_error_title": "❌ API Key Format Error",
        "validation_format_error_hint": "💡 Check API key from provider",
        "validation_invalid_key_title": "❌ API Key Invalid",
        "validation_invalid_key_hint": "💡 Create new API key from provider",
        "validation_quota_title": "⚠️ Quota Exceeded",
        "validation_quota_hint": "💡 API key valid but out of quota/credit",
        "validation_network_title": "🌐 Connection Error",
        "validation_network_hint": "💡 Check internet and try again",
        "validation_timeout_title": "⏱️ Timeout",
        "validation_timeout_hint": "💡 Server slow, try again later",
        "validation_provider_error_title": "❌ Provider Error",
        "validation_provider_error_hint": "💡 Contact support if error continues",
        
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
