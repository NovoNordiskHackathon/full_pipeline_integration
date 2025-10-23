#!/usr/bin/env python3
"""
Simple test script to verify the backend is working
"""

import requests
import json

def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing PTD Generator Backend...")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print()
    
    # Test 2: Status endpoint
    print("2. Testing status endpoint...")
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            print("✅ Status endpoint working")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    print()
    
    # Test 3: Test JSON processing
    print("3. Testing JSON processing...")
    test_data = {
        "protocol_json": {
            "elements": [
                {"path": "//Document/Title", "text": "Test Protocol"},
                {"path": "//Document/H1", "text": "Introduction"}
            ]
        },
        "ecrf_json": {
            "elements": [
                {"path": "//Document/Title", "text": "Test eCRF"},
                {"path": "//Document/H1", "text": "Data Collection"}
            ]
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/run_pipeline",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            print("✅ JSON processing test passed")
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ JSON processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ JSON processing error: {e}")
    
    print()
    print("=" * 50)
    print("🏁 Backend testing completed!")

if __name__ == "__main__":
    test_backend()