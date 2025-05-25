#!/usr/bin/env python3
"""
Examine the raw HTML being served by Next.js
"""

import requests
import re

def examine_html_source():
    print("🔍 EXAMINING RAW HTML SOURCE")
    print("=" * 40)
    
    try:
        # Get the raw HTML from the server
        response = requests.get("http://localhost:3000/dashboard/newsletters/new")
        print(f"📡 Server response: {response.status_code}")
        
        html_content = response.text
        print(f"📄 HTML content length: {len(html_content)} characters")
        
        # Look for key elements
        has_next_app = '#__next' in html_content or 'id="__next"' in html_content
        has_react_scripts = '_next/static' in html_content
        has_body = '<body' in html_content
        has_html = '<html' in html_content
        
        print("🔍 Key elements found:")
        print(f"  ✅ HTML tag: {has_html}")
        print(f"  ✅ Body tag: {has_body}")
        print(f"  {'✅' if has_next_app else '❌'} #__next container: {has_next_app}")
        print(f"  ✅ Next.js scripts: {has_react_scripts}")
        
        # Extract the body content
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
        if body_match:
            body_content = body_match.group(1)
            print(f"\n📦 Body content preview (first 500 chars):")
            print(body_content[:500])
            print("...")
            
            # Look for specific patterns
            if '#__next' not in body_content and 'id="__next"' not in body_content:
                print("\n🚨 CRITICAL: No #__next container found in body!")
                print("This explains why React cannot hydrate - there's no mount point.")
            
        # Look for script tags
        script_matches = re.findall(r'<script[^>]*src="([^"]*)"[^>]*>', html_content)
        print(f"\n📦 Found {len(script_matches)} script tags:")
        for script in script_matches[:10]:  # Show first 10
            print(f"  - {script}")
        if len(script_matches) > 10:
            print(f"  ... and {len(script_matches) - 10} more")
            
        # Check for Next.js data
        if '__NEXT_DATA__' in html_content:
            print("✅ __NEXT_DATA__ found in HTML")
        else:
            print("❌ __NEXT_DATA__ missing from HTML")
            
        return has_next_app and has_react_scripts
        
    except Exception as e:
        print(f"❌ Error examining HTML: {e}")
        return False

if __name__ == "__main__":
    success = examine_html_source()
    exit(0 if success else 1)
