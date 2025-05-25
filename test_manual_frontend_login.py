#!/usr/bin/env python3
"""
Manual Login Test
Tests logging in through the frontend and checking state
"""
import asyncio
import httpx
import json

async def test_manual_frontend_login():
    """Test logging in and checking the state"""
    print("🔐 Testing Manual Frontend Login")
    print("=" * 50)
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            # Step 1: Visit the login page
            print("1. Visiting login page...")
            response = await client.get("http://localhost:3000/auth/login", timeout=10.0)
            print(f"Login page status: {response.status_code}")
            
            # Step 2: Try to get auth token directly
            print("\n2. Getting auth token from backend...")
            login_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            response = await client.post(
                "http://localhost:8000/api/auth/login", 
                json=login_data,
                timeout=10.0
            )
            
            if response.status_code != 200:
                print(f"❌ Login failed: {response.status_code}")
                return False
            
            auth_data = response.json()
            token = auth_data["access_token"]
            print(f"✅ Got auth token: {token[:30]}...")
            
            # Step 3: Test newsletter API with token
            print("\n3. Testing newsletter API with token...")
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.get(
                "http://localhost:8000/api/newsletters/",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                newsletters = response.json()
                print(f"✅ Newsletter API works! Found {len(newsletters)} newsletters")
                
                print("\n📋 Available newsletters:")
                for i, nl in enumerate(newsletters[:5]):
                    print(f"  {i+1}. ID: {nl['id']}")
                    print(f"      Title: {nl['title']}")
                    print(f"      Status: {nl['status']}")
                    print(f"      Created: {nl.get('created_at', 'N/A')}")
                    print(f"      User ID: {nl.get('user_id', 'N/A')}")
                    print()
                
                print("\n💡 These newsletters should appear in the frontend after login!")
                print("   Token to use in browser localStorage:")
                print(f"   auth_token = {token}")
                
                return True
            else:
                print(f"❌ Newsletter API failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_manual_frontend_login())
    
    if success:
        print("\n" + "="*60)
        print("🎯 SOLUTION - How to see newsletters:")
        print("="*60)
        print("1. Open browser: http://localhost:3000/auth/login")
        print("2. Login with: test@example.com / password123")
        print("3. Check browser console for debug information")
        print("4. Newsletters should appear after successful login")
        print("\nIf still not working, check the debug boxes on the page!")
