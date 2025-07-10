# ITM Translate v1.0.11 - Critical Bug Fixes

## 📅 Release Date: 2025-07-08
## 🔧 Build: 2025070818

---

## 🎯 **Mục đích phiên bản**
Sửa lỗi nghiêm trọng trong quá trình restart và bundling dependencies

---

## 🐛 **Sửa lỗi quan trọng**
- **🔧 Restart Mechanism**: Sửa lỗi "No module named 'pydantic_core._pydantic_core'" khi restart
- **📦 PyInstaller Bundling**: Thêm pydantic và pydantic_core vào hiddenimports
- **🔄 Auto Restart**: Cải thiện batch script restart an toàn hơn
- **⚠️ Error Handling**: Thông báo lỗi chi tiết hơn với hướng dẫn cụ thể

---

## ✨ **Cải thiện**
- **Better Restart Script**: Sử dụng batch script thay vì Python script để tránh dependency issues
- **Enhanced Error Messages**: Thông báo lỗi phân loại theo từng loại lỗi cụ thể
- **Improved Manual Instructions**: Hướng dẫn thủ công chi tiết với các case lỗi khác nhau
- **Dependency Bundling**: Đầy đủ pydantic, pydantic_core, typing_extensions, annotated_types

---

## 🔧 **Thay đổi kỹ thuật**
- **PyInstaller Spec**: Thêm collect_submodules cho pydantic và pydantic_core
- **Restart Process**: Dùng batch script với error recovery thay vì Python script
- **Error Detection**: Phát hiện và xử lý riêng lỗi pydantic vs DLL
- **Process Management**: Cải thiện cách tạo và quản lý subprocess

---

## 📋 **Từ phiên bản trước (v1.0.10)**
- Tất cả tính năng của v1.0.10
- Sửa lỗi restart failure
- Sửa lỗi "No module named pydantic_core"
- Thông báo lỗi chi tiết hơn

---

## 🚀 **Hướng dẫn cập nhật**
1. **Auto Update**: Nhấn "Cập nhật chương trình" → "YES" (đã sửa lỗi)
2. **Manual Update**: Nhấn "Cập nhật chương trình" → "NO" → Làm theo hướng dẫn
3. **Khuyến nghị**: Restart máy tính sau khi cập nhật để đảm bảo ổn định

---

## ⚠️ **Lưu ý quan trọng**
- **Lỗi pydantic_core đã được sửa** trong phiên bản này
- **Auto restart giờ đã hoạt động** ổn định hơn
- **Manual restart vẫn là lựa chọn an toàn** nhất
- **Restart máy tính** sau update để tránh cache issues

---

## 🔗 **Liên kết**
- **GitHub**: https://github.com/yourusername/ITM_Translate
- **Releases**: https://github.com/yourusername/ITM_Translate/releases
- **Issues**: https://github.com/yourusername/ITM_Translate/issues

---

## 📝 **Ghi chú**
- Phiên bản này tập trung sửa lỗi restart mechanism
- Khuyến nghị update ngay để tránh các vấn đề về dependencies
- Báo cáo bug tại GitHub Issues nếu vẫn gặp vấn đề
