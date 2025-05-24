"""
ContentSyndicate Main Agent
Orchestrates all MCP servers to create personalized newsletters
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import google.generativeai as genai

from .config import settings
from .mcp_servers.content_aggregator import create_content_aggregator_server
from .mcp_servers.ai_writer import create_ai_writer_server
from .mcp_servers.personalization import create_personalization_server
from .mcp_servers.distribution import create_distribution_server
from .mcp_servers.analytics import create_analytics_server


class ContentSyndicateAgent:
    """
    Main agent that orchestrates the entire newsletter creation and distribution pipeline
    """
    
    def __init__(self):
        self.name = "ContentSyndicate Master Agent"
        self.version = "1.0.0"
        
        # Initialize Gemini AI
        genai.configure(api_key=settings.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Initialize MCP servers
        self.content_aggregator = create_content_aggregator_server()
        self.ai_writer = create_ai_writer_server()
        self.personalization = create_personalization_server()
        self.distribution = create_distribution_server()
        self.analytics = create_analytics_server()
        
        print(f"🤖 {self.name} v{self.version} initialized successfully!")
    
    async def create_newsletter_pipeline(
        self,
        user_id: int,
        newsletter_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete pipeline to create and send a personalized newsletter
        
        Args:
            user_id: User ID requesting the newsletter
            newsletter_config: Configuration for newsletter creation
        """
        try:
            print(f"🚀 Starting newsletter pipeline for user {user_id}")
            
            # Step 1: Aggregate content from multiple sources
            print("📥 Step 1: Aggregating content...")
            content_data = await self._aggregate_content(newsletter_config)
            
            if not content_data or content_data.get("error"):
                return {"error": "Failed to aggregate content", "details": content_data}
            
            # Step 2: Analyze and filter content
            print("🔍 Step 2: Analyzing content...")
            filtered_content = await self._analyze_and_filter_content(content_data, newsletter_config)
            
            # Step 3: Generate newsletter content
            print("✍️ Step 3: Generating newsletter...")
            newsletter_content = await self._generate_newsletter_content(filtered_content, newsletter_config)
            
            if newsletter_content.get("error"):
                return {"error": "Failed to generate newsletter", "details": newsletter_content}
            
            # Step 4: Personalize for audience segments
            print("👥 Step 4: Personalizing content...")
            personalized_content = await self._personalize_content(
                user_id, newsletter_content, newsletter_config
            )
            
            # Step 5: Generate social media posts
            print("📱 Step 5: Creating social media posts...")
            social_posts = await self._generate_social_posts(newsletter_content)
            
            # Step 6: Schedule/Send newsletter
            print("📧 Step 6: Distributing newsletter...")
            distribution_result = await self._distribute_newsletter(
                user_id, personalized_content, newsletter_config
            )
            
            # Step 7: Track analytics
            print("📊 Step 7: Setting up analytics tracking...")
            analytics_setup = await self._setup_analytics_tracking(user_id, newsletter_content)
            
            pipeline_result = {
                "success": True,
                "user_id": user_id,
                "newsletter_id": f"nl_{user_id}_{int(datetime.utcnow().timestamp())}",
                "content_summary": {
                    "sources_used": len(content_data.get("sources", [])),
                    "content_pieces": len(filtered_content),
                    "word_count": len(newsletter_content.get("content", {}).get("full_content", "").split())
                },
                "personalization": personalized_content.get("segments_created", 0),
                "social_posts": len(social_posts.get("twitter", [])) + len(social_posts.get("linkedin", [])),
                "distribution": distribution_result,
                "analytics": analytics_setup,
                "created_at": datetime.utcnow().isoformat(),
                "pipeline_duration": "processing_time_here"
            }
            
            print("✅ Newsletter pipeline completed successfully!")
            return pipeline_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Pipeline failed: {str(e)}",
                "user_id": user_id,
                "failed_at": datetime.utcnow().isoformat()
            }
            print(f"❌ Pipeline failed: {str(e)}")
            return error_result
    
    async def _aggregate_content(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate content from configured sources"""
        content_sources = config.get("content_sources", ["reddit", "news"])
        aggregated_content = []
        source_results = {}
        
        try:            # Reddit content
            if "reddit" in content_sources:
                reddit_config = config.get("reddit", {})
                reddit_content = await self.content_aggregator.fetch_reddit_content(
                    subreddit=reddit_config.get("subreddit", "all"),
                    sort=reddit_config.get("sort", "hot"),
                    limit=reddit_config.get("limit", 10),
                    time_filter=reddit_config.get("time_filter", "day")
                )
                
                if isinstance(reddit_content, list):
                    aggregated_content.extend(reddit_content)
                    source_results["reddit"] = {"count": len(reddit_content), "status": "success"}
                elif isinstance(reddit_content, dict) and reddit_content.get("error"):
                    source_results["reddit"] = {"count": 0, "status": "failed", "error": reddit_content["error"]}
                else:
                    source_results["reddit"] = {"count": 0, "status": "failed", "error": "Unknown response format"}
              # Twitter content
            if "twitter" in content_sources:
                twitter_config = config.get("twitter", {})
                twitter_content = await self.content_aggregator.fetch_twitter_content(
                    query=twitter_config.get("query", ""),
                    max_results=twitter_config.get("max_results", 10)
                )
                
                if isinstance(twitter_content, list):
                    aggregated_content.extend(twitter_content)
                    source_results["twitter"] = {"count": len(twitter_content), "status": "success"}
                elif isinstance(twitter_content, dict) and twitter_content.get("error"):
                    source_results["twitter"] = {"count": 0, "status": "failed", "error": twitter_content["error"]}
                else:
                    source_results["twitter"] = {"count": 0, "status": "failed", "error": "Unknown response format"}
              # News API content
            if "news" in content_sources:
                news_config = config.get("news", {})
                news_content = await self.content_aggregator.fetch_news_content(
                    api_key=news_config.get("api_key", ""),
                    query=news_config.get("query", ""),
                    sources=news_config.get("sources", ""),
                    page_size=news_config.get("page_size", 20)
                )
                
                if isinstance(news_content, list):
                    aggregated_content.extend(news_content)
                    source_results["news"] = {"count": len(news_content), "status": "success"}
                elif isinstance(news_content, dict) and news_content.get("error"):
                    source_results["news"] = {"count": 0, "status": "failed", "error": news_content["error"]}
                else:
                    source_results["news"] = {"count": 0, "status": "failed", "error": "Unknown response format"}            # RSS feeds
            if "rss" in content_sources:
                rss_feeds = config.get("rss_feeds", [])
                rss_content = []
                for feed_url in rss_feeds:
                    feed_content = await self.content_aggregator.fetch_rss_content(
                        feed_url=feed_url,
                        max_entries=10
                    )
                    if isinstance(feed_content, list):
                        rss_content.extend(feed_content)
                    elif isinstance(feed_content, dict) and not feed_content.get("error"):
                        # Handle dict response that's not an error
                        if "items" in feed_content:
                            rss_content.extend(feed_content["items"])
                
                aggregated_content.extend(rss_content)
                source_results["rss"] = {"count": len(rss_content), "status": "success"}
            
            return {
                "sources": aggregated_content,
                "source_results": source_results,
                "total_items": len(aggregated_content),
                "aggregated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Content aggregation failed: {str(e)}"}
    
    async def _analyze_and_filter_content(
        self, 
        content_data: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze and filter content based on relevance and quality"""
        sources = content_data.get("sources", [])
        
        if not sources:
            return []
        
        # Filter by keywords if specified
        keywords = config.get("keywords", [])
        exclude_keywords = config.get("exclude_keywords", [])
        
        filtered_content = []
        
        for item in sources:
            # Get text content
            text_content = " ".join([
                item.get("title", ""),
                item.get("content", ""),
                item.get("text", ""),
                item.get("summary", ""),
                item.get("description", "")
            ]).lower()
            
            # Check inclusion keywords
            if keywords:
                has_keyword = any(keyword.lower() in text_content for keyword in keywords)
                if not has_keyword:
                    continue
            
            # Check exclusion keywords
            if exclude_keywords:
                has_exclude = any(keyword.lower() in text_content for keyword in exclude_keywords)
                if has_exclude:
                    continue
              # Score content based on engagement (if available)
            engagement_score = 0
            if item.get("score"):  # Reddit
                engagement_score = min(100, max(0, item["score"] / 100))
            elif item.get("like_count"):  # Twitter
                engagement_score = min(100, max(0, item["like_count"] / 100))
            elif item.get("publishedAt"):  # News - score by recency
                pub_date = datetime.fromisoformat(item["publishedAt"].replace('Z', '+00:00'))
                # Make now() timezone-aware to match pub_date
                now_utc = datetime.now(timezone.utc) # Changed from datetime.utcnow()
                hours_old = (now_utc - pub_date).total_seconds() / 3600
                engagement_score = max(0, 100 - hours_old)
            
            item["relevance_score"] = engagement_score
            item["analyzed_at"] = datetime.utcnow().isoformat()
            
            filtered_content.append(item)        
        # Sort by relevance score and limit
        filtered_content.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        max_items = config.get("max_content_items", 15)
        
        return filtered_content[:max_items]
    
    async def _generate_newsletter_content(
        self, 
        filtered_content: List[Dict[str, Any]], 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate newsletter content using AI Writer"""
        if not filtered_content:
            return {"error": "No content available for newsletter generation"}
        
        try:
            newsletter_content = await self.ai_writer.generate_newsletter_content(
                source_articles=filtered_content,
                newsletter_topic=config.get("topic", ""),
                target_audience=config.get("target_audience", "general"),
                tone=config.get("tone", "professional"),
                length=config.get("length", "medium"),
                include_sections=config.get("sections", ["introduction", "main_content", "conclusion", "call_to_action"])
            )
            
            # Generate subject lines
            if newsletter_content.get("success"):
                content_text = newsletter_content.get("content", {}).get("full_content", "")
                subject_lines = await self.ai_writer.generate_subject_lines(
                    newsletter_content=content_text,
                    count=5,
                    style=config.get("subject_style", "engaging")            )
            
            return newsletter_content
            
        except Exception as e:
            return {"error": f"Newsletter generation failed: {str(e)}"}
    
    async def _personalize_content(
        self, 
        user_id: int, 
        newsletter_content: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Personalize content for different audience segments"""
        try:
            # Mock subscriber data (in production, this would come from database)
            subscriber_data = config.get("subscriber_data", [])
            
            if not subscriber_data:
                # Return content as-is if no subscriber data
                return {
                    "segments": {
                        "general": {
                            "content": newsletter_content.get("content", {}),
                            "subject_lines": newsletter_content.get("subject_lines", [])
                        }
                    },
                    "segments_created": 1
                }
            
            # Segment audience
            segments = await self.personalization.segment_audience(
                subscribers=subscriber_data,
                segmentation_criteria=["engagement_level", "preferences"]
            )
            
            # Personalize content for each segment
            personalized_segments = {}
            
            for segment_name, segment_subscribers in segments.items():
                if not segment_subscribers:
                    continue
                
                # Create target segment data
                target_segment = {"subscribers": segment_subscribers}
                
                # Personalize content
                personalized = await self.personalization.personalize_content(
                    content=newsletter_content.get("content", {}).get("full_content", ""),
                    target_segment=target_segment,
                    personalization_level=config.get("personalization_level", "medium")
                )
                  # Generate dynamic subject lines
                base_subject = newsletter_content.get("subject_lines", ["Newsletter"])[0]
                dynamic_subjects = await self.personalization.generate_dynamic_subject_lines(
                    base_subject=base_subject,
                    segments={segment_name: segment_subscribers}
                )
                
                personalized_segments[segment_name] = {
                    "content": personalized.get("personalized_content", ""),
                    "subject_line": dynamic_subjects.get(segment_name, base_subject),
                    "subscriber_count": len(segment_subscribers),
                    "personalization_strategy": personalized.get("strategy", {})
                }
            
            return {
                "segments": personalized_segments,
                "segments_created": len(personalized_segments),
                "total_subscribers": len(subscriber_data)
            }
            
        except Exception as e:
            return {"error": f"Personalization failed: {str(e)}"}
    
    async def _generate_social_posts(self, newsletter_content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media posts from newsletter content"""
        try:
            content_text = newsletter_content.get("content", {}).get("full_content", "")
            
            if not content_text:
                return {"error": "No content available for social media generation"}
            
            social_posts = await self.ai_writer.generate_social_media_posts(
                newsletter_content=content_text,
                platforms=["twitter", "linkedin", "facebook"],
                max_posts_per_platform=3
            )
            
            return social_posts
            
        except Exception as e:
            return {"error": f"Social media generation failed: {str(e)}"}
    
    async def _distribute_newsletter(
        self, 
        user_id: int, 
        personalized_content: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Distribute newsletter via email and social media"""
        try:
            distribution_results = {}
            
            # Email distribution
            segments = personalized_content.get("segments", {})
            
            for segment_name, segment_data in segments.items():
                # Mock recipient data (in production, get from database)
                recipients = config.get("recipients", {}).get(segment_name, [])
                
                if not recipients:
                    continue
                
                # Send newsletter email
                email_result = await self.distribution.send_newsletter_email_impl(
                    recipients=recipients,
                    subject=segment_data.get("subject_line", "Newsletter"),
                    html_content=self._convert_to_html(segment_data.get("content", "")),
                    text_content=segment_data.get("content", ""),
                    from_email=config.get("from_email", settings.from_email),
                    from_name=config.get("from_name", settings.from_name)
                )
                
                distribution_results[f"email_{segment_name}"] = email_result
            
            # Social media distribution
            if config.get("auto_post_social", False):
                social_posts = await self._generate_social_posts({"content": {"full_content": personalized_content.get("segments", {}).get("general", {}).get("content", "")}})
                
                social_result = await self.distribution.post_to_social_media_impl(
                    posts=social_posts
                )
                
                distribution_results["social_media"] = social_result
            
            return {
                "success": True,
                "distribution_results": distribution_results,
                "total_emails_sent": sum(
                    result.get("successful_sends", 0) 
                    for key, result in distribution_results.items() 
                    if key.startswith("email_")
                ),
                "distributed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Distribution failed: {str(e)}"}
    
    async def _setup_analytics_tracking(
        self, 
        user_id: int, 
        newsletter_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Setup analytics tracking for the newsletter"""
        try:
            # Mock analytics setup (in production, this would setup tracking pixels, etc.)
            analytics_config = {
                "tracking_enabled": True,
                "metrics_to_track": ["opens", "clicks", "unsubscribes", "forwards"],
                "dashboard_url": f"/analytics/user/{user_id}/newsletter/latest",
                "setup_at": datetime.utcnow().isoformat()
            }
            
            return analytics_config
            
        except Exception as e:
            return {"error": f"Analytics setup failed: {str(e)}"}
    
    def _convert_to_html(self, text_content: str) -> str:
        """Convert text content to HTML format"""
        # Simple text to HTML conversion
        html_content = text_content.replace('\n\n', '</p><p>')
        html_content = f"<p>{html_content}</p>"
        
        # Basic HTML template
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ContentSyndicate Newsletter</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; }}
                a {{ color: #007bff; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>ContentSyndicate Newsletter</h1>
                </div>
                <div class="content">
                    {html_content}
                </div>
                <div class="footer">
                    <p>Thank you for subscribing to ContentSyndicate!</p>
                    <p><a href="{{{{unsubscribe_link}}}}">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    async def quick_newsletter_generation(
        self, 
        topic: str = "", 
        sources: List[str] = None,
        target_audience: str = "general"
    ) -> Dict[str, Any]:
        """
        Quick newsletter generation for testing and demos
        
        Args:
            topic: Newsletter topic
            sources: Content sources to use
            target_audience: Target audience description
        """
        if not sources:
            sources = ["reddit", "news"]
        
        config = {
            "content_sources": sources,
            "topic": topic,
            "target_audience": target_audience,
            "tone": "professional",
            "length": "medium",
            "max_content_items": 10,
            "reddit": {
                "subreddit": "technology" if "tech" in topic.lower() else "all",
                "sort": "hot",
                "limit": 5
            },
            "news": {
                "query": topic if topic else "trending",
                "page_size": 10
            }
        }
        
        # Run just the content generation part of the pipeline
        try:
            print(f"🚀 Quick generating newsletter about: {topic}")
            
            # Aggregate content
            content_data = await self._aggregate_content(config)
            if content_data.get("error"):
                return content_data
            
            # Filter content
            filtered_content = await self._analyze_and_filter_content(content_data, config)
            
            # Generate newsletter
            newsletter_content = await self._generate_newsletter_content(filtered_content, config)
            
            # Generate social posts
            social_posts = await self._generate_social_posts(newsletter_content)
            
            result = {
                "success": True,
                "topic": topic,
                "sources_used": content_data.get("source_results", {}),
                "content_items_found": len(filtered_content),
                "newsletter": newsletter_content,
                "social_posts": social_posts,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            print("✅ Quick newsletter generation completed!")
            return result
            
        except Exception as e:
            print(f"❌ Quick generation failed: {str(e)}")
            return {"error": f"Quick generation failed: {str(e)}"}


# Factory function to create the main agent
def create_main_agent():
    """Create and return a ContentSyndicate main agent instance"""
    return ContentSyndicateAgent()


# Demo function for testing
async def demo_newsletter_creation():
    """Demo function to test newsletter creation"""
    agent = create_main_agent()
    
    # Test quick newsletter generation
    result = await agent.quick_newsletter_generation(
        topic="AI and Technology Trends",
        sources=["reddit"],
        target_audience="tech professionals"
    )
    
    print("\n" + "="*50)
    print("DEMO NEWSLETTER CREATION RESULT")
    print("="*50)
    print(json.dumps(result, indent=2, default=str))
    
    return result


if __name__ == "__main__":
    # Run demo
    import asyncio
    asyncio.run(demo_newsletter_creation())