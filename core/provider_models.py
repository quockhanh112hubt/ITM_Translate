"""
Provider Models Configuration - Định nghĩa các model có sẵn cho từng AI provider
"""

# Danh sách models cho từng provider
PROVIDER_MODELS = {
    'gemini': [
        'auto',
        'gemini-3.8-flash',
        'gemini-3.7-flash',
        'gemini-3.6-flash',
        'gemini-3.5-flash',
        'gemini-3.5-flash-lite',
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-2.5-flash-lite',
        'gemini-flash-latest',
        'gemini-pro-latest'
    ],
    'chatgpt': [
        'auto',
        'gpt-4.1-mini',
        'gpt-4.1-nano',
        'gpt-4.1',
        'gpt-4o-mini',
        'gpt-4o',
        'gpt-4-turbo',
        'gpt-4',
        'gpt-3.5-turbo'
    ],
    'groq': [
        'auto',
        'openai/gpt-oss-20b',
        'openai/gpt-oss-120b',
        'qwen/qwen3.8-27b'
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
    ],
    'google_translate': [
        'auto',
        'google-translate-v2',
        'google-translate-advanced'
    ]
}

# Model descriptions để hiển thị tooltip
MODEL_DESCRIPTIONS = {
    'auto': 'Select model for provider',
    
    # Gemini models
    'gemini-3.8-flash': 'Gemini 3.8 Flash - Recommended default model',
    'gemini-3.7-flash': 'Gemini 3.7 Flash',
    'gemini-3.6-flash': 'Gemini 3.6 Flash',
    'gemini-3.5-flash': 'Gemini 3.5 Flash',
    'gemini-3.5-flash-lite': 'Gemini 3.5 Flash-Lite - Fast, cost-efficient model',
    'gemini-2.5-flash': 'Gemini 2.5 Flash - Model mới nhất (có thể bị safety block)',
    'gemini-2.5-pro': 'Gemini 2.5 Pro - Chất lượng cao nhất (có thể bị safety block)',
    'gemini-2.5-flash-lite': 'Gemini 2.5 Flash-Lite - Fast, cost-efficient model',
    'gemini-flash-latest': 'Gemini Flash Latest - Luôn sử dụng phiên bản Flash mới nhất',
    'gemini-pro-latest': 'Gemini Pro Latest - Luôn sử dụng phiên bản Pro mới nhất',
    
    # ChatGPT models
    'gpt-4.1-mini': 'GPT-4.1 mini - Recommended fast ChatGPT model',
    'gpt-4.1-nano': 'GPT-4.1 nano - Small, fast model',
    'gpt-4.1': 'GPT-4.1 - Higher capability model',
    'gpt-4o-mini': 'GPT-4o Mini - Model mới nhất, siêu nhanh và hiệu quả (Khuyến nghị)',
    'gpt-4o': 'GPT-4o - Phiên bản tối ưu mới nhất',
    'gpt-4-turbo': 'GPT-4 Turbo - Cân bằng tốc độ và chất lượng',
    'gpt-4': 'GPT-4 - Chất lượng cao, giá đắt',
    'gpt-3.5-turbo': 'GPT-3.5 Turbo - Nhanh, giá rẻ',
    'openai/gpt-oss-20b': 'GPT OSS 20B on Groq - Fast default model',
    'openai/gpt-oss-120b': 'GPT OSS 120B on Groq - Higher capability',
    'qwen/qwen3.8-27b': 'Qwen 3.8 27B on Groq',
    
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
    'copilot-codex': 'GitHub Copilot Codex - Chuyên về code và ngôn ngữ (Cần OpenAI API key)',
    
    # Google Cloud Translate models
    'google-translate-v2': 'Google Translate v2 - Dịch thuật chính thức của Google (Khuyến nghị)',
    'google-translate-advanced': 'Google Translate Advanced - Phiên bản nâng cao với neural networks'
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
