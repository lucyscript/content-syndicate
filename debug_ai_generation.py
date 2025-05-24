#!/usr/bin/env python3
"""
Debug script to test AI generation directly
"""

import asyncio
import json
from app.mcp_servers.ai_writer import create_ai_writer_server

async def debug_ai_generation():
    """Debug AI generation step by step"""
    print("🤖 Debug: AI Generation")
    print("="*50)
    
    ai_writer = create_ai_writer_server()
    
    # Sample content from Reddit
    sample_articles = [
        {
            "title": "German court rules cookie banners must offer 'reject all' button",
            "content": "A German court has ruled that cookie banners must include a 'reject all' button that is equally prominent to the 'accept all' button. This ruling affects how websites can implement cookie consent mechanisms.",
            "url": "https://example.com/cookie-ruling",
            "source_type": "reddit",
            "score": 1500
        },
        {
            "title": "AI Model Performance Breakthrough in 2025",
            "content": "New research shows significant improvements in AI model efficiency and accuracy, with 40% better performance on benchmark tests compared to 2024 models.",
            "url": "https://example.com/ai-breakthrough",
            "source_type": "reddit",
            "score": 2300
        }
    ]
    
    print(f"📝 Testing with {len(sample_articles)} sample articles...")
    
    try:
        # Test newsletter generation
        result = await ai_writer.generate_newsletter_content(
            source_articles=sample_articles,
            newsletter_topic="Technology and Privacy Updates",
            target_audience="tech professionals",
            tone="professional",
            length="medium"
        )
        
        print("\n🎯 AI Generation Result:")
        print(f"   - Success: {result.get('success', False)}")
        print(f"   - Error: {result.get('error', 'None')}")
        
        if result.get("content"):
            content = result["content"]
            print(f"\n📋 Content Structure:")
            for key, value in content.items():
                print(f"   - {key}: {len(str(value))} characters")
                if len(str(value)) > 0:
                    preview = str(value)[:100].replace('\n', ' ')
                    print(f"     Preview: {preview}...")
        
        # Show raw response if available
        if "metadata" in result:
            print(f"\n📊 Metadata: {result['metadata']}")
            
    except Exception as e:
        print(f"❌ Error during AI generation: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_ai_generation())
