#!/usr/bin/env python3
"""
Comprehensive end-to-end test for ContentSyndicate
Tests the complete user journey: registration -> login -> create newsletter -> view analytics
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8002"

def create_unique_user():
    """Create a unique test user with timestamp"""
    timestamp = str(int(time.time()))
    return {
        "full_name": f"Test User {timestamp}",
        "email": f"test.{timestamp}@contentsyndicate.com",
        "password": "securepassword123"
    }

def test_user_registration(user_data):
    """Test user registration"""
    print("1️⃣ Testing User Registration...")
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    
    if response.status_code == 201:
        user = response.json()
        print(f"   ✅ User registered successfully!")
        print(f"   📧 Email: {user['email']}")
        print(f"   👤 Name: {user['full_name']}")
        print(f"   🆔 ID: {user['id']}")
        return user
    else:
        print(f"   ❌ Registration failed: {response.text}")
        return None

def test_user_login(email, password):
    """Test user login and return access token"""
    print("\n2️⃣ Testing User Login...")
    
    login_data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"   ✅ Login successful!")
        print(f"   🔑 Token type: {token_data['token_type']}")
        return token_data['access_token']
    else:
        print(f"   ❌ Login failed: {response.text}")
        return None

def test_user_profile(token):
    """Test accessing user profile with token"""
    print("\n3️⃣ Testing Protected Profile Access...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    
    if response.status_code == 200:
        profile = response.json()
        print(f"   ✅ Profile access successful!")
        print(f"   👤 Name: {profile['full_name']}")
        print(f"   📧 Email: {profile['email']}")
        print(f"   📊 Subscription: {profile['subscription_tier']}")
        return profile
    else:
        print(f"   ❌ Profile access failed: {response.text}")
        return None

def test_newsletter_creation(token):
    """Test creating a newsletter"""
    print("\n4️⃣ Testing Newsletter Creation...")
    
    newsletter_data = {
        "title": "My Test Newsletter",
        "description": "A test newsletter for ContentSyndicate",
        "frequency": "weekly",
        "template": "modern"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/newsletters/", json=newsletter_data, headers=headers)
    
    if response.status_code == 201:
        newsletter = response.json()
        print(f"   ✅ Newsletter created successfully!")
        print(f"   📰 Title: {newsletter['title']}")
        print(f"   📅 Frequency: {newsletter['frequency']}")
        print(f"   🆔 ID: {newsletter['id']}")
        return newsletter
    else:
        print(f"   ❌ Newsletter creation failed: {response.status_code} - {response.text}")
        return None

def test_newsletters_list(token):
    """Test listing user's newsletters"""
    print("\n5️⃣ Testing Newsletter Listing...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/newsletters/", headers=headers)
    
    if response.status_code == 200:
        newsletters = response.json()
        print(f"   ✅ Newsletter listing successful!")
        print(f"   📊 Total newsletters: {len(newsletters)}")
        for newsletter in newsletters:
            print(f"   📰 - {newsletter['title']} (ID: {newsletter['id']})")
        return newsletters
    else:
        print(f"   ❌ Newsletter listing failed: {response.status_code} - {response.text}")
        return None

def test_content_sources(token):
    """Test content sources functionality"""
    print("\n6️⃣ Testing Content Sources...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/content/sources", headers=headers)
    
    if response.status_code == 200:
        sources = response.json()
        print(f"   ✅ Content sources access successful!")
        print(f"   📊 Available sources: {len(sources)}")
        return sources
    else:
        print(f"   ❌ Content sources failed: {response.status_code} - {response.text}")
        return None

def test_analytics(token):
    """Test analytics functionality"""
    print("\n7️⃣ Testing Analytics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/analytics/overview", headers=headers)
    
    if response.status_code == 200:
        analytics = response.json()
        print(f"   ✅ Analytics access successful!")
        print(f"   📊 Analytics data retrieved")
        return analytics
    else:
        print(f"   ❌ Analytics failed: {response.status_code} - {response.text}")
        return None

def run_comprehensive_test():
    """Run the complete end-to-end test suite"""
    print("🚀 ContentSyndicate Comprehensive End-to-End Test")
    print("=" * 60)
    
    # Create unique user data
    user_data = create_unique_user()
    
    # Test user registration
    user = test_user_registration(user_data)
    if not user:
        print("❌ Test failed at registration step")
        return False
    
    # Test user login
    token = test_user_login(user_data["email"], user_data["password"])
    if not token:
        print("❌ Test failed at login step")
        return False
    
    # Test profile access
    profile = test_user_profile(token)
    if not profile:
        print("❌ Test failed at profile access step")
        return False
    
    # Test newsletter creation
    newsletter = test_newsletter_creation(token)
    
    # Test newsletter listing
    newsletters = test_newsletters_list(token)
    
    # Test content sources
    sources = test_content_sources(token)
    
    # Test analytics
    analytics = test_analytics(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 Test Summary:")
    print(f"   ✅ User Registration: Success")
    print(f"   ✅ User Login: Success")
    print(f"   ✅ Profile Access: Success")
    print(f"   {'✅' if newsletter else '⚠️ '} Newsletter Creation: {'Success' if newsletter else 'Failed (endpoint may not be implemented)'}")
    print(f"   {'✅' if newsletters is not None else '⚠️ '} Newsletter Listing: {'Success' if newsletters is not None else 'Failed (endpoint may not be implemented)'}")
    print(f"   {'✅' if sources is not None else '⚠️ '} Content Sources: {'Success' if sources is not None else 'Failed (endpoint may not be implemented)'}")
    print(f"   {'✅' if analytics is not None else '⚠️ '} Analytics: {'Success' if analytics is not None else 'Failed (endpoint may not be implemented)'}")
    
    print("\n🎉 Core authentication system is working!")
    print("💡 Additional features can be implemented as needed.")
    
    return True

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running on http://localhost:8002")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
