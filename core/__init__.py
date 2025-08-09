# Core package initialization

# Import existing modules
from .translator import translate_text
from .ai_providers import *
from .api_key_manager import *
from .tray import *

__all__ = [
    'translate_text'
]
