#!/usr/bin/env python3
"""
Quick JavaScript error check for React hydration issues
"""

from playwright.sync_api import sync_playwright
import time

def quick_js_check():
    print("🔍 QUICK JAVASCRIPT ERROR CHECK")
    print("=" * 40)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Headless for automation
        page = browser.new_page()
        
        # Capture all console messages and errors
        js_errors = []
        
        def log_console(msg):
            if msg.type in ['error', 'warning']:
                js_errors.append(f"{msg.type.upper()}: {msg.text}")
                print(f"🚨 {msg.type.upper()}: {msg.text}")
        
        def log_page_error(error):
            js_errors.append(f"PAGE ERROR: {error}")
            print(f"🚨 PAGE ERROR: {error}")
        
        page.on("console", log_console)
        page.on("pageerror", log_page_error)
        
        try:
            print("1️⃣ Loading login page...")
            page.goto("http://localhost:3000/auth/login")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            print("2️⃣ Logging in...")
            page.fill('input[type="email"]', "test@example.com")
            page.fill('input[type="password"]', "testpassword123")
            page.click('button[type="submit"]')
            page.wait_for_url("**/dashboard**", timeout=10000)
            time.sleep(2)
            
            print("3️⃣ Navigating to newsletter creation...")
            page.goto("http://localhost:3000/dashboard/newsletters/new")
            page.wait_for_load_state("networkidle")
            time.sleep(5)  # Wait longer for React to attempt hydration
            
            print("4️⃣ Checking for React and Next.js...")
            
            # Check for Next.js and React globals
            globals_check = page.evaluate("""
                () => {
                    return {
                        nextRouter: typeof window.__NEXT_ROUTER__ !== 'undefined',
                        nextData: typeof window.__NEXT_DATA__ !== 'undefined',
                        react: typeof window.React !== 'undefined',
                        reactDOM: typeof window.ReactDOM !== 'undefined',
                        nextApp: document.querySelector('#__next') !== null,
                        scriptTags: Array.from(document.querySelectorAll('script')).length,
                        nextScripts: Array.from(document.querySelectorAll('script[src*="_next"]')).length,
                        hasTopicInspiration: document.querySelector('[data-testid="topic-inspiration"]') !== null,
                        authElements: document.querySelectorAll('[data-auth]').length
                    };
                }
            """)
            
            print("📊 Global objects check:")
            for key, value in globals_check.items():
                status = "✅" if value else "❌"
                print(f"  {status} {key}: {value}")
            
            print("5️⃣ Summary of JS errors:")
            if js_errors:
                print(f"🚨 Found {len(js_errors)} JavaScript errors:")
                for error in js_errors:
                    print(f"  - {error}")
            else:
                print("✅ No JavaScript errors detected")
            
            # Take a screenshot for debugging
            page.screenshot(path="debug_screenshot.png")
            print("📸 Screenshot saved as debug_screenshot.png")
            
            return len(js_errors) == 0
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    success = quick_js_check()
    exit(0 if success else 1)
