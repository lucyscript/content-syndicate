#!/usr/bin/env python3
"""
Detailed React Hydration Test Script
Tests Next.js React hydration and client-side functionality
"""

import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def test_hydration_detailed():
    print("🔍 Starting detailed React hydration test...")
    print("=" * 60)
    
    # Test 1: Basic HTML Response
    print("\n1. Testing basic HTML response...")
    try:
        response = requests.get("http://localhost:3000/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   Content-Length: {len(response.text)}")
        
        # Check for Next.js markers
        html = response.text
        has_next_script = '__NEXT_DATA__' in html
        has_next_div = 'id="__next"' in html
        has_react_scripts = '_next/static' in html
        
        print(f"   Contains __NEXT_DATA__: {has_next_script}")
        print(f"   Contains #__next div: {has_next_div}")
        print(f"   Contains React scripts: {has_react_scripts}")
        
        if not has_next_div:
            print("   ❌ ISSUE: Missing #__next container!")
            print("   This indicates the root layout is not rendering properly")
        
        if not has_next_script:
            print("   ❌ ISSUE: Missing __NEXT_DATA__ script!")
            print("   This indicates Next.js hydration data is missing")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: JavaScript Console Errors
    print("\n2. Testing JavaScript execution and console errors...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:3000/")
        
        # Wait for page load
        time.sleep(3)
        
        # Check for console errors
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        print(f"   JavaScript errors found: {len(js_errors)}")
        for error in js_errors[:5]:  # Show first 5 errors
            print(f"   - {error['message']}")
        
        # Test 3: Check for React root element
        print("\n3. Testing React root element...")
        try:
            next_div = driver.find_element(By.ID, "__next")
            print(f"   ✅ Found #__next element")
            print(f"   Inner HTML length: {len(next_div.get_attribute('innerHTML'))}")
            
            if len(next_div.get_attribute('innerHTML').strip()) == 0:
                print("   ❌ ISSUE: #__next element is empty!")
                print("   React components are not rendering")
            else:
                print("   ✅ #__next has content")
                
        except Exception as e:
            print(f"   ❌ Could not find #__next element: {e}")
        
        # Test 4: Check for specific React components
        print("\n4. Testing for React component rendering...")
        
        # Look for any elements that should be created by React
        react_elements = []
        try:
            # Check for provider elements or any data-react attributes
            elements_with_data = driver.find_elements(By.XPATH, "//*[starts-with(@data-, 'react') or starts-with(@data-, 'testid')]")
            react_elements.extend(elements_with_data)
            
            # Check for Radix UI elements (which we know the app uses)
            radix_elements = driver.find_elements(By.XPATH, "//*[starts-with(@data-, 'radix')]")
            react_elements.extend(radix_elements)
            
        except Exception as e:
            print(f"   Error checking for React elements: {e}")
        
        print(f"   React/Data elements found: {len(react_elements)}")
        
        # Test 5: Check for Hydration Warnings
        print("\n5. Checking for hydration warnings...")
        all_logs = driver.get_log('browser')
        hydration_warnings = [log for log in all_logs if 'hydrat' in log['message'].lower()]
        
        print(f"   Hydration-related logs: {len(hydration_warnings)}")
        for warning in hydration_warnings:
            print(f"   - {warning['level']}: {warning['message']}")
        
        # Test 6: Page Source Analysis
        print("\n6. Analyzing page source structure...")
        page_source = driver.page_source
        
        has_html_tag = '<html' in page_source
        has_body_tag = '<body' in page_source
        has_providers = 'AuthProvider' in page_source or 'QueryProvider' in page_source
        has_next_scripts = '_next/static' in page_source
        
        print(f"   Has HTML structure: {has_html_tag}")
        print(f"   Has BODY tag: {has_body_tag}")
        print(f"   Has Provider references: {has_providers}")
        print(f"   Has Next.js scripts: {has_next_scripts}")
        
        driver.quit()
        
    except Exception as e:
        print(f"   ❌ Browser test error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🏁 Hydration test completed!")
    return True

if __name__ == "__main__":
    test_hydration_detailed()
