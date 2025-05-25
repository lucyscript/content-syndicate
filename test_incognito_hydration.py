#!/usr/bin/env python3

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_incognito_hydration():
    print("=== Testing Hydration in Incognito Mode ===")
    
    chrome_options = Options()
    chrome_options.add_argument("--incognito")  # Run in incognito mode to disable extensions
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Remove --headless to see what's happening
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("1. Testing minimal page in incognito mode...")
        driver.get("http://localhost:3000/minimaltest")
        time.sleep(3)
        
        # Check hydration status
        hydration_status = driver.execute_script("""
            return {
                nextDiv: document.getElementById('__next') !== null,
                react: typeof window.React !== 'undefined',
                nextData: typeof window.__NEXT_DATA__ !== 'undefined',
                nextF: typeof window.__next_f !== 'undefined' && window.__next_f.length,
                bodyChildren: document.body.children.length,
                bodyInnerHTML: document.body.innerHTML.substring(0, 200)
            };
        """)
        
        print(f"   Hydration status: {hydration_status}")
        
        # Check for any console errors
        logs = driver.get_log('browser')
        if logs:
            print("   Console messages:")
            for log in logs:
                if log['level'] in ['SEVERE', 'WARNING']:
                    print(f"     {log['level']}: {log['message']}")
        else:
            print("   No console errors")
        
        # Wait a bit longer and check again
        print("2. Waiting 5 more seconds for hydration...")
        time.sleep(5)
        
        final_status = driver.execute_script("""
            return {
                nextDiv: document.getElementById('__next') !== null,
                react: typeof window.React !== 'undefined',
                nextData: typeof window.__NEXT_DATA__ !== 'undefined'
            };
        """)
        
        print(f"   Final status: {final_status}")
        
        if final_status['nextDiv']:
            print("   ✅ SUCCESS: Hydration completed in incognito mode!")
            return True
        else:
            print("   ❌ FAILED: Still no hydration in incognito mode")
            return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_incognito_hydration()
