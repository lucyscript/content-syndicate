#!/usr/bin/env python3
"""
API Testing Script
Tests the FastAPI endpoints for newsletter operations
"""

import sys
import os
import asyncio
import httpx
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

BASE_URL = "http://localhost:8000"

async def test_api_health():
    """Test if the API is running"""
    print("🔍 Testing API health...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("✅ API is running and responding")
                return True
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure the backend server is running on http://localhost:8000")
        return False

async def test_newsletters_endpoint():
    """Test the newsletters GET endpoint"""
    print("\n🔍 Testing newsletters GET endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/newsletters/")
            
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Newsletters endpoint responding")
                print(f"Response type: {type(data)}")
                
                if isinstance(data, list):
                    print(f"📊 Found {len(data)} newsletters")
                    for i, newsletter in enumerate(data[:3]):  # Show first 3
                        print(f"  Newsletter {i+1}: {newsletter.get('title', 'No title')}")
                elif isinstance(data, dict):
                    print(f"📊 Response data keys: {list(data.keys())}")
                    if 'newsletters' in data:
                        newsletters = data['newsletters']
                        print(f"📊 Found {len(newsletters)} newsletters in 'newsletters' key")
                else:
                    print(f"📊 Unexpected response format: {data}")
                    
                return True
            else:
                print(f"❌ Newsletters endpoint error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Error text: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Newsletters endpoint test failed: {e}")
        return False

async def test_create_newsletter():
    """Test creating a newsletter via API"""
    print("\n🔍 Testing newsletter creation via API...")
    
    test_newsletter = {
        "title": f"API Test Newsletter {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "subject_line": "API Test Subject",
        "content": "This is test content created via API",
        "target_audience": "API testers",
        "status": "draft"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/newsletters/",
                json=test_newsletter,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print("✅ Newsletter created successfully via API")
                print(f"Created newsletter ID: {data.get('id')}")
                print(f"Title: {data.get('title')}")
                return True
            else:
                print(f"❌ Newsletter creation failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Error text: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Newsletter creation test failed: {e}")
        return False

async def test_content_api_endpoints():
    """Test content-related API endpoints"""
    print("\n🔍 Testing content API endpoints...")
    
    endpoints_to_test = [
        "/api/content/trending-topics",
        "/api/content/generate-topics",
        "/api/analytics/stats"
    ]
    
    results = []
    
    for endpoint in endpoints_to_test:
        try:
            async with httpx.AsyncClient() as client:
                if endpoint == "/api/content/generate-topics":
                    # POST request for topic generation
                    response = await client.post(
                        f"{BASE_URL}{endpoint}",
                        json={"count": 3, "niche": "general", "tone": "professional"}
                    )
                else:
                    # GET request
                    response = await client.get(f"{BASE_URL}{endpoint}")
                
                print(f"  {endpoint}: Status {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ Response received: {len(str(data))} chars")
                    results.append(True)
                else:
                    print(f"    ❌ Error: {response.status_code}")
                    results.append(False)
                    
        except Exception as e:
            print(f"    ❌ Exception: {e}")
            results.append(False)
    
    return all(results)

async def test_auth_requirements():
    """Test if endpoints require authentication"""
    print("\n🔍 Testing authentication requirements...")
    
    # Test without auth headers
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/newsletters/")
            
            if response.status_code == 401:
                print("✅ Authentication required (401) - this is expected")
                return True
            elif response.status_code == 200:
                print("⚠️  No authentication required - newsletters accessible without auth")
                return True
            else:
                print(f"❓ Unexpected auth response: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return False

async def test_cors_headers():
    """Test CORS headers for frontend compatibility"""
    print("\n🔍 Testing CORS headers...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test OPTIONS request (preflight)
            response = await client.options(f"{BASE_URL}/api/newsletters/")
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            }
            
            print("CORS Headers:")
            for header, value in cors_headers.items():
                if value:
                    print(f"  ✅ {header}: {value}")
                else:
                    print(f"  ❌ {header}: Not set")
            
            # Check if localhost is allowed
            origin_header = cors_headers.get('Access-Control-Allow-Origin')
            if origin_header and ('*' in origin_header or 'localhost' in origin_header or '3000' in origin_header):
                print("✅ Frontend origin appears to be allowed")
                return True
            else:
                print("⚠️  Frontend origin may not be allowed")
                return False
                
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

async def main():
    """Run all API tests"""
    print("🚀 Starting API Tests\n")
    print("="*50)
    
    tests = [
        test_api_health,
        test_newsletters_endpoint,
        test_create_newsletter,
        test_content_api_endpoints,
        test_auth_requirements,
        test_cors_headers
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    print("\n" + "="*50)
    print(f"🏁 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("✅ All API tests passed!")
    else:
        print("❌ Some API tests failed!")
        print("💡 Check the specific failures above to debug the newsletter persistence issue")

if __name__ == "__main__":
    asyncio.run(main())
