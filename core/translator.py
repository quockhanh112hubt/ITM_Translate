import os
from dotenv import load_dotenv
from .api_key_manager import api_key_manager

load_dotenv()

# Import AI providers with fallback
try:
    from .ai_providers import create_ai_provider
    AI_PROVIDERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI providers not fully available: {e}")
    AI_PROVIDERS_AVAILABLE = False
    # Fallback to Gemini only
    import google.generativeai as genai

def detect_language(text):
    """Detect language of the input text with failover support"""
    active_key = api_key_manager.get_active_key()
    if not active_key:
        return None
    
    if not AI_PROVIDERS_AVAILABLE:
        # Fallback to Gemini only
        try:
            genai.configure(api_key=active_key.key)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
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
        except Exception:
            return None
    
    # Try current provider first
    for attempt in range(api_key_manager.get_key_count()):
        current_key = api_key_manager.get_active_key()
        if not current_key:
            break
            
        try:
            provider = create_ai_provider(current_key)
            result = provider.detect_language(text)
            if result:
                # Reset failures on success
                api_key_manager.reset_key_failures(current_key)
                return result
        except Exception as e:
            print(f"Language detection failed with {current_key.provider.value}: {e}")
            api_key_manager.mark_key_failed(current_key, str(e))
            
            # Try to find next working key
            next_key = api_key_manager.find_next_working_key(exclude_current=True)
            if not next_key:
                break
    
    return None

def is_same_language(detected_lang, target_lang):
    """Check if detected language matches target language"""
    if not detected_lang or not target_lang:
        return False
    
    # Normalize language names for comparison
    detected_clean = detected_lang.lower().replace("tiếng ", "").strip()
    target_clean = target_lang.lower().replace("tiếng ", "").strip()
    
    # Direct match
    if detected_clean == target_clean:
        return True
    
    # Common mappings
    language_mappings = {
        "việt": ["vietnamese", "vietnam", "vi"],
        "anh": ["english", "en", "eng"],
        "hàn": ["korean", "korea", "ko", "kr"],
        "nhật": ["japanese", "japan", "ja", "jp"],
        "trung": ["chinese", "china", "zh", "cn"],
        "thái": ["thai", "thailand", "th"],
        "pháp": ["french", "france", "fr"],
        "đức": ["german", "germany", "de"]
    }
    
    # Check if they map to the same language
    for base_lang, variations in language_mappings.items():
        if (detected_clean == base_lang or detected_clean in variations) and \
           (target_clean == base_lang or target_clean in variations):
            return True
    
    return False

def translate_text(text, Ngon_ngu_dau_tien, Ngon_ngu_thu_2, Ngon_ngu_thu_3, return_language_info=False):
    """
    Translate text with automatic provider failover
    """
    def _attempt_translation(key_info):
        """Single translation attempt with given provider"""
        if not key_info:
            return "Lỗi: Không tìm thấy API key", None, None

        try:
            if not AI_PROVIDERS_AVAILABLE:
                # Fallback to Gemini only
                genai.configure(api_key=key_info.key)
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                
                # Step 1: Detect language if needed
                detected_source_lang = None
                if return_language_info:
                    if Ngon_ngu_dau_tien.strip().lower() in ["any language", "bất kỳ", ""]:
                        detected_source_lang = detect_language(text)
                        print(f"Detected source language: {detected_source_lang}")
                    else:
                        detected_source_lang = Ngon_ngu_dau_tien
                
                # Step 2: Determine translation direction
                if Ngon_ngu_dau_tien.strip().lower() in ["any language", "bất kỳ", ""]:
                    if detected_source_lang and detected_source_lang.lower() == "mixed":
                        target_lang = Ngon_ngu_thu_2
                    elif is_same_language(detected_source_lang, Ngon_ngu_thu_2):
                        target_lang = Ngon_ngu_thu_3
                    else:
                        target_lang = Ngon_ngu_thu_2
                else:
                    if detected_source_lang and detected_source_lang.lower() == "mixed":
                        target_lang = Ngon_ngu_thu_2
                    elif is_same_language(detected_source_lang, Ngon_ngu_thu_2):
                        target_lang = Ngon_ngu_thu_3
                    else:
                        target_lang = Ngon_ngu_thu_2

                print(f"Translation direction: {detected_source_lang} → {target_lang}")
                
                # Create prompt for Gemini
                if detected_source_lang and detected_source_lang.lower() == "mixed":
                    prompt = f"""This text contains multiple languages mixed together. Translate ALL content to {target_lang}.

Rules for mixed language translation:
- Translate every word/phrase to {target_lang}, regardless of original language
- Maintain the original structure and meaning
- Keep proper nouns and brand names (unless they have common translations)
- Keep numbers and dates unchanged
- Return ONLY the fully translated text in {target_lang}

Mixed language text to translate: {text}

Complete translation to {target_lang}:"""
                else:
                    prompt = f"""Translate this text to {target_lang}.

Rules:
- Translate every word/phrase to {target_lang}
- Preserve original tone and style
- Ensure natural grammar and correct sentence structure in {target_lang}
- Keep technical terms if widely understood
- Keep proper nouns and brand names
- Keep numbers and dates unchanged
- Return ONLY the translated text, no explanations

Text to translate: {text}

Translation:"""
                
                response = model.generate_content(prompt)
                translated_text = response.text.strip()
                
                if return_language_info:
                    return translated_text, detected_source_lang, target_lang
                else:
                    return translated_text
            else:
                # Use AI providers system
                provider = create_ai_provider(key_info)
                
                # Step 1: Detect language if needed
                detected_source_lang = None
                if return_language_info:
                    if Ngon_ngu_dau_tien.strip().lower() in ["any language", "bất kỳ", ""]:
                        detected_source_lang = provider.detect_language(text)
                        print(f"Detected source language: {detected_source_lang}")
                    else:
                        detected_source_lang = Ngon_ngu_dau_tien
                
                # Step 2: Determine translation direction
                if Ngon_ngu_dau_tien.strip().lower() in ["any language", "bất kỳ", ""]:
                    if detected_source_lang and detected_source_lang.lower() == "mixed":
                        target_lang = Ngon_ngu_thu_2
                    elif is_same_language(detected_source_lang, Ngon_ngu_thu_2):
                        target_lang = Ngon_ngu_thu_3
                    else:
                        target_lang = Ngon_ngu_thu_2
                else:
                    if detected_source_lang and detected_source_lang.lower() == "mixed":
                        target_lang = Ngon_ngu_thu_2
                    elif is_same_language(detected_source_lang, Ngon_ngu_thu_2):
                        target_lang = Ngon_ngu_thu_3
                    else:
                        target_lang = Ngon_ngu_thu_2

                print(f"Translation direction: {detected_source_lang} → {target_lang}")
                
                # Step 3: Translate using provider
                source_lang = detected_source_lang or Ngon_ngu_dau_tien
                translated_text = provider.translate_text(text, source_lang, target_lang)
                
                # Return results based on mode
                if return_language_info:
                    return translated_text, detected_source_lang, target_lang
                else:
                    return translated_text
                
        except Exception as e:
            error_str = str(e).lower()
            # Check for specific API errors that warrant provider rotation
            if "insufficient balance" in error_str or "402" in error_str:
                raise Exception("402_INSUFFICIENT_BALANCE")
            elif "429" in error_str or "quota" in error_str:
                raise Exception("429_QUOTA_EXCEEDED")
            elif "400" in error_str and ("key not valid" in error_str or "invalid" in error_str):
                raise Exception("400_INVALID_KEY")
            elif "401" in error_str or "unauthorized" in error_str:
                raise Exception("401_UNAUTHORIZED")
            else:
                raise e

    # Main translation logic with failover mechanism
    initial_key_count = api_key_manager.get_key_count()
    
    if initial_key_count == 0:
        result = "Lỗi: Không tìm thấy API key nào trong hệ thống"
        if return_language_info:
            return result, None, None
        return result

    # Try translation with current active key first
    for attempt in range(initial_key_count):
        current_key = api_key_manager.get_active_key()
        if not current_key:
            break
            
        provider_info = api_key_manager.get_provider_info()
        print(f"🔄 Translation attempt {attempt + 1}/{initial_key_count} with {provider_info['provider']} (model: {provider_info['model']}) key: {provider_info['key_preview']}")
        
        try:
            result = _attempt_translation(current_key)
            # Success - reset failure count and return result
            api_key_manager.reset_key_failures(current_key)
            print(f"✅ Translation successful with {provider_info['provider']} (index: {api_key_manager.active_index})")
            return result
            
        except Exception as e:
            error_str = str(e)
            provider_name = current_key.provider.value
            
            # Check if this is a retriable error
            if error_str in ["402_INSUFFICIENT_BALANCE", "429_QUOTA_EXCEEDED", "400_INVALID_KEY", "401_UNAUTHORIZED"]:
                # Special message for insufficient balance
                if error_str == "402_INSUFFICIENT_BALANCE":
                    print(f"💳 {provider_name} API: Insufficient Balance (Hết tiền) - Chuyển sang provider khác")
                    print(f"   � Nạp thêm credit tại: https://platform.deepseek.com/")
                else:
                    print(f"�🚨 {provider_name} API error detected: {error_str}")
                
                api_key_manager.mark_key_failed(current_key, error_str)
                
                # Try to find next working key (different provider if possible)
                next_key = api_key_manager.find_next_working_key(exclude_current=True)
                if not next_key:
                    print(f"❌ No more working keys available")
                    break
                    
                print(f"🔄 Switching from {provider_name} → {next_key.provider.value}")
                continue
            else:
                # Non-retriable error - fail immediately
                result = f"Lỗi dịch với {provider_name}: {error_str}"
                if return_language_info:
                    return result, None, None
                return result

    # All keys failed
    result = "Tất cả API key đều gặp lỗi. Vui lòng kiểm tra lại hoặc liên hệ Admin để nhận key mới."
    if return_language_info:
        return result, None, None
    return result
