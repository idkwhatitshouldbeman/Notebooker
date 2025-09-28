#!/usr/bin/env py
"""
Quick CORS test for the Flask API
"""

import requests

def test_cors_headers():
    """Test CORS headers are properly set"""
    print("🧪 Testing CORS Headers...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5002/health")
        print(f"Health endpoint status: {response.status_code}")
        
        # Test CORS preflight
        cors_response = requests.options("http://localhost:5002/api/ai/chat", headers={
            "Origin": "https://notebooker.netlify.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, X-API-Key"
        })
        
        print(f"CORS preflight status: {cors_response.status_code}")
        print("CORS Headers:")
        for header, value in cors_response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        # Test actual API call
        api_response = requests.post("http://localhost:5002/api/ai/chat", 
            json={"message": "test", "projectId": "test"},
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "notebooker-api-key-2024",
                "Origin": "https://notebooker.netlify.app"
            }
        )
        
        print(f"API call status: {api_response.status_code}")
        print("Response headers:")
        for header, value in api_response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CORS Fix Test")
    print("=" * 40)
    test_cors_headers()
