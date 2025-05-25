#!/usr/bin/env python3

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_react_hydration_diagnosis():
    print("=== React Hydration Diagnosis ===")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("1. Testing minimal page...")
        driver.get("http://localhost:3000/minimaltest")
        time.sleep(3)
        
        # Check what Next.js is doing
        next_status = driver.execute_script("""
            return {
                nextData: typeof window.__NEXT_DATA__,
                nextF: typeof window.__next_f,
                react: typeof window.React,
                reactDom: typeof window.ReactDOM,
                scripts: Array.from(document.scripts).map(s => ({
                    src: s.src,
                    loaded: s.readyState || 'unknown'
                })).filter(s => s.src.includes('_next')),
                errors: window.console ? 'available' : 'unavailable'
            };
        """)
        
        print(f"   Next.js status: {next_status}")
        
        # Check if there are any unhandled errors
        print("2. Checking for script errors...")
        error_check = driver.execute_script("""
            // Create a custom error collector
            window.errorCollector = [];
            const originalError = window.onerror;
            window.onerror = function(msg, url, line, col, error) {
                window.errorCollector.push({
                    message: msg,
                    url: url,
                    line: line,
                    col: col,
                    error: error ? error.toString() : null
                });
                if (originalError) originalError.apply(this, arguments);
            };
            
            // Also catch unhandled promise rejections
            window.addEventListener('unhandledrejection', function(event) {
                window.errorCollector.push({
                    type: 'unhandledrejection',
                    reason: event.reason ? event.reason.toString() : 'unknown'
                });
            });
            
            return 'Error collector installed';
        """)
        
        print(f"   {error_check}")
        
        # Wait a bit more for any errors to surface
        time.sleep(2)
        
        errors = driver.execute_script("return window.errorCollector || [];")
        if errors:
            print("   Collected errors:")
            for error in errors:
                print(f"     {error}")
        else:
            print("   No JavaScript errors collected")
        
        print("3. Checking script execution order...")
        script_info = driver.execute_script("""
            const scripts = Array.from(document.scripts);
            return scripts.map((script, index) => ({
                index: index,
                src: script.src || 'inline',
                async: script.async,
                defer: script.defer,
                type: script.type || 'text/javascript'
            }));
        """)
        
        for script in script_info:
            if '_next' in script['src'] or script['src'] == 'inline':
                print(f"   Script {script['index']}: {script['src']} (async:{script['async']}, defer:{script['defer']})")
        
        print("4. Manual hydration attempt...")
        # Try to manually trigger hydration
        manual_result = driver.execute_script("""
            // Try to find and execute hydration
            if (window.__next_f && window.__next_f.length > 0) {
                return 'Found __next_f data: ' + window.__next_f.length + ' chunks';
            } else {
                return 'No __next_f data found';
            }
        """)
        
        print(f"   {manual_result}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_react_hydration_diagnosis()
