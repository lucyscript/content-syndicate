#!/usr/bin/env python3

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_minimal_page():
    print("=== Testing Minimal Page Rendering ===")
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        print("1. Navigating to minimal test page...")
        driver.get("http://localhost:3000/minimaltest")
        
        # Wait for page to load
        time.sleep(3)
        
        print("2. Checking page title...")
        title = driver.title
        print(f"   Page title: {title}")
        
        print("3. Checking if page content is visible...")
        try:
            h1_element = driver.find_element(By.TAG_NAME, "h1")
            print(f"   H1 text: {h1_element.text}")
            page_rendered = True
        except:
            print("   ❌ No H1 element found")
            page_rendered = False
        
        print("4. Checking for #__next div...")
        next_div_found = driver.execute_script("return document.getElementById('__next') !== null;")
        print(f"   #__next div found: {next_div_found}")
        
        print("5. Checking React/Next.js globals...")
        react_found = driver.execute_script("return typeof window.React !== 'undefined';")
        next_data_found = driver.execute_script("return typeof window.__NEXT_DATA__ !== 'undefined';")
        next_router_ready = driver.execute_script("return typeof window.__NEXT_ROUTER_READY__ !== 'undefined';")
        
        print(f"   window.React found: {react_found}")
        print(f"   window.__NEXT_DATA__ found: {next_data_found}")
        print(f"   window.__NEXT_ROUTER_READY__ found: {next_router_ready}")
        
        print("6. Checking DOM structure...")
        html_content = driver.execute_script("return document.documentElement.outerHTML;")
        
        # Check for key elements
        has_html_tag = "<html" in html_content
        has_body_tag = "<body" in html_content
        has_next_script = "_next" in html_content or "next" in html_content.lower()
        
        print(f"   HTML tag found: {has_html_tag}")
        print(f"   BODY tag found: {has_body_tag}")
        print(f"   Next.js scripts found: {has_next_script}")
        
        print("7. Console logs...")
        logs = driver.get_log('browser')
        if logs:
            print("   Console messages:")
            for log in logs[-10:]:  # Show last 10 logs
                print(f"     {log['level']}: {log['message']}")
        else:
            print("   No console messages")
        
        print("8. Page source (first 500 chars)...")
        print(f"   {html_content[:500]}...")
        
        print("\n=== Summary ===")
        print(f"Page rendered: {page_rendered}")
        print(f"#__next div: {next_div_found}")
        print(f"React globals: {react_found}")
        print(f"Next.js ready: {next_router_ready}")
        
        if page_rendered and next_div_found:
            print("✅ Minimal page is working correctly!")
            return True
        else:
            print("❌ Issues detected with minimal page")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_minimal_page()
