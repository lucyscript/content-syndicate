#!/usr/bin/env python3
"""
Test Topic Inspiration feature after fixing authentication token persistence bug
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def test_topic_inspiration_fixed():
    """Test that Topic Inspiration now works with fixed authentication"""
    
    # Setup Chrome with options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    try:
        print("🚀 Testing Topic Inspiration with fixed authentication...")
        
        # Step 1: Navigate to login page
        driver.get("http://localhost:3000/auth/login")
        print("✓ Navigated to login page")
        
        # Step 2: Login
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        password_input = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In') or contains(text(), 'Login')]")
        
        email_input.send_keys("test@example.com")
        password_input.send_keys("testpassword123")
        login_button.click()
        print("✓ Submitted login form")
        
        # Step 3: Wait for redirect to dashboard
        wait.until(EC.url_contains("/dashboard"))
        print("✓ Successfully logged in and redirected to dashboard")
        
        # Step 4: Navigate to newsletter creation page
        driver.get("http://localhost:3000/dashboard/newsletters/new")
        wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Create New Newsletter')]")))
        print("✓ Navigated to newsletter creation page")
        
        # Step 5: Check localStorage token after fix
        auth_token = driver.execute_script("return localStorage.getItem('auth_token');")
        print(f"✓ Auth token in localStorage: {'Present' if auth_token else 'Missing'}")
        
        # Step 6: Find and click the Topic Inspiration button
        topic_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Show Suggestions') or contains(text(), 'Suggestions')]")))
        topic_button.click()
        print("✓ Clicked Topic Inspiration button")
        
        # Step 7: Wait for niche selector to appear (indicates panel opened)
        niche_selector = wait.until(EC.presence_of_element_located((By.XPATH, "//select")))
        print("✓ Topic suggestions panel opened")
        
        # Step 8: Wait for loading to complete and topics to appear
        time.sleep(3)  # Give time for API calls
        
        # Check for topic suggestions or loading state
        try:
            loading_indicator = driver.find_element(By.XPATH, "//*[contains(text(), 'Loading topic suggestions')]")
            print("⏳ Topics are loading...")
            
            # Wait for loading to complete
            wait.until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), 'Loading topic suggestions')]")))
            print("✓ Loading completed")
        except:
            print("⚠️ No loading indicator found (may have loaded instantly)")
        
        # Step 9: Check for topic suggestions
        try:
            topic_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'border') and contains(@class, 'rounded-lg') and .//h3]")
            if topic_cards:
                print(f"🎉 SUCCESS: Found {len(topic_cards)} topic suggestions!")
                
                # Display details of found topics
                for i, card in enumerate(topic_cards[:3]):  # Show first 3
                    try:
                        title = card.find_element(By.TAG_NAME, "h3").text
                        type_badge = card.find_element(By.XPATH, ".//span[contains(@class, 'bg-red-100') or contains(@class, 'bg-blue-100')]").text
                        print(f"  Topic {i+1}: {title} ({type_badge})")
                    except:
                        print(f"  Topic {i+1}: (Could not extract details)")
                
                # Step 10: Test clicking a topic suggestion
                if topic_cards:
                    print("\n🧪 Testing topic application...")
                    first_topic = topic_cards[0]
                    title_before = driver.find_element(By.NAME, "title").get_attribute("value")
                    
                    first_topic.click()
                    time.sleep(1)
                    
                    title_after = driver.find_element(By.NAME, "title").get_attribute("value")
                    
                    if title_after != title_before:
                        print(f"✅ SUCCESS: Topic applied to form! Title changed from '{title_before}' to '{title_after}'")
                    else:
                        print("⚠️ Topic clicked but title didn't change")
                
            else:
                # Check for error messages
                error_messages = driver.find_elements(By.XPATH, "//*[contains(text(), 'No topic suggestions') or contains(text(), 'Failed to load') or contains(text(), 'error')]")
                if error_messages:
                    print(f"❌ Error found: {error_messages[0].text}")
                else:
                    print("❌ No topic suggestions found and no error message")
                    
        except Exception as e:
            print(f"❌ Error checking for topics: {e}")
        
        # Step 11: Check browser console for any errors
        print("\n📋 Checking browser console for errors...")
        logs = driver.get_log('browser')
        error_logs = [log for log in logs if log['level'] == 'SEVERE']
        
        if error_logs:
            print(f"⚠️ Found {len(error_logs)} console errors:")
            for log in error_logs[-3:]:  # Show last 3 errors
                print(f"  - {log['message']}")
        else:
            print("✅ No severe console errors found")
        
        print("\n🎯 Topic Inspiration test completed!")
        
    except TimeoutException as e:
        print(f"⏰ Timeout error: {e}")
        print("❌ Test failed due to timeout")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_topic_inspiration_fixed()
