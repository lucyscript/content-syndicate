#!/usr/bin/env python3
"""
Final comprehensive test of the complete Topic Inspiration functionality
"""

import time
from playwright.sync_api import sync_playwright

def final_topic_inspiration_test():
    print("🎯 FINAL TOPIC INSPIRATION FUNCTIONALITY TEST")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Monitor all network activity
        requests_made = []
        
        def track_request(request):
            if 'api' in request.url:
                requests_made.append({
                    'url': request.url,
                    'method': request.method,
                    'timestamp': time.time()
                })
        
        def track_response(response):
            if 'api' in response.url:
                print(f"🌐 {response.request.method} {response.url} → {response.status}")
        
        page.on("request", track_request)
        page.on("response", track_response)
        
        try:
            print("1️⃣ Complete Authentication Flow Test...")
            page.goto("http://localhost:3000/auth/login")
            page.wait_for_load_state("networkidle")
            
            # Perform login
            page.fill('input[type="email"]', "test@example.com")
            page.fill('input[type="password"]', "testpassword123")
            page.click('button[type="submit"]')
            page.wait_for_url("**/dashboard**", timeout=15000)
            
            # Verify authentication state after login
            auth_check = page.evaluate("""
                () => {
                    return {
                        authToken: localStorage.getItem('auth_token'), // Changed 'authToken' to 'auth_token'
                        user: localStorage.getItem('user'),
                        axiosToken: window.axios?.defaults?.headers?.common?.Authorization
                    };
                }
            """)
            
            print(f"   🔐 Token in localStorage: {'✅' if auth_check['authToken'] else '❌'}")
            print(f"   👤 User in localStorage: {'✅' if auth_check['user'] else '❌'}")
            print(f"   🔧 Axios auth header: {'✅' if auth_check['axiosToken'] else '❌'}")
            print(f"   Initial auth_token from localStorage: {auth_check['authToken']}")
            
            print("2️⃣ Topic Inspiration UI Accessibility Test...")
            page.goto("http://localhost:3000/dashboard/newsletters/new")
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Look for Topic Inspiration elements more thoroughly
            topic_ui_elements = page.evaluate("""
                () => {
                    const elements = [];
                    
                    // Search for various Topic Inspiration indicators
                    const searchTerms = ['topic', 'inspiration', 'suggest', 'generate', 'trending'];
                    
                    searchTerms.forEach(term => {
                        // Search in text content
                        const textElements = Array.from(document.querySelectorAll('*')).filter(el => 
                            el.textContent && el.textContent.toLowerCase().includes(term) && 
                            el.children.length === 0 // Only leaf nodes
                        );
                        
                        textElements.forEach(el => {
                            elements.push({
                                type: 'text',
                                term: term,
                                content: el.textContent.trim(),
                                tagName: el.tagName.toLowerCase()
                            });
                        });
                    });
                    
                    return elements.slice(0, 10); // Limit results
                }
            """)
            
            print(f"   📋 Found {len(topic_ui_elements)} Topic-related UI elements:")
            for element in topic_ui_elements:
                print(f"     - {element['tagName']}: {element['content'][:50]}...")
            
            print("3️⃣ Manual API Call Test...")
            
            # Test direct API calls from browser context
            api_test_results = page.evaluate("""
                async () => {
                    const token = localStorage.getItem('auth_token'); // Changed 'authToken' to 'auth_token'
                    const results = [];
                    
                    if (!token) {
                        return [{error: 'No auth token found'}];
                    }
                    
                    const endpoints = [
                        '/api/content/topics/trending',
                        '/api/content/topics/generate?count=3',
                        '/api/content/trending'
                    ];
                    
                    for (const endpoint of endpoints) {
                        try {
                            const response = await fetch(`http://localhost:8000${endpoint}`, {
                                method: 'GET',
                                headers: {
                                    'Authorization': `Bearer ${token}`,
                                    'Content-Type': 'application/json'
                                }
                            });
                            
                            results.push({
                                endpoint: endpoint,
                                status: response.status,
                                success: response.ok,
                                hasData: response.ok ? 'Yes' : 'No'
                            });
                            
                        } catch (error) {
                            results.push({
                                endpoint: endpoint,
                                error: error.message
                            });
                        }
                    }
                    
                    return results;
                }
            """)
            
            print("   📡 Direct API call results:")
            for result in api_test_results:
                if 'error' in result:
                    print(f"     ❌ {result.get('endpoint', 'General')}: {result['error']}")
                else:
                    status = "✅" if result['success'] else "❌"
                    print(f"     {status} {result['endpoint']}: {result['status']} - Data: {result['hasData']}")
            
            print("4️⃣ Interactive Button Test...")
            
            # Try to find the specific "Show Suggestions" button first
            show_suggestions_button = page.query_selector('button:has-text("Show Suggestions")')
            clicked_buttons = []

            if show_suggestions_button:
                print("   🔘 Found 'Show Suggestions' button. Clicking it.")
                try:
                    show_suggestions_button.click()
                    time.sleep(2) # Wait for API calls or UI changes
                    clicked_buttons.append("Show Suggestions")
                    print("   ✅ Clicked 'Show Suggestions' button.")
                    # Verify if suggestions appear or API calls are made
                    # Re-check for API calls after this click
                    page.wait_for_load_state("networkidle", timeout=5000) # wait for potential network activity

                except Exception as e:
                    print(f"   ❌ Error clicking 'Show Suggestions' button: {e}")
            else:
                print("   ⚠️ 'Show Suggestions' button not found specifically.")

            # Fallback to general button search if specific one not found or for other interactions
            if not clicked_buttons: # Only if specific button wasn't clicked
                interactive_buttons = page.locator('button').all()
                for i, button in enumerate(interactive_buttons[:10]):  # Test more buttons
                    try:
                        button_text = button.text_content()
                        if button_text and any(term in button_text.lower() for term in ['generate', 'topic', 'suggest', 'show', 'ai', 'inspiration']):
                            print(f"   🔘 Clicking button: '{button_text.strip()}'")
                            button.click()
                            time.sleep(2)  # Wait for any API calls
                            clicked_buttons.append(button_text.strip())
                            page.wait_for_load_state("networkidle", timeout=5000) # wait for potential network activity
                            # break # Optionally break after one relevant button is clicked
                    except Exception as e:
                        print(f"   ❌ Error clicking button '{button_text.strip() if button_text else 'N/A'}': {e}")
                        pass
            
            if clicked_buttons:
                print(f"   ✅ Successfully clicked {len(clicked_buttons)} relevant buttons")
            else:
                print("   ⚠️  No relevant buttons found to click")
            
            print("5️⃣ Final API Activity Summary...")
            
            topic_requests = [r for r in requests_made if any(term in r['url'].lower() for term in ['topic', 'content', 'trending'])]
            
            if topic_requests:
                print(f"   📊 Made {len(topic_requests)} Topic/Content API requests:")
                for req in topic_requests[-5:]:  # Show last 5
                    print(f"     - {req['method']} {req['url']}")
            else:
                print("   ⚠️  No Topic/Content API requests detected")
            
            # Final screenshot
            page.screenshot(path="final_topic_inspiration_test.png", full_page=True)
            print("   📷 Final screenshot saved")
            
            print("\n" + "=" * 60)
            print("🏁 FINAL TEST COMPLETE")
            
            # Determine overall status
            has_auth = bool(auth_check['authToken'])
            axios_header_set = bool(auth_check['axiosToken'])
            user_in_storage = bool(auth_check['user'])
            has_api_success = any(r.get('success', False) for r in api_test_results if 'success' in r)
            has_ui_elements = len(topic_ui_elements) > 0
            
            if has_auth and has_api_success and has_ui_elements and axios_header_set and user_in_storage and len(clicked_buttons) > 0 and len(topic_requests) > 3:
                print("🎉 SUCCESS: Topic Inspiration is fully functional!")
            elif has_auth and has_api_success and has_ui_elements:
                # More detailed breakdown of pending issues
                pending_issues = []
                if not axios_header_set:
                    pending_issues.append("Axios header not set")
                if not user_in_storage:
                    pending_issues.append("User object not in localStorage")
                if not clicked_buttons:
                    pending_issues.append("Relevant UI buttons not clicked")
                if len(topic_requests) <= 3: # 3 are from manual test
                    pending_issues.append("No UI-triggered API calls for topics")
                print(f"⚠️ PARTIAL SUCCESS: Core auth and API direct calls work, but issues remain: {', '.join(pending_issues)}")    
            else:
                print("❌ FAILURE: Authentication not working or APIs failing")
            
            input("Press Enter to close...")
            
        except Exception as e:
            print(f"❌ Test error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    final_topic_inspiration_test()