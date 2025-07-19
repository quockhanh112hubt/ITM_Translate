"""
Demo script để test tính năng language switching
"""
import tkinter as tk
from tkinter import messagebox
from core.i18n import get_language_manager, _

def demo_language_switching():
    """Demo tính năng chuyển đổi ngôn ngữ"""
    
    # Initialize window
    root = tk.Tk()
    root.title("Language Switching Demo")
    root.geometry("400x300")
    
    # Language manager
    language_manager = get_language_manager()
    
    # Dynamic labels that will change with language
    title_label = tk.Label(root, text="", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)
    
    subtitle_label = tk.Label(root, text="", font=("Arial", 10))
    subtitle_label.pack(pady=5)
    
    def update_labels():
        """Update all labels with current language"""
        title_label.config(text=_('settings_title'))
        subtitle_label.config(text=_('auto_choose_hint'))
    
    def change_to_vietnamese():
        """Change to Vietnamese"""
        language_manager.set_language("vi")
        update_labels()
        messagebox.showinfo("Language Changed", "Đã chuyển sang tiếng Việt!")
    
    def change_to_english():
        """Change to English"""
        language_manager.set_language("en")
        update_labels()
        messagebox.showinfo("Language Changed", "Changed to English!")
    
    # Buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)
    
    vn_btn = tk.Button(button_frame, text="🇻🇳 Tiếng Việt", 
                       command=change_to_vietnamese, 
                       font=("Arial", 12), padx=20, pady=10)
    vn_btn.pack(side=tk.LEFT, padx=10)
    
    en_btn = tk.Button(button_frame, text="🇺🇸 English", 
                       command=change_to_english, 
                       font=("Arial", 12), padx=20, pady=10)
    en_btn.pack(side=tk.LEFT, padx=10)
    
    # Current language display
    current_lang_label = tk.Label(root, text=f"Current: {language_manager.get_current_language()}", 
                                  font=("Arial", 10, "italic"))
    current_lang_label.pack(pady=10)
    
    # Initial update
    update_labels()
    
    # Start demo
    root.mainloop()

if __name__ == "__main__":
    demo_language_switching()
