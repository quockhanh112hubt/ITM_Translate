#!/usr/bin/env python3
"""
Performance comparison test for translate vs replace functions

This script tests the performance difference between:
1. _on_activate_translate: 2 AI calls (language detection + translation)
2. _on_activate_replace: 1 AI call (translation only)
"""

import sys
import os
import time
import threading

# Add the parent directory to sys.path to import ITM_Translate modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_translate_vs_replace_performance():
    """Test performance difference between translate popup and replace functions"""
    print("=" * 70)
    print("🚀 TRANSLATE vs REPLACE PERFORMANCE TEST")
    print("=" * 70)
    print("📊 Testing the optimization:")
    print("   • Translate Popup: 2 AI calls (detect language + translate)")
    print("   • Replace Function: 1 AI call (translate only)")
    print("=" * 70)
    
    try:
        from core.translator import translate_text
        
        test_text = "Hello world, this is a test translation."
        
        # Test 1: Translate popup mode (2 AI calls)
        print("\n📋 TEST 1: Translate Popup Mode (2 AI calls)")
        print("-" * 50)
        print("🔄 This simulates what happens when user presses Ctrl+Q")
        print("   Step 1: Detect language")
        print("   Step 2: Translate text") 
        print("   Step 3: Show popup with language info")
        
        start_time = time.time()
        
        try:
            result_with_lang_info = translate_text(
                test_text,
                "Any Language",  # Auto-detect 
                "Vietnamese",    # Target
                "Chinese",       # Fallback
                return_language_info=True  # This triggers language detection
            )
            elapsed_translate = time.time() - start_time
            
            if isinstance(result_with_lang_info, tuple):
                translated_text, source_lang, target_lang = result_with_lang_info
                print(f"✅ Translate popup completed in {elapsed_translate:.2f}s")
                print(f"   📝 Text: {translated_text[:30]}...")
                print(f"   🌐 Direction: {source_lang} → {target_lang}")
            else:
                print(f"⚠️ Translate popup returned single result: {elapsed_translate:.2f}s")
                
        except Exception as e:
            elapsed_translate = time.time() - start_time
            print(f"❌ Translate popup failed after {elapsed_translate:.2f}s: {e}")
            elapsed_translate = float('inf')  # Set to infinity for comparison
        
        # Small delay between tests
        time.sleep(1)
        
        # Test 2: Replace mode (1 AI call)
        print("\n📋 TEST 2: Replace Mode (1 AI call)")
        print("-" * 40)
        print("🔄 This simulates what happens when user presses Ctrl+D")
        print("   Step 1: Translate text directly")
        print("   Step 2: Replace selected text")
        
        start_time = time.time()
        
        try:
            result_replace = translate_text(
                test_text,
                "Any Language",  # Auto-detect
                "Vietnamese",    # Target  
                "Chinese",       # Fallback
                return_language_info=False  # Skip language detection for speed
            )
            elapsed_replace = time.time() - start_time
            
            print(f"✅ Replace mode completed in {elapsed_replace:.2f}s")
            print(f"   📝 Text: {result_replace[:30]}...")
            print(f"   🎯 Ready for immediate replacement")
                
        except Exception as e:
            elapsed_replace = time.time() - start_time
            print(f"❌ Replace mode failed after {elapsed_replace:.2f}s: {e}")
            elapsed_replace = float('inf')  # Set to infinity for comparison
        
        # Performance comparison
        print("\n" + "=" * 70)
        print("📊 PERFORMANCE COMPARISON")
        print("=" * 70)
        
        if elapsed_translate != float('inf') and elapsed_replace != float('inf'):
            time_saved = elapsed_translate - elapsed_replace
            percent_improvement = (time_saved / elapsed_translate) * 100
            
            print(f"⏱️  Translate Popup (2 AI calls): {elapsed_translate:.2f}s")
            print(f"⚡ Replace Mode (1 AI call):    {elapsed_replace:.2f}s")
            print(f"💾 Time Saved:                  {time_saved:.2f}s")
            print(f"📈 Performance Improvement:     {percent_improvement:.1f}%")
            
            if time_saved > 0:
                print(f"\n🎉 SUCCESS: Replace mode is {percent_improvement:.1f}% faster!")
                print(f"   This means users will experience:")
                print(f"   • Faster text replacement")
                print(f"   • Reduced API usage")
                print(f"   • Better overall responsiveness")
            else:
                print(f"\n⚠️ Unexpected: Replace mode took longer than expected")
        else:
            print("❌ Could not complete performance comparison due to errors")
        
        # Test 3: Multiple rapid replacements simulation
        print(f"\n📋 TEST 3: Rapid Replace Operations")
        print("-" * 40)
        print("🔄 Simulating user doing multiple quick replacements")
        
        test_texts = [
            "Good morning",
            "Thank you very much", 
            "How are you today?",
            "See you later"
        ]
        
        total_start = time.time()
        successful_replacements = 0
        
        for i, text in enumerate(test_texts, 1):
            print(f"   Replace {i}/4: {text}")
            try:
                start = time.time()
                result = translate_text(
                    text,
                    "Any Language",
                    "Vietnamese", 
                    "Chinese",
                    return_language_info=False
                )
                elapsed = time.time() - start
                print(f"     ✅ {elapsed:.2f}s → {result[:20]}...")
                successful_replacements += 1
            except Exception as e:
                print(f"     ❌ Failed: {e}")
        
        total_elapsed = time.time() - total_start
        avg_per_replacement = total_elapsed / len(test_texts) if test_texts else 0
        
        print(f"\n📊 Rapid replacement results:")
        print(f"   • Total time: {total_elapsed:.2f}s")
        print(f"   • Average per replacement: {avg_per_replacement:.2f}s")
        print(f"   • Success rate: {successful_replacements}/{len(test_texts)}")
        
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("Make sure you're running this from the ITM_Translate directory")
    
    print("\n" + "=" * 70)
    print("🏁 PERFORMANCE TEST COMPLETED")
    print("=" * 70)
    print("💡 Optimization Summary:")
    print("   • Replace functions now skip language detection")
    print("   • This reduces AI API calls by 50% for replace operations")
    print("   • Users get faster text replacement experience")
    print("   • Translate popups still show language info when needed")
    print("=" * 70)

if __name__ == "__main__":
    test_translate_vs_replace_performance()
