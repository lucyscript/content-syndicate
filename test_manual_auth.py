#!/usr/bin/env python3
import asyncio
import httpx
import json

async def test_manual_auth():
    """Test authentication by getting a token and then testing newsletter access"""
    print("🔐 Testing Manual Authentication Flow")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Step 1: Get authentication token
            print("1. Getting authentication token...")
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
                print(f"Response: {response.text}")
                return
            
            auth_data = response.json()
            token = auth_data["access_token"]
            print(f"✅ Token obtained: {token[:30]}...")
            
            # Step 2: Test authenticated newsletter access
            print("\n2. Testing newsletter access with token...")
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.get(
                "http://localhost:8000/api/newsletters/",
                headers=headers,
                timeout=10.0
            )
            
            print(f"Newsletter API Status: {response.status_code}")
            if response.status_code == 200:
                newsletters = response.json()
                print(f"✅ Success! Found {len(newsletters)} newsletters")
                print("\nSample newsletters:")
                for nl in newsletters[:3]:  # Show first 3
                    print(f"  - ID: {nl['id']}, Title: {nl['title']}, Status: {nl['status']}")
                return True
            else:
                print(f"❌ Newsletter access failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_manual_auth())
    if success:
        print("\n✅ Backend authentication is working correctly!")
        print("💡 Issue is likely with frontend authentication state")
    else:
        print("\n❌ Backend authentication has issues")
