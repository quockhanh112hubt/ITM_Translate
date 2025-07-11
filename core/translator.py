import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def translate_text(text, Ngon_ngu_dau_tien, Ngon_ngu_thu_2, Ngon_ngu_thu_3):
    api_key = os.environ.get("ITM_TRANSLATE_KEY") or os.getenv("ITM_TRANSLATE_KEY")
    if not api_key:
        return "Lỗi: Không tìm thấy ITM_TRANSLATE_KEY"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    # Tạo prompt phù hợp với ngôn ngữ đầu vào
    if Ngon_ngu_dau_tien.strip().lower() in ["Any language", "bất kỳ", ""]:
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
5. Return ONLY the translated text, no explanations or comments

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
4. Return ONLY the translated text, no explanations or comments

Text to translate:
{text}"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Lỗi dịch: {str(e)}"
