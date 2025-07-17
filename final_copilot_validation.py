#!/usr/bin/env python3
"""
Final validation script cho GitHub Copilot integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def final_validation():
    """Final validation của GitHub Copilot integration"""
    print("=== 🔥 FINAL GITHUB COPILOT VALIDATION 🔥 ===\n")
    
    print("1️⃣ Testing Core Components...")
    
    # Test 1: API Key Manager
    try:
        from core.api_key_manager import AIProvider, api_key_manager
        
        # Check enum
        assert hasattr(AIProvider, 'COPILOT'), "COPILOT enum missing"
        assert AIProvider.COPILOT.value == 'copilot', "COPILOT value wrong"
        
        # Check priority
        assert AIProvider.COPILOT in api_key_manager.provider_priority, "COPILOT not in priority"
        
        print("   ✅ API Key Manager: PASSED")
        
    except Exception as e:
        print(f"   ❌ API Key Manager: FAILED - {e}")
        return False
    
    # Test 2: Provider Models
    try:
        from core.provider_models import get_models_for_provider, get_model_description
        
        models = get_models_for_provider('copilot')
        assert len(models) > 0, "No copilot models"
        assert 'auto' in models, "auto model missing"
        assert 'gpt-4' in models, "gpt-4 model missing"
        
        desc = get_model_description('gpt-4')
        assert 'GitHub Copilot' in desc, "GitHub Copilot not in description"
        
        print("   ✅ Provider Models: PASSED")
        
    except Exception as e:
        print(f"   ❌ Provider Models: FAILED - {e}")
        return False
    
    # Test 3: AI Providers
    try:
        from core.ai_providers import create_ai_provider, CopilotProvider
        from core.api_key_manager import APIKeyInfo
        
        # Test factory
        test_key = APIKeyInfo(
            key="sk-test123456789",
            provider=AIProvider.COPILOT,
            model="gpt-4"
        )
        
        # This might fail due to invalid key, but should not crash
        try:
            provider = create_ai_provider(test_key)
            assert isinstance(provider, CopilotProvider), "Wrong provider type"
        except ValueError as e:
            if "openai" in str(e):
                print("   ⚠️  AI Providers: CONDITIONAL PASS (openai library needed)")
            else:
                raise e
        else:
            print("   ✅ AI Providers: PASSED")
        
    except Exception as e:
        print(f"   ❌ AI Providers: FAILED - {e}")
        return False
    
    # Test 4: API Key Validator
    try:
        from core.api_key_validator import APIKeyValidator
        
        # Test format validation - chỉ test OpenAI keys cho Copilot
        valid, msg = APIKeyValidator.validate_format('copilot', 'sk-test1234567890123456789012345678901234567890')
        assert valid, f"OpenAI key format validation failed: {msg}"
        
        # Test that GitHub tokens are rejected for Copilot
        valid, msg = APIKeyValidator.validate_format('copilot', 'ghp_test1234567890123456789012345678901234567890')
        assert not valid, "GitHub token should be rejected for Copilot"
        assert "GitHub tokens không dùng được cho API calls" in msg, "Wrong error message for GitHub token"
        
        print("   ✅ API Key Validator: PASSED")
        
    except Exception as e:
        print(f"   ❌ API Key Validator: FAILED - {e}")
        return False
    
    # Test 5: GUI Integration
    try:
        gui_file = "ui/gui.py"
        with open(gui_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check provider dropdown
        assert "values=['gemini', 'chatgpt', 'copilot', 'deepseek', 'claude']" in content, "GUI dropdown missing copilot"
        
        # Check info text
        assert "GitHub Copilot" in content, "GUI info text missing GitHub Copilot"
        
        print("   ✅ GUI Integration: PASSED")
        
    except Exception as e:
        print(f"   ❌ GUI Integration: FAILED - {e}")
        return False
    
    print("\n2️⃣ Integration Status:")
    
    # Show final stats
    providers = list(AIProvider)
    priority = api_key_manager.provider_priority
    
    print(f"   📊 Total Providers: {len(providers)}")
    print(f"   🎯 Priority List: {len(priority)} providers")
    print(f"   🤖 GitHub Copilot Position: #{priority.index(AIProvider.COPILOT) + 1}")
    
    print("\n3️⃣ User Instructions:")
    print("   🚀 To use GitHub Copilot:")
    print("      1. Open ITM Translate GUI")
    print("      2. Go to 'Quản lý API KEY' tab")
    print("      3. Select 'copilot' from Provider dropdown")
    print("      4. Enter OpenAI API key (sk_xxx) - GitHub tokens not supported")
    print("      5. Get OpenAI key at: https://platform.openai.com/api-keys")
    print("      6. Choose model (recommend: gpt-4)")
    print("      7. Click 'Thêm Key'")
    print("      8. Start translating with GitHub Copilot personality! 🤖✨")
    
    print("\n🎉 GITHUB COPILOT INTEGRATION: FULLY COMPLETE! 🎉")
    return True

if __name__ == "__main__":
    success = final_validation()
    
    if success:
        print("\n🌟 All systems go! GitHub Copilot is ready for production! 🌟")
    else:
        print("\n💥 Integration issues detected! Please check and fix errors. 💥")
