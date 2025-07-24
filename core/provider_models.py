"""
Provider Models Configuration - Định nghĩa các model có sẵn cho từng AI provider
"""

# Danh sách models cho từng provider
PROVIDER_MODELS = {
    'gemini': [
        'auto',
        'gemini-2.5-pro',
        'gemini-2.5-flash',
        'gemini-2.0-flash-exp',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-1.5-flash-8b',
        'gemini-1.0-pro',
        'gemini-1.5-flash-002',
        'gemini-1.5-pro-002'
    ],
    'chatgpt': [
        'auto',
        'gpt-3.5-turbo',
        'gpt-4',
        'gpt-4-turbo',
        'gpt-4o',
        'gpt-4o-mini'
    ],
    'deepseek': [
        'auto',
        'deepseek-chat',
        'deepseek-coder'
    ],
    'claude': [
        'auto',
        'claude-3-haiku-20240307',
        'claude-3-sonnet-20240229',
        'claude-3-opus-20240229',
        'claude-3-5-sonnet-20241022'
    ],
    'copilot': [
        'auto',
        'gpt-4',
        'gpt-3.5-turbo',
        'copilot-codex'
    ]
}

# Model descriptions để hiển thị tooltip
MODEL_DESCRIPTIONS = {
    'auto': 'Select model for provider',
    
    # Gemini models
    'gemini-2.5-pro': 'Gemini 2.5 Pro - Phiên bản mới nhất, hiệu suất cao',
    'gemini-2.5-flash': 'Gemini 2.5 Flash - Phiên bản mới, siêu nhanh',
    'gemini-2.0-flash-exp': 'Gemini 2.0 Flash (Experimental) - Model mới nhất, hiệu suất cao',
    'gemini-1.5-flash': 'Gemini 1.5 Flash - Nhanh, hiệu quả (Khuyến nghị)',
    'gemini-1.5-pro': 'Gemini 1.5 Pro - Chất lượng cao, chậm hơn',
    'gemini-1.5-flash-8b': 'Gemini 1.5 Flash 8B - Model nhỏ gọn, siêu nhanh',
    'gemini-1.0-pro': 'Gemini 1.0 Pro - Phiên bản cũ',
    'gemini-1.5-flash-002': 'Gemini 1.5 Flash v002 - Phiên bản cập nhật',
    'gemini-1.5-pro-002': 'Gemini 1.5 Pro v002 - Phiên bản cập nhật',
    
    # ChatGPT models
    'gpt-3.5-turbo': 'GPT-3.5 Turbo - Nhanh, giá rẻ (Khuyến nghị)',
    'gpt-4': 'GPT-4 - Chất lượng cao, giá đắt',
    'gpt-4-turbo': 'GPT-4 Turbo - Cân bằng tốc độ và chất lượng',
    'gpt-4o': 'GPT-4o - Phiên bản tối ưu mới nhất',
    'gpt-4o-mini': 'GPT-4o Mini - Nhỏ gọn, nhanh',
    
    # DeepSeek models
    'deepseek-chat': 'DeepSeek Chat - Model chính (Khuyến nghị)',
    'deepseek-coder': 'DeepSeek Coder - Chuyên về lập trình',
    
    # Claude models
    'claude-3-haiku-20240307': 'Claude 3 Haiku - Nhanh, giá rẻ (Khuyến nghị)',
    'claude-3-sonnet-20240229': 'Claude 3 Sonnet - Cân bằng',
    'claude-3-opus-20240229': 'Claude 3 Opus - Chất lượng cao nhất',
    'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet - Phiên bản mới nhất',
    
    # GitHub Copilot models (requires OpenAI API key)
    'gpt-4': 'GitHub Copilot với GPT-4 - Chất lượng cao (Cần OpenAI API key)',
    'gpt-3.5-turbo': 'GitHub Copilot với GPT-3.5 - Nhanh, hiệu quả (Cần OpenAI API key)',
    'copilot-codex': 'GitHub Copilot Codex - Chuyên về code và ngôn ngữ (Cần OpenAI API key)'
}

def get_models_for_provider(provider: str) -> list:
    """Lấy danh sách models cho provider cụ thể"""
    return PROVIDER_MODELS.get(provider, ['auto'])

def get_model_description(model: str) -> str:
    """Lấy mô tả cho model cụ thể"""
    return MODEL_DESCRIPTIONS.get(model, 'Model tùy chỉnh')

def get_default_model(provider: str) -> str:
    """Lấy model mặc định cho provider"""
    models = get_models_for_provider(provider)
    return models[0] if models else 'auto'
