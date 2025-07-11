import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def translate_text(text, Ngon_ngu_dau_tien, Ngon_ngu_thu_2, Ngon_ngu_thu_3, return_language_info=False):
    api_key = os.environ.get("ITM_TRANSLATE_KEY") or os.getenv("ITM_TRANSLATE_KEY")
    if not api_key:
        result = "Lỗi: Không tìm thấy ITM_TRANSLATE_KEY"
        if return_language_info:
            return result, None, None
        return result

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    # Tạo prompt phù hợp với ngôn ngữ đầu vào
    if Ngon_ngu_dau_tien.strip().lower() in ["any language", "bất kỳ", ""]:
        prompt = f"""You are a professional translation assistant.

Instructions:
1. Detect the primary language of the input text based on the majority of words/content
2. For mixed-language text, identify the dominant language (>50% of meaningful content)
3. Translation rules:
   - If primary language is {Ngon_ngu_thu_2} → translate to {Ngon_ngu_thu_3}
   - Otherwise → translate to {Ngon_ngu_thu_2}
4. Preserve:
   - Original tone and style
   - Technical terms (if widely understood)
   - Proper nouns and brand names
   - Numbers and dates
5. Format your response as: "DETECTED_LANG|TARGET_LANG|TRANSLATED_TEXT"
   - DETECTED_LANG: The detected primary language name
   - TARGET_LANG: The target language you translated to
   - TRANSLATED_TEXT: The actual translation

Text to translate:
{text}"""

    else:
        prompt = f"""You are a professional translation assistant.

Instructions:
1. Source language: {Ngon_ngu_dau_tien}
2. Translation rules:
   - If text is in {Ngon_ngu_dau_tien} or mixed with {Ngon_ngu_dau_tien} as dominant → translate to {Ngon_ngu_thu_2}
   - If text is in {Ngon_ngu_thu_2} → translate to {Ngon_ngu_thu_3}
   - If text is already in target language → return as-is
3. Preserve:
   - Original tone and style
   - Technical terms (if widely understood)
   - Proper nouns and brand names
   - Numbers and dates
4. Format your response as: "SOURCE_LANG|TARGET_LANG|TRANSLATED_TEXT"
   - SOURCE_LANG: The actual source language detected
   - TARGET_LANG: The target language you translated to
   - TRANSLATED_TEXT: The actual translation

Text to translate:
{text}"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse response để extract language info
        if return_language_info:
            try:
                parts = response_text.split('|', 2)
                if len(parts) == 3:
                    source_lang, target_lang, translated_text = parts
                    return translated_text.strip(), source_lang.strip(), target_lang.strip()
                else:
                    # Fallback nếu format không đúng
                    return response_text, None, None
            except Exception:
                return response_text, None, None
        else:
            # Compatibility mode - chỉ return text
            if '|' in response_text:
                try:
                    parts = response_text.split('|', 2)
                    if len(parts) == 3:
                        return parts[2].strip()  # Chỉ lấy translated text
                except Exception:
                    pass
            return response_text
            
    except Exception as e:
        result = f"Lỗi dịch: {str(e)}"
        if return_language_info:
            return result, None, None
        return result
