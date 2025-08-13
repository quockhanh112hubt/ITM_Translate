# Tooltip Implementation Guide - ITM Translate

## Overview
Đã triển khai hệ thống tooltip cho ITM Translate với hỗ trợ đa ngôn ngữ (Tiếng Việt và Tiếng Anh).

## Features Implemented

### 1. Tooltip System (`ui/tooltip.py`)
- **ToolTip Class**: Tạo tooltips hover với delay tùy chỉnh
- **Multi-language Support**: Tự động nhận diện translation keys và hiển thị text phù hợp
- **Auto-positioning**: Tooltip tự động định vị gần widget
- **Responsive**: Ẩn tooltip khi click hoặc rời chuột

### 2. Integration với Advanced Tab
Đã thêm tooltips cho các timeout settings:

#### Timeout Settings với Tooltips:
1. **Floating Button Timeout** → `tooltip_floating_timeout`
2. **Translation Retry Timeout** → `tooltip_retry_timeout` 
3. **API Validation Timeout** → `tooltip_validation_timeout`
4. **Model Switching Delay** → `tooltip_switching_delay`

### 3. Translation Keys Added

#### Vietnamese Tooltips:
```json
"tooltip_floating_timeout": "Thời gian chờ tối đa khi chụp ảnh màn hình bằng nút dịch nổi. Nếu quá thời gian này, hệ thống sẽ dừng chụp ảnh tự động.",
"tooltip_retry_timeout": "Thời gian chờ giữa các lần thử lại khi dịch thuật gặp lỗi. Giúp tránh spam API và cải thiện tỷ lệ thành công.",
"tooltip_validation_timeout": "Thời gian chờ tối đa khi kiểm tra tính hợp lệ của API key. Thời gian quá ngắn có thể gây false negative.",
"tooltip_switching_delay": "Thời gian chờ trước khi chuyển đổi giữa các model AI. Giúp tránh conflicts và đảm bảo chuyển đổi mượt mà."
```

#### English Tooltips:
```json
"tooltip_floating_timeout": "Maximum wait time when taking screenshot with floating translate button. System will stop auto-capture if this timeout is exceeded.",
"tooltip_retry_timeout": "Wait time between retry attempts when translation encounters errors. Helps avoid API spam and improves success rate.",
"tooltip_validation_timeout": "Maximum wait time when validating API key validity. Too short timeout may cause false negatives.",
"tooltip_switching_delay": "Wait time before switching between AI models. Helps avoid conflicts and ensures smooth transitions."
```

## Usage Instructions

### For Users:
1. **Mở ứng dụng ITM Translate**
2. **Navigate đến tab "Advanced"**
3. **Scroll xuống section "⏱️ Cài đặt thời gian chờ"**
4. **Hover chuột lên các label** để xem tooltip giải thích
5. **Tooltips sẽ hiển thị theo ngôn ngữ hiện tại** của ứng dụng

### For Developers:
```python
from ui.tooltip import create_tooltip

# Tạo tooltip với translation key
label = tk.Label(parent, text="My Label")
create_tooltip(label, "translation_key")

# Tạo tooltip với text trực tiếp
create_tooltip(label, "Direct tooltip text")

# Tùy chỉnh delay và wrapping
create_tooltip(label, "tooltip_key", delay=1000, wraplength=250)
```

## File Changes Summary

### New Files:
- `ui/tooltip.py` - Tooltip utility system
- `test_tooltips.py` - Test script for tooltip functionality

### Modified Files:
- `ui/tabs/advanced_tab.py` - Added tooltip imports and integration
- `core/i18n.py` - Added tooltip translation keys for both languages

## Testing

### Manual Testing:
1. Run `python test_tooltips.py` để test tooltip standalone
2. Run ứng dụng chính và test tooltips trong Advanced tab
3. Thay đổi ngôn ngữ và verify tooltips cập nhật theo

### Expected Behavior:
- ✅ Tooltips xuất hiện sau 500ms hover
- ✅ Tooltips ẩn khi rời chuột hoặc click
- ✅ Tooltips hiển thị đúng ngôn ngữ
- ✅ Text wrapping tự động ở 300px
- ✅ Positioning thông minh tránh edge cases

## Benefits

### For Users:
- **Better UX**: Hiểu rõ ý nghĩa và tác dụng của từng timeout setting
- **Guided Configuration**: Biết được range và impact của mỗi setting
- **Multi-language**: Hỗ trợ cả Tiếng Việt và Tiếng Anh

### For Developers:
- **Reusable System**: Tooltip có thể áp dụng cho bất kỳ widget nào
- **I18n Integration**: Tự động sử dụng translation system có sẵn
- **Easy Extension**: Dễ dàng thêm tooltips mới cho features khác

## Future Enhancements

### Possible Improvements:
1. **Rich Tooltips**: Hỗ trợ HTML formatting, icons, multiple lines
2. **Dynamic Content**: Tooltips có thể thay đổi content based on context
3. **Accessibility**: Keyboard navigation support
4. **Themes**: Tooltip styling theo theme của ứng dụng
5. **Position Options**: Left, right, top, bottom positioning modes

### Extension Ideas:
- Tooltips cho API Key tab giải thích từng provider
- Tooltips cho Settings tab với detailed explanations
- Help tooltips với links đến documentation
- Context-sensitive tooltips based on current state

## Technical Notes

### Performance:
- Tooltips sử dụng `after()` method để avoid blocking UI
- Lightweight implementation không ảnh hưởng performance
- Automatic cleanup khi widget bị destroy

### Compatibility:
- ✅ Compatible với ttkbootstrap themes
- ✅ Works với tất cả tkinter widgets  
- ✅ No external dependencies
- ✅ Windows PowerShell friendly

---

**Status: ✅ COMPLETED**
Tooltip system đã được implement thành công và ready for production use!
