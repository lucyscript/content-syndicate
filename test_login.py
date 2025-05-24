#!/usr/bin/env python3
"""
Test login endpoint for ContentSyndicate API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_login():
    """Test user login endpoint"""
    
    # First, let's register a test user if one doesn't exist    
    register_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    
    print("1. Attempting to register test user...")
    register_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    
    if register_response.status_code == 201:
        print("✅ Test user registered successfully")
    elif register_response.status_code == 400:
        print("ℹ️ Test user already exists (expected)")
    else:
        print(f"❌ Unexpected registration response: {register_response.status_code}")
        print(f"Response: {register_response.text}")
    
    # Now test login
    print("\n2. Testing login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    print(f"Login Status Code: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        print("✅ Login successful!")
        print(f"Access Token (first 50 chars): {login_result['access_token'][:50]}...")
        print(f"Token Type: {login_result['token_type']}")
        
        # Test accessing protected endpoint
        print("\n3. Testing protected endpoint (/auth/me)...")
        headers = {
            "Authorization": f"Bearer {login_result['access_token']}"
        }
        
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"Protected endpoint status: {me_response.status_code}")
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            print("✅ Protected endpoint access successful!")
            print(f"User ID: {user_data['id']}")
            print(f"Email: {user_data['email']}")
            print(f"Full Name: {user_data['full_name']}")
            print(f"Subscription Tier: {user_data['subscription_tier']}")
        else:
            print(f"❌ Protected endpoint failed: {me_response.text}")
        
    else:
        print(f"❌ Login failed: {login_response.text}")
    
    # Test invalid login
    print("\n4. Testing invalid login...")
    invalid_login = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    invalid_response = requests.post(f"{BASE_URL}/api/auth/login", json=invalid_login)
    print(f"Invalid login status: {invalid_response.status_code}")
    
    if invalid_response.status_code == 401:
        print("✅ Invalid login correctly rejected")
    else:
        print(f"❌ Unexpected response for invalid login: {invalid_response.text}")

if __name__ == "__main__":
    print("ContentSyndicate Login Test")
    print("=" * 40)
    
    try:
        test_login()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
