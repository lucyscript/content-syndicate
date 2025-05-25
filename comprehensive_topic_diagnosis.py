#!/usr/bin/env python3
"""
Comprehensive Topic Inspiration Diagnosis
Tests all aspects of the Topic Inspiration feature
"""

import requests
import json

def test_newsletter_page_structure():
    print("🔍 Testing newsletter creation page structure...")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:3000/dashboard/newsletters/new", timeout=10)
        html = response.text
        
        print(f"Status: {response.status_code}")
        print(f"Content Length: {len(html)}")
        
        # Check for authentication redirection
        if 'login' in html.lower() and 'sign in' in html.lower():
            print("\n❌ Page is redirecting to login - authentication required")
            return False
        
        # Look for React hydration indicators
        has_next_data = '__NEXT_DATA__' in html
        has_next_div = 'id="__next"' in html
        has_react_scripts = '_next/static' in html
        
        print(f"\n🔍 React Hydration Check:")
        print(f"   __NEXT_DATA__ present: {has_next_data}")
        print(f"   #__next div present: {has_next_div}")
        print(f"   React scripts present: {has_react_scripts}")
        
        # Look for the specific newsletter page content
        newsletter_indicators = [
            'Create New Newsletter',
            'Newsletter Title',
            'Subject Line',
            'Target Audience',
            'Topic Inspiration',
            'Show Suggestions',
            'Generate Content'
        ]
        
        found_indicators = []
        for indicator in newsletter_indicators:
            if indicator in html:
                found_indicators.append(indicator)
        
        print(f"\n📋 Newsletter Page Elements:")
        print(f"   Found {len(found_indicators)}/{len(newsletter_indicators)} elements")
        for indicator in found_indicators:
            print(f"   ✅ {indicator}")
        
        missing_indicators = [ind for ind in newsletter_indicators if ind not in found_indicators]
        if missing_indicators:
            print(f"\n❌ Missing elements:")
            for indicator in missing_indicators:
                print(f"   ❌ {indicator}")
        
        # Check if we're getting a loading screen or the actual content
        has_loading = 'Loading...' in html or 'animate-spin' in html
        has_auth_check = 'isAuthenticated' in html or 'authLoading' in html
        
        print(f"\n🔍 Page State Analysis:")
        print(f"   Has loading indicator: {has_loading}")
        print(f"   Has auth check code: {has_auth_check}")
        
        # Extract the body content to see what's actually rendering
        if '<body' in html and '</body>' in html:
            body_start = html.find('<body')
            body_end = html.find('</body>') + 7
            body_content = html[body_start:body_end]
            
            # Look for visible content vs just scripts
            visible_content_indicators = [
                'Create New Newsletter',
                'Topic Inspiration', 
                'class="',
                'className="'
            ]
            
            visible_content_count = sum(1 for indicator in visible_content_indicators if indicator in body_content)
            print(f"   Visible content indicators: {visible_content_count}")
            
            if visible_content_count < 2:
                print("   ⚠️  Body seems to contain mostly scripts, little visible content")
                # Show a sample of the body
                print(f"\n📄 Body sample (first 500 chars):")
                clean_body = body_content.replace('><', '>\n<')[:500]
                print(clean_body)
            else:
                print("   ✅ Body contains substantial visible content")
        
        return len(found_indicators) >= 3
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_backend_apis():
    print("\n" + "=" * 60)
    print("🔍 Testing Backend API Endpoints...")
    
    # Test the backend server first
    try:
        print("\n1. Testing backend server health...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"   Backend Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Backend server is running")
        else:
            print("   ❌ Backend server issue")
    except Exception as e:
        print(f"   ❌ Backend server error: {e}")
    
    # Test specific Topic Inspiration APIs
    endpoints = [
        ("GET", "http://localhost:8000/api/content/trending", None),
        ("POST", "http://localhost:8000/api/content/topics/generate", {"count": 5, "niche": "general"}),
        ("GET", "http://localhost:3000/api/content/trending", None),
        ("POST", "http://localhost:3000/api/content/topics/generate", {"count": 5, "niche": "general"})
    ]
    
    for method, url, data in endpoints:
        try:
            print(f"\n2. Testing {method} {url}...")
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json=data, timeout=5)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ API accessible")
                try:
                    result = response.json()
                    print(f"   Response type: {type(result)}")
                    if isinstance(result, dict):
                        print(f"   Keys: {list(result.keys())}")
                except:
                    print("   Response not JSON")
            elif response.status_code == 403:
                print("   ⚠️  Authentication required")
            elif response.status_code == 404:
                print("   ❌ Endpoint not found")
            else:
                print(f"   ❌ Unexpected status")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_authentication_flow():
    print("\n" + "=" * 60)
    print("🔍 Testing Authentication Flow...")
    
    # Test login with a known user
    try:
        print("\n1. Testing login...")
        login_data = {"email": "test@example.com", "password": "password123"}
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=5)
        
        print(f"   Login Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            print("   ✅ Login successful")
            
            if token:
                print(f"   Token received: {token[:20]}...")
                
                # Test accessing protected endpoint with token
                headers = {"Authorization": f"Bearer {token}"}
                
                print("\n2. Testing authenticated API access...")
                protected_endpoints = [
                    "http://localhost:8000/api/content/trending",
                    "http://localhost:8000/api/auth/me"
                ]
                
                for endpoint in protected_endpoints:
                    try:
                        auth_response = requests.get(endpoint, headers=headers, timeout=5)
                        print(f"   {endpoint}: {auth_response.status_code}")
                        if auth_response.status_code == 200:
                            print("     ✅ Accessible with authentication")
                        else:
                            print(f"     ❌ Still blocked: {auth_response.status_code}")
                    except Exception as e:
                        print(f"     ❌ Error: {e}")
            else:
                print("   ❌ No token in response")
        else:
            print("   ❌ Login failed")
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")

def main():
    print("🚀 Comprehensive Topic Inspiration Diagnosis")
    print("=" * 60)
    
    page_ok = test_newsletter_page_structure()
    test_backend_apis()
    test_authentication_flow()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    if page_ok:
        print("✅ Newsletter page structure looks good")
        print("💡 The Topic Inspiration UI should be visible when:")
        print("   1. User is properly authenticated")
        print("   2. React components finish hydrating")
        print("   3. API endpoints are accessible")
    else:
        print("❌ Newsletter page has issues")
        print("💡 Possible fixes:")
        print("   1. Check authentication state")
        print("   2. Verify React hydration")
        print("   3. Check component rendering logic")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Try logging in to the application")
    print(f"   2. Navigate to /dashboard/newsletters/new")
    print(f"   3. Look for 'Topic Inspiration' section")
    print(f"   4. Click 'Show Suggestions' button")

if __name__ == "__main__":
    main()
