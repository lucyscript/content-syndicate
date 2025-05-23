"""
Pydantic schemas for request/response models
Data validation and serialization for ContentSyndicate API
"""

from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class SubscriptionTier(str, Enum):
    free = "free"
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"

class NewsletterStatus(str, Enum):
    draft = "draft"
    scheduled = "scheduled"
    sent = "sent"
    failed = "failed"

class ContentType(str, Enum):
    article = "article"
    video = "video"
    tweet = "tweet"
    reddit_post = "reddit_post"
    other = "other"

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    subscription_tier: Optional[SubscriptionTier] = None

class UserResponse(UserBase):
    id: int
    subscription_tier: SubscriptionTier
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Newsletter schemas
class NewsletterBase(BaseModel):
    title: str
    subject_line: Optional[str] = None
    content_sources: List[str] = []
    target_audience: Optional[str] = None
    scheduled_for: Optional[datetime] = None

class NewsletterCreate(NewsletterBase):
    pass

class NewsletterUpdate(BaseModel):
    title: Optional[str] = None
    subject_line: Optional[str] = None
    content: Optional[str] = None
    status: Optional[NewsletterStatus] = None
    scheduled_for: Optional[datetime] = None

class NewsletterResponse(NewsletterBase):
    id: int
    user_id: int
    content: str
    status: NewsletterStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    open_rate: Optional[float] = None
    click_rate: Optional[float] = None
    
    class Config:
        from_attributes = True

# Content schemas
class ContentSourceBase(BaseModel):
    platform: str
    query: str
    keywords: List[str] = []
    filters: Dict[str, Any] = {}

class ContentSourceCreate(ContentSourceBase):
    pass

class ContentSourceResponse(ContentSourceBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Analytics schemas
class NewsletterAnalyticsResponse(BaseModel):
    newsletter_id: int
    opens: int
    clicks: int
    unsubscribes: int
    open_rate: float
    click_rate: float
    unsubscribe_rate: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class DashboardMetrics(BaseModel):
    total_newsletters: int
    total_subscribers: int
    avg_open_rate: float
    avg_click_rate: float
    recent_newsletters: List[NewsletterResponse]
    trending_content: List[Dict[str, Any]]

# Subscription schemas
class SubscriberBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class SubscriberCreate(SubscriberBase):
    pass

class SubscriberResponse(SubscriberBase):
    id: int
    user_id: int
    is_active: bool
    subscribed_at: datetime
    preferences: Dict[str, Any]
    
    class Config:
        from_attributes = True

# Content generation schemas
class ContentGenerationRequest(BaseModel):
    sources: List[str]
    topic: Optional[str] = None
    tone: Optional[str] = "professional"
    length: Optional[str] = "medium"
    audience: Optional[str] = None

class ContentGenerationResponse(BaseModel):
    content: str
    title: str
    subject_line: str
    sources_used: List[Dict[str, Any]]
    generation_time: float

# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = datetime.now()

# Pagination schemas
class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be >= 1')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int
