import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def translate_text(text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Lỗi: Không tìm thấy GEMINI_API_KEY trong file .env"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    print(f"Đang dịch đoạn văn: {text}")
    prompt = f"Bạn là một mô hình dịch thuật. Nhiệm vụ của bạn dịch đoạn tin nhắn của người dùng, nếu người dùng sử dụng bất kỳ ngôn ngữ nào khác Tiếng Việt, hãy dịch nó sang Tiếng Việt. Nếu người dùng sử dụng Tiếng Việt, hãy dịch nó sang Tiếng Anh. Bạn chỉ được trả lời là nội dung đã dịch. Đây là tin nhắn của người dùng:\n{text}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Lỗi dịch: {e}"
