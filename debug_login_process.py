#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import time

async def debug_login_process():
    print("🔍 DEBUGGING LOGIN PROCESS")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Listen for console messages
        def handle_console(msg):
            print(f"[CONSOLE {msg.type}] {msg.text}")
        
        page.on("console", handle_console)
        
        # Listen for network failures
        def handle_request_failed(request):
            print(f"[NETWORK FAILED] {request.url} - {request.failure}")
        
        page.on("requestfailed", handle_request_failed)
        
        try:
            print("📍 Navigating to login page...")
            await page.goto("http://localhost:3000/auth/login")
            await page.wait_for_load_state("networkidle")
            
            print("📍 Filling in login form...")
            await page.fill('input[type="email"]', 'test@example.com')
            await page.fill('input[type="password"]', 'testpassword')
            
            print("📍 Current button state:")
            button = page.locator('button[type="submit"]')
            button_text = await button.text_content()
            is_disabled = await button.is_disabled()
            print(f"   Button text: '{button_text}'")
            print(f"   Button disabled: {is_disabled}")
            
            print("📍 Clicking login button...")
            await button.click()
            
            print("📍 Waiting for 10 seconds to observe what happens...")
            await asyncio.sleep(10)
            
            print("📍 Final button state:")
            button_text = await button.text_content()
            is_disabled = await button.is_disabled()
            print(f"   Button text: '{button_text}'")
            print(f"   Button disabled: {is_disabled}")
            
            # Check current URL
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
        except Exception as e:
            print(f"❌ Error during debug: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_login_process())
