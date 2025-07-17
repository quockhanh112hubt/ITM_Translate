"""
API Key Validator - Kiểm tra tính hợp lệ và hoạt động của API keys
"""

import re
import requests
import time
from typing import Tuple, Optional
from enum import Enum

class ValidationResult(Enum):
    SUCCESS = "success"
    INVALID_FORMAT = "invalid_format"
    INVALID_KEY = "invalid_key"
    QUOTA_EXCEEDED = "quota_exceeded"
    NETWORK_ERROR = "network_error"
    PROVIDER_ERROR = "provider_error"
    TIMEOUT = "timeout"

class APIKeyValidator:
    """Validate API keys cho các providers khác nhau"""
    
    @staticmethod
    def validate_format(provider: str, api_key: str) -> Tuple[bool, str]:
        """Kiểm tra định dạng cơ bản của API key"""
        
        if not api_key or not api_key.strip():
            return False, "API key không được để trống"
        
        api_key = api_key.strip()
        
        # Format validation cho từng provider
        if provider == 'gemini':
            if not api_key.startswith('AIza'):
                return False, "Gemini API key phải bắt đầu bằng 'AIza'"
            if len(api_key) < 30:
                return False, "Gemini API key quá ngắn (phải >= 30 ký tự)"
            if not re.match(r'^[A-Za-z0-9_-]+$', api_key):
                return False, "Gemini API key chứa ký tự không hợp lệ"
                
        elif provider == 'chatgpt':
            if not api_key.startswith('sk-'):
                return False, "OpenAI API key phải bắt đầu bằng 'sk-'"
            if len(api_key) < 40:
                return False, "OpenAI API key quá ngắn (phải >= 40 ký tự)"
            if not re.match(r'^sk-[A-Za-z0-9]+$', api_key):
                return False, "OpenAI API key chứa ký tự không hợp lệ"
                
        elif provider == 'deepseek':
            if not api_key.startswith('sk-'):
                return False, "DeepSeek API key phải bắt đầu bằng 'sk-'"
            if len(api_key) < 40:
                return False, "DeepSeek API key quá ngắn (phải >= 40 ký tự)"
            if not re.match(r'^sk-[A-Za-z0-9]+$', api_key):
                return False, "DeepSeek API key chứa ký tự không hợp lệ"
                
        elif provider == 'claude':
            if not api_key.startswith('sk-ant-'):
                return False, "Claude API key phải bắt đầu bằng 'sk-ant-'"
            if len(api_key) < 50:
                return False, "Claude API key quá ngắn (phải >= 50 ký tự)"
            if not re.match(r'^sk-ant-[A-Za-z0-9_-]+$', api_key):
                return False, "Claude API key chứa ký tự không hợp lệ"
                
        elif provider == 'copilot':
            # GitHub Copilot chỉ hỗ trợ OpenAI API keys (GitHub tokens không dùng được cho API calls)
            if not api_key.startswith('sk-'):
                return False, "GitHub Copilot chỉ hỗ trợ OpenAI API key (bắt đầu bằng 'sk-'). GitHub tokens không dùng được cho API calls."
            if len(api_key) < 40:
                return False, "OpenAI API key quá ngắn (phải >= 40 ký tự)"
            if not re.match(r'^sk-[A-Za-z0-9]+$', api_key):
                return False, "OpenAI API key chứa ký tự không hợp lệ"
        else:
            return False, f"Provider '{provider}' không được hỗ trợ"
        
        return True, "Định dạng API key hợp lệ"
    
    @staticmethod
    def test_gemini_key(api_key: str, model: str = "auto") -> Tuple[ValidationResult, str]:
        """Test Gemini API key"""
        try:
            import google.generativeai as genai
            
            # Configure với test key
            genai.configure(api_key=api_key)
            
            # Chọn model
            if model == "auto":
                model_name = "gemini-1.5-flash"
            else:
                model_name = model
            
            # Test với request nhỏ
            test_model = genai.GenerativeModel(model_name)
            response = test_model.generate_content(
                "Test", 
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=10,
                    temperature=0
                )
            )
            
            if response and response.text:
                return ValidationResult.SUCCESS, f"✅ Gemini API key hoạt động tốt (model: {model_name})"
            else:
                return ValidationResult.PROVIDER_ERROR, "❌ Gemini API trả về response rỗng"
                
        except ImportError:
            return ValidationResult.PROVIDER_ERROR, "❌ Thiếu thư viện google-generativeai"
        except Exception as e:
            error_str = str(e).lower()
            if "api key not valid" in error_str or "invalid api key" in error_str:
                return ValidationResult.INVALID_KEY, "❌ Gemini API key không hợp lệ"
            elif "quota" in error_str or "429" in error_str:
                return ValidationResult.QUOTA_EXCEEDED, "❌ Gemini API: Vượt quá quota/rate limit"
            elif "timeout" in error_str:
                return ValidationResult.TIMEOUT, "❌ Gemini API: Timeout - thử lại sau"
            elif "network" in error_str or "connection" in error_str:
                return ValidationResult.NETWORK_ERROR, "❌ Lỗi kết nối mạng"
            else:
                return ValidationResult.PROVIDER_ERROR, f"❌ Gemini API error: {str(e)}"
    
    @staticmethod
    def test_openai_key(api_key: str, model: str = "auto") -> Tuple[ValidationResult, str]:
        """Test OpenAI API key"""
        try:
            # Chọn model
            if model == "auto":
                model_name = "gpt-3.5-turbo"
            else:
                model_name = model
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 5,
                "temperature": 0
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return ValidationResult.SUCCESS, f"✅ OpenAI API key hoạt động tốt (model: {model_name})"
            elif response.status_code == 401:
                return ValidationResult.INVALID_KEY, "❌ OpenAI API key không hợp lệ"
            elif response.status_code == 429:
                return ValidationResult.QUOTA_EXCEEDED, "❌ OpenAI API: Vượt quá rate limit"
            elif response.status_code == 402:
                return ValidationResult.QUOTA_EXCEEDED, "❌ OpenAI API: Hết credit/quota"
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                return ValidationResult.PROVIDER_ERROR, f"❌ OpenAI API error ({response.status_code}): {error_msg}"
                
        except requests.exceptions.Timeout:
            return ValidationResult.TIMEOUT, "❌ OpenAI API: Timeout - thử lại sau"
        except requests.exceptions.ConnectionError:
            return ValidationResult.NETWORK_ERROR, "❌ Lỗi kết nối mạng"
        except Exception as e:
            return ValidationResult.PROVIDER_ERROR, f"❌ OpenAI API error: {str(e)}"
    
    @staticmethod
    def test_deepseek_key(api_key: str, model: str = "auto") -> Tuple[ValidationResult, str]:
        """Test DeepSeek API key"""
        try:
            # Chọn model
            if model == "auto":
                model_name = "deepseek-chat"
            else:
                model_name = model
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 5,
                "temperature": 0
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return ValidationResult.SUCCESS, f"✅ DeepSeek API key hoạt động tốt (model: {model_name})"
            elif response.status_code == 401:
                return ValidationResult.INVALID_KEY, "❌ DeepSeek API key không hợp lệ"
            elif response.status_code == 402:
                return ValidationResult.QUOTA_EXCEEDED, "❌ DeepSeek API: Insufficient Balance (Hết tiền)"
            elif response.status_code == 429:
                return ValidationResult.QUOTA_EXCEEDED, "❌ DeepSeek API: Vượt quá rate limit"
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                return ValidationResult.PROVIDER_ERROR, f"❌ DeepSeek API error ({response.status_code}): {error_msg}"
                
        except requests.exceptions.Timeout:
            return ValidationResult.TIMEOUT, "❌ DeepSeek API: Timeout - thử lại sau"
        except requests.exceptions.ConnectionError:
            return ValidationResult.NETWORK_ERROR, "❌ Lỗi kết nối mạng"
        except Exception as e:
            return ValidationResult.PROVIDER_ERROR, f"❌ DeepSeek API error: {str(e)}"
    
    @staticmethod
    def test_claude_key(api_key: str, model: str = "auto") -> Tuple[ValidationResult, str]:
        """Test Claude API key"""
        try:
            # Chọn model
            if model == "auto":
                model_name = "claude-3-haiku-20240307"
            else:
                model_name = model
            
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                "model": model_name,
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "Test"}]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return ValidationResult.SUCCESS, f"✅ Claude API key hoạt động tốt (model: {model_name})"
            elif response.status_code == 401:
                return ValidationResult.INVALID_KEY, "❌ Claude API key không hợp lệ"
            elif response.status_code == 429:
                return ValidationResult.QUOTA_EXCEEDED, "❌ Claude API: Vượt quá rate limit"
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                return ValidationResult.PROVIDER_ERROR, f"❌ Claude API error ({response.status_code}): {error_msg}"
                
        except requests.exceptions.Timeout:
            return ValidationResult.TIMEOUT, "❌ Claude API: Timeout - thử lại sau"
        except requests.exceptions.ConnectionError:
            return ValidationResult.NETWORK_ERROR, "❌ Lỗi kết nối mạng"
        except Exception as e:
            return ValidationResult.PROVIDER_ERROR, f"❌ Claude API error: {str(e)}"
    
    @staticmethod
    def test_copilot_key(api_key: str, model: str = "auto") -> Tuple[ValidationResult, str]:
        """Test GitHub Copilot API key"""
        try:
            import openai
            
            # Chọn model
            if model == "auto":
                model_name = "gpt-4"
            else:
                model_name = model
            
            # GitHub Copilot có thể sử dụng OpenAI API hoặc GitHub API
            # Thử với OpenAI API endpoint trước
            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.openai.com/v1"
            )
            
            # Test với request nhỏ
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are GitHub Copilot."},
                    {"role": "user", "content": "Test"}
                ],
                max_tokens=5,
                temperature=0
            )
            
            if response and response.choices and len(response.choices) > 0:
                return ValidationResult.SUCCESS, f"✅ GitHub Copilot API key hoạt động tốt (model: {model_name})"
            else:
                return ValidationResult.PROVIDER_ERROR, "❌ GitHub Copilot API trả về response rỗng"
                
        except ImportError:
            return ValidationResult.PROVIDER_ERROR, "❌ Thiếu thư viện openai (pip install openai)"
        except Exception as e:
            error_msg = str(e).lower()
            if "invalid api key" in error_msg or "unauthorized" in error_msg:
                return ValidationResult.INVALID_KEY, "❌ GitHub Copilot API key không hợp lệ"
            elif "quota" in error_msg or "rate limit" in error_msg:
                return ValidationResult.QUOTA_EXCEEDED, "❌ GitHub Copilot: Vượt quá quota hoặc rate limit"
            elif "insufficient" in error_msg:
                return ValidationResult.QUOTA_EXCEEDED, "❌ GitHub Copilot: Hết credit hoặc quota"
            elif "timeout" in error_msg:
                return ValidationResult.TIMEOUT, "❌ GitHub Copilot API: Timeout - thử lại sau"
            else:
                return ValidationResult.PROVIDER_ERROR, f"❌ GitHub Copilot API error: {str(e)}"
    
    @classmethod
    def validate_api_key(cls, provider: str, api_key: str, model: str = "auto") -> Tuple[ValidationResult, str]:
        """
        Validate API key hoàn chỉnh: format + connection test
        
        Returns:
            Tuple[ValidationResult, str]: (result_enum, user_message)
        """
        
        # Step 1: Kiểm tra định dạng
        format_valid, format_msg = cls.validate_format(provider, api_key)
        if not format_valid:
            return ValidationResult.INVALID_FORMAT, format_msg
        
        # Step 2: Test connection thực tế
        test_functions = {
            'gemini': cls.test_gemini_key,
            'chatgpt': cls.test_openai_key,
            'deepseek': cls.test_deepseek_key,
            'claude': cls.test_claude_key,
            'copilot': cls.test_copilot_key
        }
        
        test_func = test_functions.get(provider)
        if not test_func:
            return ValidationResult.PROVIDER_ERROR, f"Provider '{provider}' không được hỗ trợ"
        
        try:
            return test_func(api_key, model)
        except Exception as e:
            return ValidationResult.PROVIDER_ERROR, f"❌ Lỗi không mong đợi: {str(e)}"

def get_validation_message(result: ValidationResult, detail_msg: str) -> dict:
    """Chuyển validation result thành message cho user"""
    
    if result == ValidationResult.SUCCESS:
        return {
            "type": "success",
            "title": "✅ API Key hợp lệ!",
            "message": detail_msg,
            "allow_save": True
        }
    elif result == ValidationResult.INVALID_FORMAT:
        return {
            "type": "error",
            "title": "❌ Định dạng API Key không đúng",
            "message": detail_msg + "\n\n💡 Kiểm tra lại API key từ provider",
            "allow_save": False
        }
    elif result == ValidationResult.INVALID_KEY:
        return {
            "type": "error", 
            "title": "❌ API Key không hợp lệ",
            "message": detail_msg + "\n\n💡 Tạo API key mới từ provider",
            "allow_save": False
        }
    elif result == ValidationResult.QUOTA_EXCEEDED:
        return {
            "type": "warning",
            "title": "⚠️ Vượt quá giới hạn",
            "message": detail_msg + "\n\n💡 API key hợp lệ nhưng hết quota/credit",
            "allow_save": True  # Allow save, user có thể nạp tiền sau
        }
    elif result == ValidationResult.NETWORK_ERROR:
        return {
            "type": "warning",
            "title": "🌐 Lỗi kết nối",
            "message": detail_msg + "\n\n💡 Kiểm tra internet và thử lại",
            "allow_save": True  # Allow save, có thể do mạng tạm thời
        }
    elif result == ValidationResult.TIMEOUT:
        return {
            "type": "warning",
            "title": "⏱️ Timeout",
            "message": detail_msg + "\n\n💡 Server chậm, thử lại sau",
            "allow_save": True  # Allow save, có thể do server tạm thời chậm
        }
    else:  # PROVIDER_ERROR
        return {
            "type": "error",
            "title": "❌ Lỗi Provider",
            "message": detail_msg + "\n\n💡 Liên hệ support nếu lỗi tiếp tục",
            "allow_save": False
        }
