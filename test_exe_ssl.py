#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXE Build SSL Test - Diagnose SSL issues in built executable
"""

import sys
import os
import tempfile

def test_exe_ssl_environment():
    print('🔧 EXE Build SSL Environment Test')
    print('=' * 50)
    print()
    
    # Check if running as EXE
    if getattr(sys, 'frozen', False):
        print('📦 Running as EXE build')
        print(f'   Executable path: {sys.executable}')
        print(f'   Executable directory: {os.path.dirname(sys.executable)}')
    else:
        print('🐍 Running as Python script')
        print(f'   Script path: {__file__}')
    
    print()
    
    # Check temp directory
    temp_dir = tempfile.gettempdir()
    print(f'📁 Temp directory: {temp_dir}')
    print(f'   Temp directory exists: {os.path.exists(temp_dir)}')
    print(f'   Temp directory writable: {os.access(temp_dir, os.W_OK)}')
    
    print()
    
    # Test SSL libraries
    print('🔒 SSL Libraries Test:')
    try:
        import ssl
        print(f'   ✅ ssl module: Available')
        print(f'   SSL version: {ssl.OPENSSL_VERSION}')
    except Exception as e:
        print(f'   ❌ ssl module: Error - {e}')
    
    try:
        import certifi
        ca_bundle = certifi.where()
        print(f'   ✅ certifi module: Available')
        print(f'   CA bundle path: {ca_bundle}')
        print(f'   CA bundle exists: {os.path.exists(ca_bundle)}')
        if os.path.exists(ca_bundle):
            print(f'   CA bundle size: {os.path.getsize(ca_bundle)} bytes')
    except Exception as e:
        print(f'   ❌ certifi module: Error - {e}')
    
    try:
        import requests
        print(f'   ✅ requests module: Available')
        try:
            import requests.certs
            ca_bundle = requests.certs.where()
            print(f'   Requests CA bundle: {ca_bundle}')
            print(f'   Requests CA exists: {os.path.exists(ca_bundle)}')
        except Exception as e:
            print(f'   ⚠️ requests.certs: Error - {e}')
    except Exception as e:
        print(f'   ❌ requests module: Error - {e}')
    
    print()
    
    # Test config loading
    print('⚙️ Config Loading Test:')
    try:
        import json
        config_file = "config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f'   ✅ config.json loaded successfully')
            
            ssl_disabled = config.get("update_server", {}).get("disable_ssl_verification", False)
            print(f'   disable_ssl_verification: {ssl_disabled}')
        else:
            print(f'   ❌ config.json not found at: {os.path.abspath(config_file)}')
    except Exception as e:
        print(f'   ❌ Config loading error: {e}')
    
    print()
    
    # Test basic HTTPS with bypass
    print('🌐 HTTPS Connection Test (with SSL bypass):')
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.get('https://httpbin.org/get', verify=False, timeout=10)
        print(f'   ✅ HTTPS connection successful: Status {response.status_code}')
    except Exception as e:
        print(f'   ❌ HTTPS connection failed: {e}')
    
    print()
    
    # Test GitHub API with bypass
    print('📡 GitHub API Test (with SSL bypass):')
    try:
        response = requests.get(
            'https://api.github.com/repos/quockhanh112hubt/ITM_Translate/releases/latest',
            verify=False,
            timeout=10,
            headers={'User-Agent': 'ITM-Translate-Test'}
        )
        print(f'   ✅ GitHub API successful: Status {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Latest version: {data.get("tag_name", "unknown")}')
    except Exception as e:
        print(f'   ❌ GitHub API failed: {e}')
    
    print()
    print('📋 RECOMMENDATIONS:')
    print('   1. If running as EXE and SSL libraries fail:')
    print('      - Rebuild with updated PyInstaller spec')
    print('      - Include certifi and SSL certificates in build')
    print()
    print('   2. If HTTPS connections fail:')
    print('      - Enable SSL bypass in config.json temporarily')
    print('      - Check corporate firewall/proxy settings')
    print()
    print('   3. For corporate Fortinet environments:')
    print('      - Use "Enable Temporary SSL Bypass" in help dialog')
    print('      - Copy Fortinet certificates to Downloads folder')

if __name__ == "__main__":
    test_exe_ssl_environment()
