#!/usr/bin/env python3
"""
Frontend Integration Testing Script
Tests the integration between frontend and backend
"""

import sys
import os
import asyncio
import httpx
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

async def test_frontend_running():
    """Test if the frontend is running"""
    print("🔍 Testing frontend server...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(FRONTEND_URL, timeout=5.0)
            if response.status_code == 200:
                print("✅ Frontend is running and responding")
                return True
            else:
                print(f"❌ Frontend returned status: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to frontend: {e}")
        print("💡 Make sure the frontend server is running on http://localhost:3000")
        return False

async def test_api_proxy():
    """Test if frontend can proxy API requests"""
    print("\n🔍 Testing API proxy through frontend...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test API call through Next.js API routes
            response = await client.get(f"{FRONTEND_URL}/api/newsletters", timeout=10.0)
            
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ API proxy working - got JSON response")
                    print(f"Response type: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"📊 Newsletters count: {len(data)}")
                    elif isinstance(data, dict) and 'newsletters' in data:
                        print(f"📊 Newsletters count: {len(data['newsletters'])}")
                    
                    return True
                except json.JSONDecodeError:
                    print("❌ API proxy returned non-JSON response")
                    print(f"Response text: {response.text[:200]}...")
                    return False
            else:
                print(f"❌ API proxy error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False
                
    except Exception as e:
        print(f"❌ API proxy test failed: {e}")
        return False

async def test_direct_backend_vs_proxy():
    """Compare direct backend call vs frontend proxy"""
    print("\n🔍 Comparing direct backend vs frontend proxy...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Direct backend call
            try:
                backend_response = await client.get(f"{BACKEND_URL}/api/newsletters/", timeout=5.0)
                backend_status = backend_response.status_code
                backend_data = None
                if backend_status == 200:
                    backend_data = backend_response.json()
                print(f"Direct backend: Status {backend_status}")
            except Exception as e:
                print(f"Direct backend failed: {e}")
                backend_status = None
                backend_data = None
            
            # Frontend proxy call
            try:
                proxy_response = await client.get(f"{FRONTEND_URL}/api/newsletters", timeout=10.0)
                proxy_status = proxy_response.status_code
                proxy_data = None
                if proxy_status == 200:
                    proxy_data = proxy_response.json()
                print(f"Frontend proxy: Status {proxy_status}")
            except Exception as e:
                print(f"Frontend proxy failed: {e}")
                proxy_status = None
                proxy_data = None
            
            # Compare results
            if backend_status == 200 and proxy_status == 200:
                backend_count = len(backend_data) if isinstance(backend_data, list) else len(backend_data.get('newsletters', []))
                proxy_count = len(proxy_data) if isinstance(proxy_data, list) else len(proxy_data.get('newsletters', []))
                
                print(f"Backend newsletters: {backend_count}")
                print(f"Proxy newsletters: {proxy_count}")
                
                if backend_count == proxy_count:
                    print("✅ Backend and proxy return same count")
                    return True
                else:
                    print("❌ Backend and proxy return different counts!")
                    return False
            else:
                print("❌ Cannot compare - one or both calls failed")
                return False
                
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
        return False

async def test_newsletter_creation_flow():
    """Test the complete newsletter creation flow"""
    print("\n🔍 Testing newsletter creation flow...")
    
    test_newsletter = {
        "title": f"Integration Test {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "subject_line": "Integration Test Subject",
        "content": "Test content for integration testing",
        "target_audience": "Integration testers",
        "status": "draft"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # 1. Create newsletter via frontend API
            print("Step 1: Creating newsletter via frontend...")
            create_response = await client.post(
                f"{FRONTEND_URL}/api/newsletters",
                json=test_newsletter,
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )
            
            if create_response.status_code not in [200, 201]:
                print(f"❌ Creation failed: {create_response.status_code}")
                print(f"Response: {create_response.text}")
                return False
            
            created_data = create_response.json()
            newsletter_id = created_data.get('id')
            print(f"✅ Newsletter created with ID: {newsletter_id}")
            
            # 2. Verify it appears in the list
            print("Step 2: Verifying newsletter appears in list...")
            await asyncio.sleep(1)  # Give a moment for DB to update
            
            list_response = await client.get(f"{FRONTEND_URL}/api/newsletters", timeout=10.0)
            if list_response.status_code != 200:
                print(f"❌ List fetch failed: {list_response.status_code}")
                return False
            
            list_data = list_response.json()
            newsletters = list_data if isinstance(list_data, list) else list_data.get('newsletters', [])
            
            found = False
            for nl in newsletters:
                if nl.get('id') == newsletter_id:
                    found = True
                    break
            
            if found:
                print("✅ Newsletter found in list after creation")
                return True
            else:
                print("❌ Newsletter NOT found in list after creation!")
                print(f"Created ID: {newsletter_id}")
                print(f"Available IDs: {[nl.get('id') for nl in newsletters]}")
                return False
                
    except Exception as e:
        print(f"❌ Newsletter creation flow test failed: {e}")
        return False

async def test_environment_variables():
    """Test environment variable configuration"""
    print("\n🔍 Testing environment configuration...")
    
    # Check if .env file exists
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        print("✅ .env file exists")
        
        # Read and check key variables
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        important_vars = ['DATABASE_URL', 'GEMINI_API_KEY', 'SECRET_KEY']
        for var in important_vars:
            if var in env_content:
                print(f"✅ {var} is set in .env")
            else:
                print(f"❌ {var} is missing from .env")
        
        # Check database URL format
        if 'DATABASE_URL' in env_content:
            if 'sqlite:///./db/contentsyndicate.db' in env_content:
                print("✅ Database URL points to correct location")
            else:
                print("⚠️  Database URL may not point to ./db/contentsyndicate.db")
                
        return True
    else:
        print("❌ .env file not found!")
        return False

async def test_data_consistency():
    """Test data consistency between different access methods"""
    print("\n🔍 Testing data consistency...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Get data through different paths
            paths_to_test = [
                f"{BACKEND_URL}/api/newsletters/",
                f"{FRONTEND_URL}/api/newsletters"
            ]
            
            results = []
            for path in paths_to_test:
                try:
                    response = await client.get(path, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        count = len(data) if isinstance(data, list) else len(data.get('newsletters', []))
                        results.append((path, count, data))
                        print(f"✅ {path}: {count} newsletters")
                    else:
                        print(f"❌ {path}: Status {response.status_code}")
                        results.append((path, None, None))
                except Exception as e:
                    print(f"❌ {path}: Error {e}")
                    results.append((path, None, None))
            
            # Check consistency
            valid_results = [(path, count, data) for path, count, data in results if count is not None]
            if len(valid_results) >= 2:
                counts = [count for _, count, _ in valid_results]
                if all(c == counts[0] for c in counts):
                    print("✅ Data is consistent across all endpoints")
                    return True
                else:
                    print("❌ Data inconsistency detected!")
                    for path, count, _ in valid_results:
                        print(f"  {path}: {count} newsletters")
                    return False
            else:
                print("❌ Not enough valid endpoints to check consistency")
                return False
                
    except Exception as e:
        print(f"❌ Data consistency test failed: {e}")
        return False

async def main():
    """Run all integration tests"""
    print("🚀 Starting Frontend Integration Tests\n")
    print("="*60)
    
    tests = [
        test_frontend_running,
        test_api_proxy,
        test_direct_backend_vs_proxy,
        test_environment_variables,
        test_data_consistency,
        test_newsletter_creation_flow
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    print("\n" + "="*60)
    print(f"🏁 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("✅ All integration tests passed!")
        print("💡 If newsletters still don't show up, check the frontend components and hooks")
    else:
        print("❌ Some integration tests failed!")
        print("💡 Focus on fixing the failed tests to resolve the persistence issue")

if __name__ == "__main__":
    asyncio.run(main())
