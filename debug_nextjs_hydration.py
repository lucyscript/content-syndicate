#!/usr/bin/env python3
"""
Debug Next.js hydration by examining page source and console
"""

from playwright.sync_api import sync_playwright
import time

def debug_nextjs_hydration():
    print("🔍 DEBUGGING NEXT.JS HYDRATION")
    print("=" * 40)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Capture all console messages
        console_messages = []
        
        def log_console(msg):
            console_messages.append(f"[{msg.type}] {msg.text}")
            print(f"[{msg.type}] {msg.text}")
        
        def log_page_error(error):
            console_messages.append(f"[PAGE ERROR] {error}")
            print(f"🚨 [PAGE ERROR] {error}")
        
        page.on("console", log_console)
        page.on("pageerror", log_page_error)
        
        try:
            print("1️⃣ Loading newsletter creation page directly...")
            page.goto("http://localhost:3000/dashboard/newsletters/new")
            page.wait_for_load_state("networkidle")
            time.sleep(5)
            
            print("2️⃣ Checking page HTML structure...")
            
            # Get the HTML structure
            html_structure = page.evaluate("""
                () => {
                    const body = document.body;
                    const nextApp = document.querySelector('#__next');
                    const scripts = Array.from(document.querySelectorAll('script'));
                    const links = Array.from(document.querySelectorAll('link'));
                    
                    return {
                        hasBody: !!body,
                        hasNextApp: !!nextApp,
                        nextAppContent: nextApp ? nextApp.innerHTML.substring(0, 500) : 'Not found',
                        scriptCount: scripts.length,
                        nextScripts: scripts.filter(s => s.src && s.src.includes('_next')).length,
                        stylesheetCount: links.filter(l => l.rel === 'stylesheet').length,
                        bodyClasses: body.className,
                        hasReactRoot: !!document.querySelector('[data-reactroot]') || !!document.querySelector('[data-react-root]'),
                        windowKeys: Object.keys(window).filter(k => k.includes('React') || k.includes('next') || k.includes('__NEXT')),
                    };
                }
            """)
            
            print("📊 HTML Structure Analysis:")
            for key, value in html_structure.items():
                print(f"  {key}: {value}")
            
            print("3️⃣ Checking script loading status...")
            
            # Check if scripts loaded successfully
            script_status = page.evaluate("""
                () => {
                    const scripts = Array.from(document.querySelectorAll('script[src]'));
                    return scripts.map(script => ({
                        src: script.src,
                        loaded: script.readyState === 'complete' || !script.readyState,
                        hasError: !!script.onerror
                    }));
                }
            """)
            
            print(f"📦 Script loading status ({len(script_status)} scripts):")
            failed_scripts = []
            for script in script_status:
                if '_next' in script['src']:
                    status = "✅" if script['loaded'] and not script['hasError'] else "❌"
                    print(f"  {status} {script['src']}")
                    if not script['loaded'] or script['hasError']:
                        failed_scripts.append(script['src'])
            
            if failed_scripts:
                print(f"🚨 Failed scripts: {len(failed_scripts)}")
            
            print("4️⃣ Attempting manual React initialization...")
            
            # Try to manually check React initialization
            react_check = page.evaluate("""
                () => {
                    try {
                        // Check if React is available
                        if (typeof window.React !== 'undefined') {
                            return { react: 'available', version: window.React.version || 'unknown' };
                        }
                        
                        // Check if Next.js is trying to initialize
                        if (typeof window.__NEXT_DATA__ !== 'undefined') {
                            return { nextData: 'available', props: Object.keys(window.__NEXT_DATA__) };
                        }
                        
                        // Check for hydration markers
                        const hydrationMarkers = Array.from(document.querySelectorAll('[data-reactroot], [data-react-root]'));
                        if (hydrationMarkers.length > 0) {
                            return { hydrationMarkers: hydrationMarkers.length };
                        }
                        
                        return { status: 'no react detected' };
                    } catch (error) {
                        return { error: error.toString() };
                    }
                }
            """)
            
            print(f"⚛️ React initialization check: {react_check}")
            
            print("5️⃣ Console messages summary:")
            if console_messages:
                print(f"📝 Captured {len(console_messages)} console messages:")
                for msg in console_messages[-10:]:  # Show last 10 messages
                    print(f"  {msg}")
            else:
                print("📝 No console messages captured")
                
            return len(failed_scripts) == 0 and 'error' not in react_check
            
        except Exception as e:
            print(f"❌ Error during debugging: {e}")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    success = debug_nextjs_hydration()
    exit(0 if success else 1)
