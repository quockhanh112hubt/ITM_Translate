"""Language configuration management"""
import json
import os

def get_language_settings():
    """
    Get current language settings from hotkeys.json
    Returns dictionary with language settings
    """
    hotkeys_file = "hotkeys.json"
    
    # Default language settings
    default_settings = {
        'Ngon_ngu_dau_tien': 'Any Language',
        'Ngon_ngu_thu_2': 'Vietnamese',
        'Ngon_ngu_thu_3': 'English',
        'Nhom2_Ngon_ngu_dau_tien': '',
        'Nhom2_Ngon_ngu_thu_2': '',
        'Nhom2_Ngon_ngu_thu_3': '',
    }
    
    if os.path.exists(hotkeys_file):
        try:
            with open(hotkeys_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Update default settings with saved values
                for k in default_settings.keys():
                    if k in data:
                        default_settings[k] = data[k]
        except Exception:
            pass
    
    return default_settings

def get_main_languages():
    """
    Get main language pair (Ngon_ngu_thu_2 and Ngon_ngu_thu_3) for provider comparison
    Returns the actual language names as configured, not mapped codes
    """
    settings = get_language_settings()
    return {
        'source': settings.get('Ngon_ngu_thu_2', 'Vietnamese'),
        'target': settings.get('Ngon_ngu_thu_3', 'English')
    }

def map_language_to_code(language_name):
    """
    Map Vietnamese language name to language code for API calls
    """
    language_mapping = {
        'Tiếng Việt': 'Vietnamese',
        'English': 'English',
        'Vietnamese': 'Vietnamese',
        'Tiếng Anh': 'English',
        'Tiếng Trung': 'Chinese',
        'Tiếng Nhật': 'Japanese',
        'Tiếng Hàn': 'Korean',
        'Tiếng Pháp': 'French',
        'Tiếng Đức': 'German',
        'Tiếng Tây Ban Nha': 'Spanish',
        'Tiếng Nga': 'Russian',
        'Tiếng Ý': 'Italian',
        'Tiếng Bồ Đào Nha': 'Portuguese',
        'Tiếng Thái': 'Thai',
        'Tiếng Hindi': 'Hindi',
        'Tiếng Ả Rập': 'Arabic',
        # Add more mappings as needed
    }
    
    return language_mapping.get(language_name, language_name)
