import sys
import threading
import time
import pyperclip
from pynput import keyboard
from translator import translate_text
from popup import show_popup

# Hàm xử lý khi nhấn Ctrl+Q
def on_activate():
    # Copy clipboard
    time.sleep(0.1)  # Đợi clipboard cập nhật
    selected_text = pyperclip.paste()
    if selected_text.strip():
        translated = translate_text(selected_text)
        show_popup(translated)

def for_canonical(f):
    return lambda k: f(l.canonical(k))

hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<ctrl>+q'),
    on_activate
)

with keyboard.Listener(
        on_press=for_canonical(hotkey.press),
        on_release=for_canonical(hotkey.release)) as l:
    l.join()
