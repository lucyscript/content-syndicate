"""
User management routes for ContentSyndicate API
User profile, preferences, subscription management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User, Newsletter, Subscriber
from ..schemas import UserResponse, UserUpdate, PaginationParams
from ..auth import get_current_user, get_current_active_user

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile"""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
      # Update fields if provided
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.subscription_tier is not None:
        current_user.subscription_tier = user_update.subscription_tier
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.delete("/profile")
async def delete_user_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete current user's account"""
    
    # Soft delete by deactivating
    current_user.is_active = False
    db.commit()
    
    return {"message": "Account deactivated successfully"}

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    
    # Count newsletters
    newsletter_count = db.query(Newsletter).filter(
        Newsletter.user_id == current_user.id
    ).count()
    
    # Count subscribers
    subscriber_count = db.query(Subscriber).filter(
        Subscriber.user_id == current_user.id,
        Subscriber.is_active == True
    ).count()
    
    # Get recent newsletters
    recent_newsletters = db.query(Newsletter).filter(
        Newsletter.user_id == current_user.id
    ).order_by(Newsletter.created_at.desc()).limit(5).all()
    
    # Calculate average open rate
    newsletters_with_analytics = db.query(Newsletter).filter(
        Newsletter.user_id == current_user.id,
        Newsletter.open_rate.isnot(None)
    ).all()
    
    avg_open_rate = 0.0
    avg_click_rate = 0.0
    
    if newsletters_with_analytics:
        avg_open_rate = sum(n.open_rate or 0 for n in newsletters_with_analytics) / len(newsletters_with_analytics)
        avg_click_rate = sum(n.click_rate or 0 for n in newsletters_with_analytics) / len(newsletters_with_analytics)
    
    return {
        "newsletter_count": newsletter_count,
        "subscriber_count": subscriber_count,
        "avg_open_rate": round(avg_open_rate, 2),
        "avg_click_rate": round(avg_click_rate, 2),
        "recent_newsletters": [
            {
                "id": n.id,
                "title": n.title,
                "status": n.status,
                "created_at": n.created_at,
                "open_rate": n.open_rate
            }
            for n in recent_newsletters
        ]
    }

@router.get("/subscription")
async def get_subscription_info(current_user: User = Depends(get_current_active_user)):
    """Get current subscription information"""
    
    # Define subscription limits
    subscription_limits = {
        "free": {"newsletters_per_month": 2, "subscribers": 100, "content_sources": 2},
        "starter": {"newsletters_per_month": 5, "subscribers": 500, "content_sources": 5},
        "professional": {"newsletters_per_month": 20, "subscribers": 2000, "content_sources": 10},
        "enterprise": {"newsletters_per_month": -1, "subscribers": -1, "content_sources": -1}  # Unlimited
    }
    
    current_limits = subscription_limits.get(current_user.subscription_tier, subscription_limits["free"])
    
    return {
        "subscription_tier": current_user.subscription_tier,
        "limits": current_limits,
        "subscription_date": current_user.created_at,  # Placeholder
        "next_billing_date": None,  # TODO: Implement billing cycle tracking
        "is_active": current_user.is_active
    }

@router.put("/preferences")
async def update_user_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    
    current_user.preferences = preferences
    db.commit()
    
    return {"message": "Preferences updated successfully", "preferences": preferences}
