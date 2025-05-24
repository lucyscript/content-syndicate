#!/usr/bin/env python3
"""
End-to-end test of the complete ContentSyndicate newsletter generation workflow
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8002"

def test_end_to_end_workflow():
    """Test the complete newsletter creation and AI content generation workflow"""
    
    print("🚀 ContentSyndicate End-to-End Test")
    print("=" * 50)
    
    # Step 1: Login
    print("\n1️⃣ Logging in...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        print(f"Response: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful!")
    
    # Step 2: Create a newsletter
    print("\n2️⃣ Creating newsletter...")
    newsletter_data = {
        "title": "AI Revolution Weekly",
        "subject_line": "🤖 This Week in AI: Breaking Developments",
        "content_sources": ["reddit", "news"],
        "target_audience": "Tech professionals, AI enthusiasts, and developers",
        "scheduled_for": None
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/newsletters/", 
        json=newsletter_data,
        headers=headers
    )
    
    if create_response.status_code != 201:
        print("❌ Newsletter creation failed")
        print(f"Response: {create_response.text}")
        return False
    
    newsletter = create_response.json()
    newsletter_id = newsletter['id']
    print(f"✅ Newsletter created! ID: {newsletter_id}")
    print(f"   Title: {newsletter['title']}")
    print(f"   Target Audience: {newsletter.get('target_audience', 'Not set')}")
    
    # Step 3: Generate content with AI
    print("\n3️⃣ Generating content with AI...")
    generation_request = {
        "sources": ["reddit", "news"],
        "topic": "Artificial Intelligence and Machine Learning trends",
        "tone": "professional",
        "length": "medium",
        "audience": "tech professionals and AI enthusiasts"
    }
    
    start_time = time.time()
    generate_response = requests.post(
        f"{BASE_URL}/api/newsletters/{newsletter_id}/generate",
        json=generation_request,
        headers=headers
    )
    end_time = time.time()
    
    print(f"Content generation took: {end_time - start_time:.2f} seconds")
    print(f"Response status: {generate_response.status_code}")
    
    if generate_response.status_code == 200:
        content_result = generate_response.json()
        print("✅ Content generation successful!")
        print(f"   Content length: {len(content_result.get('content', ''))} characters")
        print(f"   Subject line: {content_result.get('subject_line', 'Not generated')}")
        print(f"   Sources used: {len(content_result.get('sources_used', []))} sources")
        print(f"   Generation time: {content_result.get('generation_time', 0):.3f} seconds")
        
        # Show preview of generated content
        content = content_result.get('content', '')
        if content:
            print(f"\n📄 Content Preview (first 500 chars):")
            print("-" * 50)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 50)
        else:
            print("⚠️  Warning: No content was generated!")
            
        # Show sources used
        sources_used = content_result.get('sources_used', [])
        if sources_used:
            print(f"\n📊 Sources Used:")
            for source in sources_used:
                print(f"   • {source.get('source', 'Unknown')}: {source.get('count', 0)} items ({source.get('status', 'unknown')})")
        
        return True
    else:
        print("❌ Content generation failed")
        print(f"Response: {generate_response.text}")
        return False

def test_ai_agent_direct():
    """Test the AI agent directly to see what it generates"""
    print("\n🧠 Testing AI Agent Directly")
    print("=" * 50)
    
    # Import and test the agent directly
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from app.main_agent import ContentSyndicateAgent
        import asyncio
        
        async def test_agent():
            agent = ContentSyndicateAgent()
            result = await agent.quick_newsletter_generation(
                topic="AI and Machine Learning trends",
                sources=["reddit", "news"],
                target_audience="tech professionals"
            )
            
            print("📋 Agent Result Structure:")
            print(json.dumps(result, indent=2, default=str))
            
            return result
        
        result = asyncio.run(test_agent())
        return result
        
    except Exception as e:
        print(f"❌ Direct agent test failed: {str(e)}")
        return None

if __name__ == "__main__":
    success = test_end_to_end_workflow()
    
    if not success:
        print("\n🔍 Running direct AI agent test...")
        test_ai_agent_direct()
    
    print(f"\n{'✅ Test completed successfully!' if success else '❌ Test failed!'}")
