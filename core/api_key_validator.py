"""
API Key Validator - Kiểm tra tính hợp lệ và hoạt động của API keys
"""

import re
import requests
import time
from typing import Tuple, Optional
from enum import Enum
from core.i18n import _

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
            return False, _('api_key_empty')
        
        api_key = api_key.strip()
        
        # Format validation cho từng provider
        if provider == 'gemini':
            if not api_key.startswith('AIza'):
                return False, _('gemini_key_format')
            if len(api_key) < 30:
                return False, _('gemini_key_short')
            if not re.match(r'^[A-Za-z0-9_-]+$', api_key):
                return False, _('gemini_key_invalid_chars')
                
        elif provider == 'chatgpt':
            if not api_key.startswith('sk-'):
                return False, _('openai_key_format')
            if len(api_key) < 40:
                return False, _('openai_key_short')
            if not re.match(r'^sk-[A-Za-z0-9]+$', api_key):
                return False, _('openai_key_invalid_chars')
                
        elif provider == 'deepseek':
            if not api_key.startswith('sk-'):
                return False, _('deepseek_key_format')
            if len(api_key) < 40:
                return False, _('deepseek_key_short')
            if not re.match(r'^sk-[A-Za-z0-9]+$', api_key):
                return False, _('deepseek_key_invalid_chars')
                
        elif provider == 'claude':
            if not api_key.startswith('sk-ant-'):
                return False, _('claude_key_format')
            if len(api_key) < 50:
                return False, _('claude_key_short')
            if not re.match(r'^sk-ant-[A-Za-z0-9_-]+$', api_key):
                return False, _('claude_key_invalid_chars')
                
        elif provider == 'copilot':
            # GitHub Copilot chỉ hỗ trợ OpenAI API keys (GitHub tokens không dùng được cho API calls)
            if not api_key.startswith('sk-'):
                return False, _('copilot_key_format')
            if len(api_key) < 40:
                return False, _('openai_key_short')
            if not re.match(r'^sk-[A-Za-z0-9]+$', api_key):
                return False, _('openai_key_invalid_chars')
        else:
            return False, _('provider_not_supported_validator').format(provider=provider)
        
        return True, _('api_key_format_valid')
    
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
                return ValidationResult.SUCCESS, _('gemini_working').format(model=model_name)
            else:
                return ValidationResult.PROVIDER_ERROR, _('gemini_empty_response')
                
        except ImportError:
            return ValidationResult.PROVIDER_ERROR, _('gemini_missing_library')
        except Exception as e:
            error_str = str(e).lower()
            if "api key not valid" in error_str or "invalid api key" in error_str:
                return ValidationResult.INVALID_KEY, _('gemini_invalid_key')
            elif "quota" in error_str or "429" in error_str:
                return ValidationResult.QUOTA_EXCEEDED, _('gemini_quota_exceeded')
            elif "timeout" in error_str:
                return ValidationResult.TIMEOUT, _('gemini_timeout')
            elif "network" in error_str or "connection" in error_str:
                return ValidationResult.NETWORK_ERROR, _('network_error')
            else:
                return ValidationResult.PROVIDER_ERROR, _('gemini_error').format(error=str(e))
    
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
                return ValidationResult.SUCCESS, _('openai_working').format(model=model_name)
            elif response.status_code == 401:
                return ValidationResult.INVALID_KEY, _('openai_invalid_key')
            elif response.status_code == 429:
                return ValidationResult.QUOTA_EXCEEDED, _('openai_rate_limit')
            elif response.status_code == 402:
                return ValidationResult.QUOTA_EXCEEDED, _('openai_no_credit')
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                return ValidationResult.PROVIDER_ERROR, _('openai_error').format(status=response.status_code, error=error_msg)
                
        except requests.exceptions.Timeout:
            return ValidationResult.TIMEOUT, _('openai_timeout')
        except requests.exceptions.ConnectionError:
            return ValidationResult.NETWORK_ERROR, _('network_error')
        except Exception as e:
            return ValidationResult.PROVIDER_ERROR, _('openai_error').format(status="", error=str(e))
    
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
                return ValidationResult.SUCCESS, _('deepseek_working').format(model=model_name)
            elif response.status_code == 401:
                return ValidationResult.INVALID_KEY, _('deepseek_invalid_key')
            elif response.status_code == 402:
                return ValidationResult.QUOTA_EXCEEDED, _('deepseek_no_balance')
            elif response.status_code == 429:
                return ValidationResult.QUOTA_EXCEEDED, _('deepseek_rate_limit')
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                return ValidationResult.PROVIDER_ERROR, _('deepseek_error').format(status=response.status_code, error=error_msg)
                
        except requests.exceptions.Timeout:
            return ValidationResult.TIMEOUT, _('deepseek_timeout')
        except requests.exceptions.ConnectionError:
            return ValidationResult.NETWORK_ERROR, _('network_error')
        except Exception as e:
            return ValidationResult.PROVIDER_ERROR, _('deepseek_error').format(status="", error=str(e))
    
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
                return ValidationResult.SUCCESS, _('claude_working').format(model=model_name)
            elif response.status_code == 401:
                return ValidationResult.INVALID_KEY, _('claude_invalid_key')
            elif response.status_code == 429:
                return ValidationResult.QUOTA_EXCEEDED, _('claude_rate_limit')
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                return ValidationResult.PROVIDER_ERROR, _('claude_error').format(status=response.status_code, error=error_msg)
                
        except requests.exceptions.Timeout:
            return ValidationResult.TIMEOUT, _('claude_timeout')
        except requests.exceptions.ConnectionError:
            return ValidationResult.NETWORK_ERROR, _('network_error')
        except Exception as e:
            return ValidationResult.PROVIDER_ERROR, _('claude_error').format(status="", error=str(e))
    
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
                return ValidationResult.SUCCESS, _('copilot_working').format(model=model_name)
            else:
                return ValidationResult.PROVIDER_ERROR, _('copilot_empty_response')
                
        except ImportError:
            return ValidationResult.PROVIDER_ERROR, _('copilot_missing_library')
        except Exception as e:
            error_msg = str(e).lower()
            if "invalid api key" in error_msg or "unauthorized" in error_msg:
                return ValidationResult.INVALID_KEY, _('copilot_invalid_key')
            elif "quota" in error_msg or "rate limit" in error_msg:
                return ValidationResult.QUOTA_EXCEEDED, _('copilot_quota_exceeded')
            elif "insufficient" in error_msg:
                return ValidationResult.QUOTA_EXCEEDED, _('copilot_no_credit')
            elif "timeout" in error_msg:
                return ValidationResult.TIMEOUT, _('copilot_timeout')
            else:
                return ValidationResult.PROVIDER_ERROR, _('copilot_error').format(error=str(e))
    
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
            return ValidationResult.PROVIDER_ERROR, _('provider_not_supported_validator').format(provider=provider)
        
        try:
            return test_func(api_key, model)
        except Exception as e:
            return ValidationResult.PROVIDER_ERROR, _('unexpected_error').format(error=str(e))

def get_validation_message(result: ValidationResult, detail_msg: str) -> dict:
    """Chuyển validation result thành message cho user"""
    
    if result == ValidationResult.SUCCESS:
        return {
            "type": "success",
            "title": _('validation_success_title'),
            "message": detail_msg,
            "allow_save": True
        }
    elif result == ValidationResult.INVALID_FORMAT:
        return {
            "type": "error",
            "title": _('validation_format_error_title'),
            "message": detail_msg + f"\n\n{_('validation_format_error_hint')}",
            "allow_save": False
        }
    elif result == ValidationResult.INVALID_KEY:
        return {
            "type": "error", 
            "title": _('validation_invalid_key_title'),
            "message": detail_msg + f"\n\n{_('validation_invalid_key_hint')}",
            "allow_save": False
        }
    elif result == ValidationResult.QUOTA_EXCEEDED:
        return {
            "type": "warning",
            "title": _('validation_quota_title'),
            "message": detail_msg + f"\n\n{_('validation_quota_hint')}",
            "allow_save": True  # Allow save, user có thể nạp tiền sau
        }
    elif result == ValidationResult.NETWORK_ERROR:
        return {
            "type": "warning",
            "title": _('validation_network_title'),
            "message": detail_msg + f"\n\n{_('validation_network_hint')}",
            "allow_save": True  # Allow save, có thể do mạng tạm thời
        }
    elif result == ValidationResult.TIMEOUT:
        return {
            "type": "warning",
            "title": _('validation_timeout_title'),
            "message": detail_msg + f"\n\n{_('validation_timeout_hint')}",
            "allow_save": True  # Allow save, có thể do server tạm thời chậm
        }
    else:  # PROVIDER_ERROR
        return {
            "type": "error",
            "title": _('validation_provider_error_title'),
            "message": detail_msg + f"\n\n{_('validation_provider_error_hint')}",
            "allow_save": False
        }
