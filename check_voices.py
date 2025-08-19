"""
Script to check available Windows SAPI voices
"""

print("🔍 Checking available Windows SAPI voices...")

try:
    import win32com.client
    
    # Create SAPI voice object
    voice = win32com.client.Dispatch("SAPI.SpVoice")
    voices = voice.GetVoices()
    
    print(f"📊 Total voices available: {voices.Count}")
    print("=" * 50)
    
    for i in range(voices.Count):
        voice_item = voices.Item(i)
        voice_desc = voice_item.GetDescription()
        
        print(f"Voice {i}: {voice_desc}")
        
        # Try to get additional voice info
        try:
            # Get voice attributes
            attrs = voice_item.GetAttribute("Language")
            if attrs:
                print(f"  Language: {attrs}")
            
            attrs = voice_item.GetAttribute("Gender")
            if attrs:
                print(f"  Gender: {attrs}")
                
            attrs = voice_item.GetAttribute("Age")
            if attrs:
                print(f"  Age: {attrs}")
                
        except Exception as attr_error:
            print(f"  (Could not get attributes: {attr_error})")
        
        print("-" * 30)
    
    # Test language detection from voice names
    print("\n🌐 Language detection test:")
    
    language_keywords = {
        'English': ['english', 'david', 'zira', 'en-us', 'en-gb'],
        'Chinese': ['chinese', 'zh-cn', 'zh-tw', 'mandarin'],
        'Japanese': ['japanese', 'ja-jp'],
        'Korean': ['korean', 'ko-kr'],
        'French': ['french', 'fr-fr'],
        'German': ['german', 'de-de'],
        'Spanish': ['spanish', 'es-es'],
        'Vietnamese': ['vietnamese', 'vi-vn'],
        'Russian': ['russian', 'ru-ru'],
        'Thai': ['thai', 'th-th']
    }
    
    for i in range(voices.Count):
        voice_desc = voices.Item(i).GetDescription().lower()
        detected_langs = []
        
        for lang, keywords in language_keywords.items():
            for keyword in keywords:
                if keyword in voice_desc:
                    detected_langs.append(lang)
                    break
        
        if detected_langs:
            print(f"Voice {i}: {voices.Item(i).GetDescription()} → {', '.join(detected_langs)}")
        else:
            print(f"Voice {i}: {voices.Item(i).GetDescription()} → Unknown language")
    
except Exception as e:
    print(f"❌ Error checking voices: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 Voice check completed")
