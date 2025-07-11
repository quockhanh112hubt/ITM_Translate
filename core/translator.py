import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def detect_language(text):
    """Detect language of the input text"""
    api_key = os.environ.get("ITM_TRANSLATE_KEY") or os.getenv("ITM_TRANSLATE_KEY")
    if not api_key:
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    prompt = f"""Analyze this text and determine the language composition.

If the text contains MULTIPLE different languages (mixed), return "Mixed"
If the text is primarily in ONE language (>80% of content), return the language name in Vietnamese format:

Examples:
- Korean text → "Hàn"
- English text → "Anh" 
- Japanese text → "Nhật"
- Chinese text → "Trung"
- Vietnamese text → "Việt"
- Thai text → "Thái"
- French text → "Pháp"
- German text → "Đức"
- Spanish text → "Tây Ban Nha"
- Mixed languages → "Mixed"

Text to analyze: {text}

Return only the result:"""

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
    api_key = os.environ.get("ITM_TRANSLATE_KEY") or os.getenv("ITM_TRANSLATE_KEY")
    if not api_key:
        result = "Lỗi: Không tìm thấy ITM_TRANSLATE_KEY"
        if return_language_info:
            return result, None, None
        return result

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    # Step 1: Detect language if needed
    detected_source_lang = None
    if return_language_info:
        if Ngon_ngu_dau_tien.strip().lower() in ["any language", "bất kỳ", ""]:
            detected_source_lang = detect_language(text)
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
- Preserve original tone and style
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
        result = f"Lỗi dịch: {str(e)}"
        if return_language_info:
            return result, None, None
        return result
