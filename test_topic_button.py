#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import time

async def test_topic_inspiration_button():
    print("🔍 TESTING TOPIC INSPIRATION BUTTON FUNCTIONALITY")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Listen for console messages
        def handle_console(msg):
            print(f"[CONSOLE {msg.type}] {msg.text}")
        
        page.on("console", handle_console)
        
        # Listen for network requests
        def handle_request(request):
            if 'api' in request.url:
                print(f"🌐 REQUEST: {request.method} {request.url}")
        
        def handle_response(response):
            if 'api' in response.url:
                print(f"🌐 RESPONSE: {response.status} {response.url}")
        
        page.on("request", handle_request)
        page.on("response", handle_response)
        
        try:
            print("📍 1. Navigate to login and authenticate...")
            await page.goto("http://localhost:3000/auth/login")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[type="email"]', 'test@example.com')
            await page.fill('input[type="password"]', 'testpassword123')
            await page.click('button[type="submit"]')
            await page.wait_for_url("**/dashboard**", timeout=15000)
            
            print("📍 2. Navigate to new newsletter page...")
            await page.goto("http://localhost:3000/dashboard/newsletters/new")
            await page.wait_for_load_state("networkidle")
            
            print("📍 3. Look for Topic Inspiration elements...")
              # Check if "Show Suggestions" button exists - try multiple selectors
            show_suggestions_button_testid = page.locator("[data-testid='show-topic-suggestions-button']")
            show_suggestions_button_text = page.locator("text=/.*Show.*Suggestions.*/")
            
            button_exists_testid = await show_suggestions_button_testid.count() > 0
            button_exists_text = await show_suggestions_button_text.count() > 0
            
            print(f"   'Show Suggestions' button exists (by testid): {button_exists_testid}")
            print(f"   'Show Suggestions' button exists (by text): {button_exists_text}")
            
            if button_exists_testid:
                print("📍 4. Click 'Show Suggestions' button using testid...")
                await show_suggestions_button_testid.click()
            elif button_exists_text:
                print("📍 4. Click 'Show Suggestions' button using text...")
                await show_suggestions_button_text.click()
                
            else:
                print("   ❌ Show Suggestions button not found")
            
            if button_exists_testid or button_exists_text:
                await asyncio.sleep(5)
                
                # Check for loading indicators
                loading_indicator = page.locator("[data-testid='loading-topic-suggestions']")
                loading_visible = await loading_indicator.is_visible()
                print(f"   Loading indicator visible: {loading_visible}")
                
                # Check for topic suggestion cards
                suggestion_cards = page.locator("[data-testid^='topic-suggestion-card-']")
                card_count = await suggestion_cards.count()
                print(f"   Topic suggestion cards found: {card_count}")
                
                # Check for no suggestions message
                no_suggestions = page.locator("[data-testid='no-topic-suggestions']")
                no_suggestions_visible = await no_suggestions.is_visible()
                print(f"   'No suggestions' message visible: {no_suggestions_visible}")
                
            print("📍 6. Look for alternative buttons...")
            # Look for other relevant buttons
            generate_buttons = await page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    return buttons.map(btn => ({
                        text: btn.textContent?.trim(),
                        disabled: btn.disabled,
                        visible: btn.offsetParent !== null
                    })).filter(btn => 
                        btn.text && 
                        (btn.text.toLowerCase().includes('generate') || 
                         btn.text.toLowerCase().includes('suggest') ||
                         btn.text.toLowerCase().includes('topic') ||
                         btn.text.toLowerCase().includes('ai'))
                    );
                }
            """)
            
            print(f"   Found {len(generate_buttons)} relevant buttons:")
            for btn in generate_buttons:
                print(f"     - '{btn['text']}' (disabled: {btn['disabled']}, visible: {btn['visible']})")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
        finally:
            print("📍 Test completed. Keeping browser open for manual inspection...")
            await asyncio.sleep(10)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_topic_inspiration_button())
