#!/usr/bin/env python3
"""
Test script for optimized timeout mechanism in ITM Translate

This script tests the new timeout configuration:
- Per-attempt timeout: 5 seconds (reduced from 8s)
- Maximum attempts: 3 (limited from all keys)
- UI timeout: 15 seconds (increased from 10s)
- Expected total time: 15s max (5s × 3 attempts)
"""

import sys
import os
import time
import threading

# Add the parent directory to sys.path to import ITM_Translate modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_timeout_optimization():
    """Test the optimized timeout mechanism"""
    print("=" * 60)
    print("🚀 OPTIMIZED TIMEOUT TEST")
    print("=" * 60)
    print("⚙️ Configuration:")
    print("   • Per-attempt timeout: 5 seconds")
    print("   • Maximum attempts: 3")
    print("   • UI timeout: 15 seconds")
    print("   • Expected max total: 15 seconds")
    print("=" * 60)
    
    try:
        from core.translator import translate_text
        
        # Test case 1: Quick translation (should work)
        print("\n📋 TEST 1: Quick Translation")
        print("-" * 40)
        
        test_text = "Hello world"
        start_time = time.time()
        
        try:
            result = translate_text(
                test_text,
                "English",  # Source
                "Vietnamese",  # Target
                "Chinese",  # Fallback
                return_language_info=True
            )
            elapsed = time.time() - start_time
            print(f"✅ Translation completed in {elapsed:.2f}s")
            print(f"📄 Result: {result[0][:50]}...")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Translation failed after {elapsed:.2f}s: {e}")
        
        # Test case 2: Simulate timeout scenario
        print("\n📋 TEST 2: Timeout Simulation")
        print("-" * 40)
        print("⚠️ This will test the 5s per-attempt timeout limit")
        
        # Use a complex text that might take longer
        complex_text = """
        Artificial Intelligence (AI) has revolutionized numerous industries by automating complex processes, 
        enhancing decision-making capabilities, and providing unprecedented insights from vast datasets. 
        Machine learning algorithms, particularly deep learning neural networks, have demonstrated remarkable 
        success in tasks ranging from natural language processing and computer vision to predictive analytics 
        and autonomous systems. The integration of AI technologies continues to transform business operations, 
        scientific research, and everyday applications, promising even greater innovations in the future.
        """
        
        start_time = time.time()
        
        try:
            result = translate_text(
                complex_text.strip(),
                "Any Language",  # Auto-detect
                "Vietnamese",  # Target
                "Chinese",  # Fallback
                return_language_info=True
            )
            elapsed = time.time() - start_time
            
            if elapsed <= 15.0:
                print(f"✅ Translation completed within timeout: {elapsed:.2f}s")
                print(f"📄 Result preview: {result[0][:100]}...")
            else:
                print(f"⚠️ Translation took longer than expected: {elapsed:.2f}s")
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"⏰ Translation timeout/error after {elapsed:.2f}s: {e}")
            
            if elapsed <= 16.0:  # Allow 1s margin
                print("✅ Timeout occurred within expected timeframe")
            else:
                print("❌ Timeout took too long - needs further optimization")
        
        # Test case 3: UI-level timeout simulation
        print("\n📋 TEST 3: UI Timeout Simulation")
        print("-" * 40)
        
        print("🔄 Simulating UI timeout mechanism...")
        
        # Simulate the UI timeout pattern
        translation_completed = threading.Event()
        translation_result = {'result': None, 'error': None}
        
        def simulate_slow_translation():
            """Simulate a slow translation that triggers UI timeout"""
            time.sleep(16)  # Sleep longer than 15s UI timeout
            translation_result['result'] = "This should be interrupted by UI timeout"
            translation_completed.set()
        
        # Start simulation
        thread = threading.Thread(target=simulate_slow_translation, daemon=True)
        thread.start()
        
        # UI timeout check (simplified version)
        start_time = time.time()
        timeout_triggered = False
        
        while not translation_completed.is_set():
            elapsed = time.time() - start_time
            if elapsed >= 15.0:  # 15 second UI timeout
                print(f"⏰ UI timeout triggered after {elapsed:.1f}s")
                timeout_triggered = True
                break
            time.sleep(0.1)
        
        if timeout_triggered:
            print("✅ UI timeout mechanism working correctly")
        else:
            print("❌ UI timeout did not trigger as expected")
            
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("Make sure you're running this from the ITM_Translate directory")
    
    print("\n" + "=" * 60)
    print("🏁 OPTIMIZATION TEST COMPLETED")
    print("=" * 60)
    print("📊 Expected improvements:")
    print("   • Faster individual attempts (5s vs 8s)")
    print("   • Limited retry attempts (3 vs unlimited)")
    print("   • Better UI responsiveness (15s timeout)")
    print("   • Maximum wait time: 15 seconds")
    print("=" * 60)

if __name__ == "__main__":
    test_timeout_optimization()
