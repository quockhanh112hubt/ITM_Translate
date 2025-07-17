#!/usr/bin/env python3
"""
Quick test script cho GitHub Copilot integration
"""

print("=== QUICK TEST GITHUB COPILOT ===\n")

try:
    from core.api_key_manager import AIProvider, api_key_manager
    
    print("✅ Import AIProvider thành công")
    
    # Test enum
    print("🧪 Test AIProvider enum:")
    for provider in AIProvider:
        icon = "🤖" if provider == AIProvider.COPILOT else "🔤"
        print(f"   {icon} {provider.value}")
    
    print(f"\n📊 Total providers: {len(list(AIProvider))}")
    
    # Test priority
    print("\n🎯 Current priority:")
    for i, p in enumerate(api_key_manager.provider_priority, 1):
        icon = "🤖" if p == AIProvider.COPILOT else "🔤"
        print(f"   {i}. {icon} {p.value}")
    
    # Test if COPILOT is in enum
    if hasattr(AIProvider, 'COPILOT'):
        print("\n✅ AIProvider.COPILOT exists!")
        print(f"   Value: {AIProvider.COPILOT.value}")
    else:
        print("\n❌ AIProvider.COPILOT does NOT exist!")
    
    # Test provider models
    try:
        from core.provider_models import get_models_for_provider
        copilot_models = get_models_for_provider('copilot')
        print(f"\n🤖 Copilot models: {copilot_models}")
    except Exception as e:
        print(f"\n❌ Error getting copilot models: {e}")
    
    print("\n🎉 All tests completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
