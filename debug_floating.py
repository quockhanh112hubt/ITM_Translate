#!/usr/bin/env python3
"""
Debug script để test floating button
"""
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_floating_button():
    """Debug floating button functionality"""
    print('🔍 Debugging Floating Button System')
    print('=' * 50)
    
    # Check if floating button is enabled in config
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            import json
            config = json.load(f)
            floating_enabled = config.get('floating_button_enabled', False)
            print(f'🔧 Config floating_button_enabled: {floating_enabled}')
    except Exception as e:
        print(f'❌ Error reading config: {e}')
    
    # Test import without GUI
    try:
        # Mock tkinter to avoid GUI startup
        import unittest.mock
        with unittest.mock.patch('tkinter.Tk'):
            with unittest.mock.patch('tkinter.PhotoImage'):
                print('📦 Testing imports...')
                
                # Read and analyze the code
                with open('ITM_Translate.py', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check key components
                checks = [
                    ('mouse_listener definition', 'mouse_listener = mouse.Listener('),
                    ('on_mouse_click function', 'def on_mouse_click(x, y, button, pressed):'),
                    ('on_mouse_move function', 'def on_mouse_move(x, y):'),
                    ('check_for_text_selection_v3 call', 'check_for_text_selection_v3(x, y)'),
                    ('is_dragging variable', 'is_dragging = True'),
                    ('floating button enabled check', 'if floating_button_enabled:')
                ]
                
                for name, pattern in checks:
                    if pattern in content:
                        print(f'✅ {name}')
                    else:
                        print(f'❌ {name} - NOT FOUND')
                
                # Check specific logic flow
                print('\n🔍 Logic Flow Analysis:')
                
                # 1. Mouse click starts drag
                if 'mouse_drag_start = (x, y)' in content:
                    print('✅ Mouse drag start tracking')
                else:
                    print('❌ Mouse drag start tracking missing')
                
                # 2. Mouse move detects dragging
                if 'is_dragging = True' in content:
                    print('✅ Dragging detection')
                else:
                    print('❌ Dragging detection missing')
                
                # 3. Mouse release triggers selection check
                if 'if mouse_drag_start and is_dragging' in content:
                    print('✅ Drag completion check')
                else:
                    print('❌ Drag completion check missing')
                
                # 4. Selection check calls V3 function
                if 'check_for_text_selection_v3(x, y)' in content:
                    print('✅ V3 function call')
                else:
                    print('❌ V3 function call missing')
                
                print('\n🎯 Potential Issues:')
                
                # Check for potential issues
                issues = []
                
                if content.count('check_for_text_selection_v2') > 0:
                    issues.append('Old V2 function still referenced')
                
                if content.count('on_floating_translate_click()') > 0:
                    issues.append('Old click handler still referenced')
                
                if not ('root.after(200, lambda: check_for_text_selection_v3(x, y))' in content):
                    issues.append('V3 function not called with proper delay')
                
                if not ('is_dragging = False' in content):
                    issues.append('Dragging state reset missing')
                
                if issues:
                    for issue in issues:
                        print(f'⚠️  {issue}')
                else:
                    print('✅ No obvious issues found')
                
                print('\n📋 Debugging Steps:')
                print('1. Check if floating_button_enabled = True in config.json')
                print('2. Start ITM_Translate.py')
                print('3. Try selecting text with mouse drag in a text editor')
                print('4. Check console for debug messages')
                print('5. Look for "✅ [FLOATING V3] Text selection detected" message')
                
    except Exception as e:
        print(f'❌ Error during analysis: {e}')

if __name__ == '__main__':
    debug_floating_button()
