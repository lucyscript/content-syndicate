#!/usr/bin/env python3
"""
Debug React hydration and state issues
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def debug_react_state():
    """Debug React state and hydration issues"""
    
    # Enable browser logging
    dc = DesiredCapabilities.CHROME.copy()
    dc['goog:loggingPrefs'] = { 'browser':'ALL' }
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.set_capability('goog:loggingPrefs', { 'browser':'ALL' }) # Alternative way to set logging prefs

    # driver = webdriver.Chrome(options=chrome_options, desired_capabilities=dc) # desired_capabilities is deprecated
    # For Selenium 4, merge capabilities into options
    for key, value in dc.items():
        chrome_options.set_capability(key, value)
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        print("🔐 Logging in...")
        driver.get("http://localhost:3000/auth/login")
        time.sleep(3)
        
        # Login
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        password_input = driver.find_element(By.NAME, "password")
        
        email_input.clear()
        email_input.send_keys("test@example.com")
        password_input.clear()
        password_input.send_keys("testpassword123")
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Wait for redirect
        wait.until(EC.url_contains("/dashboard"))
        print(f"✅ Successfully logged in")
        
        # Navigate to new newsletter page
        print("📄 Navigating to new newsletter page...")
        driver.get("http://localhost:3000/dashboard/newsletters/new")
        
        # Wait longer for potential hydration and JS execution
        print("⏳ Waiting for page to load and hydrate (10s)...")
        time.sleep(10)
        
        print(f"📍 Current URL: {driver.current_url}")
        
        # Check browser console logs
        print("\\n🔍 Checking browser console logs...")
        try:
            browser_logs = driver.get_log('browser')
            if browser_logs:
                print(f"Found {len(browser_logs)} console messages:")
                for log_entry in browser_logs:
                    print(f"   [{log_entry['level']}] {log_entry['message']}")
            else:
                print("   No console logs found via driver.get_log('browser').")
        except Exception as e:
            print(f"   Error getting browser logs: {e}")

        # Get full HTML source
        print("\\n📄 Getting full page HTML source...")
        full_html = driver.execute_script("return document.documentElement.outerHTML;")
        print(f"HTML Source Length: {len(full_html)}")
        # print(full_html) # Potentially very long, print first/last few lines or save to file if needed
        if len(full_html) < 2000: # If short, print it
             print(full_html)
        else:
            print(f"HTML source (first 1000 chars):\\n{full_html[:1000]}")
            print(f"HTML source (last 1000 chars):\\n{full_html[-1000:]}")


        # Check for __next div
        print("\\n⚛️ Checking for #__next div...")
        next_div_info = driver.execute_script("""
            const nextDiv = document.getElementById('__next');
            if (nextDiv) {
                return {
                    found: true,
                    innerHTMLStart: nextDiv.innerHTML.substring(0, 500),
                    childElementCount: nextDiv.childElementCount
                };
            }
            return { found: false };
        """)
        print(f"   #__next div found: {next_div_info.get('found')}")
        if next_div_info.get('found'):
            print(f"   #__next.innerHTML (start): {next_div_info.get('innerHTMLStart')}")
            print(f"   #__next child elements: {next_div_info.get('childElementCount')}")

        # Re-check for React/Next.js specific globals
        print("\\n⚛️ Re-checking React/Next.js globals...")
        js_globals = driver.execute_script("""
            return {
                reactVersion: typeof React !== 'undefined' ? React.version : 'Not found',
                nextData: typeof __NEXT_DATA__ !== 'undefined' ? 'Present' : 'Not found',
                routerReady: typeof __NEXT_ROUTER_READY__ !== 'undefined' ? __NEXT_ROUTER_READY__ : 'Not found or false'
            };
        """)
        print(f"   window.React version: {js_globals.get('reactVersion')}")
        print(f"   window.__NEXT_DATA__: {js_globals.get('nextData')}")
        print(f"   window.__NEXT_ROUTER_READY__: {js_globals.get('routerReady')}")
        
        # Check if the main content area for the page is rendering anything
        # This selector is specific to the NewNewsletterPage's top-level div
        page_specific_content_check = driver.execute_script("""
            const pageWrapper = document.querySelector('div.max-w-4xl.mx-auto.p-6');
            if (pageWrapper) {
                return {
                    found: true,
                    innerHTMLStart: pageWrapper.innerHTML.substring(0, 1000)
                };
            }
            return { found: false };
        """)
        print("\\n📄 Checking page-specific content wrapper (div.max-w-4xl.mx-auto.p-6)...")
        print(f"   Page wrapper found: {page_specific_content_check.get('found')}")
        if page_specific_content_check.get('found'):
            print(f"   Page wrapper innerHTML (start): {page_specific_content_check.get('innerHTMLStart')}")


        # Save screenshot
        driver.save_screenshot("react_debug_final.png")
        print("\\n📸 Screenshot saved as 'react_debug_final.png'")
        
    except Exception as e:
        print(f"❌ Error in script: {e}")
        driver.save_screenshot("react_debug_script_error.png")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    debug_react_state()
