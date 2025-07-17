#!/usr/bin/env python3
"""
Test script for Aid-al-Neo API
Run this after starting the server to test the endpoints
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "test_api_key_123"
ADMIN_TOKEN = "test_admin_token_456"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat():
    """Test the chat endpoint"""
    print("\nTesting chat endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "message": "Bonjour, pouvez-vous m'expliquer les règles de licenciement en France?",
            "channel": "test",
            "user_id": "test_user_123"
        }
        
        print(f"Sending request to {BASE_URL}/api/v1/chat")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            headers=headers,
            json=data,
            timeout=120  # 2 minutes timeout for model generation
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"Error response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_models():
    """Test the models endpoint"""
    print("\nTesting models endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/v1/models",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("Aid-al-Neo API Test Suite")
    print("=" * 50)
    
    # Wait a bit for server to start
    print("Waiting for server to be ready...")
    time.sleep(5)
    
    tests = [
        ("Health Check", test_health),
        ("Models List", test_models),
        ("Chat Endpoint", test_chat),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("\nYou can now:")
        print("- Access the API at: http://localhost:8000")
        print("- View documentation at: http://localhost:8000/docs")
        print("- Use the test API key: test_api_key_123")
    else:
        print("\n❌ Some tests failed. Check the server logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 