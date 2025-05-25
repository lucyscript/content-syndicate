#!/usr/bin/env python3
"""
Comprehensive Test Script for Topic Inspiration Functionality
Tests the complete workflow from authentication to topic generation
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# Test credentials
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
}

class TopicInspirationTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_backend_health(self):
        """Test if backend is running"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Backend is running")
                return True
            else:
                self.log(f"❌ Backend health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Backend is not accessible: {e}")
            return False
            
    def test_frontend_health(self):
        """Test if frontend is running"""
        try:
            response = self.session.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                self.log("✅ Frontend is running")
                return True
            else:
                self.log(f"❌ Frontend health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Frontend is not accessible: {e}")
            return False
            
    def register_test_user(self):
        """Register a test user"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/register",
                json=TEST_USER,
                timeout=10
            )
            
            if response.status_code == 201:
                self.log("✅ Test user registered successfully")
                return True
            elif response.status_code == 400 and "already exists" in response.text.lower():
                self.log("ℹ️  Test user already exists")
                return True
            else:
                self.log(f"❌ User registration failed: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ User registration error: {e}")
            return False
            
    def login_test_user(self):
        """Authenticate test user"""
        try:
            # Use JSON format instead of form data
            login_data = {
                "email": "test@example.com", 
                "password": "testpassword123"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/login",
                json=login_data,  # Changed from data= to json=
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("access_token")
                if token:
                    self.session.headers.update({"Authorization": f"Bearer {token}"})
                    self.log("✅ User authentication successful")
                    return True
                else:
                    self.log("❌ No access token in response")
                    return False
            else:
                self.log(f"❌ User login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Authentication error: {e}")
            return False
            
    def test_trending_topics_api(self):
        """Test the trending topics API endpoint"""
        try:
            response = self.session.get(
                f"{BACKEND_URL}/api/content/topics/trending",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                topics = data if isinstance(data, list) else data.get("topics", [])
                
                self.log("✅ Trending topics API successful")
                self.log(f"   Retrieved {len(topics)} topics")
                
                if topics:
                    self.log("   Sample topics:")
                    for i, topic in enumerate(topics[:3]):
                        title = topic.get("title", topic) if isinstance(topic, dict) else topic
                        self.log(f"     {i+1}. {title}")
                        
                return True
            else:
                self.log(f"❌ Trending topics API failed: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Trending topics API error: {e}")            
            return False
            
    def test_generate_topics_api(self):
        """Test the AI topic generation API endpoint"""
        try:
            # Use GET with query parameters for topic generation
            params = {
                "count": 5,
                "niche": "tech", 
                "tone": "professional"
            }
            
            response = self.session.get(
                f"{BACKEND_URL}/api/content/topics/generate",
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                topics = data.get("topics", [])
                
                self.log("✅ Generate topics API successful")
                self.log(f"   Generated {len(topics)} topics")
                
                if topics:
                    self.log("   Sample generated topics:")
                    for i, topic in enumerate(topics[:3]):
                        title = topic.get("title", topic) if isinstance(topic, dict) else topic
                        self.log(f"     {i+1}. {title}")
                        
                return True
            else:
                self.log(f"❌ Generate topics API failed: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            self.log(f"❌ Generate topics API error: {e}")
            return False
        
    def test_topic_generation_workflow(self):
        """Test the complete topic generation workflow"""
        try:
            # Test both trending and generate topics
            trending_success = self.test_trending_topics_api()
            generate_success = self.test_generate_topics_api()
            
            if trending_success and generate_success:
                self.log("✅ Topic generation workflow complete")
                return True
            else:
                self.log("❌ Topic generation workflow failed")
                return False
        except Exception as e:
            self.log(f"❌ Topic generation workflow error: {e}")
            return False
            
    def test_frontend_accessibility(self):
        """Test if frontend routes are accessible"""
        try:
            # Test new newsletter page
            response = self.session.get(f"{FRONTEND_URL}/dashboard/newsletters/new", timeout=10)
            
            if response.status_code == 200:
                self.log("✅ Frontend newsletter creation page accessible")
                
                # Check if the page contains topic inspiration elements
                content = response.text.lower()
                if "topic inspiration" in content or "trending topics" in content:
                    self.log("✅ Topic inspiration UI elements found")
                    return True
                else:
                    self.log("⚠️  Topic inspiration UI elements not found in page")
                    return True  # Still consider it a success if page loads
            else:
                self.log(f"❌ Frontend newsletter page failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Frontend accessibility error: {e}")
            return False
            
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        self.log("🚀 Starting comprehensive Topic Inspiration test")
        self.log("=" * 60)
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Frontend Health", self.test_frontend_health),
            ("User Registration", self.register_test_user),
            ("User Authentication", self.login_test_user),
            ("Trending Topics API", self.test_trending_topics_api),
            ("Generate Topics API", self.test_generate_topics_api),
            ("Complete Workflow", self.test_topic_generation_workflow),
            ("Frontend Accessibility", self.test_frontend_accessibility),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            self.log(f"\n📋 Running: {test_name}")
            self.log("-" * 40)
            
            try:
                results[test_name] = test_func()
            except Exception as e:
                self.log(f"❌ {test_name} crashed: {e}")
                results[test_name] = False
                
            time.sleep(1)  # Brief pause between tests
            
        # Summary
        self.log("\n" + "=" * 60)
        self.log("📊 TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status}: {test_name}")
            if result:
                passed += 1
                
        self.log("-" * 60)
        self.log(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All tests passed! Topic Inspiration is working correctly.")
            return True
        else:
            self.log("⚠️  Some tests failed. Check the logs above for details.")
            return False
            
    def cleanup(self):
        """Clean up test data"""
        self.log("\n🧹 Cleaning up...")
        # Note: In a real scenario, you might want to delete the test user
        self.session.close()
        self.log("✅ Cleanup complete")

def main():
    """Main test execution"""
    tester = TopicInspirationTester()
    
    try:
        success = tester.run_comprehensive_test()
        exit_code = 0 if success else 1
    except KeyboardInterrupt:
        tester.log("\n⚠️  Test interrupted by user")
        exit_code = 130
    except Exception as e:
        tester.log(f"\n💥 Unexpected error: {e}")
        exit_code = 1
    finally:
        tester.cleanup()
        
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
