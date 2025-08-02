#!/usr/bin/env python3
"""
Test script for new smart replacement prompt

This script tests the new prompt that allows AI to decide translation direction automatically:
- If text is not in target language → translate to target language
- If text is in target language → translate to fallback language
"""

import sys
import os
import time

# Add the parent directory to sys.path to import ITM_Translate modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_smart_replacement_prompt():
    """Test the new smart replacement prompt logic"""
    print("=" * 70)
    print("🧠 SMART REPLACEMENT PROMPT TEST")
    print("=" * 70)
    print("🎯 Testing new replacement logic:")
    print("   • Vietnamese text → English (fallback)")
    print("   • English text → Vietnamese (target)")
    print("   • Other languages → Vietnamese (target)")
    print("=" * 70)
    
    try:
        from core.translator import translate_text
        
        # Test scenarios with different languages
        test_cases = [
            {
                "text": "Xin chào, bạn có khỏe không?",
                "expected_direction": "Vietnamese → English",
                "description": "Vietnamese text should go to English (fallback)"
            },
            {
                "text": "Hello, how are you today?", 
                "expected_direction": "English → Vietnamese",
                "description": "English text should go to Vietnamese (target)"
            },
            {
                "text": "¿Cómo estás hoy?",
                "expected_direction": "Spanish → Vietnamese", 
                "description": "Spanish text should go to Vietnamese (target)"
            },
            {
                "text": "こんにちは、元気ですか？",
                "expected_direction": "Japanese → Vietnamese",
                "description": "Japanese text should go to Vietnamese (target)"
            },
            {
                "text": "Bonjour, comment allez-vous?",
                "expected_direction": "French → Vietnamese",
                "description": "French text should go to Vietnamese (target)"
            }
        ]
        
        # Language settings for testing
        target_lang = "Tiếng Việt"      # Primary target
        fallback_lang = "English"       # Fallback when text is already in target
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 TEST {i}: {test_case['description']}")
            print("-" * 50)
            print(f"📝 Input: {test_case['text']}")
            print(f"🎯 Expected: {test_case['expected_direction']}")
            
            start_time = time.time()
            
            try:
                # Test REPLACE mode (return_language_info=False)
                result = translate_text(
                    test_case['text'],
                    "Any Language",  # Auto-detect source
                    target_lang,     # Primary target
                    fallback_lang,   # Fallback target
                    return_language_info=False  # Replace mode
                )
                
                elapsed = time.time() - start_time
                
                print(f"✅ Translation completed in {elapsed:.2f}s")
                print(f"📄 Result: {result}")
                
                # Try to determine actual direction based on result
                input_text = test_case['text']
                output_text = result
                
                # Simple heuristics to check translation direction
                is_input_vietnamese = any(char in input_text.lower() for char in ['ạ', 'ă', 'â', 'đ', 'ê', 'ô', 'ơ', 'ư'])
                is_output_vietnamese = any(char in output_text.lower() for char in ['ạ', 'ă', 'â', 'đ', 'ê', 'ô', 'ơ', 'ư'])
                
                if is_input_vietnamese and not is_output_vietnamese:
                    actual_direction = "Vietnamese → English"
                elif not is_input_vietnamese and is_output_vietnamese:
                    actual_direction = "Other → Vietnamese"  
                else:
                    actual_direction = "Unknown direction"
                
                print(f"🧭 Detected direction: {actual_direction}")
                
                if test_case['expected_direction'].split(' → ')[1] in actual_direction:
                    print("✅ Direction matches expectation!")
                else:
                    print("⚠️ Direction might not match expectation")
                
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ Translation failed after {elapsed:.2f}s: {e}")
        
        # Performance comparison test
        print(f"\n" + "=" * 70)
        print("⚡ PERFORMANCE COMPARISON")  
        print("=" * 70)
        
        test_text = "Hello world, this is a performance test."
        
        # Test 1: OLD METHOD (with language detection)
        print("\n📋 OLD METHOD: Translate Popup (with language detection)")
        print("-" * 55)
        
        start_time = time.time()
        try:
            old_result = translate_text(
                test_text,
                "Any Language",
                target_lang,
                fallback_lang,
                return_language_info=True  # Triggers language detection
            )
            old_time = time.time() - start_time
            
            if isinstance(old_result, tuple):
                translated, source, target = old_result
                print(f"✅ Completed in {old_time:.2f}s")
                print(f"📄 Result: {translated}")
                print(f"🌐 Direction: {source} → {target}")
            else:
                print(f"⚠️ Unexpected result format: {old_time:.2f}s")
        except Exception as e:
            old_time = time.time() - start_time
            print(f"❌ Failed after {old_time:.2f}s: {e}")
            old_time = float('inf')
        
        # Small delay
        time.sleep(1)
        
        # Test 2: NEW METHOD (smart replacement)
        print("\n📋 NEW METHOD: Smart Replace (no language detection)")
        print("-" * 55)
        
        start_time = time.time()
        try:
            new_result = translate_text(
                test_text,
                "Any Language", 
                target_lang,
                fallback_lang,
                return_language_info=False  # Smart replacement mode
            )
            new_time = time.time() - start_time
            
            print(f"✅ Completed in {new_time:.2f}s")
            print(f"📄 Result: {new_result}")
            print(f"🧠 Smart direction detection built into prompt")
        except Exception as e:
            new_time = time.time() - start_time
            print(f"❌ Failed after {new_time:.2f}s: {e}")
            new_time = float('inf')
        
        # Comparison
        if old_time != float('inf') and new_time != float('inf'):
            time_saved = old_time - new_time
            improvement = (time_saved / old_time) * 100
            
            print(f"\n📊 PERFORMANCE RESULTS:")
            print(f"   • Old method: {old_time:.2f}s")
            print(f"   • New method: {new_time:.2f}s")
            print(f"   • Time saved: {time_saved:.2f}s")
            print(f"   • Improvement: {improvement:.1f}%")
            
            if improvement > 0:
                print(f"\n🎉 SUCCESS: New method is {improvement:.1f}% faster!")
            else:
                print(f"\n⚠️ New method took longer than expected")
                
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("Make sure you're running this from the ITM_Translate directory")
    
    print("\n" + "=" * 70)
    print("🏁 SMART REPLACEMENT TEST COMPLETED")
    print("=" * 70)
    print("💡 Key Benefits:")
    print("   • AI automatically detects and chooses translation direction")
    print("   • No separate language detection call needed")
    print("   • Faster replacement operations")
    print("   • Simplified logic with better user experience")
    print("=" * 70)

if __name__ == "__main__":
    test_smart_replacement_prompt()
