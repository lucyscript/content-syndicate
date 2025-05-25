#!/usr/bin/env python3
"""
Test Topic Inspiration UI specifically
Tests the newsletter creation page where Topic Inspiration should appear
"""

import requests
import time

def test_topic_inspiration_page():
    print("🔍 Testing Topic Inspiration UI on newsletter creation page...")
    print("=" * 60)
    
    # First, let's test the newsletter creation page
    try:
        # Test the newsletter creation page (should redirect to login if not authenticated)
        print("1. Testing newsletter creation page access...")
        response = requests.get("http://localhost:3000/dashboard/newsletters/new", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Length: {len(response.text)}")
        
        html = response.text
        
        # Look for the Topic Inspiration elements
        has_topic_inspiration = 'Topic Inspiration' in html
        has_suggestions_button = 'Show' in html and 'Suggestions' in html
        has_trending_topics = 'Trending' in html or 'trending' in html
        has_ai_generated = 'AI' in html and 'generated' in html.lower()
        
        print(f"\n🎯 Topic Inspiration Analysis:")
        print(f"   Contains 'Topic Inspiration': {has_topic_inspiration}")
        print(f"   Contains suggestions button: {has_suggestions_button}")
        print(f"   Contains trending references: {has_trending_topics}")
        print(f"   Contains AI generated references: {has_ai_generated}")
        
        # Look for the specific elements we know should be there
        topic_indicators = [
            'Topic Inspiration',
            'Show Suggestions',
            'Hide Suggestions', 
            'Niche:',
            'Refresh',
            'Loading topic suggestions',
            'trending',
            'ai_generated'
        ]
        
        found_indicators = []
        for indicator in topic_indicators:
            if indicator in html:
                found_indicators.append(indicator)
        
        print(f"\n📋 Found Topic Inspiration indicators:")
        for indicator in found_indicators:
            print(f"   ✅ {indicator}")
        
        missing_indicators = [ind for ind in topic_indicators if ind not in found_indicators]
        if missing_indicators:
            print(f"\n❌ Missing indicators:")
            for indicator in missing_indicators:
                print(f"   ❌ {indicator}")
        
        # Check if this is a redirect to login
        if response.status_code == 200 and len(html) < 10000:
            print(f"\n⚠️  Warning: Page seems short, might be a redirect or login page")
            if 'login' in html.lower() or 'sign in' in html.lower():
                print("   ➡️  Detected login page - authentication required")
        
        # Try to extract any React hydration content
        if 'AuthProvider' in html or 'QueryProvider' in html:
            print(f"\n✅ React providers detected - React is working")
        else:
            print(f"\n⚠️  React providers not detected")
        
        # Look for specific Topic Inspiration UI elements that should be in the HTML
        newsletter_form_elements = [
            'Newsletter Title',
            'Subject Line',
            'Target Audience',
            'Generate Content'
        ]
        
        found_form_elements = []
        for element in newsletter_form_elements:
            if element in html:
                found_form_elements.append(element)
        
        print(f"\n📝 Newsletter form elements found: {len(found_form_elements)}/{len(newsletter_form_elements)}")
        for element in found_form_elements:
            print(f"   ✅ {element}")
        
        return has_topic_inspiration and len(found_indicators) > 3
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_endpoints():
    print("\n" + "=" * 60)
    print("🔍 Testing Topic Inspiration API endpoints...")
    
    # Test trending topics endpoint
    try:
        print("\n1. Testing trending topics API...")
        response = requests.get("http://localhost:3000/api/content/trending", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 403:
            print("   ⚠️  Authentication required (403 Forbidden)")
        elif response.status_code == 200:
            print("   ✅ API accessible")
            try:
                data = response.json()
                print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            except:
                print("   Response not JSON")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test random topics generation
    try:
        print("\n2. Testing random topics generation API...")
        response = requests.post("http://localhost:3000/api/content/topics/generate", 
                               json={"count": 5, "niche": "general"}, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 403:
            print("   ⚠️  Authentication required (403 Forbidden)")
        elif response.status_code == 200:
            print("   ✅ API accessible")
            try:
                data = response.json()
                print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            except:
                print("   Response not JSON")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    success = test_topic_inspiration_page()
    test_api_endpoints()
    
    print(f"\n" + "=" * 60)
    print(f"🏁 Test Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    if not success:
        print("\n💡 Possible issues:")
        print("   1. Authentication required - need to login first")
        print("   2. React hydration not working properly")
        print("   3. Topic Inspiration component not rendering")
        print("   4. API endpoints returning errors")
    else:
        print("\n🎉 Topic Inspiration UI elements found in the page!")
        print("   The UI should be visible once authenticated.")
