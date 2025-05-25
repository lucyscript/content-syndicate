#!/usr/bin/env python3
"""
Check for JavaScript errors preventing React hydration
"""

from playwright.sync_api import sync_playwright
import time

def check_js_errors():
    print("🔍 CHECKING JAVASCRIPT ERRORS")
    print("=" * 40)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Capture all console messages and errors
        console_messages = []
        js_errors = []
        
        def log_console(msg):
            console_messages.append(f"{msg.type}: {msg.text}")
            if msg.type in ['error', 'warning']:
                js_errors.append(f"{msg.type.upper()}: {msg.text}")
                print(f"🚨 {msg.type.upper()}: {msg.text}")
            else:
                print(f"📝 {msg.type}: {msg.text}")
        
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
                        nextScripts: Array.from(document.querySelectorAll('script[src*="_next"]')).length
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
            
            print("6️⃣ Checking script loading...")
            
            # Check if scripts are loading properly
            script_info = page.evaluate("""
                () => {
                    const scripts = Array.from(document.querySelectorAll('script'));
                    return scripts.map(script => ({
                        src: script.src || 'inline',
                        loaded: !script.src || script.readyState === 'complete' || script.readyState === 'loaded',
                        hasError: script.onerror !== null
                    }));
                }
            """)
            
            print(f"📦 Found {len(script_info)} scripts:")
            failed_scripts = [s for s in script_info if s['src'] != 'inline' and not s['loaded']]
            if failed_scripts:
                print("🚨 Failed to load scripts:")
                for script in failed_scripts:
                    print(f"  - {script['src']}")
            else:
                print("✅ All scripts loaded successfully")
            
            input("Press Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_js_errors()