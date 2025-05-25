#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright

async def debug_newsletter_page():
    print("🔍 DEBUGGING NEWSLETTER PAGE RENDERING")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Listen for console messages
        def handle_console(msg):
            print(f"[CONSOLE {msg.type}] {msg.text}")
        
        page.on("console", handle_console)
        
        try:
            print("📍 1. Login...")
            await page.goto("http://localhost:3000/auth/login")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[type="email"]', 'test@example.com')
            await page.fill('input[type="password"]', 'testpassword123')
            await page.click('button[type="submit"]')
            await page.wait_for_url("**/dashboard**", timeout=15000)
            
            print("📍 2. Navigate to newsletter creation...")
            await page.goto("http://localhost:3000/dashboard/newsletters/new")
            await page.wait_for_load_state("networkidle")
            
            print("📍 3. Wait and check for Topic Inspiration elements...")
            await asyncio.sleep(3)
            
            # Check if the Topic Inspiration section is present
            topic_header = await page.locator('[data-testid="topic-inspiration-header"]').count()
            show_button = await page.locator('[data-testid="show-topic-suggestions-button"]').count()
            
            print(f"   Topic header count: {topic_header}")
            print(f"   Show suggestions button count: {show_button}")
            
            if topic_header > 0:
                header_text = await page.locator('[data-testid="topic-inspiration-header"]').text_content()
                print(f"   Header text: '{header_text}'")
            
            if show_button > 0:
                button_text = await page.locator('[data-testid="show-topic-suggestions-button"]').text_content()
                button_visible = await page.locator('[data-testid="show-topic-suggestions-button"]').is_visible()
                print(f"   Button text: '{button_text}'")
                print(f"   Button visible: {button_visible}")
            
            # Get page source to analyze
            page_content = await page.content()
            
            # Check for key strings in the HTML
            has_topic_inspiration = "Topic Inspiration" in page_content
            has_show_suggestions = "Show Suggestions" in page_content
            has_testid_header = 'data-testid="topic-inspiration-header"' in page_content
            has_testid_button = 'data-testid="show-topic-suggestions-button"' in page_content
            
            print(f"📍 4. HTML Content Analysis:")
            print(f"   'Topic Inspiration' in HTML: {has_topic_inspiration}")
            print(f"   'Show Suggestions' in HTML: {has_show_suggestions}")
            print(f"   Topic header testid in HTML: {has_testid_header}")
            print(f"   Show button testid in HTML: {has_testid_button}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            print("📍 Keeping browser open for inspection...")
            await asyncio.sleep(10)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_newsletter_page())
