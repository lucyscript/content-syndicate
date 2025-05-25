#!/usr/bin/env python3
"""
Simple test to check authentication states and Topic Inspiration rendering
"""

from playwright.sync_api import sync_playwright
import time

def test_auth_states():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Capture console logs
        console_logs = []
        def handle_console(msg):
            if '[NewNewsletterPage]' in msg.text:
                console_logs.append(msg.text)
                print(f"📝 {msg.text}")
        
        page.on("console", handle_console)
        
        try:
            print("🔐 Logging in...")
            page.goto('http://localhost:3000/auth/login')
            page.fill('input[name="email"]', 'test@example.com')
            page.fill('input[name="password"]', 'testpassword123')
            page.click('button[type="submit"]')
            page.wait_for_url('**/dashboard**', timeout=10000)
            
            print("📝 Navigating to newsletter creation page...")
            page.goto('http://localhost:3000/dashboard/newsletters/new')
            
            # Wait a bit for React to render
            time.sleep(3)
            
            print("\n🎯 Console logs captured:")
            for log in console_logs:
                print(f"   {log}")
            
            # Check for Topic Inspiration elements
            topic_header = page.locator('[data-testid="topic-inspiration-header"]')
            topic_button = page.locator('[data-testid="show-topic-suggestions-button"]')
            
            print(f"\n🎯 Topic Inspiration status:")
            print(f"   Header found: {topic_header.count() > 0}")
            print(f"   Button found: {topic_button.count() > 0}")
            
            if topic_header.count() > 0:
                print(f"   Header visible: {topic_header.is_visible()}")
            if topic_button.count() > 0:
                print(f"   Button visible: {topic_button.is_visible()}")
                
            # Take a screenshot for manual inspection
            page.screenshot(path="debug_auth_states.png")
            print(f"\n📷 Screenshot saved as debug_auth_states.png")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    test_auth_states()
