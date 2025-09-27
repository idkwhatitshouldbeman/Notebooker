#!/usr/bin/env python3
"""
Test script for the new API endpoints
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:5002"  # Change this to your Render URL when deployed
API_KEY = "notebooker-api-key-2024"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_chat():
    """Test the /api/ai/chat endpoint"""
    print("Testing /api/ai/chat...")
    
    data = {
        "message": "Help me create a technical documentation structure for my robotics project",
        "projectId": "test-project-001",
        "context": "Robotics engineering project with sensors and actuators"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/ai/chat", json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_analyze():
    """Test the /api/ai/analyze endpoint"""
    print("\nTesting /api/ai/analyze...")
    
    data = {
        "content": "This is a basic description of our robot system. It has sensors and motors.",
        "projectId": "test-project-001"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/ai/analyze", json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_draft():
    """Test the /api/ai/draft endpoint"""
    print("\nTesting /api/ai/draft...")
    
    data = {
        "topic": "Sensor Integration and Calibration",
        "projectId": "test-project-001",
        "style": "technical"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/ai/draft", json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_plan():
    """Test the /api/ai/plan endpoint"""
    print("\nTesting /api/ai/plan...")
    
    data = {
        "projectId": "test-project-001",
        "goals": ["Implement sensor fusion", "Create autonomous navigation", "Document testing procedures"]
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/ai/plan", json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_cors():
    """Test CORS headers"""
    print("\nTesting CORS...")
    
    try:
        # Test preflight request
        response = requests.options(f"{API_BASE_URL}/api/ai/chat", headers={
            "Origin": "https://notebooker.netlify.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, X-API-Key"
        })
        
        print(f"CORS Preflight Status: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        # Check for CORS headers
        cors_headers = [h for h in response.headers if 'access-control' in h.lower()]
        if cors_headers:
            print("✅ CORS headers present")
            return True
        else:
            print("❌ CORS headers missing")
            return False
            
    except Exception as e:
        print(f"CORS Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing NTBK_AI API Endpoints")
    print("=" * 50)
    
    # Test all endpoints
    results = []
    results.append(test_chat())
    results.append(test_analyze())
    results.append(test_draft())
    results.append(test_plan())
    results.append(test_cors())
    
    print("\n" + "=" * 50)
    print(f"✅ Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! API is ready for frontend integration.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
