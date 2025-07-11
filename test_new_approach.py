#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test new 2-step approach

def test_new_approach():
    print("Testing new 2-step translation approach...")
    print()
    
    # Mock detect_language function
    def mock_detect_language(text):
        if any(char in text for char in "복잡한자성탄"):
            return "Hàn"
        elif any(char in text for char in "hello world"):
            return "Anh"
        elif any(char in text for char in "xin chào"):
            return "Việt"
        return "Unknown"
    
    # Test cases
    test_cases = [
        ("복잡한 자성탄 자투리를 참 담당", "Any Language", "Tiếng Việt", "English"),
        ("Hello world how are you", "Any Language", "Tiếng Việt", "English"),
        ("Xin chào tôi là AI", "Any Language", "Tiếng Việt", "English"),
    ]
    
    for i, (text, source, target2, target3) in enumerate(test_cases, 1):
        print(f"=== Test Case {i} ===")
        print(f"Text: {text}")
        print(f"Settings: {source} → {target2} / {target3}")
        
        # Step 1: Detect language
        detected = mock_detect_language(text)
        print(f"Detected language: {detected}")
        
        # Step 2: Determine target
        if source.lower() in ["any language", "bất kỳ", ""]:
            if detected and "việt" in detected.lower():
                final_target = target3  # Việt → English
            else:
                final_target = target2  # Other → Việt
        else:
            final_target = target2
            
        print(f"Translation direction: {detected} → {final_target}")
        print(f"Expected popup title: ITM Translate v1.0.23 - {detected} → {final_target}")
        print()

if __name__ == "__main__":
    test_new_approach()
