"""
Debug script to check what's actually on the newsletter creation page
"""
import os
import time
from playwright.sync_api import sync_playwright

# Login credentials
login_credentials = {
    "email": "test@example.com",
    "password": "testpassword123"
}

def debug_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print("🔍 DEBUGGING PAGE CONTENT")
            print("="*50)
            
            # Login
            print("1️⃣ Logging in...")
            page.goto("http://localhost:3000/auth/login")
            page.wait_for_load_state("networkidle")
            
            page.fill('input[type="email"]', login_credentials["email"])
            page.fill('input[type="password"]', login_credentials["password"])
            page.click('button[type="submit"]')
            
            # Wait for redirect
            page.wait_for_url("**/dashboard/**")
            print("✅ Login successful")
            
            # Navigate to newsletter creation
            print("2️⃣ Navigating to newsletter creation...")
            page.goto("http://localhost:3000/dashboard/newsletters/new")
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            print("3️⃣ Analyzing page content...")
            
            # Get all text content
            page_text = page.inner_text('body')
            print("\n📄 PAGE TEXT CONTENT:")
            print("-" * 30)
            print(page_text[:1000] + "..." if len(page_text) > 1000 else page_text)
            
            # Look for specific strings
            search_terms = ["Topic", "Inspiration", "Suggestion", "Trending", "Generate", "AI"]
            print(f"\n🔍 SEARCHING FOR KEYWORDS:")
            print("-" * 30)
            for term in search_terms:
                if term.lower() in page_text.lower():
                    print(f"✅ Found: '{term}'")
                else:
                    print(f"❌ Missing: '{term}'")
            
            # Check for common UI elements
            print(f"\n🎯 UI ELEMENTS CHECK:")
            print("-" * 30)
            
            ui_checks = [
                ("Buttons", 'button'),
                ("Headers (h1-h6)", 'h1, h2, h3, h4, h5, h6'),
                ("Select dropdowns", 'select'),
                ("Input fields", 'input'),
                ("Divs with text", 'div:has-text("Topic")'),
            ]
            
            for name, selector in ui_checks:
                count = page.locator(selector).count()
                print(f"{name}: {count} found")
                if count > 0 and "Topic" in name:
                    # Show the text content of topic-related divs
                    elements = page.locator(selector).all()
                    for i, element in enumerate(elements[:3]):  # Show first 3
                        try:
                            text = element.inner_text()
                            if text:
                                print(f"  #{i+1}: {text[:100]}...")
                        except:
                            pass
            
            # Check for buttons with specific text patterns
            print(f"\n🔘 BUTTON ANALYSIS:")
            print("-" * 30)
            buttons = page.locator('button').all()
            for i, button in enumerate(buttons):
                try:
                    text = button.inner_text()
                    if text and any(keyword in text.lower() for keyword in ['topic', 'suggest', 'inspiration', 'generate']):
                        print(f"  Button #{i+1}: '{text}'")
                except:
                    pass
            
            # Take screenshot
            page.screenshot(path="debug_page_content.png")
            print(f"\n📷 Screenshot saved as debug_page_content.png")
            
            input("\nPress Enter to close browser...")
            
        finally:
            browser.close()

if __name__ == "__main__":
    debug_page()
