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
        
        print("🔓 [SSL] SSL verification bypassed for corporate networks")
        return True
        
    except Exception as e:
        print(f"⚠️ [SSL] Warning: Could not setup SSL bypass: {e}")
        return False

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
