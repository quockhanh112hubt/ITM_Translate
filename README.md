# ITM Translate

**Phần mềm dịch thuật AI đa nền tảng với hotkey thông minh và quản lý API keys tự động.**

> 🚀 **Version 1.1.3+** - Multi-API Provider Support với Automatic Failover

## ✨ Tính năng nổi bật

### 🤖 **Multi-AI Integration**
- Hỗ trợ 5+ AI providers: Gemini, ChatGPT, Claude, Copilot, DeepSeek
- Automatic failover khi provider bị lỗi
- Smart retry logic với backoff strategy

### 🔑 **Advanced API Management** 
- Excel-like table với auto-resize columns
- Visual status indicators (✅❌⚠️)
- Drag & drop để sắp xếp priority
- Real-time key validation

### ⚡ **Smart Translation**
- Auto language detection
- Context-aware translation
- Batch processing support  
- Professional formatting

### 🎨 **Modern Interface**
- Dark/Light theme support
- Responsive design
- Professional Excel-like tables
- System tray integration

## Tính năng chính

- ✅ **Multi-API Provider Support** - Hỗ trợ nhiều nhà cung cấp AI (Gemini, ChatGPT, Claude, Copilot, DeepSeek)
- ✅ **API Key Management** - Quản lý nhiều API keys với tính năng failover tự động
- ✅ **Smart Translation** - Dịch văn bản thông minh với retry logic và error handling
- ✅ **Hotkey tùy chỉnh** - Phím tắt để dịch nhanh (Ctrl+Q, Ctrl+D)
- ✅ **Translation Popup** - Hiển thị kết quả dịch trong popup đẹp mắt
- ✅ **Text Replacement** - Thay thế văn bản gốc bằng bản dịch tự động
- ✅ **Multi-language Support** - Hỗ trợ đa ngôn ngữ với auto-detect
- ✅ **System Tray Integration** - Chạy trong system tray với menu context
- ✅ **Auto-update System** - Tự động cập nhật từ GitHub releases

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

3. Tạo file cấu hình API keys:
   ```bash
   # Copy file mẫu
   cp api_keys.json.example api_keys.json
   
   # Hoặc tạo file api_keys.json với nội dung:
   {
     "keys": [
       {
         "key": "YOUR_API_KEY_HERE",
         "provider": "gemini",
         "model": "auto",
         "name": "My Gemini Key",
         "is_active": true,
         "failed_count": 0,
         "last_error": ""
       }
     ],
     "active_index": 0,
     "provider_priority": ["gemini", "chatgpt", "claude", "copilot", "deepseek"]
   }
   ```

4. Chạy chương trình:
   ```bash
   python ITM_Translate.py
   ```

### Từ Executable

1. Download file `.exe` từ [GitHub Releases](https://github.com/quockhanh112hubt/ITM_Translate/releases)
2. Chạy file `.exe`
3. Cấu hình API keys trong tab "Quản lý API KEY"
4. Thiết lập hotkeys trong tab "Cài Đặt"

## Sử dụng

### Hotkey mặc định:
- **Ctrl+Q**: Dịch văn bản đã chọn (hiển thị popup)
- **Ctrl+D**: Dịch và thay thế văn bản đã chọn

### Quản lý API Keys:
1. Mở tab "Quản lý API KEY"
2. Thêm API keys từ các providers khác nhau:
   - **Gemini**: Google AI Studio API key
   - **ChatGPT**: OpenAI API key  
   - **Claude**: Anthropic API key
   - **Copilot**: GitHub Copilot API key
   - **DeepSeek**: DeepSeek API key
3. Hệ thống tự động failover khi một API key bị lỗi
4. Thiết lập độ ưu tiên providers

### Cách dịch:
1. Chọn đoạn văn bản cần dịch
2. Nhấn hotkey (Ctrl+Q hoặc Ctrl+D)
3. Hệ thống tự động:
   - Detect ngôn ngữ nguồn
   - Chọn API provider phù hợp
   - Retry nếu có lỗi
   - Hiển thị kết quả

### Giao diện chính:
- **Tab Dịch**: Dịch trực tiếp trong app
- **Tab Cài Đặt**: Cấu hình hotkeys và ngôn ngữ
- **Tab Quản lý API KEY**: Quản lý keys và providers
- **Tab Nâng Cao**: Cập nhật và cài đặt nâng cao

## Auto-Update

### Cho người dùng cuối:
1. Vào tab "Nâng Cao" trong chương trình
2. Click "Cập nhật chương trình"
3. Chương trình sẽ tự động:
   - Kiểm tra version mới trên GitHub
   - Download và cài đặt update
   - Khởi động lại với version mới


## Build Executable

### Tự động (khuyến nghị):

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
├── ITM_Translate.py           # File chính
├── core/                      # Core modules
│   ├── api_key_manager.py     # Multi-API key management
│   ├── translator.py          # AI translation logic với failover
│   ├── tray.py               # System tray integration
│   ├── lockfile.py           # Single instance manager
│   ├── updater.py            # Auto-update system
│   ├── ai_providers.py       # AI provider configurations
│   └── provider_models.py    # Model definitions
├── ui/                        # User interface
│   ├── gui.py                # Main GUI với modern design
│   └── popup.py              # Translation popup
├── Resource/                  # Assets
│   ├── icon.ico              # App icon
│   └── icon.png              # App icon PNG
├── api_keys.json.example      # Template cho API keys
├── version.json              # Version information
├── config.json               # App configuration
├── hotkeys.json              # Hotkey settings
├── startup.json              # Startup configuration
├── requirements.txt          # Python dependencies
├── build_release.py          # Auto build script
├── create_release.py         # GitHub release creator
└── README.md                 # Documentation
```

## Dependencies

### Core Libraries:
- `pynput`: Hotkey detection và clipboard management
- `tkinter/ttkbootstrap`: Modern GUI framework
- `requests`: HTTP requests cho auto-update

### AI Provider SDKs:
- `google-generativeai`: Google Gemini API
- `openai`: OpenAI ChatGPT API  
- `anthropic`: Claude API
- `pillow`: Image processing

### Utilities:
- `python-dotenv`: Environment variables
- `pyinstaller`: Executable building

## API Keys & Providers

Chương trình hỗ trợ nhiều AI providers. Bạn có thể sử dụng một hoặc nhiều providers:

### 🤖 Google Gemini (Khuyến nghị)
1. Vào [Google AI Studio](https://aistudio.google.com/)
2. Tạo API key mới
3. Models hỗ trợ: `gemini-2.0-flash-exp`, `gemini-1.5-pro`, `gemini-1.5-flash`

### 🧠 OpenAI ChatGPT
1. Vào [OpenAI API](https://platform.openai.com/api-keys)
2. Tạo API key mới
3. Models hỗ trợ: `gpt-4o`, `gpt-4`, `gpt-3.5-turbo`

### 🎭 Anthropic Claude
1. Vào [Anthropic Console](https://console.anthropic.com/)
2. Tạo API key mới
3. Models hỗ trợ: `claude-3.5-sonnet`, `claude-3-opus`

### 🐙 GitHub Copilot
1. Cần GitHub Copilot subscription
2. Sử dụng GitHub token với Copilot access

### 🌊 DeepSeek
1. Vào [DeepSeek Platform](https://platform.deepseek.com/)
2. Tạo API key mới
3. Models hỗ trợ: `deepseek-chat`, `deepseek-coder`

### ⚡ Automatic Failover
- Hệ thống tự động chuyển đổi giữa các providers
- Retry logic thông minh khi có lỗi
- Priority system để ưu tiên providers

## Troubleshooting

### ❌ API Key Issues:
- **Multiple providers**: Thêm API keys từ nhiều providers để tăng độ tin cậy
- **Key validation**: Kiểm tra trạng thái keys trong tab "Quản lý API KEY"
- **Rate limits**: Hệ thống tự động retry và failover khi gặp rate limit

### ⌨️ Hotkey không hoạt động:
- **Quyền admin**: Chạy chương trình với quyền Administrator
- **Conflict detection**: Kiểm tra hotkey có bị conflict với app khác
- **Custom hotkeys**: Thay đổi hotkey trong tab "Cài Đặt"

### 🔄 Update Issues:
- **Network**: Kiểm tra kết nối internet
- **Config**: Đảm bảo file `config.json` đúng repository info
- **Permissions**: Chạy với quyền ghi file để update

### 🖥️ GUI Problems:
- **Theme**: Thử restart app nếu giao diện bị lỗi
- **DPI scaling**: Cài đặt Windows display scale 100-125%
- **Font rendering**: Đảm bảo có font system tiếng Việt

### 🌐 Translation Errors:
- **Auto-retry**: Hệ thống tự động retry 2 lần với provider khác
- **Language detection**: Thử chọn ngôn ngữ nguồn thủ công
- **Text length**: Chia nhỏ text dài (>4000 ký tự)

## 🚀 Performance & Tips

### ⚡ Optimization:
- **Cold start**: Lần dịch đầu tiên có thể chậm (~2-3s)
- **Caching**: Results được cache để tăng tốc độ
- **Parallel processing**: Multiple API calls để tăng success rate

### 💡 Best Practices:
- **Multiple APIs**: Sử dụng 2-3 providers để tăng uptime
- **Key rotation**: Thay đổi API keys định kỳ
- **Backup config**: Backup file `api_keys.json` và `config.json`

### 📊 Success Rate:
- **Single provider**: ~85-90% uptime
- **Multi-provider**: ~99%+ uptime với failover
- **Average response**: <2 seconds với cache hit

## ❓ FAQ

**Q: Có thể sử dụng miễn phí không?**
A: Có, nhưng cần API keys từ các providers (một số có tier miễn phí)

**Q: Hỗ trợ offline translation?**
A: Không, cần internet để kết nối với AI providers

**Q: Có giới hạn độ dài text?**
A: Mỗi provider có giới hạn khác nhau (~4000-8000 ký tự)

**Q: Có lưu lịch sử dịch?**
A: Hiện tại chưa, sẽ có trong version tương lai

**Q: Có mobile app?**
A: Chưa, hiện tại chỉ hỗ trợ Windows desktop

## License

Copyright © 2025 ITM Semiconductor Vietnam Company Limited
All rights reserved.

## Contact

- **Author**: KhanhIT ITMV Team
- **Company**: ITM Semiconductor Vietnam Company Limited
- **GitHub**: [ITM_Translate](https://github.com/quockhanh112hubt/ITM_Translate)
