# ITM Translate v1.1.3 - Multi-Provider AI Guide

## 🌟 Tính năng mới: Multiple AI Providers

### Tổng quan
Phiên bản v1.1.3 giới thiệu hệ thống hỗ trợ nhiều AI provider với khả năng tự động chuyển đổi (failover) khi gặp lỗi.

### 🤖 Các AI Provider được hỗ trợ

| Provider | Models Hỗ trợ | Mô tả |
|----------|---------------|--------|
| **Gemini** | gemini-2.0-flash-exp, gemini-1.5-pro | Google AI (mặc định) |
| **ChatGPT** | gpt-3.5-turbo, gpt-4, gpt-4-turbo | OpenAI |
| **DeepSeek** | deepseek-chat, deepseek-coder | DeepSeek AI |
| **Claude** | claude-3-haiku, claude-3-sonnet | Anthropic |

### 📋 Cài đặt Dependencies

```bash
# Cài đặt dependencies cho tất cả providers
pip install google-generativeai openai anthropic requests

# Hoặc chỉ cài đặt providers cần thiết
pip install google-generativeai  # Gemini (bắt buộc)
pip install openai               # ChatGPT (tùy chọn)
pip install anthropic           # Claude (tùy chọn)
```

### 🎯 Cách sử dụng

#### 1. Thêm API Keys
1. Mở ITM Translate → Tab "Quản lý API KEY"
2. Chọn Provider từ dropdown
3. Nhập Model (hoặc để "auto" cho model mặc định)
4. Nhập tên mô tả (tùy chọn)
5. Nhập API Key
6. Click "Thêm Key"

#### 2. Quản lý Provider Priority
- Sử dụng nút ↑↓ để thay đổi thứ tự ưu tiên
- Provider đầu tiên sẽ được sử dụng trước
- Khi failover, hệ thống sẽ chuyển theo thứ tự này

#### 3. Chỉnh sửa API Keys
- Click "Chỉnh sửa" để thay đổi thông tin key
- Có thể đổi provider, model, tên, hoặc enable/disable key

### 🔄 Auto Failover System

#### Cách hoạt động:
1. **Primary Provider**: Sử dụng provider đang active
2. **Error Detection**: Phát hiện lỗi API (429, 401, 400, etc.)
3. **Auto Switch**: Tự động chuyển sang provider tiếp theo
4. **Failure Tracking**: Ghi nhận số lần lỗi của mỗi key
5. **Auto Disable**: Vô hiệu hóa key sau 3 lần lỗi liên tiếp

#### Loại lỗi được xử lý:
- `429`: Quota exceeded / Rate limit
- `401`: Unauthorized / Invalid key
- `400`: Bad request / Key not valid
- Network errors, timeout errors

### 💡 Popup Title Enhancement

Popup hiện tại hiển thị thông tin chi tiết:
```
ITM Translate v1.1.3 *** English → Vietnamese *** Gemini (gemini-2.0-flash-exp) - API: ...xyz123
```

Format: `[Version] *** [Source] → [Target] *** [Provider] ([Model]) - API: [Key Preview]`

### 🎮 Demo Script

Chạy demo để test tính năng:
```bash
python demo_multi_provider.py
```

Demo sẽ hiển thị:
- ✅ Danh sách API keys hiện tại
- 🔍 Language detection test
- 🔄 Translation với multiple providers
- 🧪 Failover mechanism simulation

### 📊 Migration từ phiên bản cũ

Hệ thống tự động migrate:
- ✅ API keys cũ → Gemini provider
- ✅ Settings cũ được giữ nguyên
- ✅ Backward compatibility 100%

### 🔧 Troubleshooting

#### Lỗi "Provider not available"
```python
# Cài đặt library còn thiếu
pip install openai      # Cho ChatGPT
pip install anthropic   # Cho Claude
```

#### API Key không hoạt động
1. Kiểm tra key còn hạn sử dụng
2. Verify quota còn đủ
3. Kiểm tra permissions
4. Reset failure count trong GUI

#### Failover không hoạt động
1. Đảm bảo có ít nhất 2 API keys
2. Kiểm tra provider priority order
3. Verify keys khác provider đang active

### 🚀 Best Practices

#### Recommended Setup:
1. **Primary**: Gemini (stable, good performance)
2. **Backup**: ChatGPT (high quality)
3. **Alternative**: DeepSeek (cost-effective)

#### Key Management:
- ✅ Sử dụng ít nhất 2 providers khác nhau
- ✅ Set priority theo tùy chọn cá nhân
- ✅ Regularly check key status
- ✅ Keep backup keys updated

#### Performance Tips:
- 🔹 Gemini: Fastest response time
- 🔹 ChatGPT: Highest translation quality
- 🔹 DeepSeek: Good balance cost/quality
- 🔹 Claude: Best for complex contexts

### 📞 Support

Nếu gặp vấn đề:
1. Check console logs cho error details
2. Verify API key status
3. Test với demo script
4. Contact ITM IT Team

---

*Powered by ITM Semiconductor Vietnam Company Limited - KhanhIT IT Team*  
*Copyright © 2025 all rights reserved*
