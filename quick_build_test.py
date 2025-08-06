#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Build and Test Script for SSL EXE Issues
"""

import os
import subprocess
import sys
import shutil

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f'🚀 {description}...')
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f'   ✅ Success')
        return True
    except subprocess.CalledProcessError as e:
        print(f'   ❌ Failed: {e.stderr.strip() if e.stderr else "Unknown error"}')
        return False

def main():
    print('🔨 ITM Translate - Quick SSL EXE Build & Test')
    print('=' * 55)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('ITM_Translate.py'):
        print('❌ Error: ITM_Translate.py not found. Please run this from the project directory.')
        return
    
    # Clean previous build
    print('🧹 Cleaning previous build...')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print('   ✅ dist directory removed')
    
    if os.path.exists('build'):
        shutil.rmtree('build')
        print('   ✅ build directory removed')
    
    print()
    
    # Run PyInstaller
    if not run_command('pyinstaller --clean ITM_Translate.spec', 'Building EXE with PyInstaller'):
        print('❌ Build failed. Please check the error messages above.')
        return
    
    print()
    
    # Check if EXE was created
    exe_path = os.path.join('dist', 'ITM_Translate.exe')
    if not os.path.exists(exe_path):
        print(f'❌ EXE not found at: {exe_path}')
        return
    
    print(f'✅ EXE created successfully at: {exe_path}')
    print(f'   File size: {os.path.getsize(exe_path) / (1024*1024):.1f} MB')
    print()
    
    # Copy test script to dist directory
    test_script = 'test_exe_ssl.py'
    if os.path.exists(test_script):
        dist_test_script = os.path.join('dist', test_script)
        shutil.copy2(test_script, dist_test_script)
        print(f'✅ Test script copied to: {dist_test_script}')
    
    # Copy config.json if it exists
    if os.path.exists('config.json'):
        dist_config = os.path.join('dist', 'config.json')
        shutil.copy2('config.json', dist_config)
        print(f'✅ Config copied to: {dist_config}')
    
    print()
    print('🎯 NEXT STEPS:')
    print(f'   1. Navigate to: {os.path.abspath("dist")}')
    print('   2. Run: python test_exe_ssl.py (first)')
    print('   3. Then run: ITM_Translate.exe')
    print()
    print('   If SSL issues persist:')
    print('   • Check if config.json has "disable_ssl_verification": true')
    print('   • Test in corporate network vs. home network')
    print('   • Check Windows Defender/antivirus blocking')
    print()

if __name__ == "__main__":
    main()
