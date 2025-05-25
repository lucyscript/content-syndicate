#!/usr/bin/env python3
import sys
import os
sys.path.append('app')
from app.database import SessionLocal
from app.models import Newsletter, NewsletterStatus
from datetime import datetime

db = SessionLocal()
try:
    # Create newsletters for user ID 9 (blabla@gmail.com)
    user_id = 9
    
    newsletters_to_create = [
        {
            "title": "Tech Weekly Digest",
            "description": "Latest technology trends and insights",
            "content": "Welcome to this week's tech digest...",
            "subject_line": "This Week in Tech: AI Breakthroughs",
            "target_audience": "Tech professionals"
        },
        {
            "title": "Startup Newsletter",
            "description": "Entrepreneurship and startup news",
            "content": "Featured startups this week...",
            "subject_line": "Startup Spotlight: Rising Stars",
            "target_audience": "Entrepreneurs"
        },
        {
            "title": "AI Innovation Weekly",
            "description": "Latest in artificial intelligence",
            "content": "AI developments and breakthroughs...",
            "subject_line": "AI Weekly: ChatGPT Competitors",
            "target_audience": "AI enthusiasts"
        }
    ]
    
    created_count = 0
    for nl_data in newsletters_to_create:
        newsletter = Newsletter(
            user_id=user_id,
            title=nl_data["title"],
            description=nl_data["description"],
            content=nl_data["content"],
            subject_line=nl_data["subject_line"],
            target_audience=nl_data["target_audience"],
            status=NewsletterStatus.DRAFT,
            created_at=datetime.utcnow()
        )
        db.add(newsletter)
        created_count += 1
    
    db.commit()
    print(f'✅ Created {created_count} newsletters for blabla@gmail.com')
    print('🔄 Refresh your browser page to see the newsletters!')
    
finally:
    db.close()
