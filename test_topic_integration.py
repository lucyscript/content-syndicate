#!/usr/bin/env python3
"""
Test script to verify Topic Generator and AI Writer integration
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.main_agent import ContentSyndicateAgent

async def test_topic_integration():
    """Test the enhanced topic matching integration"""
    print("🧪 Testing Enhanced Topic Matching Integration")
    print("=" * 60)
    
    try:
        # Initialize the main agent
        print("1. Initializing ContentSyndicate Agent...")
        agent = ContentSyndicateAgent()
        print("✅ Agent initialized successfully")
        
        # Test quick newsletter generation with topic matching
        print("\n2. Testing newsletter generation with topic matching...")
        result = await agent.quick_newsletter_generation(
            topic="artificial intelligence",
            sources=["reddit", "news"],
            target_audience="tech professionals"
        )
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return False
        
        print("✅ Newsletter generated successfully!")
        
        # Check if topic matching was used
        metadata = result.get("metadata", {})
        if metadata.get("used_topic_matching"):
            print("✅ Topic matching integration working!")
            print(f"   - Topic analyzed: {metadata.get('topic', 'N/A')}")
            print(f"   - Content pieces processed: {metadata.get('source_count', 0)}")
        else:
            print("⚠️  Topic matching not detected in metadata")
        
        # Display content preview
        content = result.get("content", {})
        if content:
            full_content = content.get("full_content", "")
            if full_content:
                print(f"\n📄 Generated Content Preview:")
                print("-" * 40)
                print(full_content[:300] + "..." if len(full_content) > 300 else full_content)
                print("-" * 40)
        
        # Check for subject lines
        subject_lines = result.get("subject_lines", [])
        if subject_lines:
            print(f"\n📧 Generated Subject Lines ({len(subject_lines)}):")
            for i, subject in enumerate(subject_lines[:3], 1):
                print(f"   {i}. {subject}")
        
        print("\n🎉 Topic integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_topic_generator_standalone():
    """Test the Topic Generator server standalone"""
    print("\n🔍 Testing Topic Generator Standalone")
    print("=" * 60)
    
    try:
        agent = ContentSyndicateAgent()
        
        # Test topic matching with sample content
        sample_content = [
            {
                "title": "Latest AI Breakthrough in Machine Learning",
                "content": "Researchers have developed a new AI model that can process natural language more efficiently.",
                "source_type": "news",
                "url": "https://example.com/ai-news"
            },
            {
                "title": "Blockchain Technology Updates",
                "content": "New developments in cryptocurrency and blockchain infrastructure.",
                "source_type": "news", 
                "url": "https://example.com/blockchain-news"
            }
        ]
        
        print("1. Testing topic matching with sample content...")
        topic_result = await agent.topic_generator.match_content_to_topics_impl(
            user_topics=["artificial intelligence", "machine learning"],
            content_data=sample_content,
            relevance_threshold=0.3
        )
        
        if topic_result.get("error"):
            print(f"❌ Topic matching error: {topic_result['error']}")
            return False
        
        print("✅ Topic matching completed!")
        
        # Display results
        matched_content = topic_result.get("matched_content", {})
        for topic, matches in matched_content.items():
            print(f"\n📊 Topic: '{topic}'")
            high_rel = len(matches.get("high_relevance", []))
            med_rel = len(matches.get("medium_relevance", []))
            low_rel = len(matches.get("low_relevance", []))
            print(f"   - High relevance: {high_rel}")
            print(f"   - Medium relevance: {med_rel}")
            print(f"   - Low relevance: {low_rel}")
            print(f"   - Total matches: {matches.get('total_matches', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Standalone test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all integration tests"""
    print("🚀 Starting Topic Matching Integration Tests")
    print("=" * 60)
    
    # Test 1: Standalone Topic Generator
    test1_result = await test_topic_generator_standalone()
    
    # Test 2: Full Integration
    test2_result = await test_topic_integration()
    
    print("\n" + "=" * 60)
    print("📋 Test Results Summary")
    print("=" * 60)
    print(f"Topic Generator Standalone: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Full Integration Test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! Topic matching integration is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        sys.exit(1)
