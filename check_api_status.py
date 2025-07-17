#!/usr/bin/env python3
"""
Check API Status - Kiểm tra trạng thái và quota của các API provider
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.api_key_manager import api_key_manager
from core.ai_providers import create_ai_provider
import requests

def check_gemini_quota(api_key):
    """Kiểm tra quota Gemini API"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Test với một request nhỏ
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello")
        return True, "OK - Gemini API working"
    except Exception as e:
        return False, f"Gemini Error: {str(e)}"

def check_openai_quota(api_key):
    """Kiểm tra quota OpenAI API"""
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Test với một request nhỏ
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "OK - OpenAI API working"
        else:
            return False, f"OpenAI Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"OpenAI Error: {str(e)}"

def check_deepseek_quota(api_key):
    """Kiểm tra quota DeepSeek API"""
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Test với một request nhỏ
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "OK - DeepSeek API working"
        elif response.status_code == 402:
            return False, "❌ DeepSeek Error: Insufficient Balance (Hết tiền) - Cần nạp thêm credit vào tài khoản DeepSeek"
        elif response.status_code == 401:
            return False, "❌ DeepSeek Error: Invalid API Key"
        else:
            return False, f"DeepSeek Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"DeepSeek Error: {str(e)}"

def check_claude_quota(api_key):
    """Kiểm tra quota Claude API"""
    try:
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        # Test với một request nhỏ
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "OK - Claude API working"
        else:
            return False, f"Claude Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"Claude Error: {str(e)}"

def main():
    print("🔍 Checking API Status for ITM Translate")
    print("=" * 50)
    
    # Get all API keys
    all_keys = api_key_manager.get_all_keys()
    
    if not all_keys:
        print("❌ No API keys found! Please add API keys first.")
        return
    
    checker_map = {
        'gemini': check_gemini_quota,
        'chatgpt': check_openai_quota,
        'deepseek': check_deepseek_quota,
        'claude': check_claude_quota
    }
    
    working_count = 0
    failed_count = 0
    
    for i, key_info in enumerate(all_keys):
        print(f"\n📋 API Key {i+1}: {key_info.name}")
        print(f"   Provider: {key_info.provider.value.title()}")
        print(f"   Model: {key_info.model}")
        print(f"   Key: {key_info.key[:10]}...{key_info.key[-4:]}")
        
        # Check status
        checker = checker_map.get(key_info.provider.value)
        if checker:
            is_working, message = checker(key_info.key)
            if is_working:
                print(f"   Status: ✅ {message}")
                working_count += 1
            else:
                print(f"   Status: ❌ {message}")
                failed_count += 1
        else:
            print(f"   Status: ⚠️ No checker available for {key_info.provider.value}")
    
    print("\n" + "=" * 50)
    print(f"📊 Summary: {working_count} working, {failed_count} failed")
    
    if failed_count > 0:
        print("\n💡 Solutions for common issues:")
        print("   • DeepSeek 'Insufficient Balance': Nạp thêm credit tại https://platform.deepseek.com/")
        print("   • OpenAI errors: Check quota tại https://platform.openai.com/usage")
        print("   • Gemini errors: Check tại https://aistudio.google.com/")
        print("   • Claude errors: Check tại https://console.anthropic.com/")

if __name__ == "__main__":
    main()
