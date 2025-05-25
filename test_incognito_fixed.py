#!/usr/bin/env python3

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_incognito_hydration_fixed():
    print("=== Testing Hydration in Incognito Mode (Fixed Port) ===")
    
    chrome_options = Options()
    chrome_options.add_argument("--incognito")  # Run in incognito mode to disable extensions
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Remove --headless to see what's happening
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Test both root page and minimal test page
        for page_path in ["/", "/minimaltest"]:
            print(f"\n--- Testing {page_path} ---")
            driver.get(f"http://localhost:3001{page_path}")
            time.sleep(3)
            
            # Check hydration status
            hydration_status = driver.execute_script("""
                return {
                    nextDiv: document.getElementById('__next') !== null,
                    react: typeof window.React !== 'undefined',
                    nextData: typeof window.__NEXT_DATA__ !== 'undefined',
                    nextF: typeof window.__next_f !== 'undefined' && window.__next_f.length,
                    bodyChildren: document.body.children.length,
                    pageTitle: document.title,
                    h1Text: document.querySelector('h1') ? document.querySelector('h1').textContent : 'No H1 found'
                };
            """)
            
            print(f"   Hydration status: {hydration_status}")
            
            # Check for any console errors
            logs = driver.get_log('browser')
            severe_logs = [log for log in logs if log['level'] in ['SEVERE', 'WARNING']]
            if severe_logs:
                print("   Console messages:")
                for log in severe_logs:
                    print(f"     {log['level']}: {log['message']}")
            else:
                print("   No severe console errors")
            
            # Wait a bit longer and check again
            print("   Waiting 5 more seconds for hydration...")
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
                print(f"   ✅ SUCCESS: Hydration completed for {page_path}!")
                return True
            else:
                print(f"   ❌ FAILED: Still no hydration for {page_path}")
        
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_incognito_hydration_fixed()
