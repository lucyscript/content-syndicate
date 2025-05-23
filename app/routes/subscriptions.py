"""
Subscription management routes for ContentSyndicate API
Subscriber management, email lists, subscription tiers
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..database import get_db
from ..models import User, Subscriber
from ..schemas import (
    SubscriberCreate, SubscriberResponse,
    PaginationParams, PaginatedResponse
)
from ..auth import get_current_active_user

router = APIRouter()

@router.post("/subscribers", response_model=SubscriberResponse, status_code=status.HTTP_201_CREATED)
async def add_subscriber(
    subscriber_data: SubscriberCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a new subscriber"""
    
    # Check subscription limits
    subscription_limits = {
        "free": 100,
        "starter": 500,
        "professional": 2000,
        "enterprise": -1  # Unlimited
    }
    
    limit = subscription_limits.get(current_user.subscription_tier, 100)
    if limit != -1:
        current_count = db.query(Subscriber).filter(
            Subscriber.user_id == current_user.id,
            Subscriber.is_active == True
        ).count()
        
        if current_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Subscriber limit reached ({limit}). Upgrade to add more subscribers."
            )
    
    # Check if subscriber already exists
    existing_subscriber = db.query(Subscriber).filter(
        Subscriber.email == subscriber_data.email,
        Subscriber.user_id == current_user.id
    ).first()
    
    if existing_subscriber:
        if existing_subscriber.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already subscribed"
            )
        else:
            # Reactivate if previously unsubscribed
            existing_subscriber.is_active = True
            existing_subscriber.subscribed_at = datetime.now()
            existing_subscriber.unsubscribed_at = None
            db.commit()
            db.refresh(existing_subscriber)
            return existing_subscriber
    
    # Create new subscriber
    db_subscriber = Subscriber(
        user_id=current_user.id,
        email=subscriber_data.email,
        name=subscriber_data.name,
        is_active=True,
        subscribed_at=datetime.now(),
        preferences={}
    )
    
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    
    return db_subscriber

@router.get("/subscribers", response_model=List[SubscriberResponse])
async def get_subscribers(
    pagination: PaginationParams = Depends(),
    active_only: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get subscribers with pagination"""
    
    skip = (pagination.page - 1) * pagination.limit
    
    query = db.query(Subscriber).filter(Subscriber.user_id == current_user.id)
    
    if active_only:
        query = query.filter(Subscriber.is_active == True)
    
    subscribers = query.order_by(
        Subscriber.subscribed_at.desc()
    ).offset(skip).limit(pagination.limit).all()
    
    return subscribers

@router.get("/subscribers/{subscriber_id}", response_model=SubscriberResponse)
async def get_subscriber(
    subscriber_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific subscriber"""
    
    subscriber = db.query(Subscriber).filter(
        Subscriber.id == subscriber_id,
        Subscriber.user_id == current_user.id
    ).first()
    
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found"
        )
    
    return subscriber

@router.put("/subscribers/{subscriber_id}", response_model=SubscriberResponse)
async def update_subscriber(
    subscriber_id: int,
    subscriber_update: SubscriberCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update subscriber information"""
    
    subscriber = db.query(Subscriber).filter(
        Subscriber.id == subscriber_id,
        Subscriber.user_id == current_user.id
    ).first()
    
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found"
        )
    
    # Update fields
    if subscriber_update.email != subscriber.email:
        # Check if new email already exists
        existing = db.query(Subscriber).filter(
            Subscriber.email == subscriber_update.email,
            Subscriber.user_id == current_user.id,
            Subscriber.id != subscriber_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        subscriber.email = subscriber_update.email
    
    subscriber.name = subscriber_update.name
    
    db.commit()
    db.refresh(subscriber)
    
    return subscriber

@router.delete("/subscribers/{subscriber_id}")
async def remove_subscriber(
    subscriber_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove (unsubscribe) a subscriber"""
    
    subscriber = db.query(Subscriber).filter(
        Subscriber.id == subscriber_id,
        Subscriber.user_id == current_user.id
    ).first()
    
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found"
        )
    
    # Soft delete - mark as inactive
    subscriber.is_active = False
    subscriber.unsubscribed_at = datetime.now()
    
    db.commit()
    
    return {"message": "Subscriber removed successfully"}

@router.post("/subscribers/bulk-import")
async def bulk_import_subscribers(
    subscribers: List[SubscriberCreate],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Bulk import subscribers from a list"""
    
    # Check subscription limits
    subscription_limits = {
        "free": 100,
        "starter": 500,
        "professional": 2000,
        "enterprise": -1  # Unlimited
    }
    
    limit = subscription_limits.get(current_user.subscription_tier, 100)
    current_count = db.query(Subscriber).filter(
        Subscriber.user_id == current_user.id,
        Subscriber.is_active == True
    ).count()
    
    if limit != -1 and (current_count + len(subscribers)) > limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Bulk import would exceed subscriber limit ({limit}). Current: {current_count}, Trying to add: {len(subscribers)}"
        )
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    errors = []
    
    for subscriber_data in subscribers:
        try:
            # Check if subscriber already exists
            existing = db.query(Subscriber).filter(
                Subscriber.email == subscriber_data.email,
                Subscriber.user_id == current_user.id
            ).first()
            
            if existing:
                if existing.is_active:
                    skipped_count += 1
                    continue
                else:
                    # Reactivate
                    existing.is_active = True
                    existing.subscribed_at = datetime.now()
                    existing.unsubscribed_at = None
                    existing.name = subscriber_data.name
                    updated_count += 1
            else:
                # Create new
                new_subscriber = Subscriber(
                    user_id=current_user.id,
                    email=subscriber_data.email,
                    name=subscriber_data.name,
                    is_active=True,
                    subscribed_at=datetime.now(),
                    preferences={}
                )
                db.add(new_subscriber)
                added_count += 1
                
        except Exception as e:
            errors.append(f"Error with {subscriber_data.email}: {str(e)}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk import failed: {str(e)}"
        )
    
    return {
        "message": "Bulk import completed",
        "added": added_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "errors": errors,
        "total_processed": len(subscribers)
    }

@router.get("/subscribers/export")
async def export_subscribers(
    format: str = "csv",
    active_only: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export subscribers list"""
    
    query = db.query(Subscriber).filter(Subscriber.user_id == current_user.id)
    
    if active_only:
        query = query.filter(Subscriber.is_active == True)
    
    subscribers = query.order_by(Subscriber.subscribed_at.desc()).all()
    
    if format == "csv":
        # Return CSV data
        csv_data = "email,name,subscribed_at,status\n"
        for sub in subscribers:
            status = "active" if sub.is_active else "unsubscribed"
            csv_data += f"{sub.email},{sub.name or ''},{sub.subscribed_at},{status}\n"
        
        return {
            "format": "csv",
            "data": csv_data,
            "count": len(subscribers)
        }
    else:
        # Return JSON
        return {
            "format": "json",
            "data": [
                {
                    "email": sub.email,
                    "name": sub.name,
                    "subscribed_at": sub.subscribed_at,
                    "is_active": sub.is_active,
                    "unsubscribed_at": sub.unsubscribed_at
                }
                for sub in subscribers
            ],
            "count": len(subscribers)
        }

@router.get("/stats")
async def get_subscription_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get subscription statistics"""
    
    # Total subscribers
    total_active = db.query(Subscriber).filter(
        Subscriber.user_id == current_user.id,
        Subscriber.is_active == True
    ).count()
    
    total_inactive = db.query(Subscriber).filter(
        Subscriber.user_id == current_user.id,
        Subscriber.is_active == False
    ).count()
    
    # Growth in last 30 days
    from datetime import timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    recent_subscribers = db.query(Subscriber).filter(
        Subscriber.user_id == current_user.id,
        Subscriber.subscribed_at >= thirty_days_ago,
        Subscriber.is_active == True
    ).count()
    
    recent_unsubscribes = db.query(Subscriber).filter(
        Subscriber.user_id == current_user.id,
        Subscriber.unsubscribed_at >= thirty_days_ago
    ).count()
    
    # Subscription limits
    subscription_limits = {
        "free": 100,
        "starter": 500,
        "professional": 2000,
        "enterprise": -1
    }
    
    limit = subscription_limits.get(current_user.subscription_tier, 100)
    usage_percentage = (total_active / limit * 100) if limit != -1 else 0
    
    return {
        "total_active_subscribers": total_active,
        "total_unsubscribed": total_inactive,
        "recent_growth": recent_subscribers,
        "recent_unsubscribes": recent_unsubscribes,
        "net_growth": recent_subscribers - recent_unsubscribes,
        "subscription_limit": limit,
        "usage_percentage": round(usage_percentage, 1) if limit != -1 else None,
        "churn_rate": round((recent_unsubscribes / total_active * 100) if total_active > 0 else 0, 2)
    }

@router.post("/subscribers/{subscriber_id}/preferences")
async def update_subscriber_preferences(
    subscriber_id: int,
    preferences: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update subscriber preferences"""
    
    subscriber = db.query(Subscriber).filter(
        Subscriber.id == subscriber_id,
        Subscriber.user_id == current_user.id
    ).first()
    
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found"
        )
    
    subscriber.preferences = preferences
    db.commit()
    
    return {"message": "Preferences updated successfully", "preferences": preferences}
