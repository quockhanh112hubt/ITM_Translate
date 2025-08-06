# SSL Certificate Configuration for Corporate Environments

## 🔒 Vấn đề SSL Certificate trong môi trường Corporate

Khi sử dụng ITM Translate trong môi trường công ty có Fortinet firewall/proxy, bạn có thể gặp lỗi SSL certificate khi update ứng dụng.

## 🚨 Lỗi thường gặp:
```
SSL: CERTIFICATE_VERIFY_FAILED certificate verify failed: 
self signed certificate in certificate chain
```

## ✅ Giải pháp

### Bước 1: Lấy chứng chỉ Fortinet
Liên hệ IT Department để lấy các file chứng chỉ:
- `Fortinet_CA_SSL_F1.cer`
- `Fortinet_CA_SSL_F2.cer` 
- `Fortinet_CA_SSL_F3.cer`
- `Fortinet_CA_SSL_F5.cer`

### Bước 2: Cài đặt chứng chỉ

#### Phương pháp 1: Auto Setup (Khuyến nghị)
1. Copy tất cả file `.cer` vào thư mục `Downloads`
2. Mở ITM Translate > Advanced > Check Updates
3. Nếu gặp lỗi SSL, click "Auto Setup Certificates"
4. Ứng dụng sẽ tự động detect và setup certificates

#### Phương pháp 2: Manual Setup
1. Tạo thư mục `certificates` trong thư mục ứng dụng
2. Copy tất cả file `.cer` vào thư mục `certificates`
3. Khởi động lại ứng dụng

#### Phương pháp 3: System Certificates
1. Double-click vào từng file `.cer`
2. Chọn "Install Certificate"
3. Chọn "Local Machine" > "Place all certificates in the following store"
4. Browse > "Trusted Root Certification Authorities"
5. Khởi động lại ứng dụng

### Bước 3: Config nâng cao (nếu cần)

Chỉnh sửa file `config.json`:

```json
{
  "update_server": {
    "disable_ssl_verification": false
  },
  "ssl_certificates": {
    "auto_detect_fortinet": true,
    "certificate_paths": [
      "certificates/",
      "~/Downloads/",
      "C:/certificates/"
    ]
  }
}
```

## 🔧 Troubleshooting

### Vẫn gặp lỗi SSL?
1. Kiểm tra proxy settings trong Windows
2. Liên hệ IT để whitelist các domains:
   - `github.com`
   - `api.github.com`
   - `objects.githubusercontent.com`

### Emergency fix (Không khuyến khích)
Nếu vẫn không được, tạm thời set:
```json
{
  "update_server": {
    "disable_ssl_verification": true
  }
}
```

**⚠️ Lưu ý:** Tùy chọn này không an toàn và chỉ nên dùng tạm thời.

## 📞 Hỗ trợ
- Email: support@itm-translate.com
- GitHub Issues: https://github.com/quockhanh112hubt/ITM_Translate/issues
