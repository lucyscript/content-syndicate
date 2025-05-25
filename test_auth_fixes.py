#!/usr/bin/env python3
"""
Test script to verify the auth fixes are working properly
"""

import asyncio
from playwright.async_api import async_playwright
import json
import time

async def test_auth_fixes():
    print("🔧 TESTING AUTH FIXES")
    print("=" * 50)
    
    async with async_playwright() as p:
        # Launch browser with debugging
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"🖥️ Console: {msg.text}"))
        page.on("pageerror", lambda error: print(f"❌ Page Error: {error}"))
        
        try:
            print("\n1️⃣ Navigate to login page and clear storage...")
            await page.goto('http://localhost:3000/auth/login')
            await page.wait_for_load_state('networkidle')
            
            # Clear all storage
            await page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")            await page.reload()
            await page.wait_for_load_state('networkidle')
            
            print("\n2️⃣ Perform login...")
            await page.fill('input[name="email"]', 'test@example.com')
            await page.fill('input[name="password"]', 'testpassword123')
            
            # Click login and wait for navigation
            await page.click('button[type="submit"]')
            await page.wait_for_url('**/dashboard**', timeout=10000)
            
            print("✅ Login successful - redirected to dashboard")
            
            print("\n3️⃣ Check localStorage after login...")
            
            # Wait a moment for auth provider to process
            await page.wait_for_timeout(2000)
            
            auth_token = await page.evaluate("() => localStorage.getItem('auth_token')")
            user_data = await page.evaluate("() => localStorage.getItem('user')")
            
            print(f"   🔐 Auth token in localStorage: {'✅' if auth_token else '❌'}")
            print(f"   👤 User data in localStorage: {'✅' if user_data else '❌'}")
            
            if user_data:
                try:
                    user_obj = json.loads(user_data)
                    print(f"   📋 User object keys: {list(user_obj.keys())}")
                except:
                    print("   ⚠️ User data is not valid JSON")
            
            print("\n4️⃣ Check Axios authorization header...")
            
            # Check if axios has the auth header by making a test API call
            network_requests = []
            
            def handle_request(request):
                if 'api/' in request.url:
                    network_requests.append({
                        'url': request.url,
                        'headers': dict(request.headers)
                    })
            
            page.on("request", handle_request)
            
            print("\n5️⃣ Navigate to newsletter creation page...")
            await page.goto('http://localhost:3000/dashboard/newsletters/new')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(3000)  # Wait for any API calls
            
            print("\n6️⃣ Check for Topic Inspiration UI elements...")
            
            # Look for topic inspiration elements
            topic_elements = await page.query_selector_all('text="Topic Inspiration"')
            show_suggestions_btn = await page.query_selector('text="Show Suggestions"')
            generate_ai_btn = await page.query_selector('text="Generate with AI"')
            
            print(f"   📋 Topic Inspiration sections found: {len(topic_elements)}")
            print(f"   🔘 'Show Suggestions' button: {'✅' if show_suggestions_btn else '❌'}")
            print(f"   🤖 'Generate with AI' button: {'✅' if generate_ai_btn else '❌'}")
            
            print("\n7️⃣ Try clicking Topic Inspiration buttons...")
            
            if show_suggestions_btn:
                print("   🔘 Clicking 'Show Suggestions' button...")
                await show_suggestions_btn.click()
                await page.wait_for_timeout(2000)
                
                # Check if API calls were made
                topic_api_calls = [req for req in network_requests if 'topics' in req['url']]
                print(f"   📡 Topic API calls after click: {len(topic_api_calls)}")
                
                for call in topic_api_calls:
                    auth_header = call['headers'].get('authorization', 'Not found')
                    print(f"      - {call['url']}")
                    print(f"        Auth header: {'✅' if auth_header.startswith('Bearer') else '❌'}")
            
            print("\n8️⃣ Final network requests analysis...")
            api_requests = [req for req in network_requests if 'api/' in req['url']]
            print(f"   📊 Total API requests made: {len(api_requests)}")
            
            for i, req in enumerate(api_requests[-5:], 1):  # Show last 5 requests
                auth_header = req['headers'].get('authorization', 'Not found')
                print(f"   {i}. {req['url']}")
                print(f"      Auth: {'✅ Bearer token' if auth_header.startswith('Bearer') else '❌ No auth header'}")
            
            print("\n📷 Taking screenshot...")
            await page.screenshot(path='test_auth_fixes.png', full_page=True)
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            await page.screenshot(path='test_auth_fixes_error.png', full_page=True)
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_auth_fixes())
    print("\n🏁 Test complete!")
    input("Press Enter to exit...")
