#!/usr/bin/env python3
"""
Test if React hydration is now working after the build fix
"""

import requests
import time

def test_hydration_fix():
    print("🔧 TESTING REACT HYDRATION FIX")
    print("=" * 40)
    
    try:
        print("1️⃣ Testing page load...")
        response = requests.get("http://localhost:3000/dashboard/newsletters/new", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for the critical React elements
            checks = {
                "#__next container": '<div id="__next">' in content,
                "__NEXT_DATA__ script": '__NEXT_DATA__' in content,
                "Loading spinner only": 'animate-spin' in content and '#__next' not in content,
                "Page has actual content": len(content) > 1000,
                "React scripts present": '_next/static' in content
            }
            
            print("📊 Hydration checks:")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                print(f"  {status} {check}: {result}")
            
            # Show a preview of the content
            print(f"\n📄 Content preview (first 200 chars):")
            print(content[:200] + "...")
            
            # Check if we're still getting the loading spinner
            if checks["Loading spinner only"]:
                print("\n🚨 Still getting loading spinner - React not hydrating")
                return False
            elif checks["#__next container"] and checks["__NEXT_DATA__ script"]:
                print("\n✅ React hydration appears to be working!")
                return True
            else:
                print("\n⚠️  Mixed results - needs further investigation")
                return False
                
        else:
            print(f"❌ Page failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing hydration: {e}")
        return False

if __name__ == "__main__":
    success = test_hydration_fix()
    exit(0 if success else 1)
