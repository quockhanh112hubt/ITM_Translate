import openai
import pyperclip
import tkinter as tk
from pynput import keyboard
import threading

# ====== CẤU HÌNH ======
openai.api_key = "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"  # <--- Thay bằng API key của bạn
source_lang = "auto"
target_lang = "vi"  # Chuyển sang "en" nếu muốn dịch sang tiếng Anh
hotkey = {keyboard.Key.ctrl, keyboard.Key.shift, keyboard.KeyCode(char='d')}
# ======================

pressed_keys = set()

def translate_with_gpt(text):
    prompt = f"Dịch đoạn sau sang tiếng Việt một cách tự nhiên:\n\n{text.strip()}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Hoặc dùng "gpt-3.5-turbo" nếu chưa có GPT-4
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Lỗi khi gọi GPT: {e}"

def show_popup(text):
    popup = tk.Tk()
    popup.title("Kết quả dịch")
    popup.geometry("500x300")
    popup.attributes("-topmost", True)

    text_widget = tk.Text(popup, wrap="word", font=("Segoe UI", 11))
    text_widget.insert("1.0", text)
    text_widget.pack(expand=True, fill="both")

    popup.mainloop()

def on_activate():
    copied_text = pyperclip.paste()
    if copied_text.strip():
        print("Tổ hợp phím đã nhận! Đang dịch...")
        def translate_and_show():
            result = translate_with_gpt(copied_text)
            show_popup(result)
        threading.Thread(target=translate_and_show).start()
    else:
        print("Clipboard rỗng hoặc không có văn bản để dịch.")

def on_press(key):
    pressed_keys.add(key)
    if all(k in pressed_keys for k in hotkey):
        print("Tổ hợp phím Ctrl+Shift+D được nhấn.")
        on_activate()

def on_release(key):
    pressed_keys.discard(key)

def main():
    print("Đang chạy... Nhấn Ctrl+Shift+D sau khi chọn văn bản để dịch.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
