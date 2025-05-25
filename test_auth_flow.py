#!/usr/bin/env python3
import asyncio
import httpx
import json

async def test_auth_flow():
    """Test the complete authentication flow"""
    print("🔐 Testing Authentication Flow")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Step 1: Login to get token
            print("1. Attempting login...")
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
            print(f"✅ Login successful! Token: {token[:20]}...")
            
            # Step 2: Test authenticated endpoint
            print("\n2. Testing authenticated newsletter endpoint...")
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
                if newsletters:
                    print("Sample newsletter:")
                    print(f"  - ID: {newsletters[0]['id']}")
                    print(f"  - Title: {newsletters[0]['title']}")
                    print(f"  - Status: {newsletters[0]['status']}")
            else:
                print(f"❌ Failed: {response.text}")
            
            # Step 3: Test user info endpoint
            print("\n3. Testing user info endpoint...")
            response = await client.get(
                "http://localhost:8000/api/auth/me",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                user = response.json()
                print(f"✅ User info retrieved: {user['full_name']} ({user['email']})")
            else:
                print(f"❌ User info failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
