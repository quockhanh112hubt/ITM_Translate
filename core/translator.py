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
    if Ngon_ngu_dau_tien.strip().lower() in ["Any Language", "Bất kỳ"]:
        prompt = f"""
        You are a translation assistant.

        Follow these instructions exactly:
        1. Detect the main language of the message. If the message is written mostly in one language but contains words or short phrases from others (e.g., "OK tôi sẽ check cái đó"), treat the main language as the dominant one.
        2. If the message is clearly mixed between multiple languages without a dominant one, translate it into {Ngon_ngu_thu_2}.
        3. If the main language is {Ngon_ngu_thu_2}, translate it into {Ngon_ngu_thu_3}.
        4. Otherwise, translate the message into {Ngon_ngu_thu_2}.
        5. Do not explain, comment, or add anything. Return only the translated message.

        User's message:
        {text}
        """

    else:
        prompt = f"""
                You are a translation model.

                Your task is to:
                1. If the message is written in {Ngon_ngu_dau_tien}, or partially mixed with other languages, translate it into {Ngon_ngu_thu_2}.
                2. If the message is written in {Ngon_ngu_thu_2}, translate it into {Ngon_ngu_thu_3}.
                3. Do not explain, comment, or add anything. Return only the translated content.

                User's message:
                {text}
                """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Lỗi dịch: {str(e)}"
