"""
Content Aggregator MCP Server
Fetches trending content from various APIs (Reddit, Twitter, News, etc.)
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import praw
import tweepy
import requests
from bs4 import BeautifulSoup
import feedparser

from mcp.server.fastmcp import FastMCP
from ..config import settings
from ..models import ContentSource


class ContentAggregatorServer:
    def __init__(self):
        self.mcp = FastMCP("content-aggregator")
        self._setup_clients()
        self._register_tools()
    
    def _setup_clients(self):
        """Initialize API clients"""
        # Reddit client
        if settings.reddit_client_id and settings.reddit_client_secret:
            self.reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent
            )
        else:
            self.reddit = None
        
        # Twitter client
        if settings.twitter_bearer_token:
            self.twitter = tweepy.Client(bearer_token=settings.twitter_bearer_token)
        else:
            self.twitter = None
    
    async def fetch_reddit_content(
        self,
        subreddit: str = "all",
        sort: str = "hot",
        limit: int = 10,
        time_filter: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        Fetch trending content from Reddit
        
        Args:
            subreddit: Subreddit name (default: "all")
            sort: Sort method (hot, new, top, rising)
            limit: Number of posts to fetch
            time_filter: Time filter for top posts (hour, day, week, month, year, all)
        """
        if not self.reddit:
            return {"error": "Reddit API not configured"}
        
        try:
            sub = self.reddit.subreddit(subreddit)
            
            if sort == "hot":
                posts = sub.hot(limit=limit)
            elif sort == "new":
                posts = sub.new(limit=limit)
            elif sort == "top":
                posts = sub.top(time_filter=time_filter, limit=limit)
            elif sort == "rising":
                posts = sub.rising(limit=limit)
            else:
                posts = sub.hot(limit=limit)
            
            content = []
            for post in posts:
                content.append({
                    "id": post.id,
                    "title": post.title,
                    "url": post.url,
                    "content": post.selftext if post.selftext else "",
                    "author": str(post.author) if post.author else "Unknown",
                    "score": post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comments": post.num_comments,
                    "created_utc": datetime.fromtimestamp(post.created_utc),
                    "subreddit": post.subreddit.display_name,
                    "permalink": f"https://reddit.com{post.permalink}",
                    "source_type": "reddit"
                })
            
            return content
            
        except Exception as e:
            return {"error": f"Failed to fetch Reddit content: {str(e)}"}

    async def fetch_twitter_content(
        self,
        query: str = "",
        max_results: int = 10,
        tweet_fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch trending content from Twitter
        
        Args:
            query: Search query (empty for trending)
            max_results: Number of tweets to fetch
            tweet_fields: Additional tweet fields to include
        """
        if not self.twitter:
            return {"error": "Twitter API not configured"}
        
        try:
            if not tweet_fields:
                tweet_fields = ["created_at", "author_id", "public_metrics", "context_annotations"]
            
            if query:
                tweets = self.twitter.search_recent_tweets(
                    query=query,
                    max_results=max_results,
                    tweet_fields=tweet_fields
                )
            else:
                # Get trending topics if no query provided
                trends = self.twitter.get_trending_topics()
                if trends and trends.data:
                    # Use first trending topic as query
                    query = trends.data[0].name
                    tweets = self.twitter.search_recent_tweets(
                        query=query,
                        max_results=max_results,
                        tweet_fields=tweet_fields
                    )
                else:
                    return {"error": "No trending topics found"}
            
            if not tweets.data:
                return []
            
            content = []
            for tweet in tweets.data:
                content.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "author_id": tweet.author_id,
                    "created_at": tweet.created_at,
                    "retweet_count": tweet.public_metrics.get("retweet_count", 0),
                    "like_count": tweet.public_metrics.get("like_count", 0),
                    "reply_count": tweet.public_metrics.get("reply_count", 0),
                    "quote_count": tweet.public_metrics.get("quote_count", 0),
                    "url": f"https://twitter.com/i/status/{tweet.id}",
                    "source_type": "twitter"
                })
            
            return content
            
        except Exception as e:
            return {"error": f"Failed to fetch Twitter content: {str(e)}"}

    async def fetch_news_content(
        self,
        api_key: str = "",
        query: str = "",
        sources: str = "",
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fetch news content from News API
        
        Args:
            api_key: News API key
            query: Search query
            sources: Comma-separated news sources
            language: Language code
            sort_by: Sort method (relevancy, popularity, publishedAt)
            page_size: Number of articles
        """
        if not api_key:
            api_key = settings.news_api_key or ""
            
        if not api_key:
            return {"error": "News API key required"}
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "apiKey": api_key,
                "language": language,
                "sortBy": sort_by,
                "pageSize": page_size
            }
            
            if query:
                params["q"] = query
            if sources:
                params["sources"] = sources
            else:
                # Default to trending topics if no specific sources
                params["q"] = "trending OR viral OR breaking"
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] != "ok":
                return {"error": f"News API error: {data.get('message', 'Unknown error')}"}
            
            content = []
            for article in data.get("articles", []):
                content.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "urlToImage": article.get("urlToImage", ""),
                    "publishedAt": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "author": article.get("author", ""),
                    "source_type": "news_api"
                })
            
            return content
            
        except Exception as e:
            return {"error": f"Failed to fetch news content: {str(e)}"}

    async def fetch_rss_content(
        self,
        feed_url: str,
        max_entries: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fetch content from RSS feed
        
        Args:
            feed_url: RSS feed URL
            max_entries: Maximum number of entries to fetch
        """
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                return {"error": f"Invalid RSS feed: {feed_url}"}
            
            content = []
            for entry in feed.entries[:max_entries]:
                content.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "author": entry.get("author", ""),
                    "tags": [tag.term for tag in entry.get("tags", [])],
                    "source_type": "rss",
                    "feed_title": feed.feed.get("title", ""),
                    "feed_url": feed_url
                })
            
            return content
            
        except Exception as e:
            return {"error": f"Failed to fetch RSS content: {str(e)}"}

    def _register_tools(self):
        """Register MCP tools"""
        
        @self.mcp.tool()
        async def fetch_reddit_content_tool(
            subreddit: str = "all",
            sort: str = "hot",
            limit: int = 10,
            time_filter: str = "day"
        ) -> List[Dict[str, Any]]:
            return await self.fetch_reddit_content(subreddit, sort, limit, time_filter)

        @self.mcp.tool()
        async def fetch_twitter_content_tool(
            query: str = "",
            max_results: int = 10,
            tweet_fields: List[str] = None
        ) -> List[Dict[str, Any]]:
            return await self.fetch_twitter_content(query, max_results, tweet_fields)

        @self.mcp.tool()
        async def fetch_news_content_tool(
            api_key: str = "",
            query: str = "",
            sources: str = "",
            language: str = "en",
            sort_by: str = "publishedAt",
            page_size: int = 20
        ) -> List[Dict[str, Any]]:
            return await self.fetch_news_content(api_key, query, sources, language, sort_by, page_size)        @self.mcp.tool()
        async def fetch_rss_content_tool(
            feed_url: str,
            max_entries: int = 20
        ) -> List[Dict[str, Any]]:
            return await self.fetch_rss_content(feed_url, max_entries)


def create_content_aggregator_server():
    """Factory function to create content aggregator server"""
    return ContentAggregatorServer()
