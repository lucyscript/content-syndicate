#!/usr/bin/env python3
"""
Test newsletter API with new schema fields
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8002"

def test_newsletter_creation():
    """Test newsletter creation with new schema fields"""
    
    # First login to get token
    print("1. Logging in...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful!")
    
    # Test creating newsletter with new fields
    print("\n2. Testing newsletter creation with new schema fields...")
    newsletter_data = {
        "title": "Test Newsletter Schema",
        "subject_line": "Test Subject Line",
        "content_sources": ["https://example.com", "https://test.com"],
        "target_audience": "Developers and tech professionals",
        "scheduled_for": None
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/newsletters/", 
        json=newsletter_data,
        headers=headers
    )
    
    print(f"Newsletter creation status: {create_response.status_code}")
    
    if create_response.status_code == 201:
        newsletter = create_response.json()
        print("✅ Newsletter created successfully!")
        print(f"Newsletter ID: {newsletter['id']}")
        print(f"Title: {newsletter['title']}")
        print(f"Subject Line: {newsletter.get('subject_line', 'Not found')}")
        print(f"Target Audience: {newsletter.get('target_audience', 'Not found')}")
        print(f"Content Sources: {newsletter.get('content_sources', 'Not found')}")
        
        # Test content generation
        print(f"\n3. Testing content generation for newsletter {newsletter['id']}...")
        generation_request = {
            "sources": ["https://techcrunch.com"],
            "topic": "AI and Machine Learning",
            "tone": "professional",
            "length": "medium",
            "audience": "tech professionals"
        }
        
        generate_response = requests.post(
            f"{BASE_URL}/api/newsletters/{newsletter['id']}/generate",
            json=generation_request,
            headers=headers
        )
        
        print(f"Content generation status: {generate_response.status_code}")
        
        if generate_response.status_code == 200:
            content_result = generate_response.json()
            print("✅ Content generation successful!")
            print(f"Generated content length: {len(content_result.get('content', ''))}")
            print(f"Generation time: {content_result.get('generation_time', 0)} seconds")
            print(f"Content preview: {content_result.get('content', '')[:200]}...")
        else:
            print(f"❌ Content generation failed")
            print(f"Response: {generate_response.text}")
            
    else:
        print(f"❌ Newsletter creation failed")
        print(f"Response: {create_response.text}")

if __name__ == "__main__":
    print("ContentSyndicate Newsletter API Test")
    print("=====================================")
    test_newsletter_creation()
