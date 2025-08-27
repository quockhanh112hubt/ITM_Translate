# ITM Translate

![banner-placeholder](docs/images/banner.png)

![Release](https://img.shields.io/github/v/release/quockhanh112hubt/ITM_Translate?style=flat-square)
![License](https://img.shields.io/github/license/quockhanh112hubt/ITM_Translate?style=flat-square)
![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square)

**Phần mềm dịch thuật thông minh với AI API** — dịch nhanh bằng phím tắt, hỗ trợ nhiều provider AI và text-to-speech.

## ✨ Tính năng chính

- 🔤 **Dịch nhanh**: Chọn văn bản và nhấn phím tắt để dịch tức thì
- 🔊 **Text-to-Speech**: Đọc bản dịch bằng giọng nói
- 🎯 **Subtitle Sync**: Highlight từng từ khi đọc
- 🤖 **Multi-AI**: Hỗ trợ Gemini, ChatGPT, Claude, DeepSeek và Google Translate với failover tự động
- 🌍 **Đa ngôn ngữ**: Tự động nhận diện và dịch sang nhiều ngôn ngữ
- ⚡ **Hotkey**: Phím tắt tùy chỉnh (mặc định đề xuất `Ctrl+Q`, `Ctrl+D`)

## 🚀 Tải về & Cài đặt

Download bản cài Windows (.exe) từ trang Releases. Mỗi binary kèm checksum SHA256 trong phần release assets.

Link Releases: https://github.com/quockhanh112hubt/ITM_Translate/releases

> Gợi ý: nếu bạn muốn chạy không cài đặt, xem mục "Portable" (nếu có) hoặc chạy từ source với Python.

## 🖼️ Ảnh chụp màn hình / Demo

![screenshot-1](docs/images/screenshot-1.png)
![screenshot-2](docs/images/screenshot-2.png)

_(Thay thế 2 ảnh trên bằng ảnh thực tế của popup và settings)_

## 🚦 Thiết lập API Key
1. Mở chương trình → Tab "Quản lý API KEY"
2. Thêm API key từ một trong các providers (ví dụ):
   - **Gemini** (Google AI Studio)
   - **ChatGPT** (OpenAI)
   - **Claude** (Anthropic)
   - **DeepSeek** (DeepSeek Platform)

Lưu ý: API keys chỉ lưu cục bộ trên máy. Nếu bạn khoá/thu hồi key, cập nhật trong app để tránh lỗi.

## 🧭 Cách dùng (ngắn)
1. **Dịch popup**: Chọn văn bản → Nhấn `Ctrl+Q`
2. **Dịch thay thế**: Chọn văn bản → Nhấn `Ctrl+D`
3. **Text-to-Speech**: Click nút 🔊 trong popup
4. **Tùy chỉnh**: Tab "Cài Đặt" để thay đổi hotkey và ngôn ngữ

## ❓ Hỗ trợ & FAQ
- **Hotkey không hoạt động**: thử chạy app với quyền Administrator hoặc kiểm tra phần mềm hotkey khác gây xung đột
- **API key lỗi**: kiểm tra key trong tab "Quản lý API KEY"
- **Không có giọng đọc**: cài đặt Windows Speech Platform / kiểm tra voice pack

Q: Có thể sử dụng miễn phí không? A: Có, nhưng cần API keys từ providers (một số có tier miễn phí)

Q: Hỗ trợ offline translation? A: Không, cần internet để kết nối các providers

## 📦 Releases
Mỗi release đi kèm file .exe và file SHA256 checksum. Kiểm tra checksum trước khi chạy.

## 🤝 Contributing
Xem `CONTRIBUTING.md` để biết cách gửi issue / PR.

---
*Copyright © 2025 ITM Semiconductor Vietnam Company Limited*
