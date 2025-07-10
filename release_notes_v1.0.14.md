# ITM Translate v1.0.14 Release Notes

## 🎉 Cải thiện trải nghiệm người dùng cho dialog cập nhật

Phiên bản v1.0.14 tập trung vào việc cải thiện trải nghiệm người dùng khi sử dụng tính năng auto-update.

### ✨ Tính năng mới & Cải thiện
- **Ẩn nút khi cập nhật**: Khi nhấn "Cập nhật ngay", cả hai nút "Cập nhật ngay" và "Để sau" sẽ biến mất để tránh nhấn nhiều lần
- **Hiển thị lại khi lỗi**: Nếu có lỗi xảy ra, các nút sẽ hiển thị lại để bạn có thể thử lại
- **UI sạch sẽ hơn**: Dialog cập nhật bây giờ trông professional và dễ sử dụng hơn

### 🔧 Sửa lỗi
- Ngăn chặn việc nhấn nhiều lần vào nút "Cập nhật ngay"
- Cải thiện error handling trong dialog cập nhật
- UI không bị confusion khi đang cập nhật

### 📱 Hướng dẫn sử dụng
1. Mở ITM Translate và vào menu **Help → Kiểm tra cập nhật**
2. Nếu có update mới, nhấn **"Cập nhật ngay"**
3. Các nút sẽ biến mất và bạn sẽ thấy progress bar
4. Nếu có lỗi, các nút sẽ hiển thị lại để thử lại

### 🛠️ Technical Notes
- Tương thích với Windows 10/11
- Không thay đổi dependencies
- Build với PyInstaller để tránh DLL conflicts
- Size: ~15MB

### 📋 Test trước khi release
- [x] Update dialog flow hoạt động đúng
- [x] Error handling hoạt động đúng  
- [x] Tray icon double-click hoạt động đúng
- [x] Translation features hoạt động bình thường
- [x] Auto-restart mechanism hoạt động đúng

---

**Download:** [ITM_Translate.exe](link-to-release)  
**SHA256:** (sẽ được cập nhật sau khi upload)  
**Previous Version:** [v1.0.13](link-to-v1.0.13)
