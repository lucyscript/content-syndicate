#!/usr/bin/env py        driver.get("http://localhost:3000")hon3

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_fresh_nextjs_hydration():
    print("=== Testing Fresh Next.js App Hydration ===")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:        print("1. Navigating to fresh Next.js app...")
        driver.get("http://localhost:3000")
        
        # Wait for page load
        time.sleep(3)
        
        print("2. Checking page title...")
        title = driver.title
        print(f"   Page title: {title}")
        
        print("3. Checking for #__next div...")
        next_div = driver.execute_script("return document.getElementById('__next') !== null;")
        print(f"   #__next div found: {next_div}")
        
        print("4. Checking React/Next.js globals...")
        react_check = driver.execute_script("return typeof window.React !== 'undefined';")
        next_data_check = driver.execute_script("return typeof window.__NEXT_DATA__ !== 'undefined';")
        next_router_check = driver.execute_script("return typeof window.__NEXT_ROUTER_READY__ !== 'undefined';")
        
        print(f"   window.React found: {react_check}")
        print(f"   window.__NEXT_DATA__ found: {next_data_check}")
        print(f"   window.__NEXT_ROUTER_READY__ found: {next_router_check}")
        
        print("5. Checking page content...")
        try:
            h1_text = driver.find_element("tag name", "h1").text
            print(f"   H1 text: {h1_text}")
        except:
            print("   No H1 element found")
        
        print("6. Console logs...")
        logs = driver.get_log('browser')
        if logs:
            print("   Console messages:")
            for log in logs:
                print(f"     {log['level']}: {log['message']}")
        else:
            print("   No console messages")
        
        print("7. DOM structure...")
        body_children_count = driver.execute_script("return document.body.children.length;")
        print(f"   Body children count: {body_children_count}")
        
        # Check if we have the expected Next.js structure
        all_good = next_div and (react_check or next_data_check)
        
        print("\n=== Summary ===")
        print(f"Fresh Next.js app hydration: {'✅ Working' if all_good else '❌ Failed'}")
        
        return all_good
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_fresh_nextjs_hydration()
