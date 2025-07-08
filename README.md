# ITM Translate

Phần mềm dịch thuật tự động với hotkey, hỗ trợ auto-update từ GitHub releases.

## Tính năng chính

- ✅ Dịch văn bản bằng AI
- ✅ Hotkey tùy chỉnh để dịch nhanh
- ✅ Popup hiển thị kết quả dịch
- ✅ Thay thế văn bản gốc bằng bản dịch
- ✅ Hỗ trợ đa ngôn ngữ
- ✅ Chạy trong system tray
- ✅ **Auto-update từ GitHub releases**

## Cài đặt

### Từ Source Code

1. Clone repository:
   ```bash
   git clone https://github.com/quockhanh112hubt/ITM_Translate.git
   cd ITM_Translate
   ```

2. Cài đặt dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Tạo file `.env` và thêm API key:
   ```
   ITM_TRANSLATE_KEY=your_api_key_here
   ```

4. Chạy chương trình:
   ```bash
   python ITM_Translate.py
   ```

### Từ Executable

1. Download file `.exe` từ [GitHub Releases](https://github.com/quockhanh112hubt/ITM_Translate/releases)
2. Chạy file `.exe`
3. Cấu hình API key trong tab "Nâng Cao"

## Sử dụng

### Hotkey mặc định:
- **Ctrl+Q**: Dịch văn bản đã chọn (hiển thị popup)
- **Ctrl+D**: Dịch và thay thế văn bản đã chọn

### Cách dịch:
1. Chọn đoạn văn bản cần dịch
2. Nhấn hotkey
3. Xem kết quả trong popup hoặc văn bản được thay thế tự động

### Cấu hình:
- Mở chương trình → Tab "Cài Đặt"
- Thay đổi hotkey và ngôn ngữ
- Tab "Nâng Cao": Cấu hình API key và kiểm tra update

## Auto-Update

### Cho người dùng cuối:
1. Vào tab "Nâng Cao" trong chương trình
2. Click "Cập nhật chương trình"
3. Chương trình sẽ tự động:
   - Kiểm tra version mới trên GitHub
   - Download và cài đặt update
   - Khởi động lại với version mới

### Cho developer:
Xem file [UPDATE_SETUP.md](UPDATE_SETUP.md) để biết cách setup hệ thống update.

## Build Executable

### Tự động (khuyến nghị):
```bash
# Windows
build_release.bat

# Cross-platform
python build_release.py
```

### Thủ công:
```bash
pyinstaller --onefile --windowed --icon=Resource/icon.ico --name=ITM_Translate ITM_Translate.py
```

## Cấu trúc Project

```
ITM_Translate/
├── ITM_Translate.py        # File chính
├── core/                   # Core modules
│   ├── translator.py       # AI translation logic
│   ├── tray.py            # System tray
│   ├── lockfile.py        # Single instance
│   └── updater.py         # Auto-update system
├── ui/                     # User interface
│   ├── gui.py             # Main GUI
│   └── popup.py           # Translation popup
├── Resource/               # Assets
│   ├── icon.ico
│   └── icon.png
├── version.json           # Version info
├── config.json            # App configuration
├── requirements.txt       # Dependencies
├── build_release.bat      # Auto build (Windows)
├── build_release.py       # Auto build (Python)
└── UPDATE_SETUP.md        # Update system setup guide
```

## Dependencies

- `pynput`: Hotkey và clipboard
- `tkinter/ttkbootstrap`: GUI
- `google-generativeai`: AI translation
- `requests`: HTTP requests cho update
- `pillow`: Image processing
- `python-dotenv`: Environment variables

## API Key

Chương trình sử dụng Google Gemini API. Để lấy API key:

1. Vào [Google AI Studio](https://aistudio.google.com/)
2. Tạo API key mới
3. Copy và paste vào chương trình (tab "Nâng Cao")

## Troubleshooting

### Update không hoạt động:
- Kiểm tra kết nối internet
- Đảm bảo file cấu hình `config.json` đúng repository
- Kiểm tra có file executable trong GitHub release

### Hotkey không hoạt động:
- Chạy chương trình với quyền Administrator
- Kiểm tra hotkey có bị conflict với app khác
- Thay đổi hotkey trong cài đặt

### Lỗi API:
- Kiểm tra API key đúng và còn hạn
- Kiểm tra kết nối internet
- Thử lại sau vài phút

## License

Copyright © 2025 ITM Semiconductor Vietnam Company Limited
All rights reserved.

## Contact

- **Author**: KhanhIT ITMV Team
- **Company**: ITM Semiconductor Vietnam Company Limited
- **GitHub**: [ITM_Translate](https://github.com/quockhanh112hubt/ITM_Translate)
