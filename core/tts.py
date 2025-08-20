"""
Text-to-Speech Module - ITM Translate
Provides text-to-speech functionality using Edge-TTS (primary) with Windows SAPI fallback
"""

import threading
import sys
import os
import asyncio
import tempfile
import html
import subprocess
from typing import Optional, Dict

# TTS Engine availability check
TTS_AVAILABLE = False
tts_engine = None
edge_tts_available = False

# TTS Control State
tts_is_playing = False
tts_current_process = None
tts_stop_requested = False
tts_generation_complete_callback = None

# Edge-TTS voice mapping (Neural voices for better quality)
EDGE_VOICE_MAPPING = {
    # Vietnamese
    'vietnamese': 'vi-VN-HoaiMyNeural',
    'vi': 'vi-VN-HoaiMyNeural',
    'tiếng việt': 'vi-VN-HoaiMyNeural',
    
    # English
    'english': 'en-US-JennyNeural',
    'en': 'en-US-JennyNeural',
    'en-us': 'en-US-JennyNeural',
    'en-gb': 'en-GB-SoniaNeural',
    
    # Korean
    'korean': 'ko-KR-SunHiNeural',
    'ko': 'ko-KR-SunHiNeural',
    'ko-kr': 'ko-KR-SunHiNeural',
    
    # Chinese
    'chinese': 'zh-CN-XiaoxiaoNeural',
    'zh': 'zh-CN-XiaoxiaoNeural',
    'zh-cn': 'zh-CN-XiaoxiaoNeural',
    'zh-tw': 'zh-TW-HsiaoChenNeural',
    'mandarin': 'zh-CN-XiaoxiaoNeural',
    
    # Japanese
    'japanese': 'ja-JP-NanamiNeural',
    'ja': 'ja-JP-NanamiNeural',
    'ja-jp': 'ja-JP-NanamiNeural',
    
    # Indonesian
    'indonesian': 'id-ID-GadisNeural',
    'id': 'id-ID-GadisNeural',
    'id-id': 'id-ID-GadisNeural',
    
    # French
    'french': 'fr-FR-DeniseNeural',
    'fr': 'fr-FR-DeniseNeural',
    'fr-fr': 'fr-FR-DeniseNeural',
    
    # German
    'german': 'de-DE-KatjaNeural',
    'de': 'de-DE-KatjaNeural',
    'de-de': 'de-DE-KatjaNeural',
    
    # Spanish
    'spanish': 'es-ES-ElviraNeural',
    'es': 'es-ES-ElviraNeural',
    'es-es': 'es-ES-ElviraNeural',
    
    # Russian
    'russian': 'ru-RU-SvetlanaNeural',
    'ru': 'ru-RU-SvetlanaNeural',
    'ru-ru': 'ru-RU-SvetlanaNeural',
    
    # Thai
    'thai': 'th-TH-PremwadeeNeural',
    'th': 'th-TH-PremwadeeNeural',
    'th-th': 'th-TH-PremwadeeNeural',
}

# Check for edge-tts availability
try:
    import edge_tts
    edge_tts_available = True
    TTS_AVAILABLE = True
except ImportError:
    pass

# Fallback options
if not TTS_AVAILABLE:
    try:
        import pyttsx3
        TTS_AVAILABLE = True
    except ImportError:
        try:
            import win32com.client
            TTS_AVAILABLE = True
        except ImportError:
            TTS_AVAILABLE = False

def get_edge_voice(language_hint):
    """Get appropriate Edge-TTS voice for language"""
    if not language_hint:
        return EDGE_VOICE_MAPPING['en']  # Default to English
        
    language_clean = language_hint.lower().strip()
    
    # Direct match
    if language_clean in EDGE_VOICE_MAPPING:
        return EDGE_VOICE_MAPPING[language_clean]
    
    # Try base language (e.g., 'en' from 'en-us')
    base_lang = language_clean.split('-')[0]
    if base_lang in EDGE_VOICE_MAPPING:
        return EDGE_VOICE_MAPPING[base_lang]
    
    # Default fallback
    return EDGE_VOICE_MAPPING['en']

def create_ssml(text, rate="+0%", pitch="+0%"):
    """Create SSML for edge-tts with proper escaping"""
    escaped_text = html.escape(text, quote=False)
    
    # Simple SSML without prosody if default values
    if rate == "+0%" and pitch == "+0%":
        return escaped_text
    
    # SSML with prosody
    return f'<prosody rate="{rate}" pitch="{pitch}">{escaped_text}</prosody>'

async def speak_with_edge_tts(text, language_hint=None):
    """Speak text using Edge-TTS (async) with improved error handling"""
    global tts_stop_requested, tts_current_process
    
    try:
        voice = get_edge_voice(language_hint)
        ssml = create_ssml(text)
        
        # Check for stop request before starting
        if tts_stop_requested:

            return False
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        # Generate speech with timeout
        try:
            communicate = edge_tts.Communicate(text=ssml, voice=voice)
            
            # Use asyncio.wait_for to add timeout for speech generation
            generation_timeout = min(len(text) / 10, 60)  # Max 60s for generation
            
            await asyncio.wait_for(communicate.save(tmp_path), timeout=generation_timeout)
            
            if tts_stop_requested:

                try:
                    os.unlink(tmp_path)
                except:
                    pass
                return False
            
        except asyncio.TimeoutError:
            try:
                os.unlink(tmp_path)
            except:
                pass
            return False
        except Exception as gen_error:
            try:
                os.unlink(tmp_path)
            except:
                pass
            return False
        
        # Play audio without showing any UI
        try:
            # Audio generation complete - notify UI to cancel generation timeout
            global tts_generation_complete_callback
            if tts_generation_complete_callback:
                try:
                    tts_generation_complete_callback()
                except Exception as cb_error:
                    pass
            
            # Use Windows built-in winsound (no additional dependencies)
            import winsound
            # Convert MP3 to WAV for winsound compatibility
            # Actually, let's save directly as WAV from edge-tts
            
            # Edge-TTS saves as MP3 by default, we need to handle that
            # Use a simpler approach - PowerShell with no window
            import subprocess
            
            # Use PowerShell to play audio silently (no window)
            powershell_cmd = f'''
            Add-Type -AssemblyName presentationCore
            $mediaPlayer = New-Object system.windows.media.mediaplayer
            $mediaPlayer.open([uri]"{tmp_path}")
            $mediaPlayer.Play()
            Start-Sleep 1
            while($mediaPlayer.NaturalDuration.HasTimeSpan -eq $false) {{
                Start-Sleep 0.1
            }}
            $duration = $mediaPlayer.NaturalDuration.TimeSpan.TotalSeconds
            Start-Sleep $duration
            $mediaPlayer.Stop()
            $mediaPlayer.Close()
            '''
            
            # Run PowerShell command hidden and track process
            tts_current_process = subprocess.Popen([
                'powershell', '-WindowStyle', 'Hidden', '-Command', powershell_cmd
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Poll for completion or stop request (more responsive)
            return_code = None
            while return_code is None and not tts_stop_requested:
                return_code = tts_current_process.poll()
                if return_code is None:
                    await asyncio.sleep(0.1)  # Check every 100ms for stop request
            
            # If stop was requested, terminate process
            if tts_stop_requested and return_code is None:
                try:
                    tts_current_process.terminate()
                    await asyncio.sleep(0.2)  # Give time to terminate
                    if tts_current_process.poll() is None:
                        tts_current_process.kill()  # Force kill if needed
                except:
                    pass
            elif return_code == 0:
                pass
            else:
                # Fallback to simple approach
                if not tts_stop_requested:
                    import os
                    os.system(f'start /min "" "{tmp_path}" && timeout /t 3 /nobreak > nul')
                
        except Exception as play_error:

            # Last resort - but try to minimize window visibility
            import os
            os.system(f'powershell -WindowStyle Hidden "Start-Process \\"{tmp_path}\\" -WindowStyle Minimized"')
            await asyncio.sleep(3)  # Give time for playback
        
        # Clean up after a delay
        def cleanup():
            import time
            time.sleep(5)  # Wait longer for playback to complete
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        threading.Thread(target=cleanup, daemon=True).start()
        
        return True
        
    except Exception as e:

        return False

def speak_with_edge_tts_sync(text, language_hint=None):
    """Synchronous wrapper for edge-tts"""
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(speak_with_edge_tts(text, language_hint))
        loop.close()
        return result
    except Exception as e:

        return False

def initialize_tts():
    """Initialize TTS engine"""
    global tts_engine
    
    if not TTS_AVAILABLE:
        return False
    
    try:
        # Try Windows SAPI first (better for our use case)
        try:
            import win32com.client
            tts_engine = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Configure SAPI settings for better audio output
            try:
                # Set volume to maximum
                tts_engine.Volume = 100
                
                # Set normal speech rate
                tts_engine.Rate = 0
                
                # DON'T force specific audio output - let Windows use default device
                # This respects user's choice in Windows Sound settings
                outputs = tts_engine.GetAudioOutputs()
                if outputs.Count > 0:
                    # Use default audio output (Item 0) - respects Windows settings
                    # Don't set AudioOutput explicitly - let SAPI use system default
                    pass
                else:
                    pass
                        
            except Exception as config_error:
                pass
            
            # Test SAPI with simple text
            try:
                # tts_engine.Speak("TTS test successful", 1)
                return True
            except Exception as sapi_test_error:
                pass
                
        except Exception as sapi_error:
            # Fallback to pyttsx3
            try:
                import pyttsx3
                tts_engine = pyttsx3.init()
                
                # Configure speech rate and volume
                tts_engine.setProperty('rate', 150)  # Speed of speech
                tts_engine.setProperty('volume', 0.8)  # Volume (0.0 to 1.0)
                
                return True
                
            except Exception as pyttsx3_error:
                pass
                return False
                
    except Exception as e:
        return False
            
    except Exception as e:

        return False

def stop_tts():
    """
    Stop current TTS playback
    """
    global tts_is_playing, tts_current_process, tts_stop_requested

    tts_stop_requested = True
    tts_is_playing = False
    
    # Kill current Edge-TTS process if exists
    if tts_current_process:
        try:
            tts_current_process.terminate()

        except:
            pass
        tts_current_process = None
    
    # Stop SAPI if available
    if tts_engine and hasattr(tts_engine, 'stop'):
        try:
            tts_engine.stop()

        except:
            pass

def set_generation_complete_callback(callback):
    """Set callback to be called when TTS generation is complete and playback starts"""
    global tts_generation_complete_callback
    tts_generation_complete_callback = callback

def is_tts_playing():
    """
    Check if TTS is currently playing
    """
    return tts_is_playing

def speak_text(text, language_hint=None):
    """
    Speak the given text using TTS (Edge-TTS preferred, fallback to SAPI/pyttsx3)
    
    Args:
        text (str): Text to speak
        language_hint (str): Language hint for voice selection (optional)
    """
    global tts_is_playing, tts_stop_requested
    
    if not TTS_AVAILABLE:

        return False
    
    # Check if already playing
    if tts_is_playing:

        stop_tts()
        return False
    
    def _speak():
        global tts_is_playing, tts_stop_requested, tts_current_process
        
        try:
            # Set playing state
            tts_is_playing = True
            tts_stop_requested = False
            
            # Clean text for speech
            clean_text = clean_text_for_speech(text)
            
            if not clean_text.strip():

                return
            
            # Check for stop request before starting
            if tts_stop_requested:
                return

            if language_hint:
                pass

            # Try Edge-TTS first (best quality)
            if edge_tts_available and not tts_stop_requested:
                try:
                    success = speak_with_edge_tts_sync(clean_text, language_hint)
                    if success and not tts_stop_requested:
                        return
                    else:
                        pass
                except Exception as edge_error:
                    pass

            # Check for stop request before fallback
            if tts_stop_requested:
                pass

                return
            
            # Fallback to SAPI/pyttsx3
            if tts_engine is None:
                if not initialize_tts():

                    return
            
            # Set voice based on language hint if provided (for SAPI/pyttsx3)
            if language_hint and not tts_stop_requested:

                set_voice_by_language(language_hint)
            
            if tts_stop_requested:

                return

            # Use appropriate fallback TTS method
            if hasattr(tts_engine, 'say'):
                # pyttsx3 engine

                if not tts_stop_requested:
                    tts_engine.say(clean_text)
                    tts_engine.runAndWait()

            else:
                # Windows SAPI engine

                try:
                    if not tts_stop_requested:

                        tts_engine.Speak(clean_text, 0)  # 0 = synchronous

                except Exception as sapi_error:

                    # Try ASCII fallback
                    try:
                        if not tts_stop_requested:
                            ascii_text = clean_text.encode('ascii', errors='ignore').decode('ascii')
                            if ascii_text.strip():

                                tts_engine.Speak(ascii_text, 0)

                            else:
                                pass

                    except Exception as ascii_error:
                        pass

            if not tts_stop_requested:
                pass

            else:
                pass

        except Exception as e:
            pass

        finally:
            # Always reset state
            tts_is_playing = False
            tts_stop_requested = False
            tts_current_process = None
    
    # Run TTS in separate thread to avoid blocking UI
    threading.Thread(target=_speak, daemon=True).start()
    return True

def clean_text_for_speech(text):
    """
    Clean text for better speech output
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned text suitable for speech
    """
    if not text:
        return ""
    
    # Remove common formatting that doesn't speak well
    cleaned = text.strip()
    
    # Remove multiple newlines and replace with periods
    cleaned = cleaned.replace('\n\n', '. ')
    cleaned = cleaned.replace('\n', '. ')
    
    # Remove excessive whitespace
    cleaned = ' '.join(cleaned.split())
    
    # Remove some special characters that don't speak well
    replacements = {
        '—': '-',
        '–': '-',
        ''': "'",
        ''': "'",
        '"': '"',
        '"': '"',
        '…': '...',
        '→': ' to ',
        '←': ' from ',
        '↔': ' and ',
        '***': '',
        '━': '',
        '─': '',
        '│': '',
        '├': '',
        '└': '',
        '🔊': '',
        '📝': '',
        '✅': '',
        '❌': '',
        '⚠️': '',
        '🎯': '',
        '📊': '',
    }
    
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    # Remove email-like patterns and timestamps that are hard to pronounce
    import re
    
    # Remove timestamps like [9:08 AM] or (9:08 AM)
    cleaned = re.sub(r'\[[\d:]+\s*[AP]M\]', '', cleaned)
    cleaned = re.sub(r'\([\d:]+\s*[AP]M\)', '', cleaned)
    
    # Remove email-like patterns [@username]
    cleaned = re.sub(r'@\w+', '', cleaned)
    
    # Remove brackets with Korean/Chinese names that are hard to pronounce
    cleaned = re.sub(r'\[[^\]]*[가-힣][^\]]*\]', '', cleaned)
    cleaned = re.sub(r'\[[^\]]*[一-龯][^\]]*\]', '', cleaned)
    
    # Clean up multiple spaces again
    cleaned = ' '.join(cleaned.split())
    
    # If text is too short after cleaning, use original but simplified
    if len(cleaned.strip()) < 5 and len(text.strip()) > 5:
        # Keep original but remove most problematic characters
        cleaned = text
        for old, new in [('***', ''), ('━', ''), ('→', ' to ')]:
            cleaned = cleaned.replace(old, new)
        cleaned = ' '.join(cleaned.split())
    
    return cleaned

def stop_speech():
    """Stop current speech (if supported by engine)"""
    try:
        if tts_engine and hasattr(tts_engine, 'stop'):
            tts_engine.stop()

            return True
    except Exception as e:
        pass

    return False

def get_available_voices():
    """Get list of available voices (if supported)"""
    try:
        if not tts_engine:
            if not initialize_tts():
                return []
        
        if hasattr(tts_engine, 'getProperty'):
            # pyttsx3 engine
            voices = tts_engine.getProperty('voices')
            return [voice.id for voice in voices] if voices else []
        
        # For Windows SAPI, this is more complex, return empty for now
        return []
        
    except Exception as e:

        return []

def set_voice_by_language(language):
    """
    Set voice based on language hint
    
    Args:
        language (str): Language code or name
    """
    try:
        if not tts_engine:
            return False
        
        # Language mapping for voice selection
        language_voice_mapping = {
            # English
            'english': ['english', 'en-us', 'en-gb', 'david', 'zira'],
            'en': ['english', 'en-us', 'en-gb', 'david', 'zira'],
            
            # Vietnamese  
            'vietnamese': ['vietnamese', 'vi-vn', 'vietnam'],
            'vi': ['vietnamese', 'vi-vn', 'vietnam'],
            'tiếng việt': ['vietnamese', 'vi-vn', 'vietnam'],
            
            # Chinese
            'chinese': ['chinese', 'zh-cn', 'zh-tw', 'mandarin'],
            'zh': ['chinese', 'zh-cn', 'zh-tw', 'mandarin'],
            'zh-cn': ['chinese', 'zh-cn', 'mandarin'],
            'zh-tw': ['chinese', 'zh-tw', 'taiwan'],
            
            # Japanese
            'japanese': ['japanese', 'ja-jp', 'japan'],
            'ja': ['japanese', 'ja-jp', 'japan'],
            
            # Korean
            'korean': ['korean', 'ko-kr', 'korea'],
            'ko': ['korean', 'ko-kr', 'korea'],
            
            # French
            'french': ['french', 'fr-fr', 'france'],
            'fr': ['french', 'fr-fr', 'france'],
            
            # German
            'german': ['german', 'de-de', 'deutsch'],
            'de': ['german', 'de-de', 'deutsch'],
            
            # Spanish
            'spanish': ['spanish', 'es-es', 'espanol'],
            'es': ['spanish', 'es-es', 'espanol'],
            
            # Russian
            'russian': ['russian', 'ru-ru', 'russia'],
            'ru': ['russian', 'ru-ru', 'russia'],
            
            # Thai
            'thai': ['thai', 'th-th', 'thailand'],
            'th': ['thai', 'th-th', 'thailand'],
        }
        
        # Get available voices
        if hasattr(tts_engine, 'GetVoices'):
            voices = tts_engine.GetVoices()

            # Clean language input
            language_clean = language.lower().strip()
            
            # Find matching language keywords
            target_keywords = []
            for lang_key, keywords in language_voice_mapping.items():
                if language_clean == lang_key or language_clean in keywords:
                    target_keywords = keywords
                    break
            
            if not target_keywords:

                return False
            
            # Search for matching voice
            for i in range(voices.Count):
                voice = voices.Item(i)
                voice_desc = voice.GetDescription().lower()

                # Check if voice description contains target language keywords
                for keyword in target_keywords:
                    if keyword in voice_desc:
                        try:
                            tts_engine.Voice = voice

                            return True
                        except Exception as set_error:

                            continue

            return False
        
        return False
        
    except Exception as e:

        return False

# Initialize TTS on module load
if TTS_AVAILABLE:
    initialize_tts()
