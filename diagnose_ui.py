import time
import requests
import json

def diagnose_topic_inspiration_ui():
    """Comprehensive diagnosis of Topic Inspiration UI issues"""
    
    print("🔧 DIAGNOSING TOPIC INSPIRATION UI")
    print("=" * 50)
    
    # Test 1: Check if the page loads
    print("\n1️⃣ Testing page accessibility...")
    try:
        response = requests.get("http://localhost:3000/dashboard/newsletters/new", timeout=10)
        if response.status_code == 200:
            print("✅ Page loads successfully")
            page_content = response.text
            
            # Check for React app mounting
            if '__NEXT_DATA__' in page_content:
                print("✅ Next.js app is properly initialized")
            else:
                print("❌ Next.js initialization issue detected")
                
        else:
            print(f"❌ Page failed to load: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error loading page: {e}")
        return False
    
    # Test 2: Check for authentication status
    print("\n2️⃣ Testing authentication status...")
    try:
        # Try to get user info to see if auth is working
        auth_response = requests.get("http://localhost:8000/api/auth/me", 
                                   headers={"Authorization": "Bearer test_token"})
        print(f"Auth endpoint response: {auth_response.status_code}")
    except Exception as e:
        print(f"Auth test error: {e}")
    
    # Test 3: Check for JavaScript/React specific content
    print("\n3️⃣ Checking for React component elements...")
    react_indicators = [
        "useState", "useEffect", "React", "component", 
        "Newsletter", "Create", "dashboard"
    ]
    
    found_react = False
    for indicator in react_indicators:
        if indicator in page_content:
            found_react = True
            break
    
    if found_react:
        print("✅ React components appear to be present")
    else:
        print("❌ React components may not be rendering")
    
    # Test 4: Specific Topic Inspiration element check
    print("\n4️⃣ Searching for Topic Inspiration specific elements...")
    topic_elements = [
        "topic-inspiration", "trending-topics", "generate-topics",
        "show-suggestions", "random-topics", "loadTopicSuggestions"
    ]
    
    found_topic_elements = []
    for element in topic_elements:
        if element.lower() in page_content.lower():
            found_topic_elements.append(element)
    
    if found_topic_elements:
        print(f"✅ Found Topic Inspiration elements: {found_topic_elements}")
    else:
        print("❌ No Topic Inspiration elements found")
    
    # Test 5: Check if APIs are accessible from frontend
    print("\n5️⃣ Testing API accessibility from frontend perspective...")
    try:
        # Test if the APIs work from the same context
        trending_test = requests.get("http://localhost:8000/api/content/topics/trending?limit=3")
        generate_test = requests.get("http://localhost:8000/api/content/topics/generate?count=3")
        
        print(f"Trending API: {trending_test.status_code}")
        print(f"Generate API: {generate_test.status_code}")
        
    except Exception as e:
        print(f"API test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS COMPLETE")
    
    return True

if __name__ == "__main__":
    diagnose_topic_inspiration_ui()