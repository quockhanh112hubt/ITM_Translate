# 🌐 Tính năng Đa ngôn ngữ (Internationalization) - ITM Translate

## 📋 Tổng quan
Tính năng đa ngôn ngữ cho phép người dùng chuyển đổi giao diện chương trình giữa **Tiếng Việt** và **English** thông qua 2 nút cờ quốc gia được đặt ở góc trên phải của cửa sổ.

## 🎯 Các tính năng chính

### 1. **Nút chuyển đổi ngôn ngữ**
- 🇻🇳 **Nút cờ Việt Nam**: Chuyển toàn bộ giao diện sang tiếng Việt
- 🇺🇸 **Nút cờ English**: Chuyển toàn bộ giao diện sang tiếng Anh
- **Vị trí**: Góc trên phải cửa sổ, cạnh nút Minimize
- **Icons**: Sử dụng file `Vietnam.png` và `English.png` từ thư mục Resource
- **Kích thước**: 32x22 pixels với background frame đẹp
- **Visual effects**: Hover effects, active state highlighting

### 2. **Phạm vi dịch**
Tính năng này sẽ chuyển đổi ngôn ngữ cho:
- ✅ Tiêu đề các tab (Cài Đặt ↔ Settings, Quản lý API KEY ↔ API KEY Management...)
- ✅ Tất cả labels và nút trong tab Settings
- ✅ Tất cả labels và nút trong tab API Keys
- ✅ Tất cả labels và nút trong tab Advanced
- ✅ Footer buttons (Lưu cấu hình ↔ Save & Close Settings)
- ✅ Các dialog và popup messages
- ✅ Nút floating translate
- ✅ Error messages và validation text

### 3. **Lưu trữ ngôn ngữ**
- Ngôn ngữ được chọn sẽ được lưu vào file `language.json`
- Khi khởi động lại ứng dụng, ngôn ngữ đã chọn sẽ được áp dụng tự động
- **Ngôn ngữ mặc định**: Tiếng Việt

## 🚀 Cách sử dụng

### Chuyển đổi ngôn ngữ:
1. Mở ứng dụng ITM Translate
2. Nhìn góc trên phải cửa sổ, bạn sẽ thấy 2 nút cờ
3. Click vào:
   - 🇻🇳 để chuyển sang tiếng Việt
   - 🇺🇸 để chuyển sang tiếng Anh
4. Giao diện sẽ được cập nhật ngay lập tức

## 🔧 Cấu trúc kỹ thuật

### Files chính:
- `core/i18n.py` - Hệ thống quản lý đa ngôn ngữ
- `ui/components/language_flags.py` - Component nút cờ quốc gia
- `language.json` - File lưu trữ ngôn ngữ đã chọn

### Dictionary ngôn ngữ:
```python
TRANSLATIONS = {
    "vi": {
        "tab_settings": "Cài đặt",
        "tab_api_keys": "Quản lý API KEY",
        "tab_advanced": "Nâng Cao",
        # ... nhiều keys khác
    },
    "en": {
        "tab_settings": "Settings", 
        "tab_api_keys": "API KEY Management",
        "tab_advanced": "Advanced",
        # ... nhiều keys khác
    }
}
```

### Sử dụng trong code:
```python
from core.i18n import _

# Thay vì hard-code text:
label = ttk.Label(parent, text="Cài đặt")

# Sử dụng i18n:
label = ttk.Label(parent, text=_('tab_settings'))
```

## 📁 File icons
- `Resource/Vietnam.png` - Icon cờ Việt Nam (24x16px)
- `Resource/English.png` - Icon cờ English (24x16px)

## 🎨 UI/UX Details
- Nút cờ hiện tại được highlight với viền xanh và background nhạt
- Hover effects với viền nhô lên
- Kích thước cờ: 24x16 pixels (tỷ lệ 3:2 chuẩn)
- Fallback: Nếu không load được image, sử dụng emoji cờ

## 🧪 Testing
Chạy demo test:
```bash
python demo_language_switching.py
```

## 📝 Lưu ý
- Ngôn ngữ chỉ ảnh hưởng đến **giao diện ứng dụng**, không ảnh hưởng đến chức năng dịch
- Cài đặt ngôn ngữ độc lập với cài đặt ngôn ngữ dịch trong phần Settings
- Khi thêm text mới vào ứng dụng, cần cập nhật cả 2 ngôn ngữ trong `TRANSLATIONS`
