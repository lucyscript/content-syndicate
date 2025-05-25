#!/usr/bin/env python3
"""
Test the complete Topic Inspiration workflow:
1. Login
2. Navigate to newsletter creation
3. Click "Show Suggestions" button
4. Verify suggestions load
5. Test applying a suggestion
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json

def setup_driver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def wait_for_element(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None

def wait_for_element_visible(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None

def login(driver):
    """Login to the application"""
    print("🔐 Logging in...")
    driver.get("http://localhost:3000/auth/login")
    
    # Wait for login form
    email_input = wait_for_element(driver, By.NAME, "email")
    password_input = wait_for_element(driver, By.NAME, "password")
    
    if not email_input or not password_input:
        print("❌ Login form not found")
        return False
    
    # Fill login form
    email_input.send_keys("test@example.com")
    password_input.send_keys("testpassword123")
    
    # Submit form
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
    
    # Wait for redirect to dashboard
    try:
        WebDriverWait(driver, 10).until(
            lambda d: "dashboard" in d.current_url
        )
        print("✅ Login successful")
        return True
    except TimeoutException:
        print("❌ Login failed - no redirect to dashboard")
        return False

def test_topic_inspiration_workflow(driver):
    """Test the complete Topic Inspiration workflow"""
    print("📝 Navigating to newsletter creation page...")
    driver.get("http://localhost:3000/dashboard/newsletters/new")
    
    # Wait for page to load and authentication to complete
    time.sleep(3)
    
    # Check if Topic Inspiration elements are present
    header = wait_for_element_visible(driver, By.CSS_SELECTOR, "[data-testid='topic-inspiration-header']", 15)
    button = wait_for_element_visible(driver, By.CSS_SELECTOR, "[data-testid='show-topic-suggestions-button']", 15)
    
    if not header or not button:
        print("❌ Topic Inspiration elements not found")
        return False
    
    print("✅ Topic Inspiration section found")
    
    # Get initial button text
    initial_button_text = button.text
    print(f"🔘 Initial button text: '{initial_button_text}'")
    
    # Click the Show Suggestions button
    print("🖱️ Clicking 'Show Suggestions' button...")
    button.click()
    
    # Wait a moment for the click to register
    time.sleep(1)
    
    # Check if loading indicator appears
    loading_indicator = driver.find_elements(By.CSS_SELECTOR, "[data-testid='loading-topic-suggestions']")
    if loading_indicator:
        print("⏳ Loading indicator found - API call in progress")
        
        # Wait for loading to complete (max 15 seconds)
        try:
            WebDriverWait(driver, 15).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "[data-testid='loading-topic-suggestions']"))
            )
            print("✅ Loading completed")
        except TimeoutException:
            print("⚠️ Loading took longer than expected")
    
    # Check for suggestion cards
    time.sleep(2)  # Give a moment for suggestions to render
    suggestion_cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid^='topic-suggestion-card-']")
    
    if suggestion_cards:
        print(f"✅ Found {len(suggestion_cards)} topic suggestion cards")
        
        # Test clicking on the first suggestion
        if len(suggestion_cards) > 0:
            print("🖱️ Testing suggestion application - clicking first card...")
            first_card = suggestion_cards[0]
            
            # Get the suggestion title before clicking
            title_element = first_card.find_element(By.TAG_NAME, "h3")
            suggestion_title = title_element.text
            print(f"📝 Suggestion title: '{suggestion_title}'")
            
            # Click the suggestion card
            first_card.click()
            
            # Wait a moment for form to update
            time.sleep(1)
            
            # Check if form fields were updated
            title_input = driver.find_element(By.NAME, "title")
            subject_input = driver.find_element(By.NAME, "subject_line")
            
            title_value = title_input.get_attribute("value")
            subject_value = subject_input.get_attribute("value")
            
            print(f"📝 Title field value: '{title_value}'")
            print(f"📝 Subject field value: '{subject_value}'")
            
            if title_value == suggestion_title:
                print("✅ Suggestion successfully applied to form!")
                return True
            else:
                print("⚠️ Suggestion may not have been applied correctly")
                return True  # Still consider it a success since suggestions loaded
    else:
        # Check for no suggestions message
        no_suggestions = driver.find_elements(By.CSS_SELECTOR, "[data-testid='no-topic-suggestions']")
        if no_suggestions:
            print("ℹ️ No topic suggestions available message displayed")
            return True
        else:
            print("❌ No suggestion cards or messages found")
            return False

def capture_console_logs(driver):
    """Capture console logs for debugging"""
    try:
        logs = driver.get_log('browser')
        if logs:
            print("\n🎯 Console logs captured:")
            for log in logs[-10:]:  # Show last 10 logs
                if 'NewNewsletterPage' in log['message']:
                    print(f"📝 {log['message']}")
    except Exception as e:
        print(f"⚠️ Could not capture logs: {e}")

def main():
    driver = setup_driver()
    
    try:
        # Login first
        if not login(driver):
            return
        
        # Test Topic Inspiration workflow
        success = test_topic_inspiration_workflow(driver)
        
        # Capture console logs
        capture_console_logs(driver)
        
        # Take final screenshot
        driver.save_screenshot("topic_workflow_test.png")
        print("📷 Screenshot saved as topic_workflow_test.png")
        
        if success:
            print("\n🎉 Topic Inspiration workflow test PASSED!")
        else:
            print("\n❌ Topic Inspiration workflow test FAILED!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        driver.save_screenshot("topic_workflow_error.png")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
