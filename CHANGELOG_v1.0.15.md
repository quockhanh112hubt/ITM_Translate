# ITM Translate v1.0.15 - CMD Window & DLL Restart Fixes

**Release Date:** 2025-07-10  
**Build:** 2025071017

## 🎯 Mục tiêu chính
- Ẩn cửa sổ CMD xuất hiện trong quá trình cập nhật
- Sửa lỗi "Failed to load Python DLL" khi restart sau cập nhật
- Cải thiện trải nghiệm người dùng khi auto-update

## ✅ Đã sửa lỗi

### 1. Ẩn cửa sổ CMD khi cập nhật
- **Vấn đề**: Cửa sổ CMD màu đen hiện ra đếm "3 2 1" khi chạy batch script
- **Giải pháp**: 
  - Sử dụng `CREATE_NO_WINDOW` flag
  - Thêm `STARTUPINFO` với `SW_HIDE`
  - Chuyển tất cả echo trong batch script thành silent (`>nul`)
  - Fallback methods đều được cập nhật để ẩn window

### 2. Sửa lỗi "Failed to load Python DLL"
- **Vấn đề**: Restart ngay sau update gây conflict DLL PyInstaller
- **Giải pháp**:
  - Tăng delay từ 3 giây lên 5 giây trước khi restart
  - Thêm delay 3 giây chờ app đóng hoàn toàn
  - Thêm delay 5 giây trước khi start app mới
  - Tổng cộng 13 giây delay để tránh conflict

### 3. Cải thiện batch script
- Tất cả echo commands đều silent (`>nul`)
- Loại bỏ `pause` commands có thể block
- Cải thiện error handling
- Cleanup tốt hơn

## 🔧 Chi tiết kỹ thuật

### Files Modified
- `core/updater.py`:
  - Method `restart_application()`: Cải thiện subprocess calls
  - Batch script: Thêm delays và silent mode
  - Dialog messages: Cập nhật để phản ánh improvements

### Subprocess Improvements
```python
# Before:
shell=True, 
creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

# After:
shell=False,
creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
startupinfo=startupinfo  # với SW_HIDE
```

### Batch Script Timing
```batch
# Before:
timeout /t 3 /nobreak >nul

# After:
timeout /t 5 /nobreak >nul  # Initial delay
timeout /t 3 /nobreak >nul  # Wait for app close
timeout /t 5 /nobreak >nul  # Wait before restart
```

## 🧪 Test Cases

### ✅ Hidden CMD Window
- [x] Không có cửa sổ CMD nào hiện ra trong quá trình update
- [x] Progress bar và status vẫn hoạt động bình thường
- [x] Background process chạy silent
- [x] Fallback methods đều ẩn window

### ✅ DLL Restart Fix
- [x] Restart sau update không còn lỗi DLL
- [x] App mới start up bình thường
- [x] Version được cập nhật đúng
- [x] Tất cả features hoạt động sau restart

### ✅ Regression Tests
- [x] Update dialog UX (v1.0.14 features) vẫn hoạt động
- [x] Auto-update mechanism bình thường
- [x] Tray icon double-click hoạt động đúng
- [x] Translation features không bị ảnh hưởng

## 🔍 Before vs After

### CMD Window
- **Before**: Cửa sổ đen hiện ra đếm ngược 3-2-1
- **After**: Hoàn toàn ẩn, không có window nào hiện ra

### DLL Error
- **Before**: "Failed to load Python DLL" khi restart
- **After**: Restart mượt mà, không lỗi DLL

### User Experience
- **Before**: Confusing với cmd window + có thể crash
- **After**: Professional, silent update process

## ⚠️ Known Issues & Workarounds
- Nếu vẫn gặp lỗi DLL (hiếm): Restart máy tính và thử lại
- Antivirus có thể false positive với auto-restart: Thêm exception
- Delay 13 giây có vẻ dài nhưng cần thiết để đảm bảo stability

## 📋 Compatibility
- **OS Support**: Windows 10/11
- **Python Version**: 3.13+
- **Dependencies**: Không thay đổi từ v1.0.14

## 🚀 Installation & Update
1. Download `ITM_Translate.exe` từ GitHub Releases
2. Thay thế file cũ (hoặc dùng auto-update từ v1.0.8+)
3. Test auto-update để verify fixes

## 📝 Notes cho Developers
- `CREATE_NO_WINDOW` flag quan trọng cho ẩn CMD
- Delay timing đã được test optimal cho PyInstaller
- Fallback methods đảm bảo compatibility với các Windows versions
- Silent batch script tránh user confusion

---

**Status:** ✅ PRODUCTION READY  
**Recommended:** Update ngay để có trải nghiệm tốt nhất
