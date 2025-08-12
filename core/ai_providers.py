"""
AI Providers - Hỗ trợ multiple AI APIs
"""
import google.generativeai as genai
import requests
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from .api_key_manager import AIProvider, APIKeyInfo
from .ssl_bypass import setup_ssl_bypass

# Setup SSL bypass globally for all providers
setup_ssl_bypass()

# Optional imports with fallbacks
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not available. ChatGPT provider will be disabled.")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: Anthropic library not available. Claude provider will be disabled.")

class BaseAIProvider(ABC):
    """Base class cho tất cả AI providers"""
    
    def __init__(self, key_info: APIKeyInfo):
        self.key_info = key_info
        self.api_key = key_info.key
        self.model = key_info.model if key_info.model != "auto" else self.get_default_model()
    
    @abstractmethod
    def get_default_model(self) -> str:
        """Lấy model mặc định cho provider"""
        pass
    
    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        """Test kết nối với provider"""
        pass
    
    @abstractmethod
    def detect_language(self, text: str) -> Optional[str]:
        """Detect ngôn ngữ của text"""
        pass
    
    @abstractmethod
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Dịch text"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Lấy tên provider"""
        pass

class GeminiProvider(BaseAIProvider):
    """Google Gemini AI Provider"""
    
    def __init__(self, key_info: APIKeyInfo):
        super().__init__(key_info)
        # Configure SSL bypass for Gemini
        self._setup_gemini_ssl_bypass()
    
    def _setup_gemini_ssl_bypass(self):
        """Setup SSL bypass specifically for Gemini in corporate networks"""
        try:
            import ssl
            import os
            
            # Set environment variables for Google API client
            os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH:ECDHE:!DH:!aNULL'
            os.environ['GOOGLE_APPLICATION_CREDENTIALS_UNSAFE_SKIP_VERIFICATION'] = 'true'
            
            # Disable SSL verification globally for requests used by google-generativeai
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            class SSLBypassAdapter(HTTPAdapter):
                def init_poolmanager(self, *args, **kwargs):
                    kwargs['ssl_context'] = ssl._create_unverified_context()
                    kwargs['cert_reqs'] = 'CERT_NONE'
                    return super().init_poolmanager(*args, **kwargs)
            
            # Create a session with SSL bypass
            session = requests.Session()
            session.mount('https://', SSLBypassAdapter())
            
            # Monkey patch requests.get for google-generativeai
            original_get = requests.get
            original_post = requests.post
            
            def patched_get(*args, **kwargs):
                kwargs['verify'] = False
                return original_get(*args, **kwargs)
            
            def patched_post(*args, **kwargs):
                kwargs['verify'] = False
                return original_post(*args, **kwargs)
            
            requests.get = patched_get
            requests.post = patched_post
            
            print("🔓 [SSL] Gemini SSL bypass configured for corporate networks")
            
        except Exception as e:
            print(f"⚠️ [SSL] Warning: Could not setup Gemini SSL bypass: {e}")
    
    def get_default_model(self) -> str:
        return "gemini-1.5-flash"  # Changed from gemini-2.0-flash-exp to stable version
    
    def get_provider_name(self) -> str:
        return "Gemini"
    
    def test_connection(self) -> tuple[bool, str]:
        """Test kết nối với Gemini API"""
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            
            # Test với một prompt đơn giản
            response = model.generate_content("Hello")
            if response and response.text:
                return True, "✅ Gemini connection successful"
            else:
                return False, "❌ Gemini: No response received"
                
        except Exception as e:
            error_msg = str(e).lower()
            if "ssl" in error_msg or "certificate" in error_msg or "verify" in error_msg:
                return False, f"❌ Gemini SSL Error: {e} (Corporate network blocking connection)"
            elif "api_key" in error_msg or "401" in error_msg:
                return False, f"❌ Gemini API Key Error: {e}"
            elif "quota" in error_msg or "429" in error_msg:
                return False, f"❌ Gemini Quota Error: {e}"
            else:
                return False, f"❌ Gemini Connection Error: {e}"
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect language using Gemini"""
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            
            prompt = f"""What language is the following text used?.
            Follow these instructions exactly:
            - Analyze the text and determine the primary language used. If the message is written mostly in one language but contains words or short phrases from others (e.g., "OK tôi sẽ check cái đó"), treat the main language as the dominant one.
            - If the dominant language cannot be determined, return "Mixed".
            - Do not return any explanations or additional text, just the language name

            Text:
            {text}
            """
            
            response = model.generate_content(prompt)
            detected_lang = response.text.strip()
            detected_lang = detected_lang.replace('"', '').replace("'", "").strip()
            return detected_lang
        except Exception as e:
            print(f"Gemini language detection error: {e}")
            return None
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using Gemini"""
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            
            if source_lang and source_lang.lower() == "mixed":
                prompt = f"""Translate the following mixed-language text to {target_lang}. Keep the overall meaning and context intact:

Text to translate:
{text}

Target language: {target_lang}

Instructions:
- Translate naturally while preserving the intended meaning
- Maintain any technical terms or proper nouns appropriately
- If some parts are already in the target language, keep them as is
- Return only the translated text without explanations"""
            else:
                prompt = f"""Translate the following text from {source_lang} to {target_lang}:

Text to translate:
{text}

Instructions:
- Provide accurate and natural translation
- Maintain the tone and context of the original text
- For technical terms, use appropriate terminology in the target language
- Return only the translated text without explanations"""
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Gemini translation error: {e}")
    
    def generate_text(self, prompt: str) -> str:
        """Generate text using Gemini for unified smart translation"""
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Gemini text generation error: {e}")

class ChatGPTProvider(BaseAIProvider):
    """OpenAI ChatGPT Provider"""
    
    def __init__(self, key_info: APIKeyInfo):
        super().__init__(key_info)
        if not OPENAI_AVAILABLE:
            raise Exception("OpenAI library not available")
        
        # Use OpenAI v1.x client with optimized timeout and SSL bypass for corporate networks
        import httpx
        self.client = openai.OpenAI(
            api_key=self.api_key,
            timeout=15.0,  # Reduced timeout for faster response
            http_client=httpx.Client(verify=False)  # Disable SSL verification for corporate networks
        )
    
    def get_default_model(self) -> str:
        return "gpt-4.1-mini"  # Latest and fastest model
    
    def get_provider_name(self) -> str:
        return "ChatGPT"
    
    def test_connection(self) -> tuple[bool, str]:
        """Test kết nối với ChatGPT API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            if response and response.choices:
                return True, "✅ ChatGPT connection successful"
            else:
                return False, "❌ ChatGPT: No response received"
                
        except openai.AuthenticationError as e:
            return False, f"❌ ChatGPT API Key Error: {e}"
        except openai.RateLimitError as e:
            return False, f"❌ ChatGPT Quota Error: {e}"
        except openai.APIConnectionError as e:
            return False, f"❌ ChatGPT Connection Error: {e}"
        except Exception as e:
            error_msg = str(e).lower()
            if "ssl" in error_msg or "certificate" in error_msg:
                return False, f"❌ ChatGPT SSL Error: {e}"
            else:
                return False, f"❌ ChatGPT Error: {e}"
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect language using ChatGPT - Optimized for speed"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Detect language. Reply with language name only."},
                    {"role": "user", "content": f"Language: {text[:200]}"}  # Limit text length
                ],
                max_tokens=10,  # Very small for language detection
                temperature=0
            )
            
            detected_lang = response.choices[0].message.content.strip()
            detected_lang = detected_lang.replace('"', '').replace("'", "").strip()
            return detected_lang
        except openai.AuthenticationError as e:
            print(f"ChatGPT authentication error: {e}")
            return None
        except openai.RateLimitError as e:
            print(f"ChatGPT rate limit/quota error: {e}")
            return None
        except Exception as e:
            print(f"ChatGPT language detection error: {e}")
            return None
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using ChatGPT - Optimized for speed"""
        try:
            if source_lang and source_lang.lower() == "mixed":
                system_prompt = f"Translate mixed text to {target_lang}. Return only translation."
            else:
                system_prompt = f"Translate from {source_lang} to {target_lang}. Return only translation."
            
            # Calculate optimal max_tokens based on input length
            estimated_tokens = min(len(text) * 2, 1500)  # Reduced from 2000
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=estimated_tokens,
                temperature=0.1  # Reduced for faster, more consistent response
            )
            
            return response.choices[0].message.content.strip()
            
        except openai.AuthenticationError as e:
            raise Exception("401_UNAUTHORIZED")
        except openai.RateLimitError as e:
            error_str = str(e).lower()
            if "insufficient_quota" in error_str or "exceed" in error_str:
                raise Exception("402_INSUFFICIENT_BALANCE")
            else:
                raise Exception("429_QUOTA_EXCEEDED")
        except openai.BadRequestError as e:
            raise Exception("400_INVALID_KEY")
        except openai.APIConnectionError as e:
            raise Exception(f"Connection error: {e}")
        except Exception as e:
            raise Exception(f"ChatGPT translation error: {e}")
    
    def generate_text(self, prompt: str) -> str:
        """Generate text using ChatGPT for unified smart translation - Optimized for speed"""
        try:
            # Calculate optimal max_tokens
            estimated_tokens = min(len(prompt) * 1.5, 1500)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=int(estimated_tokens),
                temperature=0.1  # Lower temperature for faster response
            )
            
            return response.choices[0].message.content.strip()
            
        except openai.AuthenticationError as e:
            raise Exception("401_UNAUTHORIZED")
        except openai.RateLimitError as e:
            error_str = str(e).lower()
            if "insufficient_quota" in error_str or "exceed" in error_str:
                raise Exception("402_INSUFFICIENT_BALANCE")
            else:
                raise Exception("429_QUOTA_EXCEEDED")
        except openai.BadRequestError as e:
            raise Exception("400_INVALID_KEY")
        except openai.APIConnectionError as e:
            raise Exception(f"Connection error: {e}")
        except Exception as e:
            raise Exception(f"ChatGPT text generation error: {e}")

class DeepSeekProvider(BaseAIProvider):
    """DeepSeek AI Provider"""
    
    def get_default_model(self) -> str:
        return "deepseek-chat"
    
    def get_provider_name(self) -> str:
        return "DeepSeek"
    
    def test_connection(self) -> tuple[bool, str]:
        """Test kết nối với DeepSeek API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "max_tokens": 5,
                "temperature": 0
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=10,
                verify=False  # Disable SSL verification for corporate networks
            )
            
            if response.status_code == 200:
                return True, "✅ DeepSeek connection successful"
            elif response.status_code == 402:
                return False, "❌ DeepSeek: Insufficient Balance (Hết tiền)"
            elif response.status_code == 401:
                return False, "❌ DeepSeek: Invalid API Key"
            elif response.status_code == 429:
                return False, "❌ DeepSeek: Rate limit exceeded"
            else:
                return False, f"❌ DeepSeek API error: {response.status_code}"
                
        except Exception as e:
            error_msg = str(e).lower()
            if "ssl" in error_msg or "certificate" in error_msg:
                return False, f"❌ DeepSeek SSL Error: {e}"
            else:
                return False, f"❌ DeepSeek Connection Error: {e}"
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect language using DeepSeek"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a language detection expert. Respond only with the name of the primary language used in the text. If mixed languages, respond 'Mixed'."},
                    {"role": "user", "content": f"What language is this text: {text}"}
                ],
                "max_tokens": 50,
                "temperature": 0
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30,
                verify=False  # Disable SSL verification for corporate networks
            )
            
            if response.status_code == 200:
                result = response.json()
                detected_lang = result['choices'][0]['message']['content'].strip()
                detected_lang = detected_lang.replace('"', '').replace("'", "").strip()
                return detected_lang
            elif response.status_code == 402:
                print("❌ DeepSeek API: Insufficient Balance (Hết tiền) - Cần nạp thêm credit")
                print("   💳 Nạp tiền tại: https://platform.deepseek.com/")
                return None
            elif response.status_code == 401:
                print("❌ DeepSeek API: Invalid API Key")
                return None
            else:
                print(f"❌ DeepSeek API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"DeepSeek language detection error: {e}")
            return None
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using DeepSeek"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            if source_lang and source_lang.lower() == "mixed":
                system_prompt = f"You are a professional translator. Translate the following mixed-language text to {target_lang}. Maintain meaning and context. Return only the translation."
            else:
                system_prompt = f"You are a professional translator. Translate from {source_lang} to {target_lang}. Provide accurate, natural translation. Return only the translation."
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30,
                verify=False  # Disable SSL verification for corporate networks
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            elif response.status_code == 402:
                error_msg = "DeepSeek API: Insufficient Balance (Hết tiền) - Cần nạp thêm credit tại https://platform.deepseek.com/"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
            elif response.status_code == 401:
                error_msg = "DeepSeek API: Invalid API Key"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
            elif response.status_code == 429:
                error_msg = "DeepSeek API: Rate limit exceeded - Vượt quá giới hạn request"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
            else:
                error_msg = f"DeepSeek API error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
                
        except Exception as e:
            raise Exception(f"DeepSeek translation error: {e}")
    
    def generate_text(self, prompt: str) -> str:
        """Generate text using DeepSeek for unified smart translation"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30,
                verify=False  # Disable SSL verification for corporate networks
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            elif response.status_code == 402:
                raise Exception("402_INSUFFICIENT_BALANCE")
            elif response.status_code == 401:
                raise Exception("401_UNAUTHORIZED")
            elif response.status_code == 429:
                raise Exception("429_QUOTA_EXCEEDED")
            else:
                raise Exception(f"DeepSeek API error: {response.status_code}")
                
        except Exception as e:
            if str(e).startswith(("402_", "401_", "429_")):
                raise e
            raise Exception(f"DeepSeek text generation error: {e}")

class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude Provider"""
    
    def get_default_model(self) -> str:
        return "claude-3-haiku-20240307"
    
    def get_provider_name(self) -> str:
        return "Claude"
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect language using Claude"""
        if not ANTHROPIC_AVAILABLE:
            raise Exception("Anthropic library not available")
            
        try:
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                "model": self.model,
                "max_tokens": 50,
                "messages": [
                    {"role": "user", "content": f"What language is this text (respond with language name only, or 'Mixed' if multiple languages): {text}"}
                ]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=30,
                verify=False  # Disable SSL verification for corporate networks
            )
            
            if response.status_code == 200:
                result = response.json()
                detected_lang = result['content'][0]['text'].strip()
                detected_lang = detected_lang.replace('"', '').replace("'", "").strip()
                return detected_lang
            else:
                print(f"Claude API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Claude language detection error: {e}")
            return None
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using Claude"""
        if not ANTHROPIC_AVAILABLE:
            raise Exception("Anthropic library not available")
            
        try:
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            if source_lang and source_lang.lower() == "mixed":
                prompt = f"Translate the following mixed-language text to {target_lang}. Maintain meaning and context. Return only the translation:\n\n{text}"
            else:
                prompt = f"Translate from {source_lang} to {target_lang}. Provide accurate, natural translation. Return only the translation:\n\n{text}"
            
            payload = {
                "model": self.model,
                "max_tokens": 2000,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=30,
                verify=False  # Disable SSL verification for corporate networks
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text'].strip()
            else:
                raise Exception(f"Claude API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Claude translation error: {e}")

class CopilotProvider(BaseAIProvider):
    """GitHub Copilot Provider - Uses OpenAI API with Copilot branding"""
    
    def __init__(self, key_info: APIKeyInfo):
        super().__init__(key_info)
        if not OPENAI_AVAILABLE:
            raise ValueError("GitHub Copilot provider requires 'openai' library. Run: pip install openai")
        
        # Check if this is a GitHub token (not supported for API calls)
        if self.api_key.startswith('ghp_') or self.api_key.startswith('gho_'):
            raise ValueError(
                "GitHub Personal Access Tokens cannot be used for translation API calls. "
                "Please use an OpenAI API key instead. "
                "You can get one at: https://platform.openai.com/api-keys"
            )
        
        # GitHub Copilot provider uses OpenAI API with Copilot personality and SSL bypass
        import httpx
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.openai.com/v1",
            http_client=httpx.Client(verify=False)  # Disable SSL verification for corporate networks
        )
    
    def get_default_model(self) -> str:
        return "gpt-4"
    
    def detect_language(self, text: str) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are GitHub Copilot. Detect the language of the given text and return only the language code (e.g., 'en', 'vi', 'ja', 'ko', 'zh')."},
                    {"role": "user", "content": f"Detect language: {text}"}
                ],
                max_tokens=10,
                temperature=0
            )
            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            print(f"GitHub Copilot language detection error: {e}")
            return None
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        try:
            # Language mapping
            lang_map = {
                'en': 'English', 'vi': 'Vietnamese', 'ja': 'Japanese', 
                'ko': 'Korean', 'zh': 'Chinese', 'es': 'Spanish',
                'fr': 'French', 'de': 'German', 'ru': 'Russian',
                'th': 'Thai', 'ar': 'Arabic', 'hi': 'Hindi'
            }
            
            source_name = lang_map.get(source_lang, source_lang)
            target_name = lang_map.get(target_lang, target_lang)
            
            system_prompt = f"""You are GitHub Copilot, an AI coding assistant by GitHub and OpenAI. 
Your task is to translate text from {source_name} to {target_name}.
Provide only the translation, no explanations or additional text.
Maintain the original meaning and tone."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Translate to {target_name}: {text}"}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up common unwanted prefixes
            prefixes_to_remove = [
                f"Translation to {target_name}:",
                f"Translated to {target_name}:",
                "Translation:",
                "Here's the translation:",
                "The translation is:"
            ]
            
            for prefix in prefixes_to_remove:
                if result.lower().startswith(prefix.lower()):
                    result = result[len(prefix):].strip()
            
            return result
            
        except Exception as e:
            raise Exception(f"GitHub Copilot translation error: {e}")
    
    def get_provider_name(self) -> str:
        return "GitHub Copilot"

# Factory function để tạo provider instance
def create_ai_provider(key_info: APIKeyInfo) -> BaseAIProvider:
    """Factory function để tạo AI provider instance"""
    provider_map = {
        AIProvider.GEMINI: GeminiProvider,
        AIProvider.CHATGPT: ChatGPTProvider if OPENAI_AVAILABLE else None,
        AIProvider.DEEPSEEK: DeepSeekProvider,
        AIProvider.CLAUDE: ClaudeProvider if ANTHROPIC_AVAILABLE else None,
        AIProvider.COPILOT: CopilotProvider if OPENAI_AVAILABLE else None
    }
    
    provider_class = provider_map.get(key_info.provider)
    if not provider_class:
        if key_info.provider == AIProvider.CHATGPT and not OPENAI_AVAILABLE:
            raise ValueError("ChatGPT provider requires 'openai' library. Run: pip install openai")
        elif key_info.provider == AIProvider.CLAUDE and not ANTHROPIC_AVAILABLE:
            raise ValueError("Claude provider requires 'anthropic' library. Run: pip install anthropic")
        elif key_info.provider == AIProvider.COPILOT and not OPENAI_AVAILABLE:
            raise ValueError("GitHub Copilot provider requires 'openai' library. Run: pip install openai")
        else:
            raise ValueError(f"Unsupported provider: {key_info.provider}")
    
    return provider_class(key_info)
