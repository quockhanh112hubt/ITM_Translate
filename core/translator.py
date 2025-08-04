import os
import threading
import time
import signal
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

# Legacy functions - no longer used with unified smart translation
# def detect_language(text): - REMOVED
# def is_same_language(detected_lang, target_lang): - REMOVED

def translate_text(text, Ngon_ngu_dau_tien, Ngon_ngu_thu_2, Ngon_ngu_thu_3, return_language_info=False, timeout_seconds=5):
    """
    Translate text with automatic provider failover and timeout protection
    
    Args:
        return_language_info: If True, detect language first (for popup). If False, use smart replacement logic.
        timeout_seconds: Maximum time to wait for translation per attempt (default 5 seconds)
    """
    def _attempt_translation(key_info):
        """Single translation attempt with given provider"""
        if not key_info:
            return "Lỗi: Không tìm thấy API key", None, None

        # Timeout mechanism for individual translation attempts
        translation_result = {'result': None, 'error': None, 'completed': False}
        
        def do_translation():
            try:
                if not AI_PROVIDERS_AVAILABLE:
                    # Fallback to Gemini only
                    genai.configure(api_key=key_info.key)
                    model = genai.GenerativeModel("gemini-2.0-flash-exp")
                    
                    # UNIFIED SMART TRANSLATION: Single AI call for both popup and replace modes
                    print(f"🧠 [UNIFIED MODE] Using single smart AI call")
                    
                    # UNIFIED SMART PROMPT: Same for both popup and replace
                    smart_prompt = f"""You are a professional translation model.

Your task:
1. Detect the language of the input TEXT.
2. If it is not in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_2}.
3. If it is already in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_3}.

Translation rules:
- Preserve the tone, style, and sentence structure.
- Ensure fluent and natural grammar.
- Retain technical terms if commonly used.
- Do not translate proper nouns or brand names.

Output: Return ONLY the translated version of TEXT — no explanations, no comments.

TEXT to translate:
{text}
"""
                    
                    response = model.generate_content(smart_prompt)
                    translated_text = response.text.strip()
                    print (f"✨ [UNIFIED] Smart prompt: {smart_prompt}")
                    print(f"✨ [UNIFIED] Translation result: {translated_text[:50]}...")
                    
                    if return_language_info:
                        # POPUP MODE: Return translation with simplified language info
                        # Use simplified language info (no actual detection needed)
                        translation_result['result'] = (translated_text, "Auto-detected", "Auto-selected")
                    else:
                        # REPLACE MODE: Return only translation
                        translation_result['result'] = translated_text
                else:
                    # Use AI providers system with unified smart translation
                    provider = create_ai_provider(key_info)
                    
                    # UNIFIED SMART PROMPT: Same for both popup and replace
                    print(f"🧠 [UNIFIED PROVIDER] Using single smart AI call")
                    smart_prompt = f"""You are a professional translation model.

Your task:
1. Detect the language of the input TEXT.
2. If it is not in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_2}.
3. If it is already in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_3}.

Translation rules:
- Preserve the tone, style, and sentence structure.
- Ensure fluent and natural grammar.
- Retain technical terms if commonly used.
- Do not translate proper nouns or brand names.

Output: Return ONLY the translated version of TEXT — no explanations, no comments.

TEXT to translate:
{text}
"""
                    
                    # Use provider's text generation for smart translation
                    print(f'smart_prompt2: {smart_prompt}"')
                    if hasattr(provider, 'generate_text'):
                        print(f"🧠 [UNIFIED] Using provider.generate_text()")
                        translated_text = provider.generate_text(smart_prompt)
                    else:
                        # Fallback: use Gemini directly with smart prompt
                        print(f"🧠 [UNIFIED] Provider lacks generate_text, using Gemini fallback")
                        import google.generativeai as genai
                        genai.configure(api_key=key_info.key)
                        model = genai.GenerativeModel("gemini-2.0-flash-exp")
                        response = model.generate_content(smart_prompt)
                        translated_text = response.text.strip()
                    
                    print(f"✨ [UNIFIED] Translation result: {translated_text[:50]}...")
                    
                    if return_language_info:
                        # POPUP MODE: Return translation with simplified language info
                        translation_result['result'] = (translated_text, "Auto-detected", "Auto-selected")
                    else:
                        # REPLACE MODE: Return only translation
                        translation_result['result'] = translated_text
                        
                translation_result['completed'] = True
                
            except Exception as e:
                error_str = str(e).lower()
                # Check for specific API errors that warrant provider rotation
                if "insufficient balance" in error_str or "402" in error_str:
                    translation_result['error'] = Exception("402_INSUFFICIENT_BALANCE")
                elif "429" in error_str or "quota" in error_str:
                    translation_result['error'] = Exception("429_QUOTA_EXCEEDED")
                elif "400" in error_str and ("key not valid" in error_str or "invalid" in error_str):
                    translation_result['error'] = Exception("400_INVALID_KEY")
                elif "401" in error_str or "unauthorized" in error_str:
                    translation_result['error'] = Exception("401_UNAUTHORIZED")
                else:
                    translation_result['error'] = e
                translation_result['completed'] = True
        
        # Start translation in background thread
        translation_thread = threading.Thread(target=do_translation, daemon=True)
        translation_thread.start()
        
        # Wait for completion with timeout
        start_time = time.time()
        while not translation_result['completed']:
            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds:
                print(f"⏰ Translation timeout after {elapsed:.1f}s with {key_info.provider.value}")
                raise Exception(f"TIMEOUT_ERROR: Translation timed out after {timeout_seconds}s")
            time.sleep(0.1)
        
        # Check for errors
        if translation_result['error']:
            raise translation_result['error']
        
        return translation_result['result']

    # Main translation logic with failover mechanism
    initial_key_count = api_key_manager.get_key_count()
    max_attempts = min(initial_key_count, 3)  # Limit to max 3 attempts to avoid long waits
    
    if initial_key_count == 0:
        result = "Lỗi: Không tìm thấy API key nào trong hệ thống"
        if return_language_info:
            return result, None, None
        return result

    # Try translation with current active key first
    for attempt in range(max_attempts):
        current_key = api_key_manager.get_active_key()
        if not current_key:
            break
            
        provider_info = api_key_manager.get_provider_info()
        print(f"🔄 Translation attempt {attempt + 1}/{max_attempts} with {provider_info['provider']} (model: {provider_info['model']}) key: {provider_info['key_preview']}")
        
        try:
            result = _attempt_translation(current_key)
            # Success - reset failure count and return result
            api_key_manager.reset_key_failures(current_key)
            print(f"✅ Translation successful with {provider_info['provider']} (index: {api_key_manager.active_index})")
            return result
            
        except Exception as e:
            error_str = str(e)
            provider_name = current_key.provider.value
            
            # Check if this is a timeout error
            if "TIMEOUT_ERROR" in error_str:
                print(f"⏰ {provider_name} API: Translation timeout - trying next provider")
                api_key_manager.mark_key_failed(current_key, "TIMEOUT")
                
                # Try to find next working key (different provider if possible)
                next_key = api_key_manager.find_next_working_key(exclude_current=True)
                if not next_key:
                    print(f"❌ No more working keys available after timeout")
                    result = f"⏰ Hết thời gian chờ dịch ({timeout_seconds}s/attempt). Tất cả provider đều timeout."
                    if return_language_info:
                        return result, None, None
                    return result
                    
                print(f"🔄 Timeout: Switching from {provider_name} → {next_key.provider.value}")
                continue
            # Check if this is a retriable error
            elif error_str in ["402_INSUFFICIENT_BALANCE", "429_QUOTA_EXCEEDED", "400_INVALID_KEY", "401_UNAUTHORIZED"]:
                # Special message for insufficient balance
                if error_str == "402_INSUFFICIENT_BALANCE":
                    print(f"💳 {provider_name} API: Insufficient Balance (Hết tiền) - Chuyển sang provider khác")
                    print(f"   💰 Nạp thêm credit tại: https://platform.deepseek.com/")
                else:
                    print(f"🚨 {provider_name} API error detected: {error_str}")
                
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
