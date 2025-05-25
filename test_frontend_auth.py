#!/usr/bin/env python3
"""
Test frontend authentication flow and Topic Inspiration UI
"""

import requests
import json
from playwright.sync_api import sync_playwright
import time

def test_frontend_authentication():
    """Test authentication flow through the frontend"""
    
    print("🔧 TESTING FRONTEND AUTHENTICATION")
    print("=" * 50)
    
    # Test data
    login_credentials = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to False to see the browser
        page = browser.new_page()
        
        try:
            print("1️⃣ Navigating to login page...")
            page.goto("http://localhost:3000/auth/login")
            page.wait_for_load_state("networkidle")
            
            print("2️⃣ Filling login form...")
            # Wait for email input and fill it
            page.wait_for_selector('input[type="email"]', timeout=10000)
            page.fill('input[type="email"]', login_credentials["email"])
            page.fill('input[type="password"]', login_credentials["password"])
            
            print("3️⃣ Submitting login form...")
            # Click login button
            page.click('button[type="submit"]')
            
            # Wait for navigation to dashboard
            page.wait_for_url("**/dashboard**", timeout=10000)
            print("✅ Login successful - redirected to dashboard")
            
            print("4️⃣ Navigating to newsletter creation page...")
            page.goto("http://localhost:3000/dashboard/newsletters/new")
            page.wait_for_load_state("networkidle")
            
            print("5️⃣ Checking for Topic Inspiration elements...")
            
            # Wait a bit for components to load
            time.sleep(2)
            
            # Check for Topic Inspiration related elements
            topic_elements = [
                "Topic Inspiration",
                "Generate Topics",
                "Trending Topics",
                "Random Topics",
                "topic-inspiration",
                "trending-topics",
                "generate-topics"
            ]
            
            found_elements = []
            for element_text in topic_elements:
                try:
                    # Try different selector strategies
                    selectors = [
                        f'text={element_text}',
                        f'[data-testid*="{element_text.lower().replace(" ", "-")}"]',
                        f'[class*="{element_text.lower().replace(" ", "-")}"]',
                        f'[id*="{element_text.lower().replace(" ", "-")}"]'
                    ]
                    
                    for selector in selectors:
                        if page.locator(selector).count() > 0:
                            found_elements.append(f"{element_text} (via {selector})")
                            break
                except:
                    continue
            
            if found_elements:
                print("✅ Topic Inspiration elements found:")
                for element in found_elements:
                    print(f"   - {element}")
            else:
                print("❌ No Topic Inspiration elements found")
            
            print("6️⃣ Checking browser console for errors...")
            # Get console logs
            logs = []
            page.on("console", lambda msg: logs.append(f"{msg.type}: {msg.text}"))
            
            # Reload page to capture console logs
            page.reload()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            if logs:
                print("Console logs:")
                for log in logs[-10:]:  # Show last 10 logs
                    print(f"   {log}")
            
            print("7️⃣ Checking network requests...")
            # Monitor network requests for API calls
            network_requests = []
            page.on("request", lambda request: network_requests.append(f"{request.method} {request.url}"))
            page.on("response", lambda response: print(f"Response: {response.status} {response.url}"))
            
            # Try to trigger API calls by interacting with the page
            page.reload()
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Check localStorage for auth token
            auth_token = page.evaluate("() => localStorage.getItem('auth_token')")
            if auth_token:
                print(f"✅ Auth token found in localStorage: {auth_token[:50]}...")
            else:
                print("❌ No auth token found in localStorage")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    try:
        test_frontend_authentication()
    except ImportError:
        print("❌ Playwright not installed. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "playwright"])
        subprocess.run(["playwright", "install", "chromium"])
        print("✅ Playwright installed. Please run the script again.")
