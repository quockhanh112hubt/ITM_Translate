import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class TranslationHistory:
    """Quản lý lịch sử dịch thuật với search, export và import capabilities"""
    
    def __init__(self, max_history_size=500):
        self.history_file = "translation_history.json"
        self.max_history_size = max_history_size
        self.history: List[Dict] = []
        self.lock = threading.Lock()
        self.load_history()
    
    def load_history(self):
        """Load lịch sử từ file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    # Validate and clean old entries
                    self.history = [entry for entry in self.history if self._validate_entry(entry)]
                    print(f"📚 [HISTORY] Loaded {len(self.history)} translation entries")
        except Exception as e:
            print(f"❌ [HISTORY] Error loading history: {e}")
            self.history = []
    
    def save_history(self):
        """Lưu lịch sử vào file"""
        try:
            with self.lock:
                # Limit history size
                if len(self.history) > self.max_history_size:
                    # Keep only the most recent entries
                    self.history = self.history[-self.max_history_size:]
                
                data = {
                    'history': self.history,
                    'metadata': {
                        'version': '1.0',
                        'last_updated': datetime.now().isoformat(),
                        'total_entries': len(self.history)
                    }
                }
                
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ [HISTORY] Error saving history: {e}")
    
    def add_translation(self, original_text: str, translated_text: str, 
                       source_lang: str, target_lang: str, 
                       provider: str = "unknown", model: str = "auto",
                       translation_time: float = 0.0, mode: str = "popup"):
        """Thêm bản dịch mới vào lịch sử"""
        try:
            with self.lock:
                entry = {
                    'id': int(time.time() * 1000),  # Unique ID based on timestamp
                    'timestamp': datetime.now().isoformat(),
                    'original_text': original_text.strip(),
                    'translated_text': translated_text.strip(),
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'provider': provider,
                    'model': model,
                    'translation_time': translation_time,
                    'mode': mode,  # popup, replace, floating
                    'character_count': len(original_text),
                    'word_count': len(original_text.split()),
                }
                
                # Check for duplicates (same text translated recently)
                if not self._is_duplicate(entry):
                    self.history.append(entry)
                    print(f"📚 [HISTORY] Added translation: {original_text[:30]}... → {translated_text[:30]}...")
                    
                    # Save asynchronously to avoid blocking
                    threading.Thread(target=self.save_history, daemon=True).start()
                else:
                    print(f"📚 [HISTORY] Skipped duplicate translation")
                    
        except Exception as e:
            print(f"❌ [HISTORY] Error adding translation: {e}")
    
    def _is_duplicate(self, new_entry: Dict) -> bool:
        """Kiểm tra xem entry có trùng lặp với entries gần đây không"""
        # Check last 10 entries for duplicates within 1 minute
        recent_entries = self.history[-10:]
        current_time = datetime.fromisoformat(new_entry['timestamp'])
        
        for entry in recent_entries:
            try:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                time_diff = current_time - entry_time
                
                if (time_diff < timedelta(minutes=1) and 
                    entry['original_text'] == new_entry['original_text'] and
                    entry['source_lang'] == new_entry['source_lang'] and
                    entry['target_lang'] == new_entry['target_lang']):
                    return True
            except Exception:
                continue
        
        return False
    
    def _validate_entry(self, entry: Dict) -> bool:
        """Validate entry có đủ fields cần thiết không"""
        required_fields = ['original_text', 'translated_text', 'timestamp', 'source_lang', 'target_lang']
        return all(field in entry for field in required_fields)
    
    def search_history(self, query: str, limit: int = 50) -> List[Dict]:
        """Tìm kiếm trong lịch sử dịch thuật"""
        try:
            query_lower = query.lower().strip()
            if not query_lower:
                return self.get_recent_translations(limit)
            
            results = []
            for entry in reversed(self.history):  # Newest first
                # Search in original text, translated text
                if (query_lower in entry['original_text'].lower() or 
                    query_lower in entry['translated_text'].lower() or
                    query_lower in entry.get('source_lang', '').lower() or
                    query_lower in entry.get('target_lang', '').lower()):
                    results.append(entry)
                    
                if len(results) >= limit:
                    break
            
            print(f"📚 [HISTORY] Search '{query}' found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"❌ [HISTORY] Error searching history: {e}")
            return []
    
    def get_recent_translations(self, limit: int = 20) -> List[Dict]:
        """Lấy các bản dịch gần đây nhất"""
        try:
            return list(reversed(self.history[-limit:]))  # Newest first
        except Exception as e:
            print(f"❌ [HISTORY] Error getting recent translations: {e}")
            return []
    
    def get_entry_by_id(self, entry_id: str) -> Dict:
        """Lấy entry theo ID"""
        try:
            entry_id = int(entry_id) if isinstance(entry_id, str) else entry_id
            for entry in self.history:
                if entry.get('id') == entry_id:
                    return entry
            return None
        except Exception as e:
            print(f"❌ [HISTORY] Error getting entry by ID: {e}")
            return None
    
    def delete_entry(self, entry_id: str) -> bool:
        """Xóa entry theo ID"""
        try:
            entry_id = int(entry_id) if isinstance(entry_id, str) else entry_id
            with self.lock:
                for i, entry in enumerate(self.history):
                    if entry.get('id') == entry_id:
                        del self.history[i]
                        self.save_history()
                        print(f"🗑️ [HISTORY] Deleted entry ID: {entry_id}")
                        return True
                return False
        except Exception as e:
            print(f"❌ [HISTORY] Error deleting entry: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Lấy thống kê về lịch sử dịch thuật"""
        try:
            if not self.history:
                return {}
            
            stats = {
                'total_translations': len(self.history),
                'total_characters': sum(entry.get('character_count', 0) for entry in self.history),
                'total_words': sum(entry.get('word_count', 0) for entry in self.history),
                'languages_used': {},
                'providers_used': {},
                'modes_used': {},
                'avg_translation_time': 0,
                'translations_today': 0,
                'translations_this_week': 0,
                'translations_this_month': 0
            }
            
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            total_time = 0
            time_count = 0
            
            for entry in self.history:
                try:
                    # Language stats
                    source_lang = entry.get('source_lang', 'unknown')
                    target_lang = entry.get('target_lang', 'unknown')
                    lang_pair = f"{source_lang} → {target_lang}"
                    stats['languages_used'][lang_pair] = stats['languages_used'].get(lang_pair, 0) + 1
                    
                    # Provider stats
                    provider = entry.get('provider', 'unknown')
                    stats['providers_used'][provider] = stats['providers_used'].get(provider, 0) + 1
                    
                    # Mode stats
                    mode = entry.get('mode', 'unknown')
                    stats['modes_used'][mode] = stats['modes_used'].get(mode, 0) + 1
                    
                    # Time stats
                    translation_time = entry.get('translation_time', 0)
                    if translation_time > 0:
                        total_time += translation_time
                        time_count += 1
                    
                    # Date-based stats
                    entry_date = datetime.fromisoformat(entry['timestamp']).date()
                    if entry_date == today:
                        stats['translations_today'] += 1
                    if entry_date >= week_ago:
                        stats['translations_this_week'] += 1
                    if entry_date >= month_ago:
                        stats['translations_this_month'] += 1
                        
                except Exception:
                    continue
            
            if time_count > 0:
                stats['avg_translation_time'] = total_time / time_count
            
            return stats
            
        except Exception as e:
            print(f"❌ [HISTORY] Error getting statistics: {e}")
            return {}
    
    def export_history(self, filepath: str, format: str = 'json') -> bool:
        """Export lịch sử ra file"""
        try:
            if format.lower() == 'json':
                data = {
                    'export_info': {
                        'exported_at': datetime.now().isoformat(),
                        'total_entries': len(self.history),
                        'format': 'json'
                    },
                    'statistics': self.get_statistics(),
                    'history': self.history
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
            elif format.lower() == 'csv':
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Original Text', 'Translated Text', 'Source Language', 
                                   'Target Language', 'Provider', 'Mode', 'Translation Time'])
                    
                    for entry in self.history:
                        writer.writerow([
                            entry.get('timestamp', ''),
                            entry.get('original_text', ''),
                            entry.get('translated_text', ''),
                            entry.get('source_lang', ''),
                            entry.get('target_lang', ''),
                            entry.get('provider', ''),
                            entry.get('mode', ''),
                            entry.get('translation_time', 0)
                        ])
            
            print(f"📚 [HISTORY] Exported {len(self.history)} entries to {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ [HISTORY] Error exporting history: {e}")
            return False
    
    def clear_history(self, confirm: bool = False) -> bool:
        """Xóa toàn bộ lịch sử"""
        if not confirm:
            return False
            
        try:
            with self.lock:
                self.history.clear()
                self.save_history()
                print(f"🗑️ [HISTORY] History cleared")
                return True
        except Exception as e:
            print(f"❌ [HISTORY] Error clearing history: {e}")
            return False
    
    def remove_entry(self, entry_id: int) -> bool:
        """Xóa một entry cụ thể"""
        try:
            with self.lock:
                original_count = len(self.history)
                self.history = [entry for entry in self.history if entry.get('id') != entry_id]
                
                if len(self.history) < original_count:
                    self.save_history()
                    print(f"🗑️ [HISTORY] Removed entry {entry_id}")
                    return True
                else:
                    print(f"❌ [HISTORY] Entry {entry_id} not found")
                    return False
        except Exception as e:
            print(f"❌ [HISTORY] Error removing entry: {e}")
            return False

# Global instance
translation_history = TranslationHistory()
