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
        
        # Tray menu
        "tray_show_window": "Hiện cửa sổ",
        "tray_exit": "Thoát",
        "floating_button_toggle": "Nút dịch nổi",
        "floating_button_on": "BẬT",
        "floating_button_off": "TẮT",
        
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
        "save_close_settings": "Lưu",
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
        "auto_close_popup": "Tự động đóng cửa sổ dịch",
        "excluded_applications": "Ứng dụng loại trừ",
        "excluded_apps_help": "Danh sách ứng dụng sẽ KHÔNG áp dụng chức năng 'Nút dịch nổi'",
        "add_application": "Thêm ứng dụng",
        "remove_application": "Xóa ứng dụng",
        "add_office_apps": "Thêm Office",
        "add_dev_apps": "Thêm Dev Tools",
        
        # Auto-detect functionality
        "auto_detect_app": "Tự động phát hiện",
        "auto_detect_instruction": "Bấm OK và chuyển đến ứng dụng bạn muốn thêm vào danh sách loại trừ trong vòng 2 giây.",
        "detected_app": "Phát hiện ứng dụng",
        "confirm_add_app": "Xác nhận thêm ứng dụng",
        "add_to_excluded_list": "Thêm vào danh sách loại trừ",
        "cannot_detect_app": "Không thể phát hiện ứng dụng",
        "no_active_window": "Không có cửa sổ hoạt động",
        "missing_dependencies_for_detection": "Thiếu thư viện cần thiết để phát hiện ứng dụng",
        "detection_error": "Lỗi khi phát hiện ứng dụng",
        
        # Running apps dialog
        "add_running_apps": "Thêm ứng dụng đang chạy",
        "running_applications": "Ứng dụng đang chạy",
        "select_apps_to_add": "Chọn ứng dụng để thêm vào danh sách loại trừ (có thể chọn nhiều):",
        "add_selected": "Thêm đã chọn",
        "please_select_apps": "Vui lòng chọn ít nhất một ứng dụng",
        "error_loading_apps": "Lỗi khi tải danh sách ứng dụng",
        "clear_list": "Xóa toàn bộ",
        "confirm_clear_list": "Bạn có chắc muốn xóa toàn bộ danh sách ứng dụng loại trừ?",
        "list_cleared": "Danh sách đã được xóa sạch",
        "list_already_empty": "Danh sách đã trống",
        "apps_removed_from_list": "ứng dụng đã được xóa khỏi danh sách",
        "enter_application_name": "Nhập tên ứng dụng (không phân biệt hoa thường):",
        "examples": "Ví dụ",
        "success": "Thành công",
        "warning": "Cảnh báo",
        "info": "Thông tin",
        "added_to_excluded_list": "đã được thêm vào danh sách loại trừ",
        "already_in_list": "đã có trong danh sách",
        "removed_from_excluded_list": "đã được xóa khỏi danh sách loại trừ",
        "please_select_app_to_remove": "Vui lòng chọn ứng dụng để xóa",
        "office_apps_added": "ứng dụng Office đã được thêm",
        "all_office_apps_already_added": "Tất cả ứng dụng Office đã có trong danh sách",
        "dev_apps_added": "ứng dụng Dev Tools đã được thêm",
        "all_dev_apps_already_added": "Tất cả ứng dụng Dev Tools đã có trong danh sách",
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
        "save_close_settings": "Lưu",
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
        
        # Updater messages
        "update_check_title": "ITM Translate - Kiểm tra cập nhật",
        "update_available_title": "✅ Đã cập nhật!",
        "already_latest_version": "Bạn đang sử dụng phiên bản mới nhất",
        "update_check_error": "Lỗi kiểm tra cập nhật:",
        "update_note": "Lưu ý: Luôn sử dụng phiên bản mới nhất để đảm bảo có trải nghiệm tốt.\n",
        
        # About Dialog
        "about_copied": "✅ Đã sao chép",
        "about_copied_message": "Thông tin phiên bản đã được sao chép vào clipboard!",
        "about_content": """🚀 TRÌNH QUẢN LÝ DỊCH THUẬT THÔNG MINH
Công cụ dịch thuật chuyên nghiệp sử dụng AI dành cho Windows

📋 CÁC TÍNH NĂNG CHÍNH:
├─ Chọn và dịch văn bản thông minh
├─ Dịch nhanh tức thì bằng phím tắt
├─ Thay thế văn bản theo thời gian thực
├─ Tự động nhận diện ngôn ngữ bằng AI (Hỗ trợ ngôn ngữ pha trộn)
├─ Nhóm ngôn ngữ kép với phím tắt tuỳ chỉnh
└─ Hỗ trợ hơn 10 ngôn ngữ (Anh, Việt, Hàn, Trung, Nhật, Pháp, Đức, Nga, Tây Ban Nha, Thái...)

⭐ TÍNH NĂNG NÂNG CAO:
├─ Tích hợp AI cho kết quả dịch chính xác
├─ Tự động phát hiện ngôn ngữ gốc
├─ Dịch theo ngữ cảnh (Giữ nguyên ý nghĩa và giọng điệu)
├─ Tuỳ chỉnh phím tắt linh hoạt (Kết hợp Ctrl/Alt/Shift)
├─ Ghi nhớ thiết lập và sao lưu tự động
└─ Quản lý khóa API an toàn

🔧 TÍCH HỢP HỆ THỐNG:
├─ Tự khởi động cùng Windows
├─ Chạy nền trong khay hệ thống
├─ Tối ưu hiệu suất sử dụng bộ nhớ
├─ Hỗ trợ phím tắt toàn cục (Dùng được trong mọi ứng dụng)
└─ Bảo vệ khỏi khởi động nhiều phiên bản

🔄 HỆ THỐNG CẬP NHẬT:
├─ Cập nhật tự động/thủ công dựa trên phiên bản mới nhất
├─ Cập nhật nền yên lặng với quyền quản trị viên
├─ Cơ chế cập nhật dựa trên kết nối GitHub
└─ Di chuyển phiên bản mượt mà

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 THÔNG TIN PHIÊN BẢN:
├─ Phiên bản: {version_info}
├─ Bản dựng: {build_info}
├─ Ngày phát hành: {release_date}
└─ Kiến trúc: Windows x64

👥 ĐỘI NGŨ PHÁT TRIỂN:
├─ Lập trình viên: KhanhIT – Nhóm ITM
├─ Tích hợp AI: Sử dụng API Gemini
├─ Thiết kế UI/UX: Giao diện hiện đại với Bootstrap
└─ Đảm bảo chất lượng: Kiểm thử chuẩn doanh nghiệp

🏢 CÔNG TY:
Công ty TNHH ITM Semiconductor Việt Nam
🌐 GitHub: github.com/quockhanh112hubt/ITM_Translate
📧 Hỗ trợ: Liên hệ đội IT ITM Việt Nam, 2025

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 MỤC TIÊU ỨNG DỤNG
Tăng hiệu suất làm việc của bạn với công cụ dịch thuật thông minh ngay trong tầm tay

© 2025 Công ty TNHH ITM Semiconductor Việt Nam. Bảo lưu mọi quyền.""",
        
        # Help Dialog
        "help_copied": "✅ Đã sao chép",
        "help_copied_message": "Hướng dẫn Multi-AI đã được sao chép vào clipboard!",
        "help_content": """🔧 A. CÀI ĐẶT API KEYS - MULTI PROVIDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 LƯU Ý QUAN TRỌNG: Bạn cần có ít nhất 1 API key từ bất kỳ provider nào để sử dụng ITM Translate.

🤖 1. GOOGLE GEMINI (KHUYẾN NGHỊ - MIỄN PHÍ):
Bước 1: Truy cập Google AI Studio
- Mở: https://aistudio.google.com/
- Đăng nhập bằng tài khoản Google

Bước 2: Tạo API Key
- Click "Get API key" → "Create API key in new project"
- Sao chép key (bắt đầu bằng "AIza...")
- Add vào tab "Quản lý API KEY" trong ứng dụng
• Chi phí: Đây là key miễn phí với giới hạn 15 requests/phút

🌍 2. GOOGLE TRANSLATE (MIỄN PHÍ/TRẢ PHÍ):
Bước 1: Truy cập Google Cloud Console
- Mở: https://console.cloud.google.com/
- Đăng nhập bằng tài khoản Google

Bước 2: Tạo API Key cho Translation API
- Tạo project mới hoặc chọn project hiện có
- Enable "Cloud Translation API"
- Tạo API Key trong "Credentials"
- Sao chép key (bắt đầu bằng "AIza...")
• Chi phí: Free tier 500,000 characters/tháng, sau đó $20/1M characters
• Ưu điểm: Dịch trực tiếp, không cần AI prompt, tốc độ nhanh

🧠 3. OPENAI CHATGPT (TRẢ PHÍ):
- Vào: https://platform.openai.com/api-keys
- Tạo API key mới
- Models: gpt-4o, gpt-4, gpt-3.5-turbo
• Chi phí: ~$0.01-0.06 per 1000 tokens

🎭 4. ANTHROPIC CLAUDE (TRẢ PHÍ):
- Vào: https://console.anthropic.com/
- Tạo API key
- Models: claude-3.5-sonnet, claude-3-opus
• Có free tier hạn chế

🐙 5. GITHUB COPILOT:
- Cần GitHub Copilot subscription
- Sử dụng GitHub personal access token
• Chỉ dành cho token từ Copilot, không phải GitHub API key

🌊 6. DEEPSEEK (GIÁ RẺ):
- Vào: https://platform.deepseek.com/
- Models: deepseek-chat, deepseek-coder
• Có free tier hạn chế

💡 KHUYẾN NGHỊ:
• Bắt đầu với Gemini (miễn phí) hoặc Google Translate (reliable)
• Thêm 2-3 providers khác để tăng độ tin cậy
• Google Translate cho tốc độ, AI providers cho chất lượng
• Sử dụng priority system để ưu tiên provider yêu thích


📋 B. QUẢN LÝ API KEYS TRONG ỨNG DỤNG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Bước 1: Mở tab "Quản lý API KEY"
- Hiển thị trạng thái real-time của từng key

Bước 2: Thêm Key mới
- Chọn Provider từ danh sách
- Chọn Model (hoặc để "auto")
- Nhập tên key (tùy chọn)
- Dán API key vào ô "API Key"
- Click "➕ Thêm Key"

Bước 3: Hệ thống tự động validate
- Kiểm tra key trong background
- Thông báo nếu key hợp lệ
- Cảnh báo nếu key có vấn đề


🚀 C. CÁCH SỬ DỤNG DỊCH THUẬT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Bước 1: Chọn văn bản
- Bôi đen đoạn văn bản trong bất kỳ ứng dụng nào
- Hoạt động với: Word, Chrome, Email, Chat apps, PDFs...

Bước 2: Sử dụng phím tắt
- Dịch POPUP: Ctrl+Q (mặc định)
- Dịch THAY THẾ: Ctrl+D (mặc định)

Bước 3: Hệ thống AI xử lý
- Tự động chọn provider tối ưu
- AI detect ngôn ngữ nguồn
- Retry thông minh nếu gặp lỗi
- Hiển thị kết quả < 2 giây


⭐ D. CẤU HÌNH HOTKEYS & NGÔN NGỮ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nhóm mặc định (Công việc chính):
- Dịch popup: Ctrl+Q 
- Dịch thay thế: Ctrl+D
- Ngôn ngữ: Any Language → Tiếng Việt → English

Nhóm tùy chỉnh (Học tập/Dự án):
- Dịch popup: Ctrl+1
- Dịch thay thế: Ctrl+2  
- Ngôn ngữ: Tùy chỉnh theo nhu cầu

💡 MẸO HOTKEYS:
• Tránh các phím F1-F12, hoặc phím hệ thống
• Không dùng phím đã có ứng dụng khác sử dụng


🔧 E. TROUBLESHOOTING & OPTIMIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 XỬ LÝ SỰ CỐ THÔNG DỤNG:

❌ API Keys không hoạt động:
- Kiểm tra tab "Quản lý API KEY" → Status column
- Thêm backup keys từ providers khác  
- Restart app nếu cần thiết

⌨️ Hotkeys bị conflict:
- Chạy với quyền Administrator
- Đổi hotkey combination khác
- Kiểm tra apps khác có dùng hotkey tương tự

🌐 Translation fails:
- Hệ thống tự retry với provider khác
- Check kết nối internet
- Verify API quotas chưa hết

⚡ Performance tối ưu:
- Sử dụng 2-3 providers
- Giữ text length < 4000 ký tự

💡 PRO TIPS:
• Gemini: Tốt nhất cho hầu hết ngôn ngữ, tự nhiên
• ChatGPT: Tốt cho dịch kỹ thuật, công nghệ
• Setup priority: Gemini → ChatGPT → Claude""",
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
        
        # Google Translate validation messages
        "google_translate_key_short": "Google Translate API key quá ngắn (tối thiểu 30 ký tự)",
        "google_translate_key_invalid_chars": "Google Translate API key chứa ký tự không hợp lệ",
        "google_translate_working": "✅ Google Translate API key hoạt động tốt (model: {model})",
        "google_translate_missing_library": "❌ Thiếu thư viện google-cloud-translate (pip install google-cloud-translate)",
        "google_translate_invalid_key": "❌ Google Translate API key không hợp lệ",
        "google_translate_quota_exceeded": "❌ Google Translate: Vượt quá quota hoặc rate limit",
        "google_translate_billing_error": "❌ Google Translate: Chưa kích hoạt billing hoặc project không tồn tại",
        "google_translate_timeout": "❌ Google Translate API: Timeout - thử lại sau",
        "google_translate_error": "❌ Google Translate API error: {error}",
        "google_translate_empty_response": "❌ Google Translate trả về response rỗng",
        
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
        
        # Timeout tooltips
        "tooltip_floating_timeout": "Thời gian tạm tắt chức năng nút dịch nổi khi phát hiện chụp ảnh màn hình.\nSau thời gian này, nút dịch sẽ tự động xuất hiện trở lại.",
        "tooltip_retry_timeout": "Thời gian chờ tối đa cho mỗi lần thử dịch.\nNếu quá thời gian này, hệ thống sẽ thử API khác.",
        "tooltip_validation_timeout": "Thời gian chờ tối đa khi kiểm tra API key.\nTăng giá trị này nếu mạng chậm.",
        "tooltip_switching_delay": "Thời gian chờ trước khi chuyển sang model khác khi lỗi.\nGiúp tránh spam API khi có lỗi liên tục.",
        
        # Timeout settings UI
        "timeout_settings_title": "⏱️ Cài đặt thời gian chờ",
        "timeout_settings_help": "Tuỳ chỉnh thời gian chờ cho các hoạt động khác nhau (tính bằng giây)",
        "floating_button_timeout_label": "Nút dịch nổi (chụp ảnh màn hình):",
        "retry_timeout_label": "Thử lại dịch khi lỗi:",
        "validation_timeout_label": "Kiểm tra API key:",
        "switching_delay_label": "Chờ trước khi chuyển model:",
        "seconds_unit": "giây",
        "save_timeout_settings": "💾 Lưu cài đặt",
        "reset_timeout_settings": "🔄 Khôi phục mặc định",
    },
    
    "en": {
        # Window title
        "app_title": "ITM Translate v1.2.3",
        
        # Tray menu
        "tray_show_window": "Show Window",
        "tray_exit": "Exit",
        "floating_button_toggle": "Floating Button",
        "floating_button_on": "ON",
        "floating_button_off": "OFF",
        
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
        "save_close_settings": "Save",
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
        "auto_close_popup": "Auto close translation popup",
        "excluded_applications": "Excluded Applications",
        "excluded_apps_help": "List of applications that will NOT apply for 'Floating Translate Button'",
        "add_application": "Add Application",
        "remove_application": "Remove Application",
        "add_office_apps": "Add Office",
        "add_dev_apps": "Add Dev Tools",
        
        # Auto-detect functionality
        "auto_detect_app": "Auto Detect",
        "auto_detect_instruction": "Click OK and switch to the application you want to add to the exclusion list within 2 seconds.",
        "detected_app": "Detected application",
        "confirm_add_app": "Confirm add application",
        "add_to_excluded_list": "Add to exclusion list",
        "cannot_detect_app": "Cannot detect application",
        "no_active_window": "No active window",
        "missing_dependencies_for_detection": "Missing required libraries for app detection",
        "detection_error": "Error detecting application",
        
        # Running apps dialog
        "add_running_apps": "Add Running Apps",
        "running_applications": "Running Applications",
        "select_apps_to_add": "Select applications to add to exclusion list (multiple selection allowed):",
        "add_selected": "Add Selected",
        "please_select_apps": "Please select at least one application",
        "error_loading_apps": "Error loading applications list",
        "clear_list": "Clear All",
        "confirm_clear_list": "Are you sure you want to clear the entire excluded applications list?",
        "list_cleared": "List has been cleared",
        "list_already_empty": "List is already empty",
        "apps_removed_from_list": "applications removed from list",
        "enter_application_name": "Enter application name (case insensitive):",
        "examples": "Examples",
        "success": "Success",
        "warning": "Warning",
        "info": "Information",
        "added_to_excluded_list": "has been added to the excluded list",
        "already_in_list": "is already in the list",
        "removed_from_excluded_list": "has been removed from the excluded list",
        "please_select_app_to_remove": "Please select an application to remove",
        "office_apps_added": "Office applications have been added",
        "all_office_apps_already_added": "All Office applications are already in the list",
        "dev_apps_added": "Dev Tools applications have been added",
        "all_dev_apps_already_added": "All Dev Tools applications are already in the list",
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
        "save_close_settings": "Save",
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
        
        # Updater messages
        "update_check_title": "ITM Translate - Check for Updates",
        "update_available_title": "✅ Up to Date!",
        "already_latest_version": "You are using the latest version",
        "update_check_error": "Update check error:",
        "update_note": "Note: Always use the latest version to ensure the best experience.\n",
        
        # About Dialog
        "about_copied": "✅ Copied",
        "about_copied_message": "Version information has been copied to clipboard!",
        "about_content": """🚀 INTELLIGENT TRANSLATION MANAGER
Professional AI-powered translation tool for Windows

📋 MAIN FEATURES:
├─ Smart text selection and translation
├─ Instant translation with hotkeys
├─ Real-time text replacement
├─ AI-powered automatic language detection (Supports mixed languages)
├─ Dual language groups with custom hotkeys
└─ Supports 10+ languages (English, Vietnamese, Korean, Chinese, Japanese, French, German, Russian, Spanish, Thai...)

⭐ ADVANCED FEATURES:
├─ AI integration for accurate translation results
├─ Automatic source language detection
├─ Context-aware translation (Preserves meaning and tone)
├─ Flexible hotkey customization (Ctrl/Alt/Shift combinations)
├─ Settings memory and automatic backup
└─ Secure API key management

🔧 SYSTEM INTEGRATION:
├─ Auto-start with Windows
├─ Background system tray operation
├─ Optimized memory usage performance
├─ Global hotkey support (Works in any application)
└─ Multiple instance protection

🔄 UPDATE SYSTEM:
├─ Automatic/manual updates based on latest version
├─ Silent background updates with administrator privileges
├─ GitHub-based update mechanism
└─ Smooth version migration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 VERSION INFORMATION:
├─ Version: {version_info}
├─ Build: {build_info}
├─ Release Date: {release_date}
└─ Architecture: Windows x64

👥 DEVELOPMENT TEAM:
├─ Programmer: KhanhIT – ITM Team
├─ AI Integration: Using Gemini API
├─ UI/UX Design: Modern Bootstrap interface
└─ Quality Assurance: Enterprise-grade testing

🏢 COMPANY:
ITM Semiconductor Vietnam Company Limited
🌐 GitHub: github.com/quockhanh112hubt/ITM_Translate
📧 Support: Contact ITM Vietnam IT Team, 2025

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 APPLICATION GOAL
Boost your productivity with intelligent translation tools at your fingertips

© 2025 ITM Semiconductor Vietnam Company Limited. All rights reserved.""",
        
        # Help Dialog
        "help_copied": "✅ Copied",
        "help_copied_message": "Multi-AI guide has been copied to clipboard!",
        "help_content": """🔧 A. API KEYS SETUP - MULTI PROVIDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 IMPORTANT NOTE: You need at least 1 API key from any provider to use ITM Translate.

🤖 1. GOOGLE GEMINI (RECOMMENDED - FREE):
Step 1: Visit Google AI Studio
- Open: https://aistudio.google.com/
- Sign in with Google account

Step 2: Create API Key
- Click "Get API key" → "Create API key in new project"
- Copy key (starts with "AIza...")
- Add to "API KEY Management" tab in app
• Cost: Free key with 15 requests/minute limit

🌍 2. GOOGLE TRANSLATE (FREE/PAID):
Step 1: Visit Google Cloud Console
- Open: https://console.cloud.google.com/
- Sign in with Google account

Step 2: Create API Key for Translation API
- Create new project or select existing project
- Enable "Cloud Translation API"
- Create API Key in "Credentials"
- Copy key (starts with "AIza...")
• Cost: Free tier 500,000 characters/month, then $20/1M characters
• Advantage: Direct translation, no AI prompts needed, fast speed

🧠 3. OPENAI CHATGPT (PAID):
- Go to: https://platform.openai.com/api-keys
- Create new API key
- Models: gpt-4o, gpt-4, gpt-3.5-turbo
• Cost: ~$0.01-0.06 per 1000 tokens

🎭 4. ANTHROPIC CLAUDE (PAID):
- Go to: https://console.anthropic.com/
- Create API key
- Models: claude-3.5-sonnet, claude-3-opus
• Has limited free tier

🐙 5. GITHUB COPILOT:
- Requires GitHub Copilot subscription
- Use GitHub personal access token
• Only for Copilot tokens, not GitHub API keys

🌊 6. DEEPSEEK (AFFORDABLE):
- Go to: https://platform.deepseek.com/
- Models: deepseek-chat, deepseek-coder
• Has limited free tier

💡 RECOMMENDATIONS:
• Start with Gemini (free) or Google Translate (reliable)
• Add 2-3 more providers for increased reliability
• Google Translate for speed, AI providers for quality
• Use priority system to prefer your favorite provider

💡 RECOMMENDATIONS:
• Start with Gemini (free)
• Add 2-3 other providers for reliability
• Use priority system to favor preferred provider


📋 B. API KEYS MANAGEMENT IN APP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1: Open "API KEY Management" tab
- Shows real-time status of each key

Step 2: Add New Key
- Select Provider from list
- Choose Model (or leave "auto")
- Enter key name (optional)
- Paste API key in "API Key" field
- Click "➕ Add Key"

Step 3: System auto-validates
- Checks key in background
- Notifies if key is valid
- Warns if key has issues


🚀 C. HOW TO USE TRANSLATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1: Select text
- Highlight text in any application
- Works with: Word, Chrome, Email, Chat apps, PDFs...

Step 2: Use hotkeys
- POPUP translation: Ctrl+Q (default)
- REPLACE translation: Ctrl+D (default)

Step 3: AI system processes
- Automatically selects optimal provider
- AI detects source language
- Smart retry on errors
- Shows results < 2 seconds


⭐ D. HOTKEYS & LANGUAGE CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Default group (Main work):
- Popup translation: Ctrl+Q 
- Replace translation: Ctrl+D
- Languages: Any Language → Vietnamese → English

Custom group (Study/Projects):
- Popup translation: Ctrl+1
- Replace translation: Ctrl+2  
- Languages: Customizable as needed

💡 HOTKEY TIPS:
• Avoid F1-F12 keys or system keys
• Don't use keys already used by other apps


🔧 E. TROUBLESHOOTING & OPTIMIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 COMMON ISSUE FIXES:

❌ API Keys not working:
- Check "API KEY Management" tab → Status column
- Add backup keys from other providers  
- Restart app if needed

⌨️ Hotkey conflicts:
- Run with Administrator privileges
- Change to different hotkey combination
- Check if other apps use same hotkeys

🌐 Translation fails:
- System auto-retries with different provider
- Check internet connection
- Verify API quotas not exceeded

⚡ Performance optimization:
- Use 2-3 providers
- Keep text length < 4000 characters

💡 PRO TIPS:
• Gemini: Best for most languages, natural
• ChatGPT: Good for technical, tech translations
• Setup priority: Gemini → ChatGPT → Claude""",
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
        
        # Google Translate validation messages
        "google_translate_key_short": "Google Translate API key too short (minimum 30 characters)",
        "google_translate_key_invalid_chars": "Google Translate API key contains invalid characters",
        "google_translate_working": "✅ Google Translate API key working well (model: {model})",
        "google_translate_missing_library": "❌ Missing google-cloud-translate library (pip install google-cloud-translate)",
        "google_translate_invalid_key": "❌ Google Translate API key is invalid",
        "google_translate_quota_exceeded": "❌ Google Translate: Quota or rate limit exceeded",
        "google_translate_billing_error": "❌ Google Translate: Billing not enabled or project not found",
        "google_translate_timeout": "❌ Google Translate API: Timeout - try again later",
        "google_translate_error": "❌ Google Translate API error: {error}",
        "google_translate_empty_response": "❌ Google Translate returned empty response",
        
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
        
        # Timeout tooltips
        "tooltip_floating_timeout": "The time to temporarily disable floating translate button function when screenshot is detected.\nAfter this time, the translate button will automatically reappear.",
        "tooltip_retry_timeout": "Maximum wait time for each translation attempt.\nIf exceeded, the system will try another API.",
        "tooltip_validation_timeout": "Maximum wait time when checking API keys.\nIncrease this value if network is slow.",
        "tooltip_switching_delay": "Wait time before switching to another model on error.\nHelps avoid API spam when continuous errors occur.",
        
        # Timeout settings UI
        "timeout_settings_title": "⏱️ Timeout Settings",
        "timeout_settings_help": "Customize timeout values for different operations (in seconds)",
        "floating_button_timeout_label": "Floating translate button (screenshot):",
        "retry_timeout_label": "Translation retry on error:",
        "validation_timeout_label": "API key validation:",
        "switching_delay_label": "Wait before model switching:",
        "seconds_unit": "seconds",
        "save_timeout_settings": "💾 Save Settings",
        "reset_timeout_settings": "🔄 Reset to Default",
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
