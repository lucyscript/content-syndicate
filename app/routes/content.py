"""
Content management routes for ContentSyndicate API
Content sources, trending content, content curation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import User, ContentSource
from ..schemas import (
    ContentSourceCreate, ContentSourceResponse,
    PaginationParams
)
from ..auth import get_current_active_user
from ..mcp_servers.content_aggregator import ContentAggregatorServer

router = APIRouter()

# Initialize content aggregator
content_aggregator = ContentAggregatorServer()

@router.post("/sources", response_model=ContentSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_content_source(
    source_data: ContentSourceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new content source"""
    
    # Check subscription limits
    subscription_limits = {
        "free": 2,
        "starter": 5,
        "professional": 10,
        "enterprise": -1  # Unlimited
    }
    
    limit = subscription_limits.get(current_user.subscription_tier, 2)
    if limit != -1:
        current_count = db.query(ContentSource).filter(
            ContentSource.user_id == current_user.id,
            ContentSource.is_active == True
        ).count()
        
        if current_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Content source limit reached ({limit}). Upgrade to add more sources."
            )
    
    # Create content source
    db_source = ContentSource(
        user_id=current_user.id,
        platform=source_data.platform,
        query=source_data.query,
        keywords=source_data.keywords,
        filters=source_data.filters,
        is_active=True
    )
    
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    
    return db_source

@router.get("/sources", response_model=List[ContentSourceResponse])
async def get_content_sources(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's content sources"""
    
    sources = db.query(ContentSource).filter(
        ContentSource.user_id == current_user.id
    ).order_by(ContentSource.created_at.desc()).all()
    
    return sources

@router.put("/sources/{source_id}", response_model=ContentSourceResponse)
async def update_content_source(
    source_id: int,
    source_update: ContentSourceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a content source"""
    
    source = db.query(ContentSource).filter(
        ContentSource.id == source_id,
        ContentSource.user_id == current_user.id
    ).first()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content source not found"
        )
    
    # Update fields
    source.platform = source_update.platform
    source.query = source_update.query
    source.keywords = source_update.keywords
    source.filters = source_update.filters
    
    db.commit()
    db.refresh(source)
    
    return source

@router.delete("/sources/{source_id}")
async def delete_content_source(
    source_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a content source"""
    
    source = db.query(ContentSource).filter(
        ContentSource.id == source_id,
        ContentSource.user_id == current_user.id
    ).first()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content source not found"
        )
    
    # Soft delete
    source.is_active = False
    db.commit()
    
    return {"message": "Content source deleted successfully"}

@router.get("/trending")
async def get_trending_content(
    platform: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user)
):
    """Get trending content from various platforms"""
    
    try:
        # Default platforms if none specified
        platforms = [platform] if platform else ["reddit", "twitter", "news"]
        
        trending_content = []
        
        for p in platforms:
            try:
                if p == "reddit":
                    content = await content_aggregator.fetch_reddit_content(
                        subreddit="technology",
                        limit=limit // len(platforms)
                    )
                elif p == "twitter":
                    content = await content_aggregator.fetch_twitter_content(
                        query="trending tech",
                        count=limit // len(platforms)
                    )
                elif p == "news":
                    content = await content_aggregator.fetch_news_content(
                        query="technology",
                        page_size=limit // len(platforms)
                    )
                else:
                    continue
                
                trending_content.extend(content)
                
            except Exception as e:
                # Log error but continue with other platforms
                print(f"Error fetching {p} content: {e}")
                continue
        
        return {
            "content": trending_content[:limit],
            "total": len(trending_content),
            "timestamp": datetime.now(),
            "platforms": platforms
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trending content: {str(e)}"
        )

@router.post("/analyze")
async def analyze_content(
    content_url: str,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze a piece of content for relevance and engagement"""
    
    try:
        # Use content aggregator to scrape and analyze
        analysis = await content_aggregator.scrape_web_content(content_url)
        
        # Add basic sentiment and engagement prediction
        # This could be enhanced with more sophisticated AI analysis
        
        word_count = len(analysis.get("content", "").split())
        
        # Simple scoring based on content length and keywords
        engagement_score = min(100, max(10, word_count / 10))
        
        tech_keywords = ["AI", "technology", "innovation", "startup", "digital"]
        relevance_score = sum(1 for keyword in tech_keywords 
                            if keyword.lower() in analysis.get("content", "").lower()) * 20
        
        return {
            "url": content_url,
            "title": analysis.get("title", ""),
            "word_count": word_count,
            "engagement_score": round(engagement_score, 1),
            "relevance_score": min(100, relevance_score),
            "sentiment": "positive",  # Placeholder
            "key_topics": analysis.get("key_topics", []),
            "analysis_timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to analyze content: {str(e)}"
        )

@router.get("/suggestions")
async def get_content_suggestions(
    topic: Optional[str] = None,
    audience: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get content suggestions based on user's sources and preferences"""
    
    # Get user's content sources
    user_sources = db.query(ContentSource).filter(
        ContentSource.user_id == current_user.id,
        ContentSource.is_active == True
    ).all()
    
    suggestions = []
    
    try:
        for source in user_sources:
            platform_content = []
            
            if source.platform == "reddit":
                platform_content = await content_aggregator.fetch_reddit_content(
                    subreddit=source.query,
                    limit=5
                )
            elif source.platform == "twitter":
                platform_content = await content_aggregator.fetch_twitter_content(
                    query=source.query,
                    count=5
                )
            elif source.platform == "news":
                platform_content = await content_aggregator.fetch_news_content(
                    query=source.query,
                    page_size=5
                )
            
            # Add source context to each suggestion
            for content in platform_content:
                content["source_id"] = source.id
                content["source_platform"] = source.platform
                suggestions.append(content)
        
        # Sort by relevance/engagement (placeholder algorithm)
        suggestions.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return {
            "suggestions": suggestions[:20],  # Top 20 suggestions
            "total_sources": len(user_sources),
            "generated_at": datetime.now(),
            "topic_filter": topic,
            "audience_filter": audience
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestions: {str(e)}"
        )

@router.get("/platforms")
async def get_supported_platforms():
    """Get list of supported content platforms"""
    
    platforms = [
        {
            "name": "reddit",
            "display_name": "Reddit",
            "description": "Subreddits and trending posts",
            "requires_auth": False,
            "sample_query": "technology"
        },
        {
            "name": "twitter",
            "display_name": "Twitter/X",
            "description": "Tweets and trending topics",
            "requires_auth": True,
            "sample_query": "AI technology"
        },
        {
            "name": "news",
            "display_name": "News APIs",
            "description": "Latest news articles",
            "requires_auth": True,
            "sample_query": "artificial intelligence"
        },
        {
            "name": "rss",
            "display_name": "RSS Feeds",
            "description": "RSS/Atom feed content",
            "requires_auth": False,
            "sample_query": "https://feeds.example.com/tech.xml"
        }
    ]
    
    return {"platforms": platforms}
