#!/usr/bin/env python3
"""
Test script for Topic Inspiration functionality on the newsletter creation page.
This script logs into the application and checks the authentication states and UI elements.
"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to login and login
            print("🔐 Logging into the application...")
            page.goto('http://localhost:3000/auth/login')
            page.fill('input[name="email"]', 'test@example.com')
            page.fill('input[name="password"]', 'testpassword123')
            page.click('button[type="submit"]')
            
            # Wait for redirect
            page.wait_for_url('**/dashboard**', timeout=5000)
            print("✅ Successfully logged in and redirected to dashboard")
            
            # Go to new newsletter page
            print("📝 Navigating to new newsletter page...")
            page.goto('http://localhost:3000/dashboard/newsletters/new')
            
            # Add console logging
            page.add_init_script('''
                const originalLog = console.log;
                window.authLogs = [];
                console.log = function(...args) {
                    if (args.some(arg => typeof arg === 'string' && (arg.includes('NewNewsletterPage') || arg.includes('isInitialized') || arg.includes('authLoading') || arg.includes('isAuthenticated')))) {
                        window.authLogs.push(args.join(' '));
                    }
                    originalLog.apply(console, args);
                };
            ''')
            
            time.sleep(2)
            
            # Check auth states from console
            auth_logs = page.evaluate('window.authLogs || []')
            print('\n🔍 Auth State Logs:')
            for log in auth_logs:
                print(f'   {log}')
            
            # Check current DOM state
            print(f'\n📋 Page URL: {page.url}')
            print(f'📋 Page title: {page.title()}')
            
            # Check if loading spinner is showing
            loading_spinner = page.locator('.animate-spin').first
            is_loading = loading_spinner.is_visible()
            print(f'📋 Loading spinner visible: {is_loading}')
            
            # Check for authentication states directly from page
            auth_states = page.evaluate('''
                () => {
                    // Look for auth provider context
                    const authDiv = document.querySelector('[data-auth-state]');
                    if (authDiv) {
                        return authDiv.dataset.authState;
                    }
                    
                    // Check if main content is visible
                    const mainContent = document.querySelector('h1');
                    const loadingDiv = document.querySelector('.animate-spin');
                    
                    return {
                        hasMainContent: !!mainContent,
                        hasLoadingSpinner: !!loadingDiv,
                        mainContentText: mainContent ? mainContent.textContent : null
                    };
                }
            ''')
            
            print(f'📋 Auth evaluation: {auth_states}')
            
            # Check for Topic Inspiration elements specifically
            topic_header = page.locator('[data-testid="topic-inspiration-header"]')
            topic_button = page.locator('[data-testid="show-topic-suggestions-button"]')
            
            print(f'\n🎯 Topic Inspiration Elements:')
            print(f'   Header exists: {topic_header.count() > 0}')
            print(f'   Button exists: {topic_button.count() > 0}')
            
            if topic_header.count() > 0:
                print(f'   Header visible: {topic_header.is_visible()}')
            if topic_button.count() > 0:
                print(f'   Button visible: {topic_button.is_visible()}')
            
            print("\n✅ Test completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
