#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITM Translate SSL Testing Tool
Test SSL functionality in both development and EXE environments
"""

import sys
import os
import json
import tempfile

def test_ssl_in_app():
    """Test SSL functionality as it would work in the actual app"""
    print('🔒 ITM Translate SSL Functionality Test')
    print('=' * 45)
    print()
    
    # Determine if running as EXE
    is_exe = getattr(sys, 'frozen', False)
    if is_exe:
        print('📦 Environment: EXE build')
        app_dir = os.path.dirname(sys.executable)
    else:
        print('🐍 Environment: Development/Script')
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f'   App directory: {app_dir}')
    print()
    
    # Test config loading (as app would do it)
    config_path = os.path.join(app_dir, 'config.json')
    print(f'⚙️ Loading config from: {config_path}')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        ssl_bypass = config.get("update_server", {}).get("disable_ssl_verification", False)
        print(f'   ✅ Config loaded successfully')
        print(f'   SSL bypass enabled: {ssl_bypass}')
    except Exception as e:
        print(f'   ❌ Config loading failed: {e}')
        ssl_bypass = False
    
    print()
    
    # Test SSL functionality (simulate updater behavior)
    print('🌐 Testing GitHub API connection (as updater would):')
    try:
        import requests
        import urllib3
        
        if ssl_bypass:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            verify = False
            print('   🚫 SSL verification disabled (corporate bypass mode)')
        else:
            verify = True
            print('   🔒 SSL verification enabled (normal mode)')
        
        # Test GitHub API (same as updater does)
        response = requests.get(
            'https://api.github.com/repos/quockhanh112hubt/ITM_Translate/releases/latest',
            verify=verify,
            timeout=10,
            headers={'User-Agent': 'ITM-Translate-Test'}
        )
        
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get('tag_name', 'unknown')
            print(f'   ✅ GitHub API connection successful!')
            print(f'   Latest version available: {latest_version}')
            
            # Check current version
            version_file = os.path.join(app_dir, 'version.json')
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    current_version = json.load(f).get('version', 'unknown')
                print(f'   Current version: {current_version}')
                
                if latest_version != current_version:
                    print(f'   📢 Update available: {current_version} → {latest_version}')
                else:
                    print(f'   ✅ Application is up to date')
            
        else:
            print(f'   ⚠️ GitHub API returned status: {response.status_code}')
            
    except Exception as e:
        print(f'   ❌ GitHub API connection failed: {e}')
        print()
        print('🔧 TROUBLESHOOTING:')
        
        if not ssl_bypass:
            print('   • SSL verification is enabled but failed')
            print('   • This usually happens in corporate environments with Fortinet')
            print('   • Solution: Enable SSL bypass in Help > Enable SSL Bypass')
        else:
            print('   • SSL bypass is enabled but connection still failed')
            print('   • Check internet connection')
            print('   • Check firewall/proxy settings')
            print('   • Try running as administrator')
    
    print()
    print('📋 SSL CONFIGURATION STATUS:')
    if ssl_bypass:
        print('   ✅ SSL bypass: ENABLED (corporate-friendly)')
        print('   • Safe for corporate Fortinet environments')
        print('   • Bypasses certificate inspection issues')
        print('   • Can be disabled after successful update')
    else:
        print('   🔒 SSL bypass: DISABLED (secure mode)')
        print('   • Uses system certificate validation')
        print('   • Recommended for home networks')
        print('   • May fail in corporate environments')

if __name__ == "__main__":
    test_ssl_in_app()
