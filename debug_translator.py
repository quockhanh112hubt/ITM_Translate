#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test phần logic parse response

def test_parse_logic():
    # Giả lập response từ AI
    mock_response = "DETECTED_LANG|TIẾNG VIỆT|Đây là nội dung dịch thực tế"
    
    print("Testing response parsing logic...")
    print(f"Mock AI response: {mock_response}")
    print()
    
    # Test với return_language_info=True
    print("=== WITH LANGUAGE INFO ===")
    try:
        parts = mock_response.split('|', 2)
        if len(parts) == 3:
            source_lang, target_lang, translated_text = parts
            print(f"Translated: '{translated_text.strip()}'")
            print(f"Source Language: '{source_lang.strip()}'")
            print(f"Target Language: '{target_lang.strip()}'")
        else:
            print("Parse failed - not enough parts")
    except Exception as e:
        print(f"Parse error: {e}")
    
    print()
    
    # Test với return_language_info=False
    print("=== WITHOUT LANGUAGE INFO (Compatibility) ===")
    if '|' in mock_response:
        try:
            parts = mock_response.split('|', 2)
            if len(parts) == 3:
                result = parts[2].strip()  # Chỉ lấy translated text
                print(f"Translated only: '{result}'")
            elif len(parts) == 2:
                result = parts[1].strip()  # Fallback nếu chỉ có 2 phần
                print(f"Translated only (fallback): '{result}'")
        except Exception as e:
            print(f"Parse error: {e}")
    else:
        print(f"No pipe found, return as-is: '{mock_response}'")

if __name__ == "__main__":
    test_parse_logic()
