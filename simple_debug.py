#!/usr/bin/env python3
"""
Simple debug script to check Topic Inspiration visibility
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def debug_simple():
    """Simple debug to check page elements"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
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
        print(f"✅ Successfully logged in, redirected to: {driver.current_url}")
        
        # Navigate to new newsletter page
        print("📄 Navigating to new newsletter page...")
        driver.get("http://localhost:3000/dashboard/newsletters/new")
        time.sleep(5)  # Give extra time for page to load
        
        print(f"📍 Current URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")
        
        # Check if page has loaded
        try:
            main_title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            print(f"✅ Main title found: {main_title.text}")
        except:
            print("❌ Main title not found")
        
        # Check for loading indicators
        loading_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'Loading')]")
        if loading_elements:
            print(f"⏳ Found {len(loading_elements)} loading indicators, waiting...")
            time.sleep(10)
        
        # Print all h2 elements to see what's available
        h2_elements = driver.find_elements(By.TAG_NAME, "h2")
        print(f"📝 Found {len(h2_elements)} h2 elements:")
        for i, h2 in enumerate(h2_elements):
            try:
                print(f"  {i+1}. '{h2.text}' (visible: {h2.is_displayed()})")
            except:
                print(f"  {i+1}. [Error reading text]")
        
        # Check for Topic Inspiration specifically
        print("\n🎯 Looking for Topic Inspiration section...")
        
        # Try different selectors
        selectors = [
            ("[data-testid='topic-inspiration-header']", "data-testid selector"),
            ("//h2[contains(text(), 'Topic Inspiration')]", "XPath text search"),
            ("//h2[text()='Topic Inspiration']", "XPath exact text"),
            (".text-lg.font-semibold", "CSS class selector")
        ]
        
        found_element = None
        for selector, description in selectors:
            try:
                if selector.startswith("//"):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                if elements:
                    print(f"✅ Found Topic Inspiration using {description}: {len(elements)} elements")
                    for el in elements:
                        print(f"   - Text: '{el.text}' (visible: {el.is_displayed()})")
                    found_element = elements[0]
                    break
                else:
                    print(f"❌ Not found using {description}")
            except Exception as e:
                print(f"❌ Error with {description}: {e}")
        
        # Check the page source for 'Topic Inspiration'
        page_source = driver.page_source
        if "Topic Inspiration" in page_source:
            print("✅ 'Topic Inspiration' text found in page source")
        else:
            print("❌ 'Topic Inspiration' text NOT found in page source")
            
        # Check for data-testid attributes
        testid_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid]")
        print(f"\n📊 Found {len(testid_elements)} elements with data-testid:")
        for el in testid_elements[:10]:  # Show first 10
            try:
                testid = el.get_attribute("data-testid")
                tag = el.tag_name
                text = el.text[:50] if el.text else "[no text]"
                print(f"   - {tag}[data-testid='{testid}']: {text}")
            except:
                print(f"   - [Error reading element]")
        
        # Check if the issue is authentication-related
        print("\n🔐 Checking authentication status...")
        auth_token = driver.execute_script("return localStorage.getItem('auth_token');")
        user_data = driver.execute_script("return localStorage.getItem('user');")
        print(f"Auth token: {'Present' if auth_token else 'Missing'}")
        print(f"User data: {'Present' if user_data else 'Missing'}")
        
        # Test if the Topic Inspiration section appears after authentication state change
        if found_element:
            print("\n🖱️ Testing interaction with found element...")
            try:
                button = driver.find_element(By.CSS_SELECTOR, "[data-testid='show-topic-suggestions-button']")
                print("✅ Topic suggestions button found!")
                driver.execute_script("arguments[0].click();", button)
                time.sleep(3)
                print("✅ Button clicked successfully")
            except Exception as e:
                print(f"❌ Error clicking button: {e}")
        
        # Save a screenshot for analysis
        driver.save_screenshot("simple_debug.png")
        print("📸 Screenshot saved as 'simple_debug.png'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        driver.save_screenshot("simple_debug_error.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_simple()
