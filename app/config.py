"""
Configuration settings for ContentSyndicate
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys - Optional for development
    gemini_api_key: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    news_api_key: Optional[str] = None
    
    # Social Media APIs
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "ContentSyndicate/1.0"
    
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
      # Database - Use SQLite for development by default
    database_url: str = "sqlite:///./contentsyndicate.db"
    redis_url: str = "redis://localhost:6379"
    
    # Application
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    environment: str = "development"
    debug: bool = True
    allowed_origins: list = ["http://localhost:3001"] # Allow only the frontend origin
    
    # Email
    from_email: str = "noreply@contentsyndicate.com"
    from_name: str = "ContentSyndicate"
    
    # Content Generation
    max_content_sources: int = 10
    newsletter_generation_timeout: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
