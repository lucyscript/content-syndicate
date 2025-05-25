#!/usr/bin/env python3
"""
Test complete frontend Topic Inspiration flow with browser authentication
"""

import time
from playwright.sync_api import sync_playwright

def test_frontend_topic_inspiration():
    print("🌐 TESTING FRONTEND TOPIC INSPIRATION FLOW")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Capture network requests
        api_calls = []
        def log_request(request):
            if 'api' in request.url:
                api_calls.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(request.headers)
                })
        
        def log_response(response):
            if 'api' in response.url:
                print(f"📡 API {response.request.method} {response.url} -> {response.status}")
        
        page.on("request", log_request)
        page.on("response", log_response)
        
        try:
            print("1️⃣ Logging into frontend...")
            page.goto("http://localhost:3000/auth/login")
            page.wait_for_load_state("networkidle")
            
            # Login
            page.fill('input[type="email"]', "test@example.com")
            page.fill('input[type="password"]', "testpassword123")
            page.click('button[type="submit"]')
            page.wait_for_url("**/dashboard**", timeout=15000)
            print("   ✅ Login successful!")
            
            print("2️⃣ Navigating to newsletter creation...")
            page.goto("http://localhost:3000/dashboard/newsletters/new")
            page.wait_for_load_state("networkidle")
            time.sleep(5)  # Allow all React components to mount
            
            print("3️⃣ Checking for Topic Inspiration UI elements...")
            
            # Check for various possible selectors
            topic_selectors = [
                'text="Topic Inspiration"',
                'text*="Topic"',
                'text*="Inspiration"', 
                'text*="Show Suggestions"',
                'text*="Hide Suggestions"',
                'text*="Generate"',
                'button:has-text("Generate")',
                'select',
                '[data-testid*="topic"]',
                '[class*="topic"]',
                'h2',
                'h3'
            ]
            
            found_elements = []
            for selector in topic_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        elements = page.locator(selector).all()
                        for i, element in enumerate(elements):
                            try:
                                text = element.text_content()
                                if text and text.strip():
                                    found_elements.append(f"{selector}: '{text.strip()[:50]}'")
                                    if i >= 2:  # Limit to first 3 matches
                                        break
                            except:
                                pass
                except:
                    pass
            
            print(f"   📝 Found {len(found_elements)} relevant elements:")
            for element in found_elements[:10]:  # Show first 10
                print(f"     - {element}")
            
            print("4️⃣ Checking page structure...")
            
            # Get page structure
            page_structure = page.evaluate("""
                () => {
                    const structure = {
                        title: document.title,
                        headings: Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => h.textContent.trim()).filter(t => t),
                        buttons: Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim()).filter(t => t),
                        forms: document.querySelectorAll('form').length,
                        inputs: document.querySelectorAll('input').length,
                        selects: document.querySelectorAll('select').length
                    };
                    
                    return structure;
                }
            """)
            
            print(f"   📄 Page title: {page_structure['title']}")
            print(f"   📋 Headings: {page_structure['headings'][:5]}")  # First 5 headings
            print(f"   🔘 Buttons: {page_structure['buttons'][:10]}")  # First 10 buttons
            print(f"   📝 Forms: {page_structure['forms']}, Inputs: {page_structure['inputs']}, Selects: {page_structure['selects']}")
            
            print("5️⃣ Checking authentication state...")
            
            # Check auth state in browser
            auth_state = page.evaluate("""
                () => {
                    return {
                        hasToken: localStorage.getItem('authToken') !== null,
                        tokenLength: localStorage.getItem('authToken')?.length || 0,
                        hasUser: localStorage.getItem('user') !== null
                    };
                }
            """)
            
            print(f"   🔐 Auth token present: {auth_state['hasToken']}")
            print(f"   🔐 Token length: {auth_state['tokenLength']}")
            print(f"   👤 User data present: {auth_state['hasUser']}")
            
            print("6️⃣ Summary of API calls made:")
            topic_api_calls = [call for call in api_calls if 'topic' in call['url'].lower() or 'content' in call['url'].lower()]
            
            if topic_api_calls:
                print(f"   📡 Made {len(topic_api_calls)} Topic/Content API calls:")
                for call in topic_api_calls:
                    has_auth = 'authorization' in [k.lower() for k in call['headers'].keys()]
                    auth_status = "🔐" if has_auth else "❌"
                    print(f"     {auth_status} {call['method']} {call['url']}")
            else:
                print("   ⚠️  No Topic/Content API calls detected")
            
            print("7️⃣ Taking screenshot for manual inspection...")
            page.screenshot(path="topic_inspiration_frontend_test.png", full_page=True)
            print("   📷 Screenshot saved as topic_inspiration_frontend_test.png")
            
            # Check if we can manually trigger Topic Inspiration
            print("8️⃣ Attempting to trigger Topic Inspiration...")
            
            # Look for any buttons that might trigger topic generation
            generate_buttons = page.locator('button:has-text("Generate")').all()
            show_buttons = page.locator('button:has-text("Show")').all()
            
            if generate_buttons:
                print(f"   🔘 Found {len(generate_buttons)} Generate buttons")
                try:
                    generate_buttons[0].click()
                    time.sleep(3)
                    print("   ✅ Clicked first Generate button")
                except Exception as e:
                    print(f"   ❌ Error clicking Generate button: {e}")
            
            if show_buttons:
                print(f"   🔘 Found {len(show_buttons)} Show buttons")
                try:
                    show_buttons[0].click()
                    time.sleep(3)
                    print("   ✅ Clicked first Show button")
                except Exception as e:
                    print(f"   ❌ Error clicking Show button: {e}")
            
            input("Press Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    test_frontend_topic_inspiration()