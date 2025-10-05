#!/usr/bin/env python3
"""
Test script to verify CORS fixes and API endpoints
"""

import requests
import json

def test_cors_health():
    """Test CORS headers on health endpoint"""
    print("🧪 Testing CORS Health Endpoint...")
    
    try:
        # Test OPTIONS preflight request
        options_response = requests.options(
            "http://localhost:5002/health",
            headers={
                "Origin": "https://nobooker.netlify.app",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type, X-API-Key"
            }
        )
        
        print(f"OPTIONS Status: {options_response.status_code}")
        print("CORS Headers:")
        for header, value in options_response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        # Test actual GET request
        get_response = requests.get(
            "http://localhost:5002/health",
            headers={"Origin": "https://nobooker.netlify.app"}
        )
        
        print(f"GET Status: {get_response.status_code}")
        print(f"Response: {get_response.json()}")
        
        return options_response.status_code == 200 and get_response.status_code == 200
        
    except Exception as e:
        print(f"❌ Health test failed: {e}")
        return False

def test_cors_ai_chat():
    """Test CORS headers on AI chat endpoint"""
    print("\n🧪 Testing CORS AI Chat Endpoint...")
    
    try:
        # Test OPTIONS preflight request
        options_response = requests.options(
            "http://localhost:5002/api/ai/chat",
            headers={
                "Origin": "https://nobooker.netlify.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, X-API-Key"
            }
        )
        
        print(f"OPTIONS Status: {options_response.status_code}")
        print("CORS Headers:")
        for header, value in options_response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        # Test actual POST request
        post_response = requests.post(
            "http://localhost:5002/api/ai/chat",
            json={"message": "Hello", "projectId": "test"},
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "notebooker-api-key-2024",
                "Origin": "https://nobooker.netlify.app"
            }
        )
        
        print(f"POST Status: {post_response.status_code}")
        if post_response.status_code == 200:
            print(f"Response: {post_response.json()}")
        else:
            print(f"Error: {post_response.text}")
        
        return options_response.status_code == 200
        
    except Exception as e:
        print(f"❌ AI Chat test failed: {e}")
        return False

def test_projects_api():
    """Test the new projects API endpoint"""
    print("\n🧪 Testing Projects API Endpoint...")
    
    try:
        # Test GET projects
        response = requests.get(
            "http://localhost:5002/api/projects",
            headers={
                "X-API-Key": "notebooker-api-key-2024",
                "Origin": "https://nobooker.netlify.app"
            }
        )
        
        print(f"GET Projects Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Projects API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 CORS Fix Verification Tests")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:5002/", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the Flask app first:")
        print("   cd backend && python app.py")
        return
    
    # Run tests
    health_ok = test_cors_health()
    chat_ok = test_cors_ai_chat()
    projects_ok = test_projects_api()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"  AI Chat Endpoint: {'✅ PASS' if chat_ok else '❌ FAIL'}")
    print(f"  Projects API: {'✅ PASS' if projects_ok else '❌ FAIL'}")
    
    if all([health_ok, chat_ok, projects_ok]):
        print("\n🎉 All tests passed! CORS issues should be fixed.")
    else:
        print("\n⚠️  Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    main()
