
import openai
import pyperclip
import tkinter as tk
from pynput import keyboard
import threading

# ====== CẤU HÌNH ======
openai.api_key = "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"
source_lang = "auto"
target_lang = "vi"
hotkey = {keyboard.Key.ctrl, keyboard.Key.shift, keyboard.KeyCode(char='L')}
# ======================

pressed_keys = set()

def translate_with_gpt(text):
    prompt = f"Dịch đoạn sau sang tiếng Việt một cách tự nhiên: {text.strip()}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
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
        def translate_and_show():
            result = translate_with_gpt(copied_text)
            show_popup(result)
        threading.Thread(target=translate_and_show).start()

def on_press(key):
    pressed_keys.add(key)
    if all(k in pressed_keys for k in hotkey):
        on_activate()

def on_release(key):
    pressed_keys.discard(key)

def main():
    print("Đang chạy... Nhấn Ctrl+Shift+D sau khi chọn văn bản để dịch.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()  # chạy lắng nghe phím vĩnh viễn


if __name__ == "__main__":
    main()
