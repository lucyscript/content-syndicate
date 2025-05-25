#!/usr/bin/env python3
import asyncio
import httpx

async def test_frontend_access():
    """Test what the frontend is actually showing"""
    print("🔍 Testing Frontend Newsletter Access")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Check newsletters page directly
            print("1. Testing direct access to newsletters page...")
            response = await client.get("http://localhost:3000/dashboard/newsletters", timeout=10.0)
            print(f"Status: {response.status_code}")
            print(f"Final URL: {response.url}")
            
            # Check if it contains login or newsletters content
            content = response.text
            if 'login' in content.lower():
                print("✅ Page contains login elements")
            elif 'newsletter' in content.lower():
                print("✅ Page contains newsletter elements")
            else:
                print("❓ Page content unclear")
            
            # Test 2: Check login page
            print("\n2. Testing login page...")
            response = await client.get("http://localhost:3000/auth/login", timeout=10.0)
            print(f"Login page status: {response.status_code}")
            
            # Test 3: Check if we can make API calls from the frontend context
            print("\n3. Testing direct API access (should fail without auth)...")
            response = await client.get("http://localhost:8000/api/newsletters/", timeout=10.0)
            print(f"Direct API status: {response.status_code}")
            if response.status_code == 403:
                print("✅ API properly protected")
            else:
                print("❌ API not properly protected")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_frontend_access())
