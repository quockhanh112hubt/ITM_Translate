# 🚀 ITM Translate - Hướng dẫn Setup Auto-Update

## ✅ Build thành công!

Hệ thống auto-update đã hoàn thành và test thành công. Executable đã được build với tất cả dependencies cần thiết.

## 📋 Checklist hoàn thành:

- ✅ Core update system (`core/updater.py`)
- ✅ GUI integration với nút "Cập nhật chương trình"
- ✅ Version management (`version.json`)
- ✅ Build scripts (`.py` và `.bat`)
- ✅ PyInstaller spec file với đầy đủ hidden imports
- ✅ Test scripts để verify build
- ✅ Documentation đầy đủ

## 🎯 Các bước tiếp theo để có hệ thống update hoàn chỉnh:

### 1. Setup GitHub Repository

```bash
# Nếu chưa có repository
git remote add origin https://github.com/quockhanh112hubt/ITM_Translate.git

# Push code hiện tại
git push -u origin main
```

### 2. Cập nhật config.json

Sửa file `config.json` với đúng repository URL của bạn:

```json
{
    "update_server": {
        "github_repo": "quockhanh112hubt/ITM_Translate",
        "api_url": "https://api.github.com/repos/quockhanh112hubt/ITM_Translate/releases/latest",
        "check_interval_hours": 24
    }
}
```

### 3. Tạo Release đầu tiên trên GitHub

1. Vào GitHub repository → **Releases** → **Create a new release**
2. Tag version: `v1.0.3` (đã được tạo tự động)
3. Release title: `ITM Translate v1.0.3`
4. Description: Mô tả tính năng và cải tiến
5. **Upload file**: `dist/ITM_Translate.exe` 
6. **Publish release**

### 4. Test Auto-Update

1. Mở chương trình từ file `.exe`
2. Vào tab "Nâng Cao"
3. Click "Cập nhật chương trình"
4. Kiểm tra hiển thị "Đã cập nhật!" hoặc thông tin version mới

## 🔄 Quy trình Release version mới:

### Option 1: Tự động (Khuyến nghị)
```bash
# Windows
build_release.bat

# Hoặc cross-platform
python build_release.py
```

### Option 2: Thủ công
```bash
# 1. Build
python -m PyInstaller --onefile --windowed --hidden-import=ttkbootstrap --icon="Resource/icon.ico" --add-data "Resource/icon.ico;Resource" --name="ITM_Translate" ITM_Translate.py

# 2. Commit & Tag
git add .
git commit -m "Release v1.0.4"
git tag -a "v1.0.4" -m "Release version 1.0.4"
git push origin main && git push origin --tags

# 3. Tạo release trên GitHub và upload exe file
```

## 📱 Cho người dùng cuối:

Người dùng chỉ cần:
1. Download file `.exe` từ GitHub Releases
2. Chạy chương trình
3. Khi có update → tab "Nâng Cao" → "Cập nhật chương trình"
4. Chương trình tự động download và cài đặt update

## 🔧 Troubleshooting:

### Build errors:
- Đảm bảo có `python -m PyInstaller` (không phải chỉ `pyinstaller`)
- Kiểm tra file `Resource/icon.ico` tồn tại
- Chạy `pip install -r requirements.txt`

### Update không hoạt động:
- Cập nhật `config.json` với đúng GitHub repo
- Kiểm tra có internet và GitHub accessible
- Đảm bảo có file `.exe` trong GitHub release

### Executable không chạy:
- Chạy `python test_build.py` để debug
- Kiểm tra antivirus không block file
- Thử build với `--debug` flag

## 📝 Files quan trọng:

```
ITM_Translate/
├── dist/ITM_Translate.exe     # ← Upload lên GitHub releases
├── version.json               # ← Version tracking
├── config.json               # ← Cập nhật repo URL
├── build_release.py          # ← Script build tự động
├── test_build.py             # ← Test executable
└── ITM_Translate.spec        # ← PyInstaller config
```

## 🎉 Kết luận:

Hệ thống auto-update đã hoàn thành! Bạn chỉ cần:

1. **Setup GitHub repo và cập nhật config.json**
2. **Tạo release đầu tiên với file .exe**
3. **Test update function**
4. **Từ lần sau chỉ cần chạy build_release.py để release version mới**

Chúc bạn thành công! 🚀
