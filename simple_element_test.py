#!/usr/bin/env python3
"""
Simple test to find what elements are actually on the page
"""

from playwright.sync_api import sync_playwright
import time

def test_simple_elements():
    """Test what elements we can actually find"""
    
    print("🔍 SIMPLE ELEMENT DETECTION TEST")
    print("=" * 40)
    
    login_credentials = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print("1️⃣ Logging in...")
            page.goto("http://localhost:3000/auth/login")
            page.wait_for_load_state("networkidle")
            
            page.fill('input[type="email"]', login_credentials["email"])
            page.fill('input[type="password"]', login_credentials["password"])
            page.click('button[type="submit"]')
            page.wait_for_url("**/dashboard**", timeout=10000)
            print("✅ Login successful")
            
            print("2️⃣ Navigating to newsletter creation...")
            page.goto("http://localhost:3000/dashboard/newsletters/new")
            page.wait_for_load_state("networkidle")
            time.sleep(5)  # Wait longer
            
            print("3️⃣ Taking screenshot...")
            page.screenshot(path="current_page.png")
            print("📷 Screenshot saved as current_page.png")
            
            print("4️⃣ Checking for basic elements...")
            
            # Check for any h2 elements
            h2_elements = page.locator('h2').all()
            print(f"Found {len(h2_elements)} h2 elements:")
            for i, h2 in enumerate(h2_elements):
                try:
                    text = h2.text_content()
                    print(f"   h2[{i}]: '{text}'")
                except:
                    print(f"   h2[{i}]: <could not read text>")
            
            # Check for any buttons
            button_elements = page.locator('button').all()
            print(f"\nFound {len(button_elements)} button elements:")
            for i, btn in enumerate(button_elements):
                try:
                    text = btn.text_content()
                    if text and len(text.strip()) > 0:
                        print(f"   button[{i}]: '{text.strip()}'")
                except:
                    print(f"   button[{i}]: <could not read text>")
            
            # Check for select elements
            select_elements = page.locator('select').all()
            print(f"\nFound {len(select_elements)} select elements")
            
            # Check page source for "Topic Inspiration"
            page_content = page.content()
            if "Topic Inspiration" in page_content:
                print("✅ 'Topic Inspiration' text found in page source")
            else:
                print("❌ 'Topic Inspiration' text NOT found in page source")
            
            # Check for specific text
            text_checks = [
                "Topic Inspiration",
                "Show Suggestions", 
                "Hide Suggestions",
                "Create New Newsletter",
                "AI-powered topic suggestions"
            ]
            
            print("\n5️⃣ Checking for specific text...")
            for text in text_checks:
                if text in page_content:
                    print(f"   ✅ Found: '{text}'")
                else:
                    print(f"   ❌ Missing: '{text}'")
            
            print("\n6️⃣ Trying to find elements by class/id...")
            # Try to find elements with common patterns
            common_selectors = [
                '[class*="topic"]',
                '[class*="suggestion"]',
                '[class*="inspiration"]',
                '[id*="topic"]',
                'div:has-text("Topic")',
                'button:has-text("Suggestion")'
            ]
            
            for selector in common_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        print(f"   ✅ Found {count} elements with selector: {selector}")
                    else:
                        print(f"   ❌ No elements found with selector: {selector}")
                except Exception as e:
                    print(f"   ⚠️ Error with selector {selector}: {e}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="error_simple_test.png")
            
        finally:
            input("Press Enter to close browser...")
            browser.close()

if __name__ == "__main__":
    test_simple_elements()
