#!/usr/bin/env python3
"""
Debug script to test content aggregation step by step
"""

import asyncio
import json
from app.main_agent import ContentSyndicateAgent

async def debug_content_aggregation():
    """Debug content aggregation step by step"""
    print("🔍 Debug: Content Aggregation")
    print("="*50)
    
    agent = ContentSyndicateAgent()
    
    # Test config
    config = {
        "content_sources": ["reddit"],
        "topic": "AI technology",
        "target_audience": "tech professionals",
        "reddit": {
            "subreddit": "technology",
            "sort": "hot",
            "limit": 5
        }
    }
    
    # Step 1: Test content aggregation
    print("1️⃣ Testing content aggregation...")
    content_data = await agent._aggregate_content(config)
    
    print(f"📊 Aggregation result:")
    print(f"   - Error: {content_data.get('error', 'None')}")
    print(f"   - Total items: {content_data.get('total_items', 0)}")
    print(f"   - Source results: {content_data.get('source_results', {})}")
    
    if content_data.get("sources"):
        print(f"   - First item preview: {content_data['sources'][0].get('title', 'No title')[:100]}...")
    
    # Step 2: Test content filtering
    print("\n2️⃣ Testing content filtering...")
    filtered_content = await agent._analyze_and_filter_content(content_data, config)
    print(f"📋 Filtered content: {len(filtered_content)} items")
    
    if filtered_content:
        print(f"   - First filtered item: {filtered_content[0].get('title', 'No title')[:100]}...")
    
    # Step 3: Test AI generation
    print("\n3️⃣ Testing AI newsletter generation...")
    newsletter_content = await agent._generate_newsletter_content(filtered_content, config)
    
    print(f"📝 Newsletter result:")
    print(f"   - Success: {newsletter_content.get('success', False)}")
    print(f"   - Error: {newsletter_content.get('error', 'None')}")
    
    if newsletter_content.get("content"):
        content = newsletter_content["content"]
        print(f"   - Full content length: {len(content.get('full_content', ''))}")
        print(f"   - Summary length: {len(content.get('summary', ''))}")
        print(f"   - Sections: {len(content.get('sections', []))}")
        
        if content.get('full_content'):
            print(f"   - Content preview: {content['full_content'][:200]}...")

if __name__ == "__main__":
    asyncio.run(debug_content_aggregation())
