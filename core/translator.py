import os
import threading
import time
import signal
import hashlib
import json
from dotenv import load_dotenv
from .api_key_manager import api_key_manager
from .translation_history import translation_history
from .config_manager import config_manager

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

# Translation Cache System
translation_cache = {}
cache_file = "translation_cache.json"
max_cache_size = 1000  # Maximum number of cached translations

def load_translation_cache():
    """Load translation cache from file"""
    global translation_cache
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                translation_cache = json.load(f)
                print(f"📁 [CACHE] Loaded {len(translation_cache)} cached translations")
    except Exception as e:
        print(f"❌ [CACHE] Error loading cache: {e}")
        translation_cache = {}

def save_translation_cache():
    """Save translation cache to file"""
    try:
        # Limit cache size to prevent bloat
        if len(translation_cache) > max_cache_size:
            # Keep only the most recent entries (simple FIFO)
            cache_items = list(translation_cache.items())
            translation_cache.clear()
            translation_cache.update(cache_items[-max_cache_size:])
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(translation_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ [CACHE] Error saving cache: {e}")

def get_cache_key(text, lang2, lang3, return_language_info):
    """Generate cache key for translation"""
    # Include text, target languages and mode in cache key
    cache_data = f"{text}|{lang2}|{lang3}|{return_language_info}"
    return hashlib.md5(cache_data.encode('utf-8')).hexdigest()

def get_cached_translation(text, lang2, lang3, return_language_info):
    """Get cached translation if available"""
    cache_key = get_cache_key(text, lang2, lang3, return_language_info)
    if cache_key in translation_cache:
        cached_result = translation_cache[cache_key]
        print(f"💾 [CACHE] Found cached translation for: {text[:30]}...")
        return cached_result
    return None

def cache_translation(text, lang2, lang3, return_language_info, result):
    """Cache translation result"""
    cache_key = get_cache_key(text, lang2, lang3, return_language_info)
    translation_cache[cache_key] = result
    print(f"💾 [CACHE] Cached translation for: {text[:30]}...")
    
    # Save to file asynchronously to avoid blocking
    threading.Thread(target=save_translation_cache, daemon=True).start()

def clear_translation_cache():
    """Clear translation cache (useful when language settings change)"""
    global translation_cache
    translation_cache.clear()
    try:
        if os.path.exists(cache_file):
            os.remove(cache_file)
        print(f"🗑️ [CACHE] Translation cache cleared")
    except Exception as e:
        print(f"❌ [CACHE] Error clearing cache: {e}")

# Load cache on startup
load_translation_cache()

# Legacy functions - no longer used with unified smart translation
# def detect_language(text): - REMOVED
# def is_same_language(detected_lang, target_lang): - REMOVED

def translate_text(text, Ngon_ngu_dau_tien, Ngon_ngu_thu_2, Ngon_ngu_thu_3, return_language_info=False, timeout_seconds=None):
    """
    Translate text with automatic provider failover and timeout protection
    
    Args:
        return_language_info: If True, detect language first (for popup). If False, use smart replacement logic.
        timeout_seconds: Maximum time to wait for translation per attempt (if None, use config default)
    """
    
    # Get timeout from config if not specified
    if timeout_seconds is None:
        timeout_seconds = config_manager.get_translation_retry_timeout()
    
    # Check cache first
    cached_result = get_cached_translation(text, Ngon_ngu_thu_2, Ngon_ngu_thu_3, return_language_info)
    if cached_result is not None:
        return cached_result
    
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
1. Detect the language of the input text.
2. If it is not in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_2}.
3. If it is already in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_3}.

Translation rules:
- Preserve the tone, style, prioritize natural.
- Retain technical terms.
- Do not translate proper nouns or brand names.
- Do not output any explanations — only return the translated text.

text to translate:
{text}
"""
                    
                    response = model.generate_content(smart_prompt)
                    translated_text = response.text.strip()
                    print (f"✨ [UNIFIED] Smart prompt: {smart_prompt}")
                    print(f"✨ [UNIFIED] Translation result: {translated_text[:50]}...")
                    
                    if return_language_info:
                        # POPUP MODE: Return translation with actual language detection
                        try:
                            # Detect source language using Gemini
                            detect_model = genai.GenerativeModel("gemini-1.5-flash")
                            detect_prompt = f"What language is this text? Reply with language name only: {text}"
                            detect_response = detect_model.generate_content(detect_prompt)
                            detected_lang = detect_response.text.strip()
                            
                            # Determine target language based on detection logic
                            if detected_lang.lower() == Ngon_ngu_thu_2.lower():
                                target_lang = Ngon_ngu_thu_3
                            else:
                                target_lang = Ngon_ngu_thu_2
                                
                            print(f"🌐 [UNIFIED] Detected language: {detected_lang} → Target: {target_lang}")
                            translation_result['result'] = (translated_text, detected_lang, target_lang)
                        except:
                            # Fallback to simplified info if detection fails
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
1. Detect the language of the input text.
2. If it is not in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_2}.
3. If it is already in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_3}.

Translation rules:
- Preserve the tone, style, prioritize natural.
- Retain technical terms.
- Do not translate proper nouns or brand names.
- Do not output any explanations — only return the translated text.

text to translate:
{text}
"""
                    
                    # Use provider's text generation for smart translation
                    print(f'smart_prompt: {smart_prompt}"')
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
                        # POPUP MODE: Return translation with actual language detection
                        try:
                            # Detect source language using the provider
                            detected_lang = None
                            if hasattr(provider, 'detect_language'):
                                detected_lang = provider.detect_language(text)
                                print(f"🌐 [UNIFIED] {provider.__class__.__name__} detected language: {detected_lang}")
                            
                            if not detected_lang:
                                detected_lang = "Unknown"
                            
                            # Determine target language based on detection logic
                            if detected_lang.lower() == Ngon_ngu_thu_2.lower():
                                target_lang = Ngon_ngu_thu_3
                            else:
                                target_lang = Ngon_ngu_thu_2
                                
                            print(f"📝 [UNIFIED] Translation direction: {detected_lang} → {target_lang}")
                            translation_result['result'] = (translated_text, detected_lang, target_lang)
                        except Exception as e:
                            print(f"⚠️ [UNIFIED] Language detection failed: {e}")
                            # Fallback to simplified info if detection fails
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

    # Track overall translation start time for history
    overall_start_time = time.time()

    # Try translation with current active key first
    for attempt in range(max_attempts):
        current_key = api_key_manager.get_active_key()
        if not current_key:
            break
            
        provider_info = api_key_manager.get_provider_info()
        print(f"🔄 Translation attempt {attempt + 1}/{max_attempts} with {provider_info['provider']} (model: {provider_info['model']}) key: {provider_info['key_preview']}")
        
        try:
            result = _attempt_translation(current_key)
            # Success - reset failure count, cache result and return
            api_key_manager.reset_key_failures(current_key)
            print(f"✅ Translation successful with {provider_info['provider']} (index: {api_key_manager.active_index})")
            
            # Cache the successful translation
            cache_translation(text, Ngon_ngu_thu_2, Ngon_ngu_thu_3, return_language_info, result)
            
            # Add to translation history
            try:
                translation_time = time.time() - overall_start_time
                
                # Extract translated text based on mode
                if return_language_info and isinstance(result, tuple):
                    translated_text = result[0]  # First element is the translation
                    detected_lang = result[1]
                    target_lang = result[2]
                else:
                    translated_text = result
                    detected_lang = "Auto-detected"
                    target_lang = "Auto-selected"
                
                translation_history.add_translation(
                    original_text=text,
                    translated_text=translated_text,
                    source_lang=detected_lang,
                    target_lang=target_lang,
                    provider=provider_info['provider'],
                    translation_time=translation_time
                )
                print(f"📝 [HISTORY] Translation recorded (time: {translation_time:.2f}s)")
            except Exception as hist_e:
                print(f"⚠️ [HISTORY] Failed to record translation: {hist_e}")
            
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
                    print(f"❌ No more active keys available after timeout - trying disabled keys")
                    # Try retry mechanism with disabled keys
                    retry_result = _try_retry_disabled_keys(text, Ngon_ngu_dau_tien, Ngon_ngu_thu_2, max_retries=3)
                    if retry_result is not None:
                        if return_language_info:
                            return retry_result[0], retry_result[1], retry_result[2] 
                        return retry_result
                    
                    print(f"❌ All retry attempts failed after timeout")
                    result = f"⏰ Hết thời gian chờ dịch ({timeout_seconds}s/attempt). Tất cả provider đều timeout hoặc lỗi."
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
                    print(f"❌ No more active keys available - trying disabled keys")
                    # Try retry mechanism with disabled keys
                    retry_result = _try_retry_disabled_keys(text, Ngon_ngu_dau_tien, Ngon_ngu_thu_2, max_retries=3)
                    if retry_result is not None:
                        if return_language_info:
                            return retry_result[0], retry_result[1], retry_result[2] 
                        return retry_result
                    
                    print(f"❌ All retry attempts failed")
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
    result = "❌ Tất cả API keys đều gặp lỗi. Vui lòng kiểm tra lại các API keys trong tab 'Quản lý API KEY'."
    if return_language_info:
        return result, None, None
    return result


def _try_retry_disabled_keys(text: str, source_lang: str, target_lang: str, max_retries: int = 3):
    """
    Retry mechanism: Try up to max_retries disabled keys
    Returns translation result if successful, None if all retries failed
    """
    from core.api_key_manager import api_key_manager
    
    print(f"🔄 [RETRY] Starting retry mechanism with disabled keys (max {max_retries} attempts)")
    retry_count = 0
    
    while retry_count < max_retries:
        retry_count += 1
        
        # Find a disabled key to retry
        retry_key = api_key_manager.find_retry_candidate_key(exclude_current=True)
        if not retry_key:
            print(f"❌ [RETRY] No more disabled keys to retry")
            break
        
        print(f"🔄 [RETRY] Attempt {retry_count}/{max_retries}: Trying {retry_key.provider.value}")
        
        # Temporarily re-enable the key
        api_key_manager.retry_disabled_key(retry_key)
        
        # Try translation with this key
        try:
            # Import here to avoid circular imports
            from core.ai_providers import get_ai_provider
            
            provider = get_ai_provider(retry_key.provider.value)
            if provider:
                # Test with a single translation attempt
                retry_timeout = config_manager.get_translation_retry_timeout()
                result = provider.translate(text, source_lang, target_lang, retry_key.key, retry_key.model, timeout=retry_timeout)
                
                if not result.startswith("Lỗi") and not result.startswith("❌") and not result.startswith("⏰"):
                    # Success! Key is working again
                    print(f"✅ [RETRY] Success! Key {retry_key.provider.value} is working again")
                    api_key_manager.reset_key_failures(retry_key)
                    
                    # Detect languages if needed
                    detected_source = None
                    detected_target = None
                    if source_lang.lower() in ['auto', 'any language', 'mixed']:
                        try:
                            from core.ai_providers import detect_language
                            detected_source = detect_language(text)
                        except:
                            detected_source = "Unknown"
                    
                    return (result, detected_source, detected_target)
                else:
                    # Still failing, mark as failed again
                    print(f"❌ [RETRY] Key {retry_key.provider.value} still failing: {result[:100]}...")
                    api_key_manager.mark_key_failed(retry_key, "RETRY_FAILED")
                    
        except Exception as e:
            print(f"❌ [RETRY] Exception with {retry_key.provider.value}: {str(e)}")
            api_key_manager.mark_key_failed(retry_key, f"RETRY_EXCEPTION: {str(e)}")
    
    print(f"❌ [RETRY] All {retry_count} retry attempts failed")
    return None


def translate_with_specific_provider(text, provider_name, Ngon_ngu_thu_2, Ngon_ngu_thu_3):
    """
    Translate text using a specific provider by name (for comparison UI)
    Does not change the active provider.
    
    Args:
        text: Text to translate
        provider_name: Name of the provider to use (e.g., "Gemini", "ChatGPT")
        Ngon_ngu_thu_2: Primary language 
        Ngon_ngu_thu_3: Secondary language
        
    Returns:
        Tuple: (translated_text, detected_source_lang, target_lang) or error message
    """
    try:
        # Find the API key with matching name
        target_key = None
        for key_info in api_key_manager.get_all_keys():
            if key_info.name == provider_name:
                target_key = key_info
                break
        
        if not target_key:
            return f"❌ Provider '{provider_name}' not found"
        
        print(f"🔄 [SPECIFIC] Using {provider_name} ({target_key.provider.value}) for comparison")
        
        # Create provider instance
        if AI_PROVIDERS_AVAILABLE:
            provider = create_ai_provider(target_key)
            
            # Check if provider creation failed (e.g., library not available)
            if provider is None:
                return f"❌ Provider '{provider_name}' is not available in this build (missing required libraries)"
            
            # For Google Translate: Use efficient 2-step detection + translation
            if target_key.provider.value == 'google_translate':
                # Step 1: Detect source language (REST API - fast & cheap)
                detected_lang = None
                try:
                    if hasattr(provider, 'detect_language'):
                        detected_lang = provider.detect_language(text)
                        print(f"🌐 [SPECIFIC] {provider_name} detected language: {detected_lang}")
                except Exception as e:
                    print(f"⚠️ [SPECIFIC] Language detection failed for {provider_name}: {e}")
                    detected_lang = "Unknown"
                
                # Step 2: Determine target language based on detection
                if detected_lang and detected_lang.lower() == Ngon_ngu_thu_2.lower():
                    target_lang = Ngon_ngu_thu_3
                    print(f"📝 [SPECIFIC] Text is in {Ngon_ngu_thu_2} → translating to {Ngon_ngu_thu_3}")
                else:
                    target_lang = Ngon_ngu_thu_2  
                    print(f"📝 [SPECIFIC] Text is not in {Ngon_ngu_thu_2} → translating to {Ngon_ngu_thu_2}")
                
                # Step 3: Create optimized prompt for Google Translate
                smart_prompt = f"""You are a professional translation model.

Translate the following text to {target_lang}.

Translation rules:
- Preserve the tone, style, prioritize natural.
- Retain technical terms.
- Do not translate proper nouns or brand names.
- Do not output any explanations — only return the translated text.

text to translate:
{text}
"""
                
                # Use provider's generate_text method
                if hasattr(provider, 'generate_text'):
                    print(f"Dich: {smart_prompt}")
                    translated_text = provider.generate_text(smart_prompt)
                else:
                    translated_text = f"❌ Provider {provider_name} doesn't support smart translation"
                
                print(f"✅ [SPECIFIC] {provider_name} translation: {translated_text[:50]}...")
                
                # Return tuple with language info
                return (translated_text, detected_lang or "Unknown", target_lang)
            
            else:
                # For AI Providers: Use single smart prompt with language detection + translation
                print(f"🧠 [SPECIFIC] {provider_name} using single smart AI call (detect + translate)")
                
                smart_prompt = f"""You are a professional translation model.

Your task:
1. Detect the language of the input text.
2. If it is not in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_2}.
3. If it is already in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_3}.

Translation rules:
- Preserve the tone, style, prioritize natural.
- Retain technical terms.
- Do not translate proper nouns or brand names.
- Do not output any explanations — only return the translated text.

text to translate:
{text}
"""
                
                # Use provider's generate_text method
                if hasattr(provider, 'generate_text'):
                    print(f"Dich: {smart_prompt}")
                    translated_text = provider.generate_text(smart_prompt)
                else:
                    translated_text = f"❌ Provider {provider_name} doesn't support smart translation"
                
                print(f"✅ [SPECIFIC] {provider_name} translation: {translated_text[:50]}...")
                
                # For AI providers, we need to infer the language direction from the result
                # Since we can't detect without extra AI call, use simplified approach
                detected_lang = "Auto-detected"
                target_lang = "Auto-selected"
                
                # Return tuple with simplified language info for AI providers
                return (translated_text, detected_lang, target_lang)
            
        else:
            # Fallback to Gemini if AI providers not available
            import google.generativeai as genai
            genai.configure(api_key=target_key.key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Detect language with Gemini
            try:
                detect_prompt = f"What language is this text? Reply with language name only: {text}"
                detect_response = model.generate_content(detect_prompt)
                detected_lang = detect_response.text.strip()
                print(f"🌐 [SPECIFIC] Gemini fallback detected language: {detected_lang}")
            except:
                detected_lang = "Unknown"
            
            # Determine target language
            if detected_lang and detected_lang.lower() == Ngon_ngu_thu_2.lower():
                target_lang = Ngon_ngu_thu_3
            else:
                target_lang = Ngon_ngu_thu_2
            
            smart_prompt = f"""You are a professional translation model.

Your task:
1. Detect the language of the input text.
2. If it is not in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_2}.
3. If it is already in {Ngon_ngu_thu_2}, translate it to {Ngon_ngu_thu_3}.

Translation rules:
- Preserve the tone, style, prioritize natural.
- Retain technical terms.
- Do not translate proper nouns or brand names.
- Do not output any explanations — only return the translated text.

text to translate:
{text}
"""
            
            response = model.generate_content(smart_prompt)
            translated_text = response.text.strip()
            print(f"✅ [SPECIFIC] {provider_name} (Gemini fallback) translation: {translated_text[:50]}...")
            return (translated_text, detected_lang, target_lang)
            
    except Exception as e:
        error_msg = f"❌ Error with {provider_name}: {str(e)}"
        print(error_msg)
        return error_msg
