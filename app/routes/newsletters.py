"""
Newsletter management routes for ContentSyndicate API
Create, manage, and distribute newsletters
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio

from ..database import get_db
from ..models import User, Newsletter, ContentSource, NewsletterStatus
from ..schemas import (
    NewsletterCreate, NewsletterUpdate, NewsletterResponse,
    ContentGenerationRequest, ContentGenerationResponse,
    PaginationParams
)
from ..auth import get_current_active_user, require_subscription
from ..main_agent import ContentSyndicateAgent

router = APIRouter()

# Initialize the main agent
agent = ContentSyndicateAgent()

@router.post("/", response_model=NewsletterResponse, status_code=status.HTTP_201_CREATED)
async def create_newsletter(
    newsletter_data: NewsletterCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new newsletter"""
    
    # Check subscription limits
    if current_user.subscription_tier == "free":
        # Free tier: 2 newsletters per month
        from datetime import datetime, timedelta
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_count = db.query(Newsletter).filter(
            Newsletter.user_id == current_user.id,
            Newsletter.created_at >= month_start
        ).count()
        
        if monthly_count >= 2:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Monthly newsletter limit reached. Upgrade to create more newsletters."
            )
      # Create newsletter
    db_newsletter = Newsletter(
        user_id=current_user.id,
        title=newsletter_data.title,
        subject_line=newsletter_data.subject_line,
        content_sources=newsletter_data.content_sources,
        target_audience=newsletter_data.target_audience,
        scheduled_for=newsletter_data.scheduled_for,
        content="",  # Will be generated
        status=NewsletterStatus.DRAFT
    )
    
    db.add(db_newsletter)
    db.commit()
    db.refresh(db_newsletter)
    
    return db_newsletter

@router.get("/", response_model=List[NewsletterResponse])
async def get_newsletters(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's newsletters with pagination"""
    
    skip = (pagination.page - 1) * pagination.limit
    
    newsletters = db.query(Newsletter).filter(
        Newsletter.user_id == current_user.id
    ).order_by(
        Newsletter.created_at.desc()
    ).offset(skip).limit(pagination.limit).all()
    
    return newsletters

@router.get("/{newsletter_id}", response_model=NewsletterResponse)
async def get_newsletter(
    newsletter_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific newsletter"""
    
    newsletter = db.query(Newsletter).filter(
        Newsletter.id == newsletter_id,
        Newsletter.user_id == current_user.id
    ).first()
    
    if not newsletter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Newsletter not found"
        )
    
    return newsletter

@router.put("/{newsletter_id}", response_model=NewsletterResponse)
async def update_newsletter(
    newsletter_id: int,
    newsletter_update: NewsletterUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a newsletter"""
    
    newsletter = db.query(Newsletter).filter(
        Newsletter.id == newsletter_id,
        Newsletter.user_id == current_user.id
    ).first()
    
    if not newsletter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Newsletter not found"
        )
    
    # Update fields
    if newsletter_update.title is not None:
        newsletter.title = newsletter_update.title
    if newsletter_update.subject_line is not None:
        newsletter.subject_line = newsletter_update.subject_line
    if newsletter_update.content is not None:
        newsletter.content = newsletter_update.content
    if newsletter_update.status is not None:
        newsletter.status = newsletter_update.status
    if newsletter_update.scheduled_for is not None:
        newsletter.scheduled_for = newsletter_update.scheduled_for
    
    db.commit()
    db.refresh(newsletter)
    
    return newsletter

@router.delete("/{newsletter_id}")
async def delete_newsletter(
    newsletter_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a newsletter"""
    
    newsletter = db.query(Newsletter).filter(
        Newsletter.id == newsletter_id,
        Newsletter.user_id == current_user.id
    ).first()
    
    if not newsletter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Newsletter not found"
        )
    
    # Don't delete sent newsletters, just mark as inactive
    if newsletter.status == "sent":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete sent newsletters"
        )
    
    db.delete(newsletter)
    db.commit()
    
    return {"message": "Newsletter deleted successfully"}

@router.post("/{newsletter_id}/generate", response_model=ContentGenerationResponse)
async def generate_newsletter_content(
    newsletter_id: int,
    generation_request: ContentGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate content for a newsletter using AI"""
    
    newsletter = db.query(Newsletter).filter(
        Newsletter.id == newsletter_id,
        Newsletter.user_id == current_user.id
    ).first()
    
    if not newsletter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Newsletter not found"
        )
    
    try:        # Use the main agent to generate content
        start_time = datetime.now()
        result = await agent.quick_newsletter_generation(
            topic=generation_request.topic or newsletter.title,
            sources=generation_request.sources or newsletter.content_sources,
            target_audience=generation_request.audience or newsletter.target_audience
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
          # Extract content from the AI result
        newsletter_data = result.get("newsletter", {})
        content_text = ""
        subject_line = ""
        
        if newsletter_data.get("success"):
            content_data = newsletter_data.get("content", {})
            content_text = content_data.get("full_content", "")
            # Try to get subject line from AI result
            subject_lines = newsletter_data.get("subject_lines", [])
            if subject_lines:
                subject_line = subject_lines[0] if isinstance(subject_lines, list) else str(subject_lines)
        
        # Update newsletter with generated content
        newsletter.content = content_text
        newsletter.subject_line = subject_line or newsletter.subject_line
        
        db.commit()
        db.refresh(newsletter)
        
        # Convert sources_used from dict to list format expected by schema
        sources_used_dict = result.get("sources_used", {})
        sources_used_list = []
        for source_name, source_info in sources_used_dict.items():
            sources_used_list.append({
                "source": source_name,
                "status": source_info.get("status", "unknown"),
                "count": source_info.get("count", 0),
                "error": source_info.get("error", None)
            })
        
        return ContentGenerationResponse(
            content=content_text,
            title=newsletter.title,
            subject_line=subject_line,
            sources_used=sources_used_list,
            generation_time=generation_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/{newsletter_id}/send")
async def send_newsletter(
    newsletter_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_subscription),
    db: Session = Depends(get_db)
):
    """Send newsletter to subscribers"""
    
    newsletter = db.query(Newsletter).filter(
        Newsletter.id == newsletter_id,
        Newsletter.user_id == current_user.id
    ).first()
    
    if not newsletter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Newsletter not found"
        )
    
    if newsletter.status == "sent":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Newsletter already sent"
        )
    
    if not newsletter.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Newsletter content is empty. Generate content first."
        )
    
    # Update status to sending
    newsletter.status = "scheduled"
    db.commit()
    
    # Add background task to send emails
    background_tasks.add_task(send_newsletter_emails, newsletter_id, db)
    
    return {"message": "Newsletter scheduled for sending"}

async def send_newsletter_emails(newsletter_id: int, db: Session):
    """Background task to send newsletter emails"""
    try:
        # This would use the distribution MCP server
        # For now, just update the status
        newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
        if newsletter:
            newsletter.status = "sent"
            newsletter.sent_at = datetime.now()
            db.commit()
    except Exception as e:
        # Log error and update status
        newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
        if newsletter:
            newsletter.status = "failed"
            db.commit()

@router.get("/{newsletter_id}/preview")
async def preview_newsletter(
    newsletter_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Preview newsletter content"""
    
    newsletter = db.query(Newsletter).filter(
        Newsletter.id == newsletter_id,
        Newsletter.user_id == current_user.id
    ).first()
    
    if not newsletter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Newsletter not found"
        )
    
    # Return HTML preview
    return {
        "html_content": newsletter.content,
        "subject_line": newsletter.subject_line,
        "title": newsletter.title
    }
