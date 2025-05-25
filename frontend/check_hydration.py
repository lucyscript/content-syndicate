#!/usr/bin/env python3
"""
Check if Next.js hydration is working properly
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_hydration():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Testing hydration on minimal test page...")
        driver.get("http://localhost:3000/minimaltest")
        
        # Wait for page to load
        time.sleep(3)
        
        # Check if #__next exists
        next_div = driver.find_elements(By.ID, "__next")
        print(f"#__next div found: {len(next_div) > 0}")
        
        if next_div:
            print(f"#__next innerHTML: {next_div[0].get_attribute('innerHTML')[:200]}...")
        
        # Check for React globals
        react_exists = driver.execute_script("return typeof window.React !== 'undefined'")
        next_data_exists = driver.execute_script("return typeof window.__NEXT_DATA__ !== 'undefined'")
        
        print(f"window.React exists: {react_exists}")
        print(f"window.__NEXT_DATA__ exists: {next_data_exists}")
        
        # Check for any JavaScript errors
        logs = driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if errors:
            print("\nJavaScript errors found:")
            for error in errors:
                print(f"  - {error['message']}")
        else:
            print("No JavaScript errors found")
        
        # Check page source for hydration markers
        page_source = driver.page_source
        has_next_script = '<script src="/_next/' in page_source
        has_react_script = 'react' in page_source.lower()
        
        print(f"Next.js scripts found: {has_next_script}")
        print(f"React-related content found: {has_react_script}")
        
        return len(next_div) > 0 and next_data_exists
        
    except Exception as e:
        print(f"Error during hydration check: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    is_hydrated = check_hydration()
    print(f"\nHydration working: {is_hydrated}")
