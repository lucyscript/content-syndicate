"""
Celery tasks for ContentSyndicate
Background tasks for content processing, syndication, and analytics
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from celery import shared_task
from sqlalchemy.orm import Session

from .database import get_db_session
from .models import User, ContentSource, Newsletter, NewsletterAnalytics

logger = logging.getLogger(__name__)

@shared_task
def process_content_sources():
    """Process and analyze content from various sources"""
    try:
        db = next(get_db_session())
        
        # Get recent content sources for processing
        content_sources = db.query(ContentSource).filter(
            ContentSource.scraped_at >= datetime.utcnow() - timedelta(hours=24)
        ).limit(10).all()
        
        processed_count = 0
        for content in content_sources:
            try:
                # Process content (sentiment analysis, keyword extraction, etc.)
                # This would integrate with AI services
                if content.sentiment_score is None:
                    content.sentiment_score = 50  # Placeholder - would use actual AI processing
                if content.relevance_score is None:
                    content.relevance_score = 75  # Placeholder - would use actual AI processing
                
                db.commit()
                processed_count += 1
                logger.info(f"Processed content source: {content.id}")
            except Exception as e:
                logger.error(f"Error processing content source {content.id}: {str(e)}")
        
        db.close()
        return f"Processed {processed_count} content sources"
    except Exception as e:
        logger.error(f"Error in process_content_sources task: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def send_scheduled_newsletters():
    """Send newsletters that are scheduled for delivery"""
    try:
        db = next(get_db_session())
        now = datetime.utcnow()
        
        # Get newsletters scheduled for sending
        newsletters = db.query(Newsletter).filter(
            Newsletter.status.in_(["ready"]),
            Newsletter.scheduled_send_time <= now
        ).all()
        
        sent_count = 0
        for newsletter in newsletters:
            try:
                # Here you would integrate with email service (SendGrid, etc.)
                # For now, just mark as sent
                newsletter.status = "sent"
                newsletter.sent_at = now
                
                # Get subscriber count for this user
                user = db.query(User).filter(User.id == newsletter.user_id).first()
                if user:
                    newsletter.recipient_count = len(user.subscribers) if user.subscribers else 0
                
                db.commit()
                sent_count += 1
                logger.info(f"Sent newsletter: {newsletter.id}")
            except Exception as e:
                logger.error(f"Error sending newsletter {newsletter.id}: {str(e)}")
                newsletter.status = "failed"
                db.commit()
        
        db.close()
        return f"Sent {sent_count} newsletters"
    except Exception as e:
        logger.error(f"Error in send_scheduled_newsletters task: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def generate_newsletter_content(newsletter_id: int):
    """Generate content for a newsletter using AI"""
    try:
        db = next(get_db_session())
        newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
        
        if not newsletter:
            return f"Newsletter {newsletter_id} not found"
        
        # Here you would integrate with AI content generation
        # For now, just create basic content
        if not newsletter.content:
            newsletter.content = f"Generated content for newsletter: {newsletter.title}"
            newsletter.html_content = f"<h1>{newsletter.title}</h1><p>Generated content for newsletter: {newsletter.title}</p>"
            newsletter.status = "ready"
            newsletter.updated_at = datetime.utcnow()
            
            db.commit()
        
        db.close()
        logger.info(f"Generated content for newsletter: {newsletter_id}")
        return f"Generated content for newsletter {newsletter_id}"
    except Exception as e:
        logger.error(f"Error generating content for newsletter {newsletter_id}: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def cleanup_old_analytics():
    """Clean up old analytics data (older than 90 days)"""
    try:
        db = next(get_db_session())
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Delete old newsletter analytics records
        deleted_count = db.query(NewsletterAnalytics).filter(
            NewsletterAnalytics.created_at < cutoff_date
        ).delete()
        
        db.commit()
        db.close()
        
        logger.info(f"Cleaned up {deleted_count} old analytics records")
        return f"Cleaned up {deleted_count} records"
    except Exception as e:
        logger.error(f"Error in cleanup_old_analytics task: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def update_content_metrics():
    """Update metrics for content sources"""
    try:
        db = next(get_db_session())
        
        # Update relevance scores for recent content
        recent_content = db.query(ContentSource).filter(
            ContentSource.scraped_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        updated_count = 0
        for content in recent_content:
            try:
                # Update metrics (this would integrate with analytics APIs)
                # Placeholder logic
                if content.engagement_metrics is None:
                    content.engagement_metrics = {"views": 100, "likes": 10, "shares": 5}
                    updated_count += 1
                
                db.commit()
            except Exception as e:
                logger.error(f"Error updating metrics for content {content.id}: {str(e)}")
        
        db.close()
        logger.info(f"Updated metrics for {updated_count} content sources")
        return f"Updated metrics for {updated_count} content sources"
    except Exception as e:
        logger.error(f"Error in update_content_metrics task: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def generate_analytics_report(user_id: int, report_type: str = "weekly"):
    """Generate analytics report for a user"""
    try:
        db = next(get_db_session())
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return f"User {user_id} not found"
        
        # Generate basic analytics report
        newsletter_count = db.query(Newsletter).filter(Newsletter.user_id == user_id).count()
        sent_newsletters = db.query(Newsletter).filter(
            Newsletter.user_id == user_id,
            Newsletter.status == "sent"
        ).count()
        
        report = {
            "user_id": user_id,
            "report_type": report_type,
            "newsletter_count": newsletter_count,
            "sent_newsletters": sent_newsletters,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        db.close()
        logger.info(f"Generated {report_type} analytics report for user {user_id}")
        return report
    except Exception as e:
        logger.error(f"Error generating analytics report for user {user_id}: {str(e)}")
        return f"Error: {str(e)}"

# Health check task
@shared_task
def health_check():
    """Simple health check task to verify Celery is working"""
    try:
        db = next(get_db_session())
        user_count = db.query(User).count()
        db.close()
        
        result = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "user_count": user_count
        }
        logger.info("Health check completed successfully")
        return result
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}
