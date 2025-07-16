import os
from dotenv import load_dotenv
import google.generativeai as genai
from .api_key_manager import api_key_manager

load_dotenv()

def detect_language(text):
    """Detect language of the input text"""
    api_key = api_key_manager.get_active_key()
    if not api_key:
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    prompt = f"""What language is the following text used?.
    Follow these instructions exactly:
    - Analyze the text and determine the primary language used. If the message is written mostly in one language but contains words or short phrases from others (e.g., "OK tôi sẽ check cái đó"), treat the main language as the dominant one.
    - If the dominant language cannot be determined, return "Mixed".
    - Do not return any explanations or additional text, just the language name

    Text:
    {text}

    """

    try:
        response = model.generate_content(prompt)
        detected_lang = response.text.strip()
        # Remove any extra quotes or formatting
        detected_lang = detected_lang.replace('"', '').replace("'", "").strip()
        return detected_lang
    except Exception:
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
    Translate text with automatic API key rotation on errors
    """
    def _attempt_translation(api_key):
        """Single translation attempt with given API key"""
        if not api_key:
            return "Lỗi: Không tìm thấy API key", None, None

        genai.configure(api_key=api_key)
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
            # Auto-detect mode
            if detected_source_lang and detected_source_lang.lower() == "mixed":
                # Mixed language → always translate to thu_2
                target_lang = Ngon_ngu_thu_2
                # Keep detected_source_lang as "Mixed" for display
            elif is_same_language(detected_source_lang, Ngon_ngu_thu_2):
                target_lang = Ngon_ngu_thu_3  # Source matches thu_2 → translate to thu_3
            else:
                target_lang = Ngon_ngu_thu_2  # Source different → translate to thu_2
        else:
            # Fixed source mode
            if detected_source_lang and detected_source_lang.lower() == "mixed":
                # Mixed language → always translate to thu_2
                target_lang = Ngon_ngu_thu_2
            elif is_same_language(detected_source_lang, Ngon_ngu_thu_2):
                target_lang = Ngon_ngu_thu_3
            else:
                target_lang = Ngon_ngu_thu_2

        print(f"Translation direction: {detected_source_lang} → {target_lang}")
        
        # Step 3: Create translation prompt
        if detected_source_lang and detected_source_lang.lower() == "mixed":
            # Special prompt for mixed language content
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
            # Standard prompt for single language
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

        try:
            response = model.generate_content(prompt)
            translated_text = response.text.strip()
            
            # Return results based on mode
            if return_language_info:
                return translated_text, detected_source_lang, target_lang
            else:
                return translated_text
                
        except Exception as e:
            error_str = str(e).lower()
            # Check for specific API errors that warrant key rotation
            if "429" in error_str or "quota" in error_str:
                raise Exception("429_QUOTA_EXCEEDED")
            elif "400" in error_str and ("key not valid" in error_str or "invalid" in error_str):
                raise Exception("400_INVALID_KEY")
            else:
                raise e

    # Main translation logic with retry mechanism
    initial_key_count = api_key_manager.get_key_count()
    
    if initial_key_count == 0:
        result = "Lỗi: Không tìm thấy API key nào trong hệ thống"
        if return_language_info:
            return result, None, None
        return result

    # Try translation with current active key first
    for attempt in range(initial_key_count):
        current_key = api_key_manager.get_active_key()
        print(f"🔄 Translation attempt {attempt + 1}/{initial_key_count} with key: {current_key[:10] if current_key else 'None'}... (index: {api_key_manager.active_index})")
        
        try:
            result = _attempt_translation(current_key)
            # Success - return result
            print(f"✅ Translation successful with key index {api_key_manager.active_index}")
            return result
            
        except Exception as e:
            error_str = str(e)
            
            # Check if this is a retriable error
            if error_str in ["429_QUOTA_EXCEEDED", "400_INVALID_KEY"]:
                print(f"🚨 API error detected: {error_str}, rotating to next key...")
                
                # If this is the last attempt, don't rotate, just fail
                if attempt == initial_key_count - 1:
                    print(f"❌ Last attempt failed, no more keys to try")
                    break
                
                # Rotate to next key
                old_index = api_key_manager.active_index
                next_key = api_key_manager.rotate_to_next_key()
                print(f"🔄 Rotated from key index {old_index} → {api_key_manager.active_index} ({next_key[:10] if next_key else 'None'}...)")
                continue
            else:
                # Non-retriable error - fail immediately
                result = f"Lỗi dịch: {error_str}"
                if return_language_info:
                    return result, None, None
                return result

    # All keys failed
    result = "Tất cả API key đều gặp lỗi. Vui lòng kiểm tra lại hoặc liên hệ Admin để nhận key mới."
    if return_language_info:
        return result, None, None
    return result
