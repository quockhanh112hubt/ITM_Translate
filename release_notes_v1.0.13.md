# ITM Translate v1.0.13

## 📅 Release Date: 2025-07-10
## 🔧 Build: 2025071015

Auto build release

---

## 📋 Changelog
# ITM Translate v1.0.13 - Critical Bug Fixes

## 📅 Release Date: 2025-07-10
## 🔧 Build: 2025071015

---

## 🎯 **Mục đích phiên bản**
Sửa lỗi quan trọng: restart mechanism và double-click tray icon

---

## 🐛 **Sửa lỗi quan trọng**
- **🔧 Restart Mechanism**: Sửa lỗi batch script không được gọi khi auto restart
- **🖱️ Double-Click Tray**: Sửa lỗi double-click tray icon không hoạt động
- **📝 Debug Logging**: Thêm debug logs để theo dõi quá trình restart và tray events
- **🛡️ Fallback Methods**: Nhiều phương pháp fallback cho restart và tray handling

---

## ✨ **Cải thiện**
- **Multiple Restart Methods**: 3 phương pháp khác nhau để chạy batch script
- **Enhanced Tray Handling**: Sử dụng Windows API để xử lý tray messages
- **Better Error Handling**: Xử lý lỗi tốt hơn với debug information
- **Focus Management**: Cải thiện focus khi hiện cửa sổ từ tray

---

## 🔧 **Thay đổi kỹ thuật**
- **Restart Process**: 
  - Method 1: subprocess.Popen với DETACHED_PROCESS
  - Method 2: os.system với start /min
  - Method 3: cmd /c start với subprocess
- **Tray Handling**:
  - Windows API message handling cho double-click
  - Monkey patch _listener._on_notify
  - Default action fallback
  - Debug logging cho tất cả events

---

## 📋 **Từ phiên bản trước (v1.0.12)**
- Tất cả tính năng của v1.0.12
- **FIXED**: Auto restart giờ chạy batch script đúng cách
- **FIXED**: Double-click tray icon giờ hoạt động
- Thêm debug logs để troubleshoot

---

## 🚀 **Hướng dẫn cập nhật**
1. **Auto Update**: Nhấn "Cập nhật chương trình" → "YES" (đã fix)
2. **Test Restart**: Batch script giờ sẽ chạy tự động
3. **Test Tray**: Double-click vào tray icon để mở cửa sổ
4. **Check Logs**: Xem console output để debug nếu cần

---

## ⚠️ **Lưu ý quan trọng**
- **Auto restart đã được sửa** - batch script giờ chạy đúng cách
- **Double-click tray đã hoạt động** - sử dụng Windows API
- **Debug logs** được thêm để theo dõi quá trình
- **Multiple fallback methods** đảm bảo reliability

---

## 🧪 **Test Cases**
1. **Update từ v1.0.12 → v1.0.13**
2. **Chọn "YES" auto restart** → Batch script phải chạy
3. **Minimize to tray** → Double-click để mở lại
4. **Check console logs** → Verify tray events được detect

---

## 🔗 **Liên kết**
- **GitHub**: https://github.com/quockhanh112hubt/ITM_Translate
- **Releases**: https://github.com/quockhanh112hubt/ITM_Translate/releases
- **Issues**: https://github.com/quockhanh112hubt/ITM_Translate/issues

---

## 📝 **Ghi chú**
- Phiên bản này tập trung sửa 2 lỗi chính từ user feedback
- Thêm debug logs để dễ troubleshoot trong tương lai
- Báo cáo feedback về restart và tray interaction tại GitHub Issues


---

## 📥 Download
- **ITM_Translate.exe**: Main executable file
- **Source code**: Available in ZIP and TAR formats

## 🔧 Installation
1. Download `ITM_Translate.exe`
2. Run the executable
3. For updates: Use the built-in update feature

## 📝 Notes
- This version includes auto-update functionality
- Backup your settings before updating
- Report issues at GitHub Issues
