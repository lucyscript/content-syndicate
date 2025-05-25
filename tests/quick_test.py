#!/usr/bin/env python3
"""
Quick Test Runner
Runs a subset of critical tests to quickly identify the persistence issue
"""

import sys
import os
import asyncio
import subprocess
import sqlite3
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

def quick_db_check():
    """Quick database check"""
    print("🔍 Quick Database Check")
    print("-" * 30)
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'contentsyndicate.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file missing!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check newsletter count
        cursor.execute("SELECT COUNT(*) FROM newsletters")
        newsletter_count = cursor.fetchone()[0]
        
        # Check user count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        print(f"📊 Users: {user_count}")
        print(f"📊 Newsletters: {newsletter_count}")
        
        if newsletter_count > 0:
            # Show latest newsletters
            cursor.execute("""
                SELECT id, title, status, user_id, created_at 
                FROM newsletters 
                ORDER BY created_at DESC 
                LIMIT 3
            """)
            latest = cursor.fetchall()
            print("📋 Latest newsletters:")
            for nl in latest:
                print(f"  ID:{nl[0]} '{nl[1]}' ({nl[2]}) User:{nl[3]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

async def quick_api_check():
    """Quick API check"""
    print("\n🔍 Quick API Check")
    print("-" * 30)
    
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            # Test backend health
            try:
                response = await client.get("http://localhost:8000/", timeout=3.0)
                print(f"✅ Backend: Status {response.status_code}")
                backend_ok = response.status_code == 200
            except:
                print("❌ Backend: Not responding")
                backend_ok = False
            
            # Test newsletter endpoint
            if backend_ok:
                try:
                    response = await client.get("http://localhost:8000/api/newsletters/", timeout=3.0)
                    print(f"📡 Newsletter API: Status {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        count = len(data) if isinstance(data, list) else len(data.get('newsletters', []))
                        print(f"📊 API returned {count} newsletters")
                        return True
                    else:
                        print(f"❌ Newsletter API error: {response.text[:100]}")
                        return False
                except Exception as e:
                    print(f"❌ Newsletter API error: {e}")
                    return False
            else:
                return False
                
    except Exception as e:
        print(f"❌ API check failed: {e}")
        return False

async def quick_frontend_check():
    """Quick frontend check"""
    print("\n🔍 Quick Frontend Check")
    print("-" * 30)
    
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            # Test frontend health
            try:
                response = await client.get("http://localhost:3000", timeout=3.0)
                print(f"✅ Frontend: Status {response.status_code}")
                frontend_ok = response.status_code == 200
            except:
                print("❌ Frontend: Not responding")
                frontend_ok = False
            
            # Test frontend API proxy
            if frontend_ok:
                try:
                    response = await client.get("http://localhost:3000/api/newsletters", timeout=5.0)
                    print(f"📡 Frontend API: Status {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        count = len(data) if isinstance(data, list) else len(data.get('newsletters', []))
                        print(f"📊 Frontend API returned {count} newsletters")
                        return True
                    else:
                        print(f"❌ Frontend API error: {response.text[:100]}")
                        return False
                except Exception as e:
                    print(f"❌ Frontend API error: {e}")
                    return False
            else:
                return False
                
    except Exception as e:
        print(f"❌ Frontend check failed: {e}")
        return False

def check_processes():
    """Check if required processes are running"""
    print("\n🔍 Process Check")
    print("-" * 30)
    
    try:
        # Check for Python processes (backend)
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
        output = result.stdout
        
        port_8000 = ':8000' in output
        port_3000 = ':3000' in output
        
        print(f"🖥️  Port 8000 (Backend): {'✅ Active' if port_8000 else '❌ Not active'}")
        print(f"🌐 Port 3000 (Frontend): {'✅ Active' if port_3000 else '❌ Not active'}")
        
        if not port_8000:
            print("💡 Start backend: cd app && python main.py")
        if not port_3000:
            print("💡 Start frontend: cd frontend && npm run dev")
        
        return port_8000 and port_3000
        
    except Exception as e:
        print(f"❌ Process check failed: {e}")
        return False

def check_file_structure():
    """Check critical file structure"""
    print("\n🔍 File Structure Check")
    print("-" * 30)
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    critical_files = [
        'db/contentsyndicate.db',
        '.env',
        'app/main.py',
        'app/routes/newsletters.py',
        'frontend/src/app/dashboard/newsletters/page.tsx',
        'frontend/src/hooks/useNewsletters.ts'
    ]
    
    all_exist = True
    for file_path in critical_files:
        full_path = os.path.join(base_dir, file_path)
        exists = os.path.exists(full_path)
        print(f"{'✅' if exists else '❌'} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist

async def create_test_newsletter_quick():
    """Create a test newsletter to verify the entire flow"""
    print("\n🔍 Quick Newsletter Creation Test")
    print("-" * 30)
    
    import httpx
    
    test_data = {
        "title": f"Quick Test {datetime.now().strftime('%H:%M:%S')}",
        "subject_line": "Quick test subject",
        "content": "Quick test content",
        "target_audience": "Testers",
        "status": "draft"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Try creating via backend
            print("Creating via backend...")
            response = await client.post(
                "http://localhost:8000/api/newsletters/",
                json=test_data,
                timeout=5.0
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                newsletter_id = data.get('id')
                print(f"✅ Created newsletter ID: {newsletter_id}")
                
                # Verify it appears in listings
                await asyncio.sleep(0.5)
                
                response = await client.get("http://localhost:8000/api/newsletters/", timeout=5.0)
                if response.status_code == 200:
                    newsletters = response.json()
                    count = len(newsletters) if isinstance(newsletters, list) else len(newsletters.get('newsletters', []))
                    print(f"✅ Backend now shows {count} newsletters")
                
                # Check frontend proxy
                try:
                    response = await client.get("http://localhost:3000/api/newsletters", timeout=5.0)
                    if response.status_code == 200:
                        newsletters = response.json()
                        count = len(newsletters) if isinstance(newsletters, list) else len(newsletters.get('newsletters', []))
                        print(f"✅ Frontend proxy shows {count} newsletters")
                        return True
                    else:
                        print(f"❌ Frontend proxy error: {response.status_code}")
                        return False
                except:
                    print("❌ Frontend proxy not accessible")
                    return False
                    
            else:
                print(f"❌ Creation failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Newsletter creation test failed: {e}")
        return False

async def main():
    """Run quick diagnostic tests"""
    print("🚀 Quick Diagnostic Tests")
    print("=" * 50)
    
    # Sync tests
    db_ok = quick_db_check()
    files_ok = check_file_structure()
    processes_ok = check_processes()
    
    # Async tests
    api_ok = await quick_api_check()
    frontend_ok = await quick_frontend_check()
    creation_ok = await create_test_newsletter_quick()
    
    print("\n" + "=" * 50)
    print("🏁 Quick Test Summary")
    print("-" * 50)
    
    tests = [
        ("Database", db_ok),
        ("File Structure", files_ok),
        ("Processes", processes_ok),
        ("API", api_ok),
        ("Frontend", frontend_ok),
        ("Newsletter Creation", creation_ok)
    ]
    
    for name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print(f"\nResults: {passed}/{total} passed")
    
    if not all(result for _, result in tests):
        print("\n💡 Troubleshooting suggestions:")
        if not processes_ok:
            print("- Start both backend and frontend servers")
        if not db_ok:
            print("- Check database file and run migrations")
        if not api_ok:
            print("- Check backend server logs for errors")
        if not frontend_ok:
            print("- Check frontend server and API proxy configuration")
        if not creation_ok:
            print("- Check API endpoints and authentication")

if __name__ == "__main__":
    asyncio.run(main())
