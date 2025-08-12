"""
SSL Bypass Utility - Bypass SSL verification for corporate networks
"""
import ssl
import os
import urllib3
from urllib3.exceptions import InsecureRequestWarning

def setup_ssl_bypass():
    """
    Setup SSL bypass for all HTTP libraries globally
    This is needed for corporate networks with self-signed certificates
    """
    try:
        # Disable SSL warnings
        urllib3.disable_warnings(InsecureRequestWarning)
        
        # Create unverified SSL context
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Set environment variables for various libraries
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        
        # Additional bypass for Google libraries
        setup_google_ssl_bypass()
        
        print("🔓 [SSL] SSL verification bypassed for corporate networks")
        return True
        
    except Exception as e:
        print(f"⚠️ [SSL] Warning: Could not setup SSL bypass: {e}")
        return False

def setup_google_ssl_bypass():
    """
    Setup SSL bypass specifically for Google libraries (Gemini)
    """
    try:
        import requests
        import urllib3.util.connection as urllib3_cn
        
        # Monkey patch requests to disable SSL verification
        original_request = requests.Session.request
        
        def patched_request(self, *args, **kwargs):
            kwargs['verify'] = False
            return original_request(self, *args, **kwargs)
        
        requests.Session.request = patched_request
        
        # Patch urllib3 connection for Google API
        original_create_connection = urllib3_cn.create_connection
        
        def patched_create_connection(address, *args, **kwargs):
            # Remove SSL context from kwargs if present
            kwargs.pop('ssl_context', None)
            return original_create_connection(address, *args, **kwargs)
        
        urllib3_cn.create_connection = patched_create_connection
        
        print("🔓 [SSL] Google API SSL bypass configured")
        
    except Exception as e:
        print(f"⚠️ [SSL] Warning: Could not setup Google SSL bypass: {e}")

def restore_ssl_verification():
    """
    Restore normal SSL verification (for testing purposes)
    """
    try:
        # Restore default SSL context
        ssl._create_default_https_context = ssl.create_default_context
        
        # Clean environment variables
        for var in ['PYTHONHTTPSVERIFY', 'CURL_CA_BUNDLE', 'REQUESTS_CA_BUNDLE']:
            if var in os.environ:
                del os.environ[var]
        
        print("🔒 [SSL] SSL verification restored")
        return True
        
    except Exception as e:
        print(f"⚠️ [SSL] Warning: Could not restore SSL verification: {e}")
        return False

# Auto-setup SSL bypass when module is imported
if __name__ != "__main__":
    setup_ssl_bypass()
