import sys
import threading
import time
import pyperclip
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController, Key
from translator import translate_text
from popup import show_popup

kb = KeyboardController()

def on_activate_translate():
    # Gửi Ctrl+C để copy text được chọn
    kb.press(Key.ctrl)
    kb.press('c')
    kb.release('c')
    kb.release(Key.ctrl)
    time.sleep(0.15)  # Đợi clipboard cập nhật
    selected_text = pyperclip.paste()
    if selected_text.strip():
        translated = translate_text(selected_text)
        show_popup(translated)

def on_activate_replace():
    # Gửi Ctrl+C để copy text được chọn
    kb.press(Key.ctrl)
    kb.press('c')
    kb.release('c')
    kb.release(Key.ctrl)
    time.sleep(0.15)
    selected_text = pyperclip.paste()
    if selected_text.strip():
        translated = translate_text(selected_text)
        pyperclip.copy(translated)
        time.sleep(0.05)
        # Gửi Ctrl+V để dán kết quả dịch thay thế đoạn bôi đen
        kb.press(Key.ctrl)
        kb.press('v')
        kb.release('v')
        kb.release(Key.ctrl)
        time.sleep(0.15)
        # Kiểm tra lại xem đã dán thành công chưa
        kb.press(Key.ctrl)
        kb.press('c')
        kb.release('c')
        kb.release(Key.ctrl)
        time.sleep(0.1)
        pasted = pyperclip.paste()
        if pasted.strip() != translated.strip():
            from popup import show_popup
            show_popup('Không thể thay thế văn bản tự động. Kết quả dịch đã được lưu vào clipboard, bạn hãy dán thủ công.')

def for_canonical(f):
    return lambda k: f(l.canonical(k))

hotkeys = {
    '<ctrl>+q': on_activate_translate,
    '<ctrl>+w': on_activate_replace
}

class MultiHotKey:
    def __init__(self, hotkey_map):
        # Lưu hotkeys dưới dạng list các tuple (frozenset phím, callback)
        self.hotkeys = [(frozenset(keyboard.HotKey.parse(k)), v) for k, v in hotkey_map.items()]
        self._pressed = set()
        self._active = set()  # Đánh dấu các combo đang active
    def press(self, key):
        self._pressed.add(key)
        for combo, callback in self.hotkeys:
            if combo <= self._pressed and combo not in self._active:
                self._active.add(combo)
                threading.Thread(target=self._run_and_reset, args=(combo, callback)).start()
    def release(self, key):
        self._pressed.discard(key)
        # Khi nhả phím, bỏ active cho các combo không còn đủ phím
        for combo in list(self._active):
            if not combo <= self._pressed:
                self._active.discard(combo)
    def _run_and_reset(self, combo, callback):
        try:
            callback()
        finally:
            self._active.discard(combo)

multi_hotkey = MultiHotKey(hotkeys)

with keyboard.Listener(
        on_press=for_canonical(multi_hotkey.press),
        on_release=for_canonical(multi_hotkey.release)) as l:
    l.join()
