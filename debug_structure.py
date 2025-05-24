#!/usr/bin/env python3
"""
Debug script to check the exact structure returned by quick_newsletter_generation
"""

import asyncio
import json
from app.main_agent import ContentSyndicateAgent

async def debug_quick_generation_structure():
    """Debug the structure returned by quick_newsletter_generation"""
    print("🔍 Debug: Quick Newsletter Generation Structure")
    print("="*50)
    
    agent = ContentSyndicateAgent()
    
    result = await agent.quick_newsletter_generation(
        topic="AI Technology Trends",
        sources=["reddit"],
        target_audience="tech professionals"
    )
    
    print("📋 Full Result Structure:")
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(debug_quick_generation_structure())
