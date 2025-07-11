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
    
    prompt = f"""Detect the primary language of this text. Return ONLY the language name in Vietnamese format.

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

For mixed language text, return the dominant language (>50% of content).

Text to analyze: {text}

Return only the language name:"""

    try:
        response = model.generate_content(prompt)
        detected_lang = response.text.strip()
        # Remove any extra quotes or formatting
        detected_lang = detected_lang.replace('"', '').replace("'", "").strip()
        return detected_lang
    except Exception:
        return None

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
        if detected_source_lang and "việt" in detected_source_lang.lower():
            target_lang = Ngon_ngu_thu_3  # Việt → English (or thu_3)
        else:
            target_lang = Ngon_ngu_thu_2  # Other → Việt
    else:
        # Fixed source mode
        if detected_source_lang and "việt" in detected_source_lang.lower():
            target_lang = Ngon_ngu_thu_3
        elif detected_source_lang and any(lang in detected_source_lang.lower() for lang in [Ngon_ngu_thu_2.lower().replace("tiếng ", "")]):
            target_lang = Ngon_ngu_thu_3
        else:
            target_lang = Ngon_ngu_thu_2

    # Step 3: Create simple translation prompt
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
