# ITM Translate - Hệ thống Auto Update

## Cài đặt hệ thống Auto Update

### 1. Chuẩn bị repository trên GitHub

1. Tạo repository mới trên GitHub (ví dụ: `quockhanh112hubt/ITM_Translate`)
2. Push code lên repository
3. Cập nhật file `config.json`:
   ```json
   {
       "update_server": {
           "github_repo": "quockhanh112hubt/ITM_Translate",
           "api_url": "https://api.github.com/repos/quockhanh112hubt/ITM_Translate/releases/latest",
           "check_interval_hours": 24
       }
   }
   ```

### 2. Build và Release

#### Cách 1: Sử dụng script tự động (Windows)
```bash
# Chạy script build tự động
build_release.bat
```

#### Cách 2: Sử dụng script Python (Cross-platform)
```bash
python build_release.py
```

#### Cách 3: Thủ công
1. Cập nhật version trong `version.json`
2. Build executable:
   ```bash
   pyinstaller --onefile --windowed --icon=Resource/icon.ico --name=ITM_Translate ITM_Translate.py
   ```
3. Commit và tạo tag:
   ```bash
   git add .
   git commit -m "Release v1.0.1"
   git tag -a "v1.0.1" -m "Release version 1.0.1"
   git push origin main
   git push origin --tags
   ```

### 3. Tạo Release trên GitHub

1. Vào GitHub repository → Releases → Create a new release
2. Chọn tag vừa tạo (ví dụ: `v1.0.1`)
3. Điền thông tin release:
   - Release title: `ITM Translate v1.0.1`
   - Description: Mô tả những thay đổi
4. Upload file `dist/ITM_Translate.exe` vào phần Assets
5. Publish release

### 4. Kiểm tra Update

Trong chương trình:
1. Vào tab "Nâng Cao"
2. Click "Cập nhật chương trình"
3. Chương trình sẽ tự động kiểm tra và download update

## Cấu trúc hệ thống Update

```
ITM_Translate/
├── core/
│   └── updater.py          # Module xử lý update
├── version.json            # Thông tin version hiện tại
├── config.json             # Cấu hình server update
├── build_release.bat       # Script build tự động (Windows)
├── build_release.py        # Script build tự động (Python)
└── requirements.txt        # Dependencies (đã thêm requests)
```

## Tính năng Update

### Người dùng cuối:
- Click nút "Cập nhật chương trình" để kiểm tra update
- Tự động download và cài đặt update
- Khởi động lại chương trình sau khi update

### Developer:
- Script build tự động tạo version, build executable, commit, tag
- Hỗ trợ cả Windows batch script và Python script
- Tự động cập nhật version.json với build number

## Lưu ý quan trọng

### Bảo mật:
- Update chỉ download từ GitHub releases chính thức
- Verify checksum nếu cần thiết
- Backup file cũ trước khi update

### Deployment:
- Đảm bảo file executable có đủ quyền ghi vào thư mục cài đặt
- Test update trên môi trường production
- Chuẩn bị rollback plan

### Troubleshooting:
- Nếu update fail, file backup sẽ được restore
- Log errors trong temp directory
- Kiểm tra kết nối internet và GitHub API

## Ví dụ Workflow

1. Developer fix bug hoặc thêm tính năng
2. Chạy `build_release.bat` hoặc `build_release.py`
3. Script tự động:
   - Hỏi version mới
   - Update version.json
   - Build executable
   - Commit + tag + push
4. Tạo release trên GitHub với file executable
5. Người dùng click "Cập nhật chương trình" → tự động update

## API Rate Limit

GitHub API có rate limit:
- 60 requests/hour cho unauthenticated
- 5000 requests/hour cho authenticated

Nếu cần, có thể thêm GitHub token vào config.json:
```json
{
    "update_server": {
        "github_token": "ghp_your_token_here",
        "github_repo": "quockhanh112hubt/ITM_Translate"
    }
}
```
