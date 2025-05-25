#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import time

async def debug_auth_provider():
    print("🔍 DEBUGGING AUTH PROVIDER INITIALIZATION")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Listen for console messages
        def handle_console(msg):
            print(f"[CONSOLE {msg.type}] {msg.text}")
        
        page.on("console", handle_console)
        
        try:
            print("📍 Navigating to login page...")
            await page.goto("http://localhost:3000/auth/login")
            
            print("📍 Waiting for 5 seconds to see initialization process...")
            await asyncio.sleep(5)
            
            print("📍 Checking current state...")
            
            # Execute JavaScript to check current state
            auth_state = await page.evaluate("""
                () => {
                    const button = document.querySelector('button[type="submit"]');
                    return {
                        buttonText: button ? button.textContent : 'not found',
                        buttonDisabled: button ? button.disabled : 'not found',
                        localStorage: {
                            authToken: localStorage.getItem('auth_token'),
                            user: localStorage.getItem('user')
                        }
                    };
                }
            """)
            
            print(f"📍 Current auth state: {auth_state}")
            
        except Exception as e:
            print(f"❌ Error during debug: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_auth_provider())
