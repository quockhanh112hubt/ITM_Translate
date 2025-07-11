#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test mixed language handling

def is_same_language(detected_lang, target_lang):
    """Check if detected language matches target language"""
    if not detected_lang or not target_lang:
        return False
    
    # Normalize language names for comparison
    detected_clean = detected_lang.lower().replace("tiếng ", "").strip()
    target_clean = target_lang.lower().replace("tiếng ", "").strip()
    
    # Direct match
    if detected_clean == target_clean:
        return True
    
    # Common mappings
    language_mappings = {
        "việt": ["vietnamese", "vietnam", "vi"],
        "anh": ["english", "en", "eng"],
        "hàn": ["korean", "korea", "ko", "kr"],
        "nhật": ["japanese", "japan", "ja", "jp"],
        "trung": ["chinese", "china", "zh", "cn"],
        "thái": ["thai", "thailand", "th"],
        "pháp": ["french", "france", "fr"],
        "đức": ["german", "germany", "de"]
    }
    
    # Check if they map to the same language
    for base_lang, variations in language_mappings.items():
        if (detected_clean == base_lang or detected_clean in variations) and \
           (target_clean == base_lang or target_clean in variations):
            return True
    
    return False

def test_mixed_language():
    print("Testing mixed language handling...")
    print()
    
    # Test cases with mixed language
    test_cases = [
        # Case 1: Normal single language
        ("Hàn", "Any Language", "Tiếng Việt", "English"),
        ("Việt", "Any Language", "Tiếng Việt", "English"),
        ("Anh", "Any Language", "Tiếng Việt", "English"),
        
        # Case 2: Mixed language scenarios
        ("Mixed", "Any Language", "Tiếng Việt", "English"),
        ("Mixed", "Any Language", "English", "Nhật"),
        ("Mixed", "Any Language", "Hàn", "Trung"),
    ]
    
    for i, (detected, source_setting, thu_2, thu_3) in enumerate(test_cases, 1):
        print(f"=== Test Case {i} ===")
        print(f"User settings: {source_setting} → {thu_2} / {thu_3}")
        print(f"Detected language: {detected}")
        
        # New logic with mixed language handling
        if detected and detected.lower() == "mixed":
            # Mixed language → always translate to thu_2
            target = thu_2
            display_source = "Multi language"
        elif is_same_language(detected, thu_2):
            target = thu_3  # Source matches thu_2 → translate to thu_3
            display_source = detected
        else:
            target = thu_2  # Source different → translate to thu_2
            display_source = detected
            
        direction = f"{display_source} → {target}"
        print(f"Translation direction: {direction}")
        print(f"Expected popup: ITM Translate v1.0.25 - {direction}")
        print()

if __name__ == "__main__":
    test_mixed_language()
