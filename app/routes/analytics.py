"""
Analytics routes for ContentSyndicate API
Newsletter performance, engagement metrics, dashboard data
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import User, Newsletter, NewsletterAnalytics, Subscriber
from ..schemas import NewsletterAnalyticsResponse, DashboardMetrics
from ..auth import get_current_active_user

router = APIRouter()

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics and overview"""
    
    # Total newsletters
    total_newsletters = db.query(Newsletter).filter(
        Newsletter.user_id == current_user.id
    ).count()
    
    # Total active subscribers
    total_subscribers = db.query(Subscriber).filter(
        Subscriber.user_id == current_user.id,
        Subscriber.is_active == True
    ).count()
    
    # Average open and click rates
    newsletters_with_analytics = db.query(Newsletter).filter(
        Newsletter.user_id == current_user.id,
        Newsletter.open_rate.isnot(None)
    ).all()
    
    avg_open_rate = 0.0
    avg_click_rate = 0.0
    
    if newsletters_with_analytics:
        avg_open_rate = sum(n.open_rate or 0 for n in newsletters_with_analytics) / len(newsletters_with_analytics)
        avg_click_rate = sum(n.click_rate or 0 for n in newsletters_with_analytics) / len(newsletters_with_analytics)
    
    # Recent newsletters
    recent_newsletters = db.query(Newsletter).filter(
        Newsletter.user_id == current_user.id
    ).order_by(Newsletter.created_at.desc()).limit(5).all()
    
    # Trending content placeholder
    trending_content = [
        {
            "title": "AI Tools for Content Creation",
            "platform": "reddit",
            "engagement": 245,
            "source": "r/technology"
        },
        {
            "title": "Newsletter Marketing Trends 2025",
            "platform": "twitter",
            "engagement": 156,
            "source": "@marketingpro"
        }
    ]
    
    return DashboardMetrics(
        total_newsletters=total_newsletters,
        total_subscribers=total_subscribers,
        avg_open_rate=round(avg_open_rate, 2),
        avg_click_rate=round(avg_click_rate, 2),
        recent_newsletters=recent_newsletters,
        trending_content=trending_content
    )

@router.get("/newsletters/{newsletter_id}", response_model=NewsletterAnalyticsResponse)
async def get_newsletter_analytics(
    newsletter_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a specific newsletter"""
    
    # Verify newsletter ownership
    newsletter = db.query(Newsletter).filter(
        Newsletter.id == newsletter_id,
        Newsletter.user_id == current_user.id
    ).first()
    
    if not newsletter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Newsletter not found"
        )
    
    # Get or create analytics record
    analytics = db.query(NewsletterAnalytics).filter(
        NewsletterAnalytics.newsletter_id == newsletter_id
    ).first()
    
    if not analytics:
        # Create placeholder analytics if none exist
        analytics = NewsletterAnalytics(
            newsletter_id=newsletter_id,
            opens=0,
            clicks=0,
            unsubscribes=0,
            open_rate=0.0,
            click_rate=0.0,
            unsubscribe_rate=0.0
        )
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
    
    return analytics

@router.get("/performance")
async def get_performance_overview(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get performance overview for the last N days"""
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Get newsletters in the date range
    newsletters = db.query(Newsletter).filter(
        Newsletter.user_id == current_user.id,
        Newsletter.created_at >= start_date
    ).order_by(Newsletter.created_at.desc()).all()
    
    # Calculate metrics
    total_sent = len([n for n in newsletters if n.status == "sent"])
    total_opens = sum(n.open_rate or 0 for n in newsletters if n.open_rate) * total_sent / 100 if total_sent > 0 else 0
    total_clicks = sum(n.click_rate or 0 for n in newsletters if n.click_rate) * total_sent / 100 if total_sent > 0 else 0
    
    # Group by date for trend analysis
    daily_stats = {}
    for newsletter in newsletters:
        date_key = newsletter.created_at.date().isoformat()
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                "date": date_key,
                "newsletters_sent": 0,
                "total_opens": 0,
                "total_clicks": 0
            }
        
        if newsletter.status == "sent":
            daily_stats[date_key]["newsletters_sent"] += 1
            daily_stats[date_key]["total_opens"] += (newsletter.open_rate or 0) / 100
            daily_stats[date_key]["total_clicks"] += (newsletter.click_rate or 0) / 100
    
    return {
        "period_days": days,
        "total_newsletters_sent": total_sent,
        "total_opens": int(total_opens),
        "total_clicks": int(total_clicks),
        "avg_open_rate": round(sum(n.open_rate or 0 for n in newsletters) / len(newsletters) if newsletters else 0, 2),
        "avg_click_rate": round(sum(n.click_rate or 0 for n in newsletters) / len(newsletters) if newsletters else 0, 2),
        "daily_breakdown": list(daily_stats.values()),
        "top_performing": [
            {
                "id": n.id,
                "title": n.title,
                "open_rate": n.open_rate,
                "click_rate": n.click_rate,
                "sent_at": n.sent_at
            }
            for n in sorted(newsletters, key=lambda x: x.open_rate or 0, reverse=True)[:5]
            if n.status == "sent"
        ]
    }

@router.get("/subscribers")
async def get_subscriber_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get subscriber growth and engagement analytics"""
    
    # Total subscribers
    total_subscribers = db.query(Subscriber).filter(
        Subscriber.user_id == current_user.id,
        Subscriber.is_active == True
    ).count()
    
    # Subscriber growth over time (last 12 months)
    twelve_months_ago = datetime.now() - timedelta(days=365)
    monthly_growth = db.query(
        func.date_trunc('month', Subscriber.subscribed_at).label('month'),
        func.count(Subscriber.id).label('new_subscribers')
    ).filter(
        Subscriber.user_id == current_user.id,
        Subscriber.subscribed_at >= twelve_months_ago
    ).group_by('month').order_by('month').all()
    
    # Recent unsubscribes
    recent_unsubscribes = db.query(Subscriber).filter(
        Subscriber.user_id == current_user.id,
        Subscriber.is_active == False,
        Subscriber.unsubscribed_at >= datetime.now() - timedelta(days=7)
    ).count()
    
    # Engagement by subscriber segment (placeholder)
    engagement_segments = [
        {"segment": "Highly Engaged", "count": int(total_subscribers * 0.2), "avg_open_rate": 85.5},
        {"segment": "Moderately Engaged", "count": int(total_subscribers * 0.5), "avg_open_rate": 45.2},
        {"segment": "Low Engagement", "count": int(total_subscribers * 0.3), "avg_open_rate": 12.8}
    ]
    
    return {
        "total_active_subscribers": total_subscribers,
        "growth_last_month": len([g for g in monthly_growth if g.month >= datetime.now() - timedelta(days=30)]),
        "unsubscribes_last_week": recent_unsubscribes,
        "monthly_growth": [
            {
                "month": g.month.strftime("%Y-%m"),
                "new_subscribers": g.new_subscribers
            }
            for g in monthly_growth
        ],
        "engagement_segments": engagement_segments,
        "churn_rate": round((recent_unsubscribes / total_subscribers * 100) if total_subscribers > 0 else 0, 2)
    }

@router.get("/content-performance")
async def get_content_performance(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get performance analytics for different content types and topics"""
    
    # Get newsletters with analytics
    newsletters = db.query(Newsletter).filter(
        Newsletter.user_id == current_user.id,
        Newsletter.status == "sent",
        Newsletter.open_rate.isnot(None)
    ).order_by(Newsletter.open_rate.desc()).limit(limit).all()
    
    # Analyze content sources performance
    source_performance = {}
    for newsletter in newsletters:
        for source in newsletter.content_sources:
            if source not in source_performance:
                source_performance[source] = {
                    "source": source,
                    "newsletters": 0,
                    "avg_open_rate": 0,
                    "avg_click_rate": 0
                }
            
            source_performance[source]["newsletters"] += 1
            source_performance[source]["avg_open_rate"] += newsletter.open_rate or 0
            source_performance[source]["avg_click_rate"] += newsletter.click_rate or 0
    
    # Calculate averages
    for source in source_performance.values():
        if source["newsletters"] > 0:
            source["avg_open_rate"] = round(source["avg_open_rate"] / source["newsletters"], 2)
            source["avg_click_rate"] = round(source["avg_click_rate"] / source["newsletters"], 2)
    
    # Best performing newsletters
    best_performing = [
        {
            "id": n.id,
            "title": n.title,
            "open_rate": n.open_rate,
            "click_rate": n.click_rate,
            "sent_at": n.sent_at,
            "content_sources": n.content_sources
        }
        for n in newsletters
    ]
    
    return {
        "best_performing_newsletters": best_performing,
        "content_source_performance": list(source_performance.values()),
        "average_performance": {
            "open_rate": round(sum(n.open_rate or 0 for n in newsletters) / len(newsletters) if newsletters else 0, 2),
            "click_rate": round(sum(n.click_rate or 0 for n in newsletters) / len(newsletters) if newsletters else 0, 2)
        },
        "recommendations": [
            "Focus on content from high-performing sources",
            "Optimize subject lines for better open rates",
            "Include more interactive content for clicks"
        ]
    }

@router.post("/newsletters/{newsletter_id}/track")
async def track_newsletter_event(
    newsletter_id: int,
    event_type: str,  # "open", "click", "unsubscribe"
    subscriber_email: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Track newsletter events (opens, clicks, unsubscribes)"""
    
    # Verify newsletter ownership
    newsletter = db.query(Newsletter).filter(
        Newsletter.id == newsletter_id,
        Newsletter.user_id == current_user.id
    ).first()
    
    if not newsletter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Newsletter not found"
        )
    
    # Get or create analytics record
    analytics = db.query(NewsletterAnalytics).filter(
        NewsletterAnalytics.newsletter_id == newsletter_id
    ).first()
    
    if not analytics:
        analytics = NewsletterAnalytics(
            newsletter_id=newsletter_id,
            opens=0,
            clicks=0,
            unsubscribes=0,
            open_rate=0.0,
            click_rate=0.0,
            unsubscribe_rate=0.0
        )
        db.add(analytics)
    
    # Update metrics based on event type
    if event_type == "open":
        analytics.opens += 1
    elif event_type == "click":
        analytics.clicks += 1
    elif event_type == "unsubscribe":
        analytics.unsubscribes += 1
        
        # Also update subscriber status if email provided
        if subscriber_email:
            subscriber = db.query(Subscriber).filter(
                Subscriber.email == subscriber_email,
                Subscriber.user_id == current_user.id
            ).first()
            if subscriber:
                subscriber.is_active = False
                subscriber.unsubscribed_at = datetime.now()
    
    # Recalculate rates (assuming total sends = total subscribers)
    total_subscribers = db.query(Subscriber).filter(
        Subscriber.user_id == current_user.id,
        Subscriber.is_active == True
    ).count()
    
    if total_subscribers > 0:
        analytics.open_rate = (analytics.opens / total_subscribers) * 100
        analytics.click_rate = (analytics.clicks / total_subscribers) * 100
        analytics.unsubscribe_rate = (analytics.unsubscribes / total_subscribers) * 100
    
    db.commit()
    
    return {"message": f"Event '{event_type}' tracked successfully"}
