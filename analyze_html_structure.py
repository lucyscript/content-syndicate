#!/usr/bin/env python3
"""
Detailed HTML Structure Analysis
Examines the complete HTML output to understand why #__next is missing
"""

import requests
import re

def analyze_html_structure():
    print("🔍 Analyzing complete HTML structure...")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:3000/", timeout=10)
        html = response.text
        
        print(f"Status: {response.status_code}")
        print(f"Total HTML length: {len(html)}")
        
        # Split HTML into sections for analysis
        head_match = re.search(r'<head[^>]*>(.*?)</head>', html, re.DOTALL)
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        
        if head_match:
            head_content = head_match.group(1)
            print(f"\n📋 HEAD section analysis:")
            print(f"   Length: {len(head_content)}")
            
            # Check for Next.js specific items in head
            has_next_css = '_next/static' in head_content
            has_turbopack = 'turbopack' in head_content
            script_count = head_content.count('<script')
            
            print(f"   Next.js CSS: {has_next_css}")
            print(f"   Turbopack refs: {has_turbopack}")
            print(f"   Script tags: {script_count}")
        
        if body_match:
            body_content = body_match.group(1).strip()
            print(f"\n📋 BODY section analysis:")
            print(f"   Length: {len(body_content)}")
            
            # Show the complete body content (this is where the issue likely is)
            print(f"\n📄 Complete BODY content:")
            print("=" * 40)
            print(body_content)
            print("=" * 40)
            
            # Check what's actually in the body
            has_next_div = '__next' in body_content
            has_scripts = '<script' in body_content
            has_noscript = '<noscript' in body_content
            div_count = body_content.count('<div')
            
            print(f"\n🔍 Body content analysis:")
            print(f"   Contains __next: {has_next_div}")
            print(f"   Contains scripts: {has_scripts}")
            print(f"   Contains noscript: {has_noscript}")
            print(f"   Total div count: {div_count}")
            
            # Look for any error messages or unusual content
            if 'error' in body_content.lower():
                print("   ⚠️  Contains 'error' text")
            if 'exception' in body_content.lower():
                print("   ⚠️  Contains 'exception' text")
            if len(body_content) < 100:
                print("   ⚠️  Body content is very short - possible rendering issue")
        
        # Check for any Next.js error indicators
        print(f"\n🔍 Error detection:")
        error_patterns = [
            'Application error',
            'ChunkLoadError',
            'Module not found',
            'Compilation error',
            'Server Error',
            '500',
            '404'
        ]
        
        found_errors = []
        for pattern in error_patterns:
            if pattern in html:
                found_errors.append(pattern)
        
        if found_errors:
            print(f"   Found error patterns: {found_errors}")
        else:
            print("   No obvious error patterns found")
        
        # Look for the actual app content - maybe it's rendering differently
        print(f"\n🔍 Searching for app content patterns:")
        app_patterns = [
            'AuthProvider',
            'QueryProvider',
            'data-testid',
            'className=',
            'tailwind',
            'radix'
        ]
        
        found_patterns = []
        for pattern in app_patterns:
            if pattern in html:
                found_patterns.append(pattern)
        
        print(f"   Found app patterns: {found_patterns}")
        
        return body_content if body_match else None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    body = analyze_html_structure()
    
    if body is not None:
        print(f"\n🏁 Analysis complete!")
        if '__next' not in body:
            print(f"❌ CONFIRMED: #__next div is missing from body")
            print(f"💡 This suggests the root layout is not rendering at all")
        else:
            print(f"✅ Found __next reference in body")
    else:
        print(f"❌ Could not analyze HTML structure")
