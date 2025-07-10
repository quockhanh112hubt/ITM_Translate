# ITM Translate v1.0.16 Release Notes

## 🎉 Hiển thị version rõ ràng cho người dùng

Phiên bản v1.0.16 tập trung vào việc hiển thị thông tin version rõ ràng để người dùng dễ dàng biết họ đang sử dụng phiên bản nào.

### ✨ Tính năng mới

#### 📱 Version trong tiêu đề cửa sổ
- **Hiển thị**: `ITM Translate v1.0.16` thay vì chỉ `ITM Translate`
- **Lợi ích**: Ngay lập tức biết version đang dùng
- **Dynamic**: Tự động đọc từ file version.json

#### 🔧 Version trong tray icon
- **Tooltip**: Hiển thị `ITM Translate v1.0.16` khi hover chuột
- **Consistent**: Thông tin version nhất quán ở mọi nơi
- **Menu**: Vẫn giữ nguyên chức năng hiện/ẩn và thoát

#### 📋 About dialog cải thiện
- **Format mới**: Professional với build number và release date
- **Thông tin chi tiết**: Version, Build, Release Date
- **Dễ đọc**: Layout rõ ràng với emoji icons

### 🔧 Cải thiện kỹ thuật

- **Version Reading**: Dynamic từ file, không hardcode
- **Fallback Mechanism**: Luôn hiển thị được version ngay cả khi lỗi
- **Performance**: Minimal overhead, đọc file chỉ khi cần
- **Maintainable**: Dễ maintain và update

### 📱 Hướng dẫn sử dụng

1. **Kiểm tra version**: Nhìn vào tiêu đề cửa sổ
2. **Tray icon**: Hover chuột vào icon trong system tray
3. **About dialog**: Vào **Help → Thông tin về chương trình**
4. **Support**: Dễ dàng báo cáo version khi cần hỗ trợ

### 🛠️ Technical Details

- **Files modified**: `ui/gui.py`, `core/tray.py`
- **Version source**: `version.json` và `core/version.json`
- **Fallback**: Default `1.0.0` nếu không đọc được file
- **Encoding**: UTF-8 support cho tất cả text

### 📋 Compatibility

- Tương thích hoàn toàn với các version trước
- Không breaking changes
- Size: ~15MB (không thay đổi)
- Performance: Không impact đáng kể

### ⚠️ Lưu ý

- Version hiển thị được đọc từ file `version.json`
- Nếu file bị lỗi, sẽ fallback về `1.0.0`
- Thông tin version giúp ích cho việc troubleshooting

### 🔄 Update từ version cũ

- Auto-update từ v1.0.8+ hoạt động bình thường
- Manual update: Download và thay thế file exe
- Verify: Kiểm tra title bar sau khi update

---

**Download:** [ITM_Translate.exe](link-to-release)  
**Previous Version:** [v1.0.15](link-to-v1.0.15)  
**Full Changelog:** [CHANGELOG_v1.0.16.md](CHANGELOG_v1.0.16.md)

**User Benefits:**
✅ Dễ dàng biết version đang dùng  
✅ Professional appearance  
✅ Better support experience  
✅ Consistent version display
