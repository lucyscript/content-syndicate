"""
Database models for ContentSyndicate
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class SubscriptionTier(enum.Enum):
    CREATOR = "creator"
    PROFESSIONAL = "professional" 
    AGENCY = "agency"


class ContentType(enum.Enum):
    SOCIAL_MEDIA = "social_media"
    EMAIL_MARKETING = "email_marketing"
    BLOG_CONTENT = "blog_content"
    VIDEO_CONTENT = "video_content"
    BUSINESS_CONTENT = "business_content"


class ContentSubtype(enum.Enum):
    # Social Media
    TWITTER_POST = "twitter_post"
    TWITTER_THREAD = "twitter_thread"
    LINKEDIN_POST = "linkedin_post"
    LINKEDIN_ARTICLE = "linkedin_article"
    INSTAGRAM_CAPTION = "instagram_caption"
    INSTAGRAM_STORY = "instagram_story"
    TIKTOK_SCRIPT = "tiktok_script"
    FACEBOOK_POST = "facebook_post"
    
    # Email Marketing
    NEWSLETTER = "newsletter"
    EMAIL_SEQUENCE = "email_sequence"
    PROMOTIONAL_EMAIL = "promotional_email"
    
    # Blog Content
    BLOG_POST = "blog_post"
    GUEST_POST_PITCH = "guest_post_pitch"
    CONTENT_SERIES = "content_series"
    
    # Video Content
    YOUTUBE_SCRIPT = "youtube_script"
    PODCAST_SHOW_NOTES = "podcast_show_notes"
    VIDEO_AD_SCRIPT = "video_ad_script"
    
    # Business Content
    PRESS_RELEASE = "press_release"
    CASE_STUDY = "case_study"
    WHITE_PAPER = "white_paper"


class Platform(enum.Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"
    MEDIUM = "medium"
    MAILCHIMP = "mailchimp"
    CONVERTKIT = "convertkit"
    SUBSTACK = "substack"
    GHOST = "ghost"


class ContentStatus(enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class ContentSourceType(enum.Enum):
    REDDIT = "reddit"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    NEWS_API = "news_api"
    RSS = "rss"


class NewsletterStatus(enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    SENT = "sent"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.CREATOR)
    stripe_customer_id = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    newsletters = relationship("Newsletter", back_populates="user")
    content_items = relationship("ContentItem", back_populates="user")
    oauth_connections = relationship("OAuthConnection", back_populates="user")
    content_generations = relationship("ContentGeneration", back_populates="user")
    content_preferences = relationship("ContentPreference", back_populates="user")
    subscribers = relationship("Subscriber", back_populates="user")


# New Models for Content Syndicate Hub

class ContentItem(Base):
    """Universal content item that can be any type of content"""
    __tablename__ = "content_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content classification
    content_type = Column(Enum(ContentType), nullable=False)
    content_subtype = Column(Enum(ContentSubtype), nullable=False)
      # Basic content data
    title = Column(String, nullable=False)
    content = Column(Text)
    html_content = Column(Text)
    content_metadata = Column(JSON)  # Flexible field for content-specific data
    
    # AI generation data
    generation_prompt = Column(Text)
    content_sources = Column(JSON)
    target_audience = Column(String)
    tone = Column(String)
    length = Column(String)
    
    # Status and scheduling
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    scheduled_for = Column(DateTime)
    published_at = Column(DateTime)
    
    # Platform-specific versions
    platform_versions = Column(JSON)  # Different versions for different platforms
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="content_items")
    distributions = relationship("DistributionLog", back_populates="content_item")
    analytics = relationship("ContentAnalytics", back_populates="content_item")


class OAuthConnection(Base):
    """Store OAuth tokens for connected platforms"""
    __tablename__ = "oauth_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    platform = Column(Enum(Platform), nullable=False)
    platform_user_id = Column(String)  # Platform's user ID
    platform_username = Column(String)
    
    # OAuth tokens
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    token_expires_at = Column(DateTime)
    
    # Platform-specific data
    platform_data = Column(JSON)  # Store additional platform info
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="oauth_connections")


class DistributionLog(Base):
    """Track content distribution across platforms"""
    __tablename__ = "distribution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    oauth_connection_id = Column(Integer, ForeignKey("oauth_connections.id"), nullable=False)
    
    platform = Column(Enum(Platform), nullable=False)
    platform_post_id = Column(String)  # ID from the platform
    
    # Distribution data
    content_version = Column(Text)  # The actual content that was posted
    status = Column(String)  # success, failed, pending
    error_message = Column(Text)
    
    scheduled_for = Column(DateTime)
    published_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    content_item = relationship("ContentItem", back_populates="distributions")


class ContentAnalytics(Base):
    """Track performance analytics for content across platforms"""
    __tablename__ = "content_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    
    # Engagement metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    
    # Email-specific metrics
    opens = Column(Integer, default=0)
    open_rate = Column(Integer, default=0)
    click_rate = Column(Integer, default=0)
    
    # Platform-specific metrics
    platform_metrics = Column(JSON)
    
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    content_item = relationship("ContentItem", back_populates="analytics")


# Keep existing models for backward compatibility
class ContentPreference(Base):
    __tablename__ = "content_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_source = Column(Enum(ContentSourceType), nullable=False)
    source_config = Column(JSON)  # Store source-specific configuration
    keywords = Column(JSON)  # List of keywords/topics
    exclude_keywords = Column(JSON)  # List of words to exclude
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="content_preferences")


class Newsletter(Base):
    __tablename__ = "newsletters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    subject_line = Column(String)  # Email subject line
    content = Column(Text)
    html_content = Column(Text)
    status = Column(Enum(NewsletterStatus), default=NewsletterStatus.DRAFT)
    scheduled_send_time = Column(DateTime)
    scheduled_for = Column(DateTime, default=datetime.utcnow)  # Alternative field name for scheduling
    sent_at = Column(DateTime)
    recipient_count = Column(Integer, default=0)
    open_rate = Column(Integer, default=0)
    click_rate = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Content generation fields
    content_sources = Column(JSON)  # List of content sources to use
    target_audience = Column(String)  # Target audience description
    
    # Metadata for AI generation
    source_articles = Column(JSON)  # List of source articles used
    generation_prompt = Column(Text)
    personalization_data = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="newsletters")


class Subscriber(Base):
    __tablename__ = "subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    tags = Column(JSON)  # For segmentation
    preferences = Column(JSON)  # Content preferences
    subscription_date = Column(DateTime, default=datetime.utcnow)
    last_engagement = Column(DateTime)
    
    # Analytics
    total_opens = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    engagement_score = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="subscribers")


class ContentSource(Base):
    __tablename__ = "content_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(Enum(ContentSourceType), nullable=False)
    title = Column(String, nullable=False)
    url = Column(String)
    content = Column(Text)
    summary = Column(Text)
    author = Column(String)
    published_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    engagement_metrics = Column(JSON)  # likes, shares, comments
    keywords = Column(JSON)
    sentiment_score = Column(Integer)  # -100 to 100
    relevance_score = Column(Integer)  # 0 to 100
    
    # Source-specific data
    source_metadata = Column(JSON)


class NewsletterAnalytics(Base):
    __tablename__ = "newsletter_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    newsletter_id = Column(Integer, ForeignKey("newsletters.id"), nullable=False)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=False)
    
    # Engagement events
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    unsubscribed_at = Column(DateTime)
    
    # Click tracking
    clicked_links = Column(JSON)  # List of clicked URLs
    time_spent_reading = Column(Integer)  # seconds
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentGeneration(Base):
    """Track multi-format content generation sessions"""
    __tablename__ = "content_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generation_type = Column(String, nullable=False)  # "multi_format", "single_format", "repurpose"
    formats_generated = Column(JSON)  # List of formats generated
    input_data = Column(Text)  # JSON string of input parameters
    result_data = Column(Text)  # JSON string of generated content
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="content_generations")
