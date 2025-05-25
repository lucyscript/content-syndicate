#!/usr/bin/env python3
"""
Debug why Topic Inspiration is not showing up
"""

from playwright.sync_api import sync_playwright
import time

def debug_topic_inspiration():
    """Debug Topic Inspiration visibility"""
    
    print("🐛 DEBUGGING TOPIC INSPIRATION VISIBILITY")
    print("=" * 45)
    
    login_credentials = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Capture console logs and errors
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))
        
        try:
            print("1️⃣ Logging in...")
            page.goto("http://localhost:3000/auth/login")
            page.wait_for_load_state("networkidle")
            
            page.fill('input[type="email"]', login_credentials["email"])
            page.fill('input[type="password"]', login_credentials["password"])
            page.click('button[type="submit"]')
            page.wait_for_url("**/dashboard**", timeout=10000)
            print("✅ Login successful")
            
            print("2️⃣ Checking authentication state...")
            auth_check = page.evaluate("""
                () => {
                    const token = localStorage.getItem('auth_token');
                    const user = JSON.parse(localStorage.getItem('user') || 'null');
                    return {
                        hasToken: !!token,
                        tokenLength: token ? token.length : 0,
                        hasUser: !!user,
                        userEmail: user ? user.email : null
                    };
                }
            """)
            print(f"   Token present: {auth_check['hasToken']}")
            print(f"   Token length: {auth_check['tokenLength']}")
            print(f"   User present: {auth_check['hasUser']}")
            print(f"   User email: {auth_check['userEmail']}")
            
            print("3️⃣ Navigating to newsletter creation...")
            page.goto("http://localhost:3000/dashboard/newsletters/new")
            page.wait_for_load_state("networkidle")
            time.sleep(5)
            
            print("4️⃣ Checking page structure...")
            # Get the page title
            title = page.title()
            print(f"   Page title: {title}")
            
            # Check if we're on the right page
            url = page.url
            print(f"   Current URL: {url}")
            
            # Check for any React errors or loading states
            react_errors = page.evaluate("""
                () => {
                    const errors = [];
                    // Check for React error boundaries
                    const errorElements = document.querySelectorAll('[data-react-error], .error-boundary');
                    errorElements.forEach(el => errors.push(el.textContent));
                    
                    // Check for loading indicators
                    const loaders = document.querySelectorAll('.animate-spin, [class*="loading"], [class*="spinner"]');
                    
                    return {
                        errors: errors,
                        hasLoaders: loaders.length > 0,
                        loaderCount: loaders.length
                    };
                }
            """)
            
            if react_errors['errors']:
                print("   ❌ React errors found:")
                for error in react_errors['errors']:
                    print(f"      {error}")
            else:
                print("   ✅ No React errors detected")
                
            if react_errors['hasLoaders']:
                print(f"   🔄 {react_errors['loaderCount']} loading indicators present")
            else:
                print("   ✅ No loading indicators")
            
            print("5️⃣ Examining page content structure...")
            # Get the main content structure
            content_structure = page.evaluate("""
                () => {
                    const main = document.querySelector('main') || document.body;
                    const structure = [];
                    
                    function analyzeElement(el, depth = 0) {
                        if (depth > 3) return; // Limit depth
                        
                        const indent = '  '.repeat(depth);
                        const tag = el.tagName.toLowerCase();
                        const classes = el.className || '';
                        const text = el.textContent ? el.textContent.slice(0, 50) + '...' : '';
                        
                        structure.push(`${indent}${tag}${classes ? '.' + classes.split(' ').join('.') : ''}: ${text}`);
                        
                        Array.from(el.children).slice(0, 5).forEach(child => {
                            analyzeElement(child, depth + 1);
                        });
                    }
                    
                    analyzeElement(main);
                    return structure;
                }
            """)
            
            print("   Page structure:")
            for line in content_structure[:20]:  # Show first 20 lines
                print(f"   {line}")
            
            print("6️⃣ Console logs...")
            if console_logs:
                print("   Recent console logs:")
                for log in console_logs[-10:]:
                    print(f"   {log}")
            else:
                print("   No console logs captured")
            
            print("7️⃣ Checking if component is conditionally rendered...")
            # Check React component state
            component_state = page.evaluate("""
                () => {
                    // Look for any state-related attributes or data
                    const elements = document.querySelectorAll('[data-*], [aria-*]');
                    const states = {};
                    
                    elements.forEach(el => {
                        Array.from(el.attributes).forEach(attr => {
                            if (attr.name.startsWith('data-') || attr.name.startsWith('aria-')) {
                                states[attr.name] = attr.value;
                            }
                        });
                    });
                    
                    return states;
                }
            """)
            
            print("   Component states/attributes:")
            for key, value in list(component_state.items())[:10]:
                print(f"   {key}: {value}")
            
            # Take screenshot
            page.screenshot(path="debug_topic_page.png")
            print("📷 Screenshot saved as debug_topic_page.png")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="debug_error.png")
            
        finally:
            input("Press Enter to close browser...")
            browser.close()

if __name__ == "__main__":
    debug_topic_inspiration()
