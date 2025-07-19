"""
Language Flag Buttons Component
Hiển thị 2 nút cờ quốc gia ở góc trên phải cửa sổ
"""
import tkinter as tk
from tkinter import PhotoImage
import os
from PIL import Image, ImageTk
from core.i18n import get_language_manager, _

class LanguageFlagButtons:
    def __init__(self, parent, on_language_change=None):
        self.parent = parent
        self.on_language_change = on_language_change
        self.language_manager = get_language_manager()
        
        # Load flag images
        self.load_flag_images()
        
        # Create flag buttons container
        self.create_flag_buttons()
        
    def load_flag_images(self):
        """Load flag images from Resource folder"""
        try:
            # Get correct path to Resource folder (go up 2 levels from ui/components/)
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            vietnam_path = os.path.join(base_path, "Resource", "Vietnam.png")
            english_path = os.path.join(base_path, "Resource", "English.png")
            
            print(f"🔍 Looking for flags at:")
            print(f"  Vietnam: {vietnam_path}")
            print(f"  English: {english_path}")
            
            # Load and resize images
            self.vietnam_img = None
            self.english_img = None
            
            if os.path.exists(vietnam_path):
                img = Image.open(vietnam_path)
                img = img.resize((32, 22), Image.Resampling.LANCZOS)  # Larger size
                self.vietnam_img = ImageTk.PhotoImage(img)
                print("✅ Vietnam flag loaded successfully")
            else:
                print("❌ Vietnam.png not found")
            
            if os.path.exists(english_path):
                img = Image.open(english_path)
                img = img.resize((32, 22), Image.Resampling.LANCZOS)  # Larger size
                self.english_img = ImageTk.PhotoImage(img)
                print("✅ English flag loaded successfully")
            else:
                print("❌ English.png not found")
                
        except Exception as e:
            print(f"❌ Error loading flag images: {e}")
            # Fallback to emoji flags
            self.vietnam_img = None
            self.english_img = None
    
    def create_flag_buttons(self):
        """Create flag buttons in title bar area"""
        # Create container frame for flags (positioned at top-right)
        self.flags_frame = tk.Frame(self.parent, bg='#f0f0f0', relief='raised', bd=1)
        
        # Vietnam flag button
        self.vietnam_btn = tk.Button(
            self.flags_frame,
            image=self.vietnam_img if self.vietnam_img else None,
            text="🇻🇳" if not self.vietnam_img else "",
            font=('Segoe UI', 12) if not self.vietnam_img else None,
            relief='flat',
            bd=1,
            padx=4,
            pady=3,
            cursor='hand2',
            command=lambda: self.change_language("vi"),
            bg='#f8f8f8',
            activebackground='#e3f2fd',
            width=36 if self.vietnam_img else None,
            height=26 if self.vietnam_img else None
        )
        
        # English flag button  
        self.english_btn = tk.Button(
            self.flags_frame,
            image=self.english_img if self.english_img else None,
            text="🇺🇸" if not self.english_img else "",
            font=('Segoe UI', 12) if not self.english_img else None,
            relief='flat',
            bd=1,
            padx=4,
            pady=3,
            cursor='hand2',
            command=lambda: self.change_language("en"),
            bg='#f8f8f8',
            activebackground='#e3f2fd',
            width=36 if self.english_img else None,
            height=26 if self.english_img else None
        )
        
        # Pack buttons horizontally with minimal spacing
        self.vietnam_btn.pack(side='left', padx=1, pady=2)
        self.english_btn.pack(side='left', padx=1, pady=2)
        
        # Highlight current language
        self.update_button_states()
        
        # Tooltips
        self.create_tooltips()
    
    def create_tooltips(self):
        """Create tooltips for flag buttons"""
        try:
            # Enhanced tooltips with language info
            def on_vietnam_enter(e):
                self.vietnam_btn.configure(relief='raised')
                # Optional: Show tooltip text
                
            def on_vietnam_leave(e):
                current_lang = self.language_manager.get_current_language()
                if current_lang == "vi":
                    self.vietnam_btn.configure(relief='solid')
                else:
                    self.vietnam_btn.configure(relief='flat')
                
            def on_english_enter(e):
                self.english_btn.configure(relief='raised')
                
            def on_english_leave(e):
                current_lang = self.language_manager.get_current_language()
                if current_lang == "en":
                    self.english_btn.configure(relief='solid')
                else:
                    self.english_btn.configure(relief='flat')
            
            self.vietnam_btn.bind('<Enter>', on_vietnam_enter)
            self.vietnam_btn.bind('<Leave>', on_vietnam_leave)
            self.english_btn.bind('<Enter>', on_english_enter)  
            self.english_btn.bind('<Leave>', on_english_leave)
            
        except Exception as e:
            print(f"Error creating tooltips: {e}")
    
    def update_button_states(self):
        """Update button appearance based on current language"""
        current_lang = self.language_manager.get_current_language()
        
        # Reset both buttons
        self.vietnam_btn.configure(relief='flat', bg='#f8f8f8', bd=1)
        self.english_btn.configure(relief='flat', bg='#f8f8f8', bd=1)
        
        # Highlight active language
        if current_lang == "vi":
            self.vietnam_btn.configure(relief='solid', bg='#e8f5e8', bd=2)
        elif current_lang == "en":
            self.english_btn.configure(relief='solid', bg='#e8f5e8', bd=2)
    
    def change_language(self, language):
        """Change application language"""
        if self.language_manager.set_language(language):
            self.update_button_states()
            
            # Call callback to refresh UI
            if self.on_language_change:
                self.on_language_change(language)
            
            print(f"🌐 Language changed to: {'Vietnamese' if language == 'vi' else 'English'}")
    
    def pack(self, **kwargs):
        """Pack the flag buttons frame"""
        self.flags_frame.pack(**kwargs)
        
    def place(self, **kwargs):
        """Place the flag buttons frame"""
        self.flags_frame.place(**kwargs)
        
    def grid(self, **kwargs):
        """Grid the flag buttons frame"""
        self.flags_frame.grid(**kwargs)
    
    def destroy(self):
        """Destroy the flag buttons"""
        if hasattr(self, 'flags_frame'):
            self.flags_frame.destroy()
