#!/usr/bin/env python3

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_hydration_detailed():
    print("=== Detailed Hydration Test ===")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("1. Navigating to minimal test page...")
        driver.get("http://localhost:3000/minimaltest")
        
        # Wait for initial page load
        time.sleep(2)
        
        print("2. Checking initial state...")
        initial_html = driver.page_source[:1000]
        print(f"   Initial HTML (first 1000 chars): {initial_html}")
        
        print("3. Waiting for potential hydration...")
        # Wait up to 10 seconds for hydration
        for i in range(10):
            time.sleep(1)
            
            # Check for #__next div
            next_div = driver.execute_script("return document.getElementById('__next') !== null;")
            react_found = driver.execute_script("return typeof window.React !== 'undefined';")
            next_data = driver.execute_script("return typeof window.__NEXT_DATA__ !== 'undefined';")
            
            if next_div or react_found or next_data:
                print(f"   Hydration detected at {i+1} seconds!")
                break
            else:
                print(f"   Waiting... ({i+1}/10 seconds)")
        
        print("4. Final state check...")
        final_checks = {
            "#__next div": driver.execute_script("return document.getElementById('__next') !== null;"),
            "window.React": driver.execute_script("return typeof window.React !== 'undefined';"),
            "window.__NEXT_DATA__": driver.execute_script("return typeof window.__NEXT_DATA__ !== 'undefined';"),
            "window.__NEXT_ROUTER_READY__": driver.execute_script("return typeof window.__NEXT_ROUTER_READY__ !== 'undefined';"),
        }
        
        for check, result in final_checks.items():
            print(f"   {check}: {result}")
        
        print("5. Checking for JavaScript errors...")
        logs = driver.get_log('browser')
        if logs:
            print("   Console messages:")
            for log in logs:
                print(f"     {log['level']}: {log['message']}")
        else:
            print("   No console messages")
        
        print("6. Checking script loading...")
        scripts = driver.find_elements(By.TAG_NAME, "script")
        print(f"   Total scripts found: {len(scripts)}")
        
        next_scripts = [s for s in scripts if s.get_attribute("src") and "_next" in s.get_attribute("src")]
        print(f"   Next.js scripts found: {len(next_scripts)}")
        
        for script in next_scripts[:5]:  # Show first 5
            src = script.get_attribute("src")
            print(f"     {src}")
        
        print("7. Checking DOM structure...")
        body_children = driver.execute_script("""
            const body = document.body;
            const children = Array.from(body.children);
            return children.map(child => ({
                tagName: child.tagName,
                id: child.id,
                className: child.className,
                innerHTML: child.innerHTML.substring(0, 100)
            }));
        """)
        
        print("   Body children:")
        for child in body_children:
            print(f"     <{child['tagName']} id='{child['id']}' class='{child['className']}'>{child['innerHTML'][:50]}...")
        
        print("8. Network requests check...")
        performance_entries = driver.execute_script("""
            return performance.getEntriesByType('navigation').concat(
                performance.getEntriesByType('resource')
            ).filter(entry => entry.name.includes('_next')).slice(0, 10);
        """)
        
        print(f"   Next.js network requests: {len(performance_entries)}")
        for entry in performance_entries:
            print(f"     {entry['name']} - Status: {entry.get('responseStatus', 'N/A')}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_hydration_detailed()
