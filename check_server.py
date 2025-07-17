#!/usr/bin/env python3
"""
Simple server health check script
Run this to check if the server is running and accessible
"""

import requests
import time
import sys

def check_server():
    """Check if the server is running"""
    url = "http://localhost:8000/api/v1/health"
    
    print(f"Checking server at: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - server is not running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout - server might be starting up")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def wait_for_server(max_wait=60):
    """Wait for server to start up"""
    print(f"Waiting for server to start (max {max_wait} seconds)...")
    
    for i in range(max_wait):
        if check_server():
            return True
        print(f"Attempt {i+1}/{max_wait} - waiting 2 seconds...")
        time.sleep(2)
    
    print("❌ Server did not start within the timeout period")
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--wait":
        success = wait_for_server()
        sys.exit(0 if success else 1)
    else:
        success = check_server()
        sys.exit(0 if success else 1) 