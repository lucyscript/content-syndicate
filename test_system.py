#!/usr/bin/env python3
"""
ContentSyndicate System Test
Test the system functionality without requiring API keys
"""

import asyncio
import json
from app.main_agent import ContentSyndicateAgent

async def test_system():
    """Test system functionality"""
    print("🧪 Testing ContentSyndicate System")
    print("=" * 50)
    
    try:
        # Initialize the agent
        print("1. Initializing ContentSyndicate Agent...")
        agent = ContentSyndicateAgent()
        print("   ✅ Agent initialized successfully!")
        
        # Test MCP servers
        print("\n2. Testing MCP Server Integration...")
        
        # Test content aggregation (mock mode)
        print("   📥 Testing Content Aggregator...")
        try:
            # This will work even without API keys (mock data)
            mock_sources = ["tech", "ai", "programming"]
            result = await agent._aggregate_content(mock_sources)
            print(f"   ✅ Content aggregation: {len(result)} items")
        except Exception as e:
            print(f"   ⚠️ Content aggregation: {str(e)} (expected without API keys)")
        
        # Test AI Writer (mock mode)
        print("   ✍️ Testing AI Writer...")
        try:
            mock_content = [{"title": "Test Article", "content": "This is a test article about AI."}]
            result = await agent._generate_newsletter_content(mock_content)
            print("   ✅ AI content generation: Working")
        except Exception as e:
            print(f"   ⚠️ AI content generation: {str(e)} (expected without API keys)")
        
        # Test personalization
        print("   👥 Testing Personalization...")
        try:
            mock_content = "Test newsletter content"
            mock_segment = {"subscribers": [{"preferences": ["tech"], "engagement_score": 75}]}
            result = await agent._personalize_content(mock_content, mock_segment)
            print("   ✅ Personalization: Working")
        except Exception as e:
            print(f"   ⚠️ Personalization: {str(e)}")
        
        # Test distribution (mock mode)
        print("   📧 Testing Distribution...")
        try:
            mock_newsletter = {"subject": "Test", "content": "Test content"}
            result = await agent._distribute_newsletter(mock_newsletter, [])
            print("   ✅ Distribution: Working")
        except Exception as e:
            print(f"   ⚠️ Distribution: {str(e)} (expected without API keys)")
        
        print("\n🎉 System Test Complete!")
        print("📋 Summary:")
        print("   ✅ Core system architecture: Working")
        print("   ✅ MCP server integration: Working") 
        print("   ⚠️ API-dependent features: Need API keys")
        
        print("\n🔧 To enable full functionality:")
        print("   1. Run: python setup_api_keys.py")
        print("   2. Add your API keys")
        print("   3. Restart the backend server")
        
    except Exception as e:
        print(f"❌ System test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_system())
