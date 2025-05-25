#!/usr/bin/env python3

"""
Debug script to check console logs and component state during Topic Inspiration rendering
"""

import time
from playwright.sync_api import sync_playwright

def debug_topic_inspiration_console():
    print("🔍 DEBUGGING TOPIC INSPIRATION CONSOLE LOGS")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        # Collect console messages
        console_messages = []
        
        def handle_console(msg):
            message = f"[{msg.type}] {msg.text}"
            console_messages.append(message)
            print(message)
        
        def handle_page_error(error):
            print(f"❌ PAGE ERROR: {error}")
        
        page.on("console", handle_console)
        page.on("pageerror", handle_page_error)
        
        try:
            print("📍 1. Navigate to login...")
            page.goto("http://localhost:3000/auth/login")
            page.wait_for_load_state("networkidle")
            
            print("📍 2. Perform login...")
            page.fill('input[type="email"]', 'test@example.com')
            page.fill('input[type="password"]', 'testpassword123')
            page.click('button[type="submit"]')
            page.wait_for_url("**/dashboard**", timeout=15000)
            
            print("📍 3. Navigate to newsletter creation...")
            page.goto("http://localhost:3000/dashboard/newsletters/new")
            page.wait_for_load_state("networkidle")
            
            print("📍 4. Wait for component to stabilize...")
            time.sleep(3)
            
            print("📍 5. Check component state via JavaScript...")
            
            # Check React component state
            component_state = page.evaluate("""
                () => {
                    // Try to find React component instance
                    const topicHeader = document.querySelector('[data-testid="topic-inspiration-header"]');
                    const showButton = document.querySelector('[data-testid="show-topic-suggestions-button"]');
                    
                    return {
                        topicHeaderExists: !!topicHeader,
                        topicHeaderText: topicHeader ? topicHeader.textContent : null,
                        showButtonExists: !!showButton,
                        showButtonText: showButton ? showButton.textContent : null,
                        showButtonVisible: showButton ? showButton.offsetParent !== null : false,
                        pageTitle: document.title,
                        url: window.location.href,
                        authTokenExists: !!localStorage.getItem('auth_token'),
                        userExists: !!localStorage.getItem('user'),
                        totalElements: document.querySelectorAll('*').length,
                        bodyInnerHTML: document.body.innerHTML.substring(0, 500) + '...'
                    };
                }
            """)
            
            print("📍 6. Component State Analysis:")
            print(f"   Topic Header Exists: {component_state['topicHeaderExists']}")
            print(f"   Topic Header Text: {component_state['topicHeaderText']}")
            print(f"   Show Button Exists: {component_state['showButtonExists']}")
            print(f"   Show Button Text: {component_state['showButtonText']}")
            print(f"   Show Button Visible: {component_state['showButtonVisible']}")
            print(f"   Page Title: {component_state['pageTitle']}")
            print(f"   Current URL: {component_state['url']}")
            print(f"   Auth Token Exists: {component_state['authTokenExists']}")
            print(f"   User Exists: {component_state['userExists']}")
            print(f"   Total DOM Elements: {component_state['totalElements']}")
            
            print("📍 7. Take screenshot...")
            page.screenshot(path="debug_topic_console.png")
            
            print("📍 8. Check for React DevTools...")
            react_check = page.evaluate("""
                () => {
                    return {
                        reactDevTools: !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__,
                        react: !!window.React,
                        nextJs: !!window.__NEXT_DATA__
                    };
                }
            """)
            
            print(f"   React DevTools: {react_check['reactDevTools']}")
            print(f"   React Available: {react_check['react']}")
            print(f"   Next.js Available: {react_check['nextJs']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            print("📍 Console Messages Summary:")
            for msg in console_messages[-10:]:  # Last 10 messages
                print(f"   {msg}")
            
            print("Press Enter to close...")
            input()
            browser.close()

if __name__ == "__main__":
    debug_topic_inspiration_console()
