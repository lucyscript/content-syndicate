
"""
Debug Next.js app initialization issues
"""

import requests
import time

def debug_app_init():
    print("🔍 DEBUGGING NEXT.JS APP INITIALIZATION")
    print("=" * 50)
    
    # Test different routes to see if the issue is route-specific
    routes_to_test = [
        "/",
        "/auth/login", 
        "/dashboard",
        "/dashboard/newsletters/new",
        "/landing"
    ]
    
    for route in routes_to_test:
        print(f"\n📍 Testing route: {route}")
        try:
            response = requests.get(f"http://localhost:3000{route}", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check key indicators
                indicators = {
                    "Has #__next": '<div id="__next">' in content,
                    "Has __NEXT_DATA__": '__NEXT_DATA__' in content,
                    "Has loading spinner": 'animate-spin' in content,
                    "Has actual content": len(content.strip()) > 500,
                    "Has React scripts": '_next/static' in content
                }
                
                print(f"  Status: {response.status_code}")
                for indicator, result in indicators.items():
                    status = "✅" if result else "❌"
                    print(f"  {status} {indicator}")
                
                # If this route is working, extract some key info
                if indicators["Has #__next"] and indicators["Has __NEXT_DATA__"]:
                    print(f"  🎉 Route {route} is working correctly!")
                    return route
                    
            else:
                print(f"  ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n⚠️  No routes are rendering properly")
    return None

if __name__ == "__main__":
    working_route = debug_app_init()
    
    if working_route:
        print(f"\n✅ Found working route: {working_route}")
        print("The issue may be route-specific or authentication-related")
    else:
        print("\n❌ No routes are working - this is a fundamental Next.js app issue")
        print("Possible causes:")
        print("- Root layout issues")
        print("- Provider configuration errors") 
        print("- Build/compilation problems")
        print("- Development server issues")