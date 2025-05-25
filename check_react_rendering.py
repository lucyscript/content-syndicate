#!/usr/bin/env python3
"""
Check for React rendering and hydration issues
"""

from playwright.sync_api import sync_playwright
import time

def check_react_rendering():
    print("🔍 CHECKING REACT RENDERING ISSUES")
    print("=" * 50)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Capture console messages
        console_messages = []
        def log_console(msg):
            console_messages.append(f"{msg.type}: {msg.text}")
            print(f"CONSOLE {msg.type.upper()}: {msg.text}")
        
        page.on("console", log_console)
        
        try:
            print("1️⃣ Loading login page...")
            page.goto("http://localhost:3000/auth/login")
            page.wait_for_load_state("networkidle")
            
            print("2️⃣ Logging in...")
            page.fill('input[type="email"]', "test@example.com")
            page.fill('input[type="password"]', "testpassword123")
            page.click('button[type="submit"]')
            page.wait_for_url("**/dashboard**", timeout=10000)
            
            print("3️⃣ Navigating to newsletter creation...")
            page.goto("http://localhost:3000/dashboard/newsletters/new")
            page.wait_for_load_state("networkidle")
            
            # Wait for React to fully hydrate
            time.sleep(5)
            
            print("4️⃣ Checking for React hydration...")
            
            # Check if React has mounted
            react_mounted = page.evaluate("""
                () => {
                    return window.React !== undefined || 
                           document.querySelector('[data-reactroot]') !== null ||
                           document.querySelector('#__next') !== null;
                }
            """)
            print(f"React mounted: {react_mounted}")
            
            # Check for hydration errors
            hydration_errors = [msg for msg in console_messages if 'hydrat' in msg.lower() or 'mismatch' in msg.lower()]
            if hydration_errors:
                print("🚨 Hydration errors found:")
                for error in hydration_errors:
                    print(f"  - {error}")
            else:
                print("✅ No hydration errors detected")
            
            # Check for any React errors
            react_errors = [msg for msg in console_messages if 'error' in msg.lower() and 'react' in msg.lower()]
            if react_errors:
                print("🚨 React errors found:")
                for error in react_errors:
                    print(f"  - {error}")
            
            print("5️⃣ Checking component structure...")
            
            # Check for any components that are actually rendered
            component_info = page.evaluate("""
                () => {
                    const components = [];
                    
                    // Check for common React component indicators
                    const reactElements = document.querySelectorAll('[data-testid], [class*="component"], [class*="Component"]');
                    components.push(`React-like elements: ${reactElements.length}`);
                    
                    // Check for newsletter-specific elements
                    const newsletterElements = document.querySelectorAll('[class*="newsletter"], [class*="Newsletter"]');
                    components.push(`Newsletter elements: ${newsletterElements.length}`);
                    
                    // Check for form elements
                    const formElements = document.querySelectorAll('form, input, textarea, button');
                    components.push(`Form elements: ${formElements.length}`);
                    
                    // Check for any h1, h2, h3 headers
                    const headers = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    const headerTexts = Array.from(headers).map(h => h.textContent.trim()).filter(t => t);
                    components.push(`Headers found: ${headerTexts.join(', ')}`);
                    
                    return components;
                }
            """)
            
            for info in component_info:
                print(f"  📋 {info}")
            
            print("6️⃣ Checking for loading states...")
            
            # Check if there are any loading indicators
            loading_indicators = page.evaluate("""
                () => {
                    const loadingElements = document.querySelectorAll('[class*="loading"], [class*="Loading"], [class*="spinner"], [class*="Spinner"]');
                    const loadingTexts = Array.from(document.querySelectorAll('*')).filter(el => 
                        el.textContent && (el.textContent.includes('Loading') || el.textContent.includes('loading'))
                    );
                    
                    return {
                        loadingElements: loadingElements.length,
                        loadingTexts: loadingTexts.map(el => el.textContent.trim())
                    };
                }
            """)
            
            print(f"  🔄 Loading elements: {loading_indicators['loadingElements']}")
            if loading_indicators['loadingTexts']:
                print(f"  🔄 Loading texts: {loading_indicators['loadingTexts']}")
            
            print("7️⃣ Checking page content...")
            
            # Get the full page text content
            page_text = page.evaluate("() => document.body.textContent")
            
            # Check for specific terms
            terms_to_check = [
                "Topic Inspiration", "Show Suggestions", "trending", "Generate", 
                "Newsletter", "Create", "Content", "AI"
            ]
            
            found_terms = []
            for term in terms_to_check:
                if term.lower() in page_text.lower():
                    found_terms.append(term)
            
            print(f"  📝 Found terms: {found_terms}")
            print(f"  📝 Page text length: {len(page_text)} characters")
            
            # Take a screenshot for manual inspection
            page.screenshot(path="react_rendering_debug.png", full_page=True)
            print("📷 Screenshot saved as react_rendering_debug.png")
            
            input("Press Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_react_rendering()