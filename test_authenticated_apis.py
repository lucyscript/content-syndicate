#!/usr/bin/env python3
"""
Test Topic Inspiration APIs with authentication
"""

import requests

def test_authenticated_apis():
    print('🔐 Testing Topic Inspiration APIs with authentication...')
    print('=' * 60)
    
    # Login first
    login_data = {'email': 'test@example.com', 'password': 'testpassword123'}
    try:
        print('1️⃣ Attempting login...')
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        print(f'   Login status: {login_response.status_code}')
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            print('   ✅ Login successful!')
            
            # Test endpoints with auth
            print('\n2️⃣ Testing API endpoints with authentication...')
            endpoints = [
                '/api/content/topics/trending',
                '/api/content/topics/generate', 
                '/api/content/trending'
            ]
            
            for endpoint in endpoints:
                try:
                    print(f'\n📡 Testing {endpoint}...')
                    if 'generate' in endpoint:
                        # POST request for generate endpoint
                        r = requests.get(f'http://localhost:8000{endpoint}?count=5', headers=headers)
                    else:
                        # GET request for other endpoints
                        r = requests.get(f'http://localhost:8000{endpoint}', headers=headers)
                    
                    print(f'   Status: {r.status_code}')
                    
                    if r.status_code == 200:
                        try:
                            data = r.json()
                            if isinstance(data, dict):
                                print(f'   ✅ Success! Response keys: {list(data.keys())}')
                                if 'topics' in data:
                                    print(f'   📝 Topics count: {len(data["topics"])}')
                            elif isinstance(data, list):
                                print(f'   ✅ Success! List with {len(data)} items')
                            else:
                                print(f'   ✅ Success! Response type: {type(data)}')
                        except:
                            print(f'   ✅ Success! Non-JSON response: {r.text[:100]}...')
                    elif r.status_code == 500:
                        print(f'   ❌ Server error: {r.text[:100]}...')
                    elif r.status_code == 404:
                        print(f'   ❌ Endpoint not found')
                    else:
                        print(f'   ⚠️  Unexpected status: {r.text[:100]}...')
                        
                except Exception as e:
                    print(f'   ❌ Error: {e}')
        else:
            print(f'   ❌ Login failed: {login_response.text}')
            
    except Exception as e:
        print(f'❌ Login error: {e}')

    print('\n' + '=' * 60)
    print('🏁 Authentication test complete')

if __name__ == "__main__":
    test_authenticated_apis()