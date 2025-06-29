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
    print(f"Đang dịch đoạn văn: {text}")
    prompt = f"Bạn là một mô hình dịch thuật. Nhiệm vụ của bạn dịch đoạn tin nhắn của người dùng, nếu người dùng sử dụng ngôn ngữ {Ngon_ngu_dau_tien} hoặc nhiều ngôn ngữ khác nhau, hãy dịch nó sang {Ngon_ngu_thu_2}. Nếu người dùng sử dụng {Ngon_ngu_thu_2}, hãy dịch nó sang {Ngon_ngu_thu_3}. Bạn chỉ được trả lời là nội dung đã dịch. Đây là tin nhắn của người dùng:\n{text}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Lỗi dịch: {e}"
