import os
from dotenv import load_dotenv
# import google.generativeai as genai
from google import genai

load_dotenv()

def translate_text(text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Lỗi: Không tìm thấy GEMINI_API_KEY trong file .env"
    client = genai.Client(api_key=api_key)
    prompt = f"Dịch đoạn văn sau sang tiếng Việt:\n{text}"
    try:
        response = client.generate_content(model="gemini-pro", prompt=prompt)
        return response.text.strip()
    except Exception as e:
        return f"Lỗi dịch: {e}"
