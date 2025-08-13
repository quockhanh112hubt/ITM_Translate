"""
Tooltip utility for ITM Translate
Creates hover tooltips for GUI elements with i18n support
"""

import tkinter as tk
from core.i18n import get_language_manager, _


class ToolTip:
    """
    Create a tooltip for a given widget with i18n support
    """
    
    def __init__(self, widget, text='widget info', delay=500, wraplength=300):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wraplength = wraplength
        self.tooltip_window = None
        self.id = None
        self.x = self.y = 0
        
        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)  # Hide on click
    
    def on_enter(self, event=None):
        """Mouse entered widget"""
        self.schedule_tooltip()
    
    def on_leave(self, event=None):
        """Mouse left widget"""
        self.cancel_tooltip()
        self.hide_tooltip()
    
    def schedule_tooltip(self):
        """Schedule tooltip to show after delay"""
        self.cancel_tooltip()
        self.id = self.widget.after(self.delay, self.show_tooltip)
    
    def cancel_tooltip(self):
        """Cancel scheduled tooltip"""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
    
    def show_tooltip(self, event=None):
        """Display tooltip"""
        if self.tooltip_window or not self.text:
            return
        
        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Configure tooltip style
        self.tooltip_window.configure(bg="#ffffe0", relief="solid", borderwidth=1)
        
        # Get translated text if it's a translation key
        tooltip_text = self.text
        if isinstance(self.text, str) and not ' ' in self.text and '_' in self.text:
            # Looks like a translation key
            tooltip_text = _(self.text)
        
        # Create label with text
        label = tk.Label(
            self.tooltip_window,
            text=tooltip_text,
            justify='left',
            background="#ffffe0",
            relief="flat",
            borderwidth=0,
            wraplength=self.wraplength,
            font=("Arial", 9)
        )
        label.pack(ipadx=5, ipady=3)
        
        # Make sure tooltip appears on top
        self.tooltip_window.attributes('-topmost', True)
    
    def hide_tooltip(self):
        """Hide tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def update_text(self, new_text):
        """Update tooltip text (useful for dynamic content)"""
        self.text = new_text


def create_tooltip(widget, text, delay=500, wraplength=300):
    """
    Convenience function to create a tooltip
    
    Args:
        widget: The widget to attach tooltip to
        text: Tooltip text (can be translation key or direct text)
        delay: Delay in milliseconds before showing tooltip
        wraplength: Maximum width for text wrapping
    
    Returns:
        ToolTip instance
    """
    return ToolTip(widget, text, delay, wraplength)


def create_help_tooltip(widget, help_key, delay=500):
    """
    Create a tooltip with help icon style
    
    Args:
        widget: The widget to attach tooltip to  
        help_key: Translation key for help text
        delay: Delay before showing tooltip
    """
    # Add a small help indicator to the widget if possible
    try:
        # For labels, we can modify the text to include a help indicator
        if isinstance(widget, tk.Label):
            current_text = widget.cget('text')
            if not current_text.endswith(' ?'):
                widget.config(text=current_text + ' ?')
    except:
        pass
    
    return create_tooltip(widget, help_key, delay, wraplength=400)
