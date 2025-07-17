# 💳 Hướng dẫn khắc phục lỗi DeepSeek "Insufficient Balance"

## Vấn đề
- **Lỗi**: `402 - Insufficient Balance`
- **Nguyên nhân**: Tài khoản DeepSeek hết credit
- **Giải pháp**: Nạp thêm tiền vào tài khoản

## Cách khắc phục

### 1. Nạp tiền vào tài khoản DeepSeek
1. Truy cập: https://platform.deepseek.com/
2. Đăng nhập vào tài khoản
3. Vào mục "Billing" hoặc "Credits"
4. Nạp thêm credit (thường từ $5-20 là đủ dùng lâu)

### 2. Kiểm tra quota hiện tại
```bash
python check_api_status.py
```

### 3. Tính năng tự động failover
- **Ưu điểm**: Khi DeepSeek hết tiền, system sẽ tự động chuyển sang Gemini
- **Không ảnh hưởng**: Người dùng vẫn translate bình thường
- **Thông báo rõ ràng**: System sẽ báo cần nạp tiền cho DeepSeek

## Lưu ý
- DeepSeek có giá rẻ nhất trong các provider
- Gemini miễn phí nhưng có giới hạn quota
- Nên có ít nhất 2 provider để backup lẫn nhau

## Kiểm tra trạng thái API keys
```bash
# Kiểm tra tất cả API keys
python check_api_status.py

# Test failover mechanism  
python test_failover.py
```
