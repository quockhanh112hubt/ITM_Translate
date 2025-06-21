import sys
import threading
import time
import pyperclip
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController, Key
from translator import translate_text
from popup import show_popup

# Hàm xử lý khi nhấn Ctrl+Q
def on_activate():
    # Gửi Ctrl+C để copy text được chọn
    kb = KeyboardController()
    kb.press(Key.ctrl)
    kb.press('c')
    kb.release('c')
    kb.release(Key.ctrl)
    time.sleep(0.15)  # Đợi clipboard cập nhật
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
