#!/usr/bin/env python3
"""
Test script để thêm sample data vào Translation History
và test History UI
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from core.translation_history import translation_history
import time

def add_sample_translations():
    """Thêm sample translations vào history"""
    samples = [
        {
            'original': 'Hello, how are you?',
            'translated': 'Xin chào, bạn khỏe không?',
            'source_lang': 'English',
            'target_lang': 'Vietnamese',
            'provider': 'gemini'
        },
        {
            'original': 'Tôi đang học lập trình Python',
            'translated': 'I am learning Python programming',
            'source_lang': 'Vietnamese',
            'target_lang': 'English',
            'provider': 'deepseek'
        },
        {
            'original': '안녕하세요, 만나서 반갑습니다',
            'translated': 'Xin chào, rất vui được gặp bạn',
            'source_lang': 'Korean',
            'target_lang': 'Vietnamese',
            'provider': 'gemini'
        },
        {
            'original': 'Thank you very much for your help',
            'translated': 'Cảm ơn bạn rất nhiều vì sự giúp đỡ',
            'source_lang': 'English',
            'target_lang': 'Vietnamese',
            'provider': 'claude'
        },
        {
            'original': 'Hôm nay thời tiết đẹp quá!',
            'translated': 'The weather is so beautiful today!',
            'source_lang': 'Vietnamese',
            'target_lang': 'English',
            'provider': 'gemini'
        }
    ]
    
    print("📚 Adding sample translations to history...")
    for i, sample in enumerate(samples):
        translation_history.add_translation(
            original_text=sample['original'],
            translated_text=sample['translated'],
            source_lang=sample['source_lang'],
            target_lang=sample['target_lang'],
            provider=sample['provider'],
            translation_time=0.5 + (i * 0.2),  # Vary translation times
            mode='test'
        )
        print(f"  ✅ Added: {sample['original'][:30]}...")
        time.sleep(0.1)  # Small delay between entries
    
    print(f"\n📊 Total translations in history: {len(translation_history.history)}")

def show_history_stats():
    """Hiển thị thống kê history"""
    stats = translation_history.get_statistics()
    print("\n📈 TRANSLATION STATISTICS:")
    print(f"  Total translations: {stats.get('total_translations', 0)}")
    print(f"  Total characters: {stats.get('total_characters', 0):,}")
    print(f"  Average time: {stats.get('average_time', 0):.2f}s")
    
    print("\n🤖 Providers:")
    for provider, count in stats.get('providers_used', {}).items():
        print(f"  {provider}: {count}")
    
    print("\n🌐 Language pairs:")
    for pair, count in stats.get('languages_used', {}).items():
        print(f"  {pair}: {count}")

if __name__ == "__main__":
    print("🧪 ITM Translate History Test Script")
    print("=" * 50)
    
    # Add sample data
    add_sample_translations()
    
    # Show stats
    show_history_stats()
    
    print("\n✨ Sample data added successfully!")
    print("📖 You can now open ITM Translate and check the History tab.")
    print("🎯 Test features: search, filter, statistics, export...")
