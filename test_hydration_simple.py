#!/usr/bin/env python3
"""
Simple React Hydration Test Script
Tests Next.js React hydration without browser automation
"""

import requests
import re

def test_hydration_simple():
    print("🔍 Testing React hydration...")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3000/", timeout=10)
        html = response.text
        
        print(f"Status: {response.status_code}")
        print(f"Content-Length: {len(html)}")
        
        # Check for critical Next.js elements
        has_next_div = 'id="__next"' in html
        has_next_data = '__NEXT_DATA__' in html
        has_react_scripts = '_next/static' in html
        has_html_tag = '<html' in html
        has_body_tag = '<body' in html
        
        print(f"\n🔍 HTML Structure Analysis:")
        print(f"   Has <html> tag: {has_html_tag}")
        print(f"   Has <body> tag: {has_body_tag}")
        print(f"   Has #__next div: {has_next_div}")
        print(f"   Has __NEXT_DATA__: {has_next_data}")
        print(f"   Has React scripts: {has_react_scripts}")
        
        # Extract and analyze the structure
        if has_next_div:
            # Find the __next div content
            next_match = re.search(r'<div id="__next"[^>]*>(.*?)</div>', html, re.DOTALL)
            if next_match:
                next_content = next_match.group(1).strip()
                print(f"   #__next content length: {len(next_content)}")
                if len(next_content) == 0:
                    print("   ❌ CRITICAL: #__next div is empty!")
                else:
                    print("   ✅ #__next has content")
                    # Show first 200 chars of content
                    preview = next_content[:200].replace('\n', ' ')
                    print(f"   Content preview: {preview}...")
            else:
                print("   ❌ Could not extract #__next content")
        else:
            print("   ❌ CRITICAL: No #__next div found!")
            
        # Check for provider patterns
        has_auth_provider = 'AuthProvider' in html or 'auth-provider' in html
        has_query_provider = 'QueryProvider' in html or 'query-provider' in html
        
        print(f"\n🔍 Provider Analysis:")
        print(f"   AuthProvider references: {has_auth_provider}")
        print(f"   QueryProvider references: {has_query_provider}")
        
        # Look for specific app content
        has_navigation = 'nav' in html.lower()
        has_main_content = 'main' in html.lower()
        has_footer = 'footer' in html.lower()
        
        print(f"\n🔍 App Content Analysis:")
        print(f"   Has navigation: {has_navigation}")
        print(f"   Has main content: {has_main_content}")
        print(f"   Has footer: {has_footer}")
        
        # Show the complete HTML structure (truncated)
        print(f"\n📄 HTML Sample (first 1000 chars):")
        print(html[:1000])
        print("...")
        
        if not has_next_div:
            print(f"\n❌ ROOT ISSUE IDENTIFIED:")
            print(f"   The #__next div is missing from the HTML output.")
            print(f"   This means Next.js is not properly rendering the root layout.")
            print(f"   Possible causes:")
            print(f"   - Root layout.tsx is not being used")
            print(f"   - Provider components are crashing")
            print(f"   - App router configuration issue")
            
        return has_next_div and has_next_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_hydration_simple()
    print(f"\n🏁 Test Result: {'✅ PASS' if success else '❌ FAIL'}")
