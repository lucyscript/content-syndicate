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
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class ContentSource(enum.Enum):
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
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.STARTER)
    stripe_customer_id = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    newsletters = relationship("Newsletter", back_populates="user")
    content_preferences = relationship("ContentPreference", back_populates="user")
    subscribers = relationship("Subscriber", back_populates="user")


class ContentPreference(Base):
    __tablename__ = "content_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_source = Column(Enum(ContentSource), nullable=False)
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
    scheduled_for = Column(DateTime)  # Alternative field name for scheduling
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
    source_type = Column(Enum(ContentSource), nullable=False)
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
