#!/usr/bin/env python3
"""
Debug login flow step by step
"""

from playwright.sync_api import sync_playwright
import time

def debug_login():
    """Debug login flow step by step"""
    
    print("🔍 DEBUGGING LOGIN FLOW")
    print("=" * 30)
    
    # Test data
    login_credentials = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser
        page = browser.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.type}: {msg.text}"))
        page.on("request", lambda request: print(f"REQUEST: {request.method} {request.url}"))
        page.on("response", lambda response: print(f"RESPONSE: {response.status} {response.url}"))
        
        try:
            print("1️⃣ Navigating to login page...")
            page.goto("http://localhost:3000/auth/login")
            page.wait_for_load_state("networkidle")
            
            # Take screenshot
            page.screenshot(path="login_page.png")
            print("📷 Screenshot saved as login_page.png")
            
            print("2️⃣ Checking page elements...")
            # Check if elements exist
            email_input = page.locator('input[type="email"]')
            password_input = page.locator('input[type="password"]')
            submit_button = page.locator('button[type="submit"]')
            
            print(f"Email input found: {email_input.count() > 0}")
            print(f"Password input found: {password_input.count() > 0}")
            print(f"Submit button found: {submit_button.count() > 0}")
            
            if email_input.count() == 0:
                print("❌ Email input not found. Page content:")
                print(page.content()[:500] + "...")
                return
            
            print("3️⃣ Filling login form...")
            page.fill('input[type="email"]', login_credentials["email"])
            page.fill('input[type="password"]', login_credentials["password"])
            
            print("4️⃣ Submitting form...")
            # Click submit and wait
            page.click('button[type="submit"]')
            
            print("5️⃣ Waiting for response...")
            # Wait a bit to see what happens
            time.sleep(5)
            
            # Check current URL
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Check for error messages
            error_elements = page.locator('.text-red-600, .error, [class*="error"]')
            if error_elements.count() > 0:
                print("❌ Error messages found:")
                for i in range(error_elements.count()):
                    print(f"   - {error_elements.nth(i).text_content()}")
            
            # Check localStorage
            auth_token = page.evaluate("() => localStorage.getItem('auth_token')")
            print(f"Auth token in localStorage: {auth_token}")
            
            # Take final screenshot
            page.screenshot(path="after_login.png")
            print("📷 Screenshot saved as after_login.png")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="error_state.png")
            
        finally:
            input("Press Enter to close browser...")
            browser.close()

if __name__ == "__main__":
    debug_login()
