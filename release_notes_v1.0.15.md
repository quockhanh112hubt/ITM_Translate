# ITM Translate v1.0.15 Release Notes

## 🎉 Sửa lỗi quan trọng cho auto-update

Phiên bản v1.0.15 tập trung vào việc sửa 2 lỗi quan trọng trong quá trình auto-update được báo cáo từ phiên bản trước.

### ✨ Tính năng đã cải thiện

#### 🔇 Ẩn cửa sổ CMD khi cập nhật
- **Trước đây**: Cửa sổ CMD màu đen hiện ra đếm "3 2 1" khi cập nhật
- **Bây giờ**: Hoàn toàn ẩn, quá trình update diễn ra trong background

#### 🚀 Sửa lỗi restart sau update
- **Trước đây**: Lỗi "Failed to load Python DLL" khi khởi động lại
- **Bây giờ**: Restart mượt mà với delay timing được tối ưu

#### ⏱️ Cải thiện timing
- Tăng delay để tránh conflict DLL
- Total 13 giây delay đảm bảo stability
- Background process hoàn toàn silent

### 🔧 Sửa lỗi

- **CMD Window**: Không còn cửa sổ command line hiện ra
- **DLL Error**: Giải quyết lỗi PyInstaller bundling khi restart
- **User Experience**: Update process professional và không gây confusion

### 📱 Hướng dẫn test

1. Mở ITM Translate và vào **Help → Kiểm tra cập nhật**
2. Nếu có update, nhấn **"Cập nhật ngay"**
3. Quan sát: Không có cửa sổ CMD nào hiện ra
4. Chọn **YES** để auto-restart
5. App sẽ restart sau ~13 giây delay (để tránh DLL conflict)
6. Verify app hoạt động bình thường

### 🛠️ Technical Details

- **Hidden Window**: Sử dụng `CREATE_NO_WINDOW` và `SW_HIDE`
- **DLL Fix**: Optimal delay timing cho PyInstaller
- **Batch Script**: Hoàn toàn silent mode
- **Fallback Methods**: Tất cả đều được cập nhật

### 📋 Compatibility

- Tương thích với Windows 10/11
- Không breaking changes từ v1.0.14
- Size: ~15MB
- Requires: .NET Framework 4.8+ (thường có sẵn)

### ⚠️ Lưu ý

- Delay 13 giây có vẻ dài nhưng cần thiết cho stability
- Nếu antivirus block: Thêm exception cho ITM_Translate.exe
- Nếu vẫn lỗi DLL (hiếm): Restart máy tính

---

**Download:** [ITM_Translate.exe](link-to-release)  
**Previous Version:** [v1.0.14](link-to-v1.0.14)  
**Full Changelog:** [CHANGELOG_v1.0.15.md](CHANGELOG_v1.0.15.md)
