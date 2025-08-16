"""
AI Providers - Hỗ trợ multiple AI APIs
"""
import google.generativeai as genai
import requests
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from .api_key_manager import AIProvider, APIKeyInfo

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

try:
    from google.cloud import translate_v2 as translate
    GOOGLE_CLOUD_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_TRANSLATE_AVAILABLE = False
    print("Warning: Google Cloud Translate library not available. Google Translate provider will be disabled.")

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
    
    def get_default_model(self) -> str:
        return "gemini-1.5-flash"  # Changed from gemini-2.0-flash-exp to stable version
    
    def get_provider_name(self) -> str:
        return "Gemini"
    
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
            print(f"Phat hien ngonngu{prompt}")
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
                timeout=30
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
                timeout=30
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
                timeout=30
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
                timeout=30
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
                timeout=30
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


class GoogleTranslateProvider(BaseAIProvider):
    """Google Cloud Translation API Provider"""
    
    def __init__(self, key_info: APIKeyInfo):
        super().__init__(key_info)
        if not GOOGLE_CLOUD_TRANSLATE_AVAILABLE:
            raise ImportError("Google Cloud Translate library not available. Run: pip install google-cloud-translate")
        
        # Sử dụng REST API trực tiếp với requests thay vì client library
        # Vì Google Cloud Translate v2 API có thể gây conflict với credentials
        self.api_key = self.api_key
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
        
        # Language mapping - Google Translate codes to our internal codes
        self.language_map = {
            'vi': 'vi',     # Vietnamese
            'en': 'en',     # English
            'zh': 'zh-cn',  # Chinese Simplified
            'zh-cn': 'zh-cn',
            'zh-tw': 'zh-tw',
            'ja': 'ja',     # Japanese
            'ko': 'ko',     # Korean
            'fr': 'fr',     # French
            'de': 'de',     # German
            'es': 'es',     # Spanish
            'it': 'it',     # Italian
            'pt': 'pt',     # Portuguese
            'ru': 'ru',     # Russian
            'ar': 'ar',     # Arabic
            'th': 'th',     # Thai
            'id': 'id',     # Indonesian
        }
    
    def get_default_model(self) -> str:
        return "google-translate-v2"
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect ngôn ngữ sử dụng Google Cloud Translation REST API"""
        try:
            import requests
            
            url = f"{self.base_url}/detect"
            params = {
                'key': self.api_key,
                'q': text
            }
            
            response = requests.post(url, data=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if 'data' in result and 'detections' in result['data']:
                detected_lang = result['data']['detections'][0][0]['language']
                # Convert Google language code to our internal format
                return self._convert_from_google_lang(detected_lang)
            
            return None
            
        except Exception as e:
            print(f"🚫 Google Translate language detection error: {e}")
            return None
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Dịch text sử dụng Google Cloud Translation REST API"""
        try:
            import requests
            
            # Handle 'auto' source language - detect first
            if source_lang == 'auto' or source_lang.lower() == 'auto':
                detected_lang = self.detect_language(text)
                google_source = self._convert_to_google_lang(detected_lang) if detected_lang else 'en'
            else:
                # Convert our internal language codes to Google format
                google_source = self._convert_to_google_lang(source_lang)
            
            google_target = self._convert_to_google_lang(target_lang)
            
            # Prepare API call
            url = f"{self.base_url}"
            params = {
                'key': self.api_key,
                'q': text,
                'source': google_source,
                'target': google_target,
                'format': 'text'
            }
            
            # Perform translation
            response = requests.post(url, data=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if 'data' in result and 'translations' in result['data']:
                translated_text = result['data']['translations'][0]['translatedText']
                
                # Clean up HTML entities that might be returned
                import html
                translated_text = html.unescape(translated_text)
                
                return translated_text
            else:
                raise Exception("No translation data in response")
            
        except Exception as e:
            raise Exception(f"Google Translate API error: {str(e)}")
    
    def _convert_to_google_lang(self, lang: str) -> str:
        """Convert internal language code to Google Translate format"""
        # Google Translate usually uses simpler codes
        lang_mapping = {
            'vietnamese': 'vi',
            'english': 'en',
            'chinese': 'zh-cn',
            'japanese': 'ja',
            'korean': 'ko',
            'french': 'fr',
            'german': 'de',
            'spanish': 'es',
            'italian': 'it',
            'portuguese': 'pt',
            'russian': 'ru',
            'arabic': 'ar',
            'thai': 'th',
            'indonesian': 'id'
        }
        
        # Return mapped language or original if not found
        return lang_mapping.get(lang.lower(), lang.lower())
    
    def _convert_from_google_lang(self, google_lang: str) -> str:
        """Convert Google language code to our internal format"""
        reverse_mapping = {
            'vi': 'vietnamese',
            'en': 'english', 
            'zh': 'chinese',
            'zh-cn': 'chinese',
            'zh-tw': 'chinese',
            'ja': 'japanese',
            'ko': 'korean',
            'fr': 'french',
            'de': 'german',
            'es': 'spanish',
            'it': 'italian',
            'pt': 'portuguese',
            'ru': 'russian',
            'ar': 'arabic',
            'th': 'thai',
            'id': 'indonesian'
        }
        
        return reverse_mapping.get(google_lang, google_lang)
    
    def generate_text(self, prompt: str) -> str:
        """
        Extract text from smart prompt and translate directly.
        Translator.py uses this for unified interface.
        """
        try:
            # Extract text from smart prompt
            # Format: "...If it is not in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_2}.\n3. If it is already in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_3}..."
            
            lines = prompt.split('\n')
            text_to_translate = None
            ngon_ngu_thu_2 = None
            ngon_ngu_thu_3 = None
            
            # Extract target languages from smart prompt
            for line in lines:
                if 'If it is not in' in line and 'translate it to' in line:
                    # Parse: "2. If it is not in Vietnamese, translate it to Vietnamese."
                    parts = line.split('translate it to')
                    if len(parts) >= 2:
                        ngon_ngu_thu_2 = parts[1].strip(' .').lower()
                elif 'If it is already in' in line and 'translate it to' in line:
                    # Parse: "3. If it is already in Vietnamese, translate it to English."
                    parts = line.split('translate it to')
                    if len(parts) >= 2:
                        ngon_ngu_thu_3 = parts[1].strip(' .').lower()
            
            # Find the line with "text to translate:" and extract everything after it
            for i, line in enumerate(lines):
                if 'text to translate:' in line.lower():
                    # Get all remaining lines after "text to translate:"
                    remaining_lines = lines[i + 1:]
                    # Join them and strip whitespace
                    text_to_translate = '\n'.join(remaining_lines).strip()
                    break
            
            if not text_to_translate:
                # Fallback: try to find text after the last line break
                if lines:
                    text_to_translate = lines[-1].strip()
                
            if not text_to_translate:
                raise Exception("Could not extract text from translation prompt")
            
            # Set fallback values if parsing failed
            if not ngon_ngu_thu_2:
                ngon_ngu_thu_2 = 'vietnamese'
            if not ngon_ngu_thu_3:
                ngon_ngu_thu_3 = 'english'
            
            print(f"🔍 [GOOGLE] Extracted text: '{text_to_translate[:100]}...'")
            print(f"🎯 [GOOGLE] Target languages: {ngon_ngu_thu_2} ↔ {ngon_ngu_thu_3}")
            
            # Auto-detect source language
            detected_lang = self.detect_language(text_to_translate)
            print(f"🌐 [GOOGLE] Detected language: {detected_lang}")
            
            # Apply correct logic: if detected == Ngon_ngu_thu_2 → translate to Ngon_ngu_thu_3, else → translate to Ngon_ngu_thu_2
            if detected_lang and detected_lang.lower() == ngon_ngu_thu_2.lower():
                target_lang = ngon_ngu_thu_3
                print(f"📝 [GOOGLE] Text is in {ngon_ngu_thu_2} → translating to {ngon_ngu_thu_3}")
            else:
                target_lang = ngon_ngu_thu_2
                print(f"📝 [GOOGLE] Text is not in {ngon_ngu_thu_2} → translating to {ngon_ngu_thu_2}")
            
            # Use translate_text method with proper language handling
            result = self.translate_text(text_to_translate, detected_lang or 'en', target_lang)
            print(f"✅ [GOOGLE] Translation result: '{result[:100]}...'")
            return result
            
        except Exception as e:
            print(f"❌ [GOOGLE] Generate text error: {str(e)}")
            raise Exception(f"Google Translate generate_text error: {str(e)}")
    
    def get_provider_name(self) -> str:
        return "Google Translate"


# Factory function để tạo provider instance
def create_ai_provider(key_info: APIKeyInfo) -> BaseAIProvider:
    """Factory function để tạo AI provider instance"""
    provider_map = {
        AIProvider.GEMINI: GeminiProvider,
        AIProvider.CHATGPT: ChatGPTProvider if OPENAI_AVAILABLE else None,
        AIProvider.DEEPSEEK: DeepSeekProvider,
        AIProvider.CLAUDE: ClaudeProvider if ANTHROPIC_AVAILABLE else None,
        AIProvider.COPILOT: CopilotProvider if OPENAI_AVAILABLE else None,
        AIProvider.GOOGLE_TRANSLATE: GoogleTranslateProvider if GOOGLE_CLOUD_TRANSLATE_AVAILABLE else None
    }
    
    provider_class = provider_map.get(key_info.provider)
    if not provider_class:
        if key_info.provider == AIProvider.CHATGPT and not OPENAI_AVAILABLE:
            raise ValueError("ChatGPT provider requires 'openai' library. Run: pip install openai")
        elif key_info.provider == AIProvider.CLAUDE and not ANTHROPIC_AVAILABLE:
            raise ValueError("Claude provider requires 'anthropic' library. Run: pip install anthropic")
        elif key_info.provider == AIProvider.COPILOT and not OPENAI_AVAILABLE:
            raise ValueError("GitHub Copilot provider requires 'openai' library. Run: pip install openai")
        elif key_info.provider == AIProvider.GOOGLE_TRANSLATE and not GOOGLE_CLOUD_TRANSLATE_AVAILABLE:
            # Return None instead of raising error - let caller handle this gracefully
            return None
        else:
            raise ValueError(f"Unsupported provider: {key_info.provider}")
    
    return provider_class(key_info)
