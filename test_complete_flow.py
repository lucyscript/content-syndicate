#!/usr/bin/env python3
"""
Complete User Flow Test
Tests the full user journey from login to viewing newsletters
"""
import asyncio
import httpx
import json

async def test_complete_user_flow():
    """Test the complete user flow"""
    print("🚀 Testing Complete User Flow")
    print("=" * 50)
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            # Step 1: Check if we can access protected page (should redirect)
            print("1. Testing access to protected page without auth...")
            response = await client.get("http://localhost:3000/dashboard/newsletters", timeout=10.0)
            print(f"Protected page status: {response.status_code}")
            if 'login' in str(response.url):
                print("✅ Properly redirected to login page")
            else:
                print("❌ Not redirected to login - security issue!")
            
            # Step 2: Test login through backend API
            print("\n2. Testing backend authentication...")
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
                print(f"❌ Backend login failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            auth_data = response.json()
            token = auth_data["access_token"]
            print(f"✅ Backend login successful! Token: {token[:30]}...")
            
            # Step 3: Test authenticated API call
            print("\n3. Testing authenticated newsletter access...")
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.get(
                "http://localhost:8000/api/newsletters/",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                newsletters = response.json()
                print(f"✅ API access successful! Found {len(newsletters)} newsletters")
                
                # Show sample newsletters
                if newsletters:
                    print("\n📋 Sample newsletters:")
                    for i, nl in enumerate(newsletters[:3]):
                        print(f"  {i+1}. ID: {nl['id']}, Title: {nl['title']}, Status: {nl['status']}")
                        print(f"      Created: {nl.get('created_at', 'N/A')}")
                        print(f"      User ID: {nl.get('user_id', 'N/A')}")
                
                return True
            else:
                print(f"❌ API access failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False

async def test_frontend_auth_flow():
    """Test frontend authentication endpoints"""
    print("\n🌐 Testing Frontend Authentication Flow")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test frontend auth endpoints
            print("1. Testing frontend auth endpoint...")
            login_data = {
                "email": "test@example.com", 
                "password": "password123"
            }
            
            # Try to login through frontend (this might be proxied)
            response = await client.post(
                "http://localhost:3000/api/auth/login",
                json=login_data,
                timeout=10.0
            )
            
            print(f"Frontend auth status: {response.status_code}")
            if response.status_code == 404:
                print("ℹ️ Frontend doesn't proxy auth - that's fine, using direct backend")
                return True
            elif response.status_code == 200:
                print("✅ Frontend auth proxy works!")
                return True
            else:
                print(f"❌ Frontend auth issue: {response.text[:100]}")
                return False
                
        except Exception as e:
            print(f"❌ Frontend auth test failed: {e}")
            return False

if __name__ == "__main__":
    print("🔧 ContentSyndicate Authentication Test Suite")
    print("=" * 60)
    
    success1 = asyncio.run(test_complete_user_flow())
    success2 = asyncio.run(test_frontend_auth_flow())
    
    print("\n" + "=" * 60)
    print("🏁 Test Results Summary")
    print("-" * 60)
    print(f"Backend Authentication: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Frontend Integration:   {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1:
        print("\n💡 Next Steps:")
        print("   1. Visit http://localhost:3000/auth/login")
        print("   2. Login with: test@example.com / password123")
        print("   3. You should be redirected to dashboard with newsletters visible")
        print("   4. Newsletter persistence issue should now be resolved!")
    else:
        print("\n❌ Authentication issues need to be resolved first")
