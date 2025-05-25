#!/usr/bin/env python3

"""
Test script to check Topic Inspiration section rendering on newsletter creation page.
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """Setup Chrome driver with options"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def login_user(driver):
    """Login with test user credentials"""
    try:
        print("🔑 Logging in...")
        driver.get("http://localhost:3000/auth/login")
        
        # Wait for login form
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email']"))
        )
        
        # Find password field
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
          # Enter credentials
        email_field.clear()
        email_field.send_keys("test@example.com")
        password_field.clear()
        password_field.send_keys("testpassword123")
        
        # Find and click login button
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Wait for redirect to dashboard
        WebDriverWait(driver, 15).until(
            lambda d: "dashboard" in d.current_url or "login" not in d.current_url
        )
        
        current_url = driver.current_url
        if "dashboard" in current_url:
            print(f"✅ Login successful! Redirected to: {current_url}")
            return True
        else:
            print(f"❌ Login may have failed. Current URL: {current_url}")
            return False
            
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return False

def test_topic_inspiration_section(driver):
    """Test the Topic Inspiration section rendering and functionality"""
    try:
        print("\n🧪 Testing Topic Inspiration Section...")
        
        # Navigate to newsletter creation page
        driver.get("http://localhost:3000/dashboard/newsletters/new")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print(f"📍 Current URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")
        
        # Check if Topic Inspiration header exists
        try:
            topic_header = driver.find_element(By.CSS_SELECTOR, "[data-testid='topic-inspiration-header']")
            print(f"✅ Topic Inspiration header found: '{topic_header.text}'")
        except:
            print("❌ Topic Inspiration header NOT found")
            # Try alternative selectors
            try:
                topic_header_alt = driver.find_element(By.XPATH, "//h2[contains(text(), 'Topic Inspiration')]")
                print(f"✅ Topic Inspiration header found (alternative): '{topic_header_alt.text}'")
            except:
                print("❌ Topic Inspiration header NOT found (alternative selector)")
        
        # Check if Show Suggestions button exists
        try:
            show_suggestions_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='show-topic-suggestions-button']")
            print(f"✅ Show Suggestions button found: '{show_suggestions_btn.text}'")
            print(f"   Button is displayed: {show_suggestions_btn.is_displayed()}")
            print(f"   Button is enabled: {show_suggestions_btn.is_enabled()}")
        except:
            print("❌ Show Suggestions button NOT found")
            # Try alternative selectors
            try:
                show_suggestions_alt = driver.find_element(By.XPATH, "//button[contains(text(), 'Show') and contains(text(), 'Suggestions')]")
                print(f"✅ Show Suggestions button found (alternative): '{show_suggestions_alt.text}'")
            except:
                print("❌ Show Suggestions button NOT found (alternative selector)")
        
        # Check for Topic Inspiration container/section
        try:
            topic_section = driver.find_element(By.XPATH, "//div[contains(@class, 'mb-6') and contains(@class, 'border-b')]")
            print(f"✅ Topic section container found")
            print(f"   Section text content: {topic_section.text[:200]}...")
        except:
            print("❌ Topic section container NOT found")
        
        # Get all text content on page to analyze
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Check for key phrases
        key_phrases = ["Topic Inspiration", "Show Suggestions", "Hide Suggestions", "AI-powered topic", "kickstart your newsletter"]
        found_phrases = []
        missing_phrases = []
        
        for phrase in key_phrases:
            if phrase in page_text:
                found_phrases.append(phrase)
            else:
                missing_phrases.append(phrase)
        
        print(f"\n📝 Key phrase analysis:")
        print(f"   ✅ Found phrases: {found_phrases}")
        print(f"   ❌ Missing phrases: {missing_phrases}")
        
        # Check if there are any buttons with "Suggestion" in text
        suggestion_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Suggestion') or contains(text(), 'suggestion')]")
        print(f"\n🔘 Buttons with 'Suggestion' text: {len(suggestion_buttons)}")
        for i, btn in enumerate(suggestion_buttons):
            print(f"   {i+1}. '{btn.text}' - Displayed: {btn.is_displayed()}")
        
        # Check if there are any elements with "Topic" text
        topic_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Topic') or contains(text(), 'topic')]")
        print(f"\n📚 Elements with 'Topic' text: {len(topic_elements)}")
        for i, elem in enumerate(topic_elements[:5]):  # Show first 5
            print(f"   {i+1}. {elem.tag_name}: '{elem.text[:50]}...'")
        
        # Test clicking the Show Suggestions button if found
        try:
            show_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='show-topic-suggestions-button']")
            print(f"\n🖱️ Attempting to click Show Suggestions button...")
            
            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView(true);", show_btn)
            time.sleep(1)
            
            # Click button
            show_btn.click()
            print("✅ Show Suggestions button clicked")
            
            # Wait a moment for any content to load
            time.sleep(3)
            
            # Check for loading indicator
            try:
                loading_indicator = driver.find_element(By.CSS_SELECTOR, "[data-testid='loading-topic-suggestions']")
                print("✅ Loading indicator found")
            except:
                print("ℹ️ No loading indicator found")
            
            # Check for topic suggestion cards
            topic_cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid^='topic-suggestion-card-']")
            print(f"📋 Topic suggestion cards found: {len(topic_cards)}")
            
            # Check for "no suggestions" message
            try:
                no_suggestions = driver.find_element(By.CSS_SELECTOR, "[data-testid='no-topic-suggestions']")
                print(f"ℹ️ No suggestions message: '{no_suggestions.text}'")
            except:
                print("ℹ️ No 'no suggestions' message found")
            
        except Exception as e:
            print(f"❌ Failed to test Show Suggestions button: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Topic Inspiration section: {str(e)}")
        return False

def main():
    """Main test function"""
    driver = None
    try:
        print("🚀 Starting Topic Inspiration Rendering Test...")
        
        driver = setup_driver()
        
        # Login first
        if not login_user(driver):
            print("❌ Cannot proceed without successful login")
            return
        
        # Test Topic Inspiration section
        test_topic_inspiration_section(driver)
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    finally:
        if driver:
            input("\nPress Enter to close browser...")
            driver.quit()

if __name__ == "__main__":
    main()
