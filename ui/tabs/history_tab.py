import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import tempfile
import subprocess
import os
import sys
from datetime import datetime, timedelta
from core.translator import translation_history

class HistoryTab:
    def show_statistics(self):
        """Show detailed statistics window"""
        try:
            stats = translation_history.get_statistics()
            
            # Simple message box instead of complex window
            stats_text = f"""📊 TRANSLATION STATISTICS

🔢 Total Translations: {stats.get('total_translations', 0)}
⚡ Average Speed: {stats.get('average_time', 0):.2f} seconds

🤖 PROVIDERS:
{json.dumps(stats.get('providers_used', {}), indent=2)}

🌐 LANGUAGES:
{json.dumps(stats.get('languages_used', {}), indent=2)}
"""
            
            messagebox.showinfo("📊 Translation Statistics", stats_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load statistics: {e}")
            print(f"❌ [STATISTICS] Error: {e}")

    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame)
        self.frame.pack(fill='both', expand=True)  # Pack the frame into parent!
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="✅ History Tab Loaded Successfully", 
                                      foreground='green', font=('Segoe UI', 9))
        self.status_label.pack(pady=5)
        
        try:
            # Search and filter frame with colorful icons
            self.search_frame = ttk.LabelFrame(self.frame, text="🔍 Search & Filter", padding=10)
            self.search_frame.pack(fill='x', padx=10, pady=(10, 5))
            
            # Search text with icon
            search_label = ttk.Label(self.search_frame, text="🔎 Search:", foreground='#1976d2')
            search_label.grid(row=0, column=0, sticky='w', padx=(0, 5))
            self.search_var = tk.StringVar()
            self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=30)
            self.search_entry.grid(row=0, column=1, padx=(0, 10))
            self.search_entry.bind('<KeyRelease>', self.on_search_change)
            
            # Language filters with colorful icons
            from_label = ttk.Label(self.search_frame, text="🌐 From:", foreground='#388e3c')
            from_label.grid(row=0, column=2, sticky='w', padx=(0, 5))
            self.source_lang_var = tk.StringVar()
            self.source_lang_combo = ttk.Combobox(self.search_frame, textvariable=self.source_lang_var, width=12)
            self.source_lang_combo.grid(row=0, column=3, padx=(0, 10))
            self.source_lang_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
            
            to_label = ttk.Label(self.search_frame, text="🎯 To:", foreground='#f57c00')
            to_label.grid(row=0, column=4, sticky='w', padx=(0, 5))
            self.target_lang_var = tk.StringVar()
            self.target_lang_combo = ttk.Combobox(self.search_frame, textvariable=self.target_lang_var, width=12)
            self.target_lang_combo.grid(row=0, column=5, padx=(0, 10))
            self.target_lang_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
            
            # Time filter with icon
            time_label = ttk.Label(self.search_frame, text="📅 Time:", foreground='#7b1fa2')
            time_label.grid(row=0, column=6, sticky='w', padx=(0, 5))
            self.time_filter_var = tk.StringVar(value="All")
            self.time_filter_combo = ttk.Combobox(self.search_frame, textvariable=self.time_filter_var, 
                                                values=["All", "Today", "Yesterday", "Last 7 days", "Last 30 days"], 
                                                width=12, state="readonly")
            self.time_filter_combo.grid(row=0, column=7, padx=(0, 10))
            self.time_filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
            
            # Action buttons with colorful icons
            self.action_frame = ttk.Frame(self.search_frame)
            self.action_frame.grid(row=1, column=0, columnspan=8, pady=(10, 0), sticky='w')
            
            # Create styled buttons
            refresh_btn = ttk.Button(self.action_frame, text="🔄 Refresh", command=self.refresh_history)
            refresh_btn.pack(side='left', padx=(0, 5))
            
            clear_btn = ttk.Button(self.action_frame, text="🗑️ Clear All", command=self.clear_history)
            clear_btn.pack(side='left', padx=(0, 5))
            
            stats_btn = ttk.Button(self.action_frame, text="📊 Statistics", command=self.show_statistics)
            stats_btn.pack(side='left', padx=(0, 5))
            
            # New: View Full Details button
            details_btn = ttk.Button(self.action_frame, text="📄 View Full Details", command=self.view_full_details)
            details_btn.pack(side='left', padx=(0, 5))
            
            export_json_btn = ttk.Button(self.action_frame, text="📤 Export JSON", command=self.export_json)
            export_json_btn.pack(side='left', padx=(0, 5))
            
            export_csv_btn = ttk.Button(self.action_frame, text="📄 Export CSV", command=self.export_csv)
            export_csv_btn.pack(side='left', padx=(0, 5))
            
            # History display frame with read-only text
            self.display_frame = ttk.LabelFrame(self.frame, text="📚 Translation History (Read-Only)", padding=10)
            self.display_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))
            
            # Create read-only text widget with improved styling
            self.history_text = tk.Text(self.display_frame, wrap='word', height=15, 
                                       font=('Consolas', 10), 
                                       bg='#f8f9fa', 
                                       relief='sunken',
                                       state='disabled')  # Make it read-only by default
            scrollbar = ttk.Scrollbar(self.display_frame, orient="vertical", command=self.history_text.yview)
            self.history_text.configure(yscrollcommand=scrollbar.set)
            
            # Create context menu for copying
            self.context_menu = tk.Menu(self.history_text, tearoff=0)
            self.context_menu.add_command(label="📋 Copy Selected Text", command=self.copy_selected_text)
            self.context_menu.add_command(label="📄 View Full Details", command=self.view_full_details)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="🔄 Refresh", command=self.refresh_history)
            
            # Bind context menu
            self.history_text.bind("<Button-3>", self.show_context_menu)
            
            self.history_text.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Load initial data
            self.update_language_filters()
            self.refresh_history()
            
            # Update status label
            self.status_label.config(text="✅ History Tab Loaded Successfully", foreground='green')
            
        except Exception as e:
            print(f"❌ [HISTORY TAB] Error in __init__: {e}")
            self.status_label.config(text=f"❌ Error loading History Tab: {e}", foreground='red')
    
    def get_filtered_history(self):
        """Get history data with current filters applied - IMPROVED TIME FILTERING"""
        try:
            # Get search criteria
            search_text = self.search_var.get().strip().lower()
            source_lang = self.source_lang_var.get()
            target_lang = self.target_lang_var.get()
            time_filter = self.time_filter_var.get()
            
            # Calculate time range with improved logic
            since_date = None
            until_date = None
            
            now = datetime.now()
            
            if time_filter == "Today":
                since_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                until_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            elif time_filter == "Yesterday":
                yesterday = now - timedelta(days=1)
                since_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
                until_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
            elif time_filter == "Last 7 days":
                since_date = now - timedelta(days=7)
                until_date = now
            elif time_filter == "Last 30 days":
                since_date = now - timedelta(days=30)
                until_date = now
            
            # Get all history first
            if search_text:
                results = translation_history.search_history(query=search_text, limit=1000)
            else:
                results = translation_history.get_recent_translations(limit=1000)
            
            # Apply additional filters manually
            filtered_results = []
            for entry in results:
                # Improved time filter with until_date support
                if since_date:
                    try:
                        entry_time = datetime.fromisoformat(entry['timestamp'])
                        if entry_time < since_date:
                            continue
                        if until_date and entry_time > until_date:
                            continue
                    except:
                        # Skip entries with invalid timestamps
                        continue
                
                # Language filters
                if source_lang and source_lang != "All" and entry.get('source_lang', '') != source_lang:
                    continue
                if target_lang and target_lang != "All" and entry.get('target_lang', '') != target_lang:
                    continue
                
                filtered_results.append(entry)
            
            return filtered_results
            
        except Exception as e:
            print(f"❌ [FILTER] Error: {e}")
            return []

    def view_full_details(self):
        """View full details of all filtered translations"""
        try:
            history_data = self.get_filtered_history()
            
            if not history_data:
                messagebox.showinfo("ℹ️ No Data", "No translations found with current filters!")
                return
            
            # Create temporary file with full details
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', 
                                                  delete=False, encoding='utf-8')
            
            temp_file.write("🌍 ITM TRANSLATE - FULL HISTORY DETAILS\n")
            temp_file.write("=" * 60 + "\n\n")
            
            for i, entry in enumerate(history_data, 1):
                temp_file.write(f"📝 TRANSLATION #{i}\n")
                temp_file.write("-" * 40 + "\n")
                temp_file.write(f"⏰ Time: {entry.get('timestamp', 'N/A')}\n")
                temp_file.write(f"🌐 Source ({entry.get('source_lang', 'N/A')}): {entry.get('original_text', 'N/A')}\n")
                temp_file.write(f"🎯 Target ({entry.get('target_lang', 'N/A')}): {entry.get('translated_text', 'N/A')}\n")
                temp_file.write(f"🤖 Provider: {entry.get('provider', 'N/A')} | Model: {entry.get('model', 'N/A')}\n")
                temp_file.write(f"⚡ Speed: {entry.get('translation_time', 'N/A')}s | Mode: {entry.get('mode', 'N/A')}\n")
                temp_file.write("\n")
            
            temp_file.close()
            
            # Open file with default program
            import subprocess
            import os
            
            if os.name == 'nt':  # Windows
                os.startfile(temp_file.name)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', temp_file.name])
            
            messagebox.showinfo("✅ File Opened", f"Full details opened in text editor!\n\nFile: {temp_file.name}")
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to view full details: {e}")
            print(f"❌ [VIEW_DETAILS] Error: {e}")

    def refresh_history(self):
        """Refresh the history display with current filters"""
        try:
            # Enable text widget for editing
            self.history_text.config(state='normal')
            
            # Clear existing content
            self.history_text.delete('1.0', tk.END)
            
            # Configure text formatting tags
            self.history_text.tag_configure("bold", font=('Consolas', 11, 'bold'), foreground='#1976d2')
            self.history_text.tag_configure("time_bold", font=('Consolas', 11, 'bold'), foreground="#008000")
            self.history_text.tag_configure("header", font=('Consolas', 11, 'bold'), foreground='#1976d2')
            self.history_text.tag_configure("original_label", font=('Consolas', 11, 'bold'), foreground='#d32f2f')  # Red and bold for Original
            self.history_text.tag_configure("translated_label", font=('Consolas', 11, 'bold'), foreground='#008000')  # Green and bold for Translated

            # Get filtered history
            history_data = self.get_filtered_history()
            
            if not history_data:
                self.history_text.insert('1.0', "📭 No translation history found.\n\n✨ Try making some translations to see them here!\n🔍 Or adjust your search/filter criteria.")
                self.history_text.config(state='disabled')  # Make read-only again
                return
            
            # Calculate average translation time for header
            avg_time_str = ""
            if history_data:
                total_time = 0
                valid_times = 0
                for entry in history_data:
                    time_val = entry.get('translation_time', 0)
                    if isinstance(time_val, (int, float)) and time_val > 0:
                        total_time += time_val
                        valid_times += 1
                
                if valid_times > 0:
                    avg_time = total_time / valid_times
                    avg_time_str = f" | ⚡ Average time: {avg_time:.2f}s"
            
            # Display history in improved format with color coding
            header = f"📚 Translation History ({len(history_data)} entries){avg_time_str}\n"
            header += "=" * 60 + "\n\n"
            self.history_text.insert('1.0', header, "header")
            
            for i, entry in enumerate(history_data, 1):
                # Format time with better display
                try:
                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    time_str = entry_time.strftime('%m/%d %H:%M')
                    
                    # Add day info for better context
                    days_ago = (datetime.now().date() - entry_time.date()).days
                    if days_ago == 0:
                        day_info = "Today"
                    elif days_ago == 1:
                        day_info = "Yesterday"
                    elif days_ago < 7:
                        day_info = f"{days_ago} days ago"
                    else:
                        day_info = entry_time.strftime('%Y-%m-%d')
                    
                    time_str = f"{time_str} ({day_info})"
                except:
                    time_str = entry.get('timestamp', 'Unknown time')
                
                # Format entry with improved styling
                provider = entry.get('provider', 'unknown')
                translation_time = entry.get('translation_time', 0)
                
                lang_pair = f"{entry['source_lang']} → {entry['target_lang']}"
                
                # Insert entry parts with different formatting
                entry_start = self.history_text.index(tk.END)
                
                self.history_text.insert(tk.END, f"🔸 {i}. [{time_str}] 🤖 {provider} ")
                
                # Insert translation time with bold formatting
                time_text = f"({translation_time:.2f}s)"
                self.history_text.insert(tk.END, time_text, "time_bold")
                
                self.history_text.insert(tk.END, f"\n   💡 {lang_pair}\n")
                
                # Insert "Original:" with red bold formatting
                self.history_text.insert(tk.END, "   📝Original:  ", "original_label")
                self.history_text.insert(tk.END, f"{entry['original_text'][:250]}{'...' if len(entry['original_text']) > 250 else ''}\n")
                
                # Insert "Translated:" with red bold formatting
                self.history_text.insert(tk.END, "   ✅Translated: ", "translated_label")
                self.history_text.insert(tk.END, f"{entry['translated_text'][:250]}{'...' if len(entry['translated_text']) > 250 else ''}\n")
                self.history_text.insert(tk.END, "-" * 60 + "\n\n")
            
            # Add footer with total count
            footer = f"\n📊 Total entries displayed: {len(history_data)}"
            
            footer += "\n"
            if len(history_data) < len(translation_history.history):
                footer += f"💡 Tip: {len(translation_history.history) - len(history_data)} entries hidden by filters"
            
            self.history_text.insert(tk.END, footer, "bold")
            
            # Make text widget read-only
            self.history_text.config(state='disabled')
                
        except Exception as e:
            print(f"❌ [HISTORY TAB] Error refreshing history: {e}")
            self.history_text.config(state='normal')
            self.history_text.delete('1.0', tk.END)
            self.history_text.insert('1.0', f"❌ Error loading history: {e}\n\nPlease check the console for details.")
            self.history_text.config(state='disabled')
    
    def copy_selected_text(self):
        """Copy selected text to clipboard"""
        try:
            selected_text = self.history_text.selection_get()
            if selected_text:
                self.frame.clipboard_clear()
                self.frame.clipboard_append(selected_text)
                messagebox.showinfo("📋 Copied", "Selected text copied to clipboard!")
        except tk.TclError:
            messagebox.showwarning("⚠️ No Selection", "Please select some text first!")
    
    def show_context_menu(self, event):
        """Show context menu for history text"""
        try:
            self.context_menu.post(event.x_root, event.y_root)
        except:
            pass
    
    def update_language_filters(self):
        """Update language filter comboboxes with available languages"""
        try:
            stats = translation_history.get_statistics()
            languages = set()
            
            # Get languages from translation history entries directly
            for entry in translation_history.history:
                if 'source_lang' in entry:
                    languages.add(entry['source_lang'])
                if 'target_lang' in entry:
                    languages.add(entry['target_lang'])
            
            sorted_languages = ["All"] + sorted(languages)
            
            self.source_lang_combo['values'] = sorted_languages
            self.target_lang_combo['values'] = sorted_languages
            
            # Set default values
            if not self.source_lang_var.get():
                self.source_lang_var.set("All")
            if not self.target_lang_var.get():
                self.target_lang_var.set("All")
                
        except Exception as e:
            print(f"Error updating language filters: {e}")
            # Set minimal values in case of error
            self.source_lang_combo['values'] = ["All"]
            self.target_lang_combo['values'] = ["All"]
            self.source_lang_var.set("All")
            self.target_lang_var.set("All")
    
    def on_search_change(self, event=None):
        """Handle search text changes"""
        self.refresh_history()
    
    def on_filter_change(self, event=None):
        """Handle filter changes"""
        self.refresh_history()
    
    def truncate_text(self, text, max_length):
        """Truncate text for display"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def clear_history(self):
        """Clear all translation history - Simple approach: recreate file"""
        try:
            if messagebox.askyesno("🗑️ Confirm Clear", 
                                   "Are you sure you want to clear ALL translation history?\n\n⚠️ This action cannot be undone!"):
                
                # Simple approach: Just create a new empty history file
                import os
                history_file = "translation_history.json"
                
                # Create empty history structure
                empty_history = {
                    "version": "2.0",
                    "created_at": datetime.now().isoformat(),
                    "translations": []
                }
                
                # Write empty history to file (overwrite existing)
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(empty_history, f, ensure_ascii=False, indent=2)
                
                # Clear in-memory history as well
                translation_history.history.clear()
                
                # Refresh UI
                self.refresh_history()
                self.update_language_filters()
                
                messagebox.showinfo("✅ Cleared", "Translation history cleared successfully!")
                print("🗑️ [CLEAR] History cleared by recreating file")
                
        except Exception as e:
            messagebox.showerror("❌ Clear Error", f"Failed to clear history: {e}")
            print(f"❌ [CLEAR] Error: {e}")
    
    def export_json(self):
        """Export history to JSON file"""
        try:
            # Create safe filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"translation_history_{timestamp}.json"
            
            file_path = filedialog.asksaveasfilename(
                title="📤 Export Translation History",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=filename  # Use initialfile instead of initialname
            )
            
            if file_path:
                # Get filtered history data
                history_data = self.get_filtered_history()
                
                if not history_data:
                    messagebox.showwarning("⚠️ No Data", "No translation history to export!")
                    return
                
                export_data = {
                    "export_info": {
                        "generated_at": datetime.now().isoformat(),
                        "total_entries": len(history_data),
                        "app_version": "ITM Translate v2.0.5",
                        "exported_by": "ITM Translate History Tab"
                    },
                    "translations": history_data
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("✅ Export Complete", f"✅ {len(history_data)} entries exported to:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("❌ Export Error", f"Failed to export JSON: {e}")
            print(f"❌ [EXPORT_JSON] Error: {e}")
    
    def export_csv(self):
        """Export history to CSV file"""
        try:
            # Create safe filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"translation_history_{timestamp}.csv"
            
            file_path = filedialog.asksaveasfilename(
                title="📄 Export Translation History",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=filename  # Use initialfile instead of initialname
            )
            
            if file_path:
                history_data = self.get_filtered_history()
                
                if not history_data:
                    messagebox.showwarning("⚠️ No Data", "No translation history to export!")
                    return
                
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['timestamp', 'original_text', 'translated_text', 'source_lang', 
                                'target_lang', 'provider', 'model', 'translation_time', 'mode']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for entry in history_data:
                        # Write only the specified fields, handle missing data gracefully
                        row = {}
                        for field in fieldnames:
                            value = entry.get(field, '')
                            # Convert non-string values to strings for CSV
                            if isinstance(value, (int, float)):
                                row[field] = str(value)
                            else:
                                row[field] = str(value) if value is not None else ''
                        writer.writerow(row)
                
                messagebox.showinfo("✅ Export Complete", f"✅ {len(history_data)} entries exported to:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("❌ Export Error", f"Failed to export CSV: {e}")
            print(f"❌ [EXPORT_CSV] Error: {e}")
