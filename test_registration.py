#!/usr/bin/env python3
"""
Test script to verify the registration API endpoint works correctly
with the updated full_name field.
"""
import requests
import json

import time

# Test registration data with full_name field - using timestamp to ensure uniqueness
timestamp = str(int(time.time()))
test_user = {
    "full_name": f"Test User {timestamp}",
    "email": f"test.user.{timestamp}@example.com",
    "password": "newpassword123"
}

def test_registration():
    """Test user registration with new schema"""
    url = "http://localhost:8002/api/auth/register"
    
    try:
        response = requests.post(url, json=test_user)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            user_data = response.json()
            print("✅ Registration successful!")
            print(f"User ID: {user_data.get('id')}")
            print(f"Email: {user_data.get('email')}")
            print(f"Full Name: {user_data.get('full_name')}")
            print(f"Subscription Plan: {user_data.get('subscription_plan')}")
            return True
        else:
            print("❌ Registration failed!")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure it's running on http://localhost:8002")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_login():
    """Test user login after registration"""
    url = "http://localhost:8002/api/auth/login"
    
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    
    try:
        response = requests.post(url, json=login_data)
        
        print(f"\nLogin Status Code: {response.status_code}")
        
        if response.status_code == 200:
            login_response = response.json()
            print("✅ Login successful!")
            print(f"Access Token: {login_response.get('access_token')[:50]}...")
            print(f"Token Type: {login_response.get('token_type')}")
            return login_response.get('access_token')
        else:
            print("❌ Login failed!")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_user_profile(access_token):
    """Test getting user profile with token"""
    url = "http://localhost:8002/api/auth/me"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"\nProfile Status Code: {response.status_code}")
        
        if response.status_code == 200:
            profile_data = response.json()
            print("✅ Profile fetch successful!")
            print(f"Profile Full Name: {profile_data.get('full_name')}")
            print(f"Profile Email: {profile_data.get('email')}")
            return True
        else:
            print("❌ Profile fetch failed!")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Profile fetch error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing ContentSyndicate Registration API")
    print("=" * 50)
    
    # Test registration
    registration_success = test_registration()
    
    if registration_success:
        # Test login
        access_token = test_login()
        
        if access_token:
            # Test profile
            test_user_profile(access_token)
    
    print("\n" + "=" * 50)
    print("🏁 API test completed!")
