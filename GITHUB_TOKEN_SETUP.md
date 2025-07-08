# 🔐 Hướng dẫn setup GitHub Token cho Private Repository

## Vấn đề hiện tại
Repository của bạn đang ở chế độ **private**, GitHub API không thể truy cập mà không có authentication token.

## Giải pháp

### Option 1: Chuyển Repository thành Public (Khuyến nghị - Đơn giản nhất)

1. Vào GitHub repository: https://github.com/quockhanh112hubt/ITM_Translate
2. Click **Settings** (tab cuối cùng)
3. Scroll xuống cuối trang
4. Tìm phần **"Danger Zone"**
5. Click **"Change repository visibility"**
6. Chọn **"Make public"**
7. Confirm bằng cách gõ tên repository

✅ **Ưu điểm**: Đơn giản, không cần setup gì thêm
❌ **Nhược điểm**: Code sẽ public cho mọi người xem

### Option 2: Sử dụng GitHub Token (Giữ Private)

#### Bước 1: Tạo GitHub Personal Access Token

1. Vào GitHub → Click avatar (góc phải) → **Settings**
2. Scroll xuống → Click **"Developer settings"** (bên trái)
3. Click **"Personal access tokens"** → **"Tokens (classic)"**
4. Click **"Generate new token"** → **"Generate new token (classic)"**
5. Điền thông tin:
   - **Note**: `ITM Translate Auto Update`
   - **Expiration**: `No expiration` (hoặc 1 year)
   - **Scopes**: Chọn ✅ **`repo`** (Full control of private repositories)
6. Click **"Generate token"**
7. **QUAN TRỌNG**: Copy token ngay (chỉ hiện 1 lần!)

#### Bước 2: Thêm Token vào Config

Mở file `config.json` và thêm token:

```json
{
    "update_server": {
        "github_repo": "quockhanh112hubt/ITM_Translate",
        "api_url": "https://api.github.com/repos/quockhanh112hubt/ITM_Translate/releases/latest",
        "github_token": "ghp_your_token_here_xxxxxxxxxxxxxxxxxxxxxxx",
        "check_interval_hours": 24
    }
}
```

✅ **Ưu điểm**: Repository vẫn private
❌ **Nhược điểm**: Phức tạp hơn, cần quản lý token

## Khuyến nghị

**Cho app translation tool**: Nên chọn **Option 1 (Make Public)** vì:
- Đơn giản, không cần setup phức tạp
- Translation tool không cần giấu code
- Dễ dàng cho user download và update
- Không lo token hết hạn

**Chỉ chọn Option 2 nếu**:
- Bạn thực sự cần giữ code private
- Sẵn sàng manage GitHub token
- Hiểu rõ về GitHub API và security

## Test sau khi setup

1. Restart chương trình
2. Vào tab "Nâng Cao"
3. Click "Cập nhật chương trình"
4. Kiểm tra không còn lỗi 404

## Troubleshooting

### Vẫn lỗi 404 sau khi setup token:
- Kiểm tra token có quyền `repo`
- Kiểm tra repository name trong config.json đúng
- Kiểm tra token chưa hết hạn

### Token không work:
- Tạo token mới
- Đảm bảo chọn scope `repo`
- Copy/paste cẩn thận, không thêm space

### Repository public nhưng vẫn lỗi:
- Đợi vài phút để GitHub sync
- Tạo release đầu tiên trên GitHub
- Kiểm tra repository có tồn tại và accessible
