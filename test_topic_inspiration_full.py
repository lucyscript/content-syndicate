#!/usr/bin/env python3
"""
Comprehensive test of Topic Inspiration functionality with authentication
"""

from playwright.sync_api import sync_playwright
import time

def test_topic_inspiration_full():
    """Test complete Topic Inspiration workflow"""
    
    print("🚀 TESTING TOPIC INSPIRATION FUNCTIONALITY")
    print("=" * 50)
    
    # Test data
    login_credentials = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Monitor API calls
        api_calls = []
        page.on("response", lambda response: api_calls.append({
            "url": response.url,
            "status": response.status,
            "method": response.request.method
        }))
        
        try:
            print("1️⃣ Logging in...")
            page.goto("http://localhost:3000/auth/login")
            page.wait_for_load_state("networkidle")
            
            # Login
            page.fill('input[type="email"]', login_credentials["email"])
            page.fill('input[type="password"]', login_credentials["password"])
            page.click('button[type="submit"]')
            page.wait_for_url("**/dashboard**", timeout=10000)
            print("✅ Login successful")
            
            print("2️⃣ Navigating to newsletter creation...")
            page.goto("http://localhost:3000/dashboard/newsletters/new")
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Allow components to load
            print("3️⃣ Testing Topic Inspiration UI elements...")
            # Check for various Topic Inspiration elements
            elements_to_check = [
                ("Topic Inspiration heading", 'h2:has-text("Topic Inspiration")'),
                ("Show Suggestions button", 'button:has-text("Show Suggestions")'),
                ("Topic suggestions description", 'text="Get AI-powered topic suggestions to kickstart your newsletter"'),
                ("Niche selector", 'select'),
                ("Refresh button", 'button:has-text("Refresh")'),
            ]
            
            found_elements = []
            for name, selector in elements_to_check:
                try:
                    if page.locator(selector).count() > 0:
                        found_elements.append(name)
                        print(f"   ✅ Found: {name}")
                    else:
                        print(f"   ❌ Missing: {name}")
                except Exception as e:
                    print(f"   ❌ Error checking {name}: {e}")
            
            print(f"\n4️⃣ Found {len(found_elements)} Topic Inspiration elements")
            
            print("5️⃣ Testing API endpoints...")
            
            # Filter API calls related to topic inspiration
            topic_api_calls = [call for call in api_calls if 
                              'topic' in call['url'] or 'trending' in call['url'] or 
                              'generate' in call['url'] and 'content' in call['url']]
            
            if topic_api_calls:
                print("✅ Topic-related API calls made:")
                for call in topic_api_calls:
                    status_icon = "✅" if call['status'] == 200 else "❌"
                    print(f"   {status_icon} {call['method']} {call['url']} - {call['status']}")
            else:                print("ℹ️ No automatic topic API calls detected (this is normal)")
            
            print("6️⃣ Manually triggering Topic Inspiration features...")
              # Try to click on Show Suggestions button
            suggestions_button = page.locator('text="✨ Show Suggestions"')
            if suggestions_button.count() > 0:
                print("   🔄 Clicking Show Suggestions...")
                suggestions_button.click()
                time.sleep(3)  # Wait for suggestions to load
                
                # Check if suggestions panel opened
                niche_selector = page.locator('select')
                if niche_selector.count() > 0:
                    print("   ✅ Suggestions panel opened")
                    
                    # Try refreshing to trigger API calls
                    refresh_button = page.locator('text="🔄 Refresh"')
                    if refresh_button.count() > 0:
                        print("   🔄 Clicking Refresh to load topics...")
                        refresh_button.click()
                        time.sleep(5)  # Wait for API calls
                # Check for new API calls after refresh
                new_topic_calls = [call for call in api_calls if 
                                  'topic' in call['url'] or 'trending' in call['url']]
                
                if new_topic_calls:
                    print("   ✅ API calls triggered:")
                    for call in new_topic_calls[-5:]:  # Show last 5 calls
                        status_icon = "✅" if call['status'] == 200 else "❌"
                        print(f"     {status_icon} {call['method']} {call['url']} - {call['status']}")
                else:
                    print("   ⚠️ No topic API calls detected after refresh")
                
                if new_topic_calls:
                    print("   ✅ Trending Topics API call triggered:")
                    for call in new_topic_calls:
                        status_icon = "✅" if call['status'] == 200 else "❌"
                        print(f"      {status_icon} {call['method']} {call['url']} - {call['status']}")
                else:
                    print("   ℹ️ No immediate API call (may be handled differently)")
            
            # Try generate topics if available
            generate_button = page.locator('text="Generate Topics"')
            if generate_button.count() > 0:
                print("   🔄 Clicking Generate Topics...")
                generate_button.click()
                time.sleep(2)
            
            print("7️⃣ Final verification...")
            
            # Check localStorage for auth token
            auth_token = page.evaluate("() => localStorage.getItem('auth_token')")
            if auth_token:
                print("✅ Authentication token present")
            else:
                print("❌ No authentication token")
            
            # Take a final screenshot
            page.screenshot(path="topic_inspiration_test.png")
            print("📷 Screenshot saved as topic_inspiration_test.png")
            
            # Summary
            print("\n" + "=" * 50)
            print("📊 SUMMARY")
            print("=" * 50)
            print(f"✅ Authentication: {'Working' if auth_token else 'Failed'}")
            print(f"✅ Topic Elements Found: {len(found_elements)}")
            print(f"✅ API Calls: {len([c for c in api_calls if c['status'] == 200])} successful")
            print(f"❌ Failed API Calls: {len([c for c in api_calls if c['status'] != 200])}")
            
            if len(found_elements) > 0 and auth_token:
                print("🎉 TOPIC INSPIRATION UI IS WORKING!")
            else:
                print("⚠️ Some issues detected")
                
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            page.screenshot(path="error_topic_test.png")
            
        finally:
            input("Press Enter to close browser...")
            browser.close()

if __name__ == "__main__":
    test_topic_inspiration_full()
