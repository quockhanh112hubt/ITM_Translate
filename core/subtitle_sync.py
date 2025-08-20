"""
Subtitle Sync Module - ITM Translate
Provides word-by-word highlighting during TTS playback (karaoke effect)
"""

import threading
import time
import re
from typing import List, Tuple, Optional, Callable

class SubtitleSync:
    """Handles synchronized text highlighting during TTS playback"""
    
    def __init__(self):
        self.text = ""
        self.original_text = ""  # Store original text for mapping
        self.words = []
        self.word_positions = []  # (start_char, end_char) for each word in cleaned text
        self.original_positions = []  # Mapped positions in original text
        self.current_word_index = 0
        self.is_active = False
        self.highlight_callback = None
        self.sync_thread = None
        self.stop_requested = False
        
    def prepare_text(self, text: str, original_text: str = None) -> List[Tuple[int, int, str]]:
        """
        Parse text into words exactly as TTS will speak them
        
        Args:
            text: Cleaned text for TTS (what will be spoken)
            original_text: Original text displayed in UI
        
        Returns: List of (start_pos, end_pos, word) in original text
        """
        self.text = text  # Cleaned text that TTS will read
        self.original_text = original_text or text
        self.words = []
        self.word_positions = []  # Positions in original text
        self.original_positions = []
        
        # Parse words from cleaned text (what TTS actually reads)
        import re
        
        # Split cleaned text into actual spoken words only
        # Remove punctuation that TTS doesn't speak
        spoken_text = re.sub(r'[^\w\s\u00C0-\u1EF9]', ' ', text)  # Keep only letters, numbers, Vietnamese chars
        spoken_words = spoken_text.split()  # Simple space split for spoken words
        
        # Find each spoken word in the original text and get its position
        search_start = 0
        
        for word in spoken_words:
            if not word.strip():
                continue
                
            # Find this word in original text, starting from search_start
            word_pos = self.original_text.lower().find(word.lower(), search_start)
            
            if word_pos != -1:
                # Found the word in original text
                word_end = word_pos + len(word)
                
                # Store word and its position in original text
                self.words.append(word)
                self.word_positions.append((word_pos, word_end))
                self.original_positions.append((word_pos, word_end))
                
                # Move search start to after this word
                search_start = word_end
            else:
                # Word not found in original - try approximate position
                if len(self.words) > 0:
                    # Use position after last found word
                    last_end = self.word_positions[-1][1]
                    approx_start = last_end + 1
                    approx_end = approx_start + len(word)
                else:
                    # First word - start at beginning
                    approx_start = 0
                    approx_end = len(word)
                
                self.words.append(word)
                self.word_positions.append((approx_start, approx_end))
                self.original_positions.append((approx_start, approx_end))
                search_start = approx_end
        
        return [(pos[0], pos[1], word) for pos, word in zip(self.original_positions, self.words)]
    
    def estimate_word_timing(self, total_duration: float) -> List[float]:
        """
        Estimate timing for each spoken word
        Only actual spoken words, no punctuation
        """
        if not self.words:
            return []
            
        # All words in self.words are actual spoken words (no punctuation)
        # Simple equal distribution with slight variation based on word length
        word_weights = []
        
        for word in self.words:
            # Weight based on word length (longer words take slightly more time)
            if len(word) <= 2:
                weight = 0.8  # Short words like "có", "là"
            elif len(word) <= 4:
                weight = 1.0  # Medium words
            else:
                weight = 1.0 + (len(word) - 4) * 0.1  # Longer words
                
            word_weights.append(weight)
        
        if not word_weights:
            return []
            
        total_weight = sum(word_weights)
        
        # Reserve 5% for start delay and 5% for end padding
        usable_duration = total_duration * 0.9
        start_delay = total_duration * 0.05
        
        # Distribute duration proportionally
        word_timings = []
        current_time = start_delay
        
        for weight in word_weights:
            word_duration = (weight / total_weight) * usable_duration
            word_timings.append(current_time)
            current_time += word_duration
            
        return word_timings
    
    def start_sync(self, duration: float, highlight_callback: Callable[[int, int], None]):
        """
        Start synchronized highlighting
        
        Args:
            duration: Total audio duration in seconds
            highlight_callback: Function to call for highlighting (start_pos, end_pos)
        """
        if not self.words or not highlight_callback:
            return
            
        self.highlight_callback = highlight_callback
        self.is_active = True
        self.stop_requested = False
        self.current_word_index = 0
        
        # Calculate word timings
        word_timings = self.estimate_word_timing(duration)
        
        # Start sync thread
        self.sync_thread = threading.Thread(
            target=self._sync_worker,
            args=(word_timings,),
            daemon=True
        )
        self.sync_thread.start()
    
    def _sync_worker(self, word_timings: List[float]):
        """Worker thread for synchronized highlighting"""
        start_time = time.time()
        
        for i, timing in enumerate(word_timings):
            if self.stop_requested:
                break
                
            # Wait until it's time for this word
            elapsed = time.time() - start_time
            wait_time = timing - elapsed
            
            if wait_time > 0:
                time.sleep(wait_time)
            
            if self.stop_requested:
                break
                
            # Highlight current word using original text positions
            if i < len(self.original_positions):
                start_pos, end_pos = self.original_positions[i]
                self.current_word_index = i
                
                if self.highlight_callback:
                    try:
                        self.highlight_callback(start_pos, end_pos)
                    except Exception:
                        pass  # Ignore callback errors
        
        # Clear highlighting when done
        if self.highlight_callback and not self.stop_requested:
            try:
                self.highlight_callback(-1, -1)  # Signal to clear highlight
            except Exception:
                pass
                
        self.is_active = False
    
    def stop_sync(self):
        """Stop synchronized highlighting"""
        self.stop_requested = True
        self.is_active = False
        
        if self.sync_thread and self.sync_thread.is_alive():
            # Give thread a moment to finish gracefully
            try:
                self.sync_thread.join(timeout=1.0)
            except Exception:
                pass
    
    def is_syncing(self) -> bool:
        """Check if sync is currently active"""
        return self.is_active and not self.stop_requested

# Global subtitle sync instance
subtitle_sync = SubtitleSync()

def prepare_subtitle_sync(text: str, original_text: str = None) -> List[Tuple[int, int, str]]:
    """Prepare text for subtitle sync with optional original text mapping"""
    return subtitle_sync.prepare_text(text, original_text)

def start_subtitle_sync(duration: float, highlight_callback: Callable[[int, int], None]):
    """Start subtitle synchronization"""
    subtitle_sync.start_sync(duration, highlight_callback)

def stop_subtitle_sync():
    """Stop subtitle synchronization"""
    subtitle_sync.stop_sync()

def is_subtitle_syncing() -> bool:
    """Check if subtitle sync is active"""
    return subtitle_sync.is_syncing()

def debug_word_parsing(text: str, original_text: str = None) -> List[Tuple[int, int, str]]:
    """Debug function to test word parsing"""
    sync = SubtitleSync()
    words_info = sync.prepare_text(text, original_text)
    
    print(f"Debug: TTS will read: '{text}'")
    print(f"Debug: UI displays: '{original_text or text}'")
    print(f"Debug: Parsed {len(words_info)} words:")
    for i, (start, end, word) in enumerate(words_info):
        actual_text = (original_text or text)[start:end]
        print(f"  [{i}] pos {start}-{end}: '{word}' -> highlights: '{actual_text}'")
    
    return words_info
