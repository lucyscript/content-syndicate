"""
Topic Generator MCP Server

This server analyzes trending content from multiple APIs to generate
relevant topic suggestions and match user topics with content.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter, defaultdict
import re
import random

import mcp.server.stdio
from mcp import server
from mcp.server.models import InitializationOptions
import mcp.types as types
from pydantic import AnyUrl
import google.generativeai as genai

from .content_aggregator import ContentAggregatorServer
from ..config import settings

logger = logging.getLogger(__name__)

class TopicGeneratorServer:
    def __init__(self):
        self.name = "topic-generator"
        self.version = "1.0.0"
        self.content_aggregator = ContentAggregatorServer()
        
        # Initialize Gemini for topic analysis using settings
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
            logger.info("Gemini AI model initialized successfully")
        else:
            logger.warning("GEMINI_API_KEY not set, AI topic generation will use fallback")
            self.model = None

    async def fetch_trending_topics_impl(
        self,
        platforms: List[str] = None,
        limit: int = 20,
        categories: List[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch trending topics from multiple platforms and analyze patterns
        
        Args:
            platforms: List of platforms to analyze ['reddit', 'twitter', 'news']
            limit: Number of topics to return
            categories: Filter by categories ['tech', 'business', 'health', 'entertainment']
        """
        try:
            if not platforms:
                platforms = ["reddit", "twitter", "news"]
            
            all_content = []
            platform_data = {}
            
            # Fetch content from each platform
            for platform in platforms:
                try:
                    if platform == "reddit":
                        content = await self.content_aggregator.fetch_reddit_content(
                            subreddit="all", 
                            sort="hot", 
                            limit=50
                        )
                    elif platform == "twitter":
                        content = await self.content_aggregator.fetch_twitter_content(
                            query="trending", 
                            max_results=50
                        )
                    elif platform == "news":
                        content = await self.content_aggregator.fetch_news_content(
                            query="trending", 
                            page_size=50
                        )
                    else:
                        continue
                    
                    platform_data[platform] = content
                    all_content.extend(content)
                    
                except Exception as e:
                    logger.error(f"Error fetching {platform} content: {e}")
                    continue
              # Analyze content to extract topics
            topics = await self._analyze_trending_topics(all_content, categories)
            
            # Generate topic suggestions with descriptions
            topic_suggestions = await self._generate_topic_suggestions(topics[:limit])
            
            # Ensure we have exactly the requested number of suggestions
            if len(topic_suggestions) < limit:
                # Fill remaining slots with diverse AI-generated topics
                additional_needed = limit - len(topic_suggestions)
                diverse_topics = await self._generate_diverse_suggestions([])
                topic_suggestions.extend(diverse_topics[:additional_needed])
            
            return {
                "trending_topics": topic_suggestions[:limit],  # Ensure exact count
                "total_analyzed": len(all_content),
                "platforms_analyzed": list(platform_data.keys()),
                "categories": categories or "all",
                "generated_at": datetime.now().isoformat(),
                "platform_breakdown": {
                    platform: len(data) for platform, data in platform_data.items()
                }
            }
        except Exception as e:
            logger.error(f"Error in fetch_trending_topics_impl: {e}")
            return {"error": f"Failed to fetch trending topics: {str(e)}"}

    async def generate_random_topics_impl(
        self,
        count: int = 10,
        niche: str = "general",
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate random topic suggestions using AI
        
        Args:
            count: Number of topics to generate
            niche: Target niche (tech, business, health, lifestyle, etc.)
            tone: Content tone (professional, casual, technical, etc.)
        """
        try:            # Check if the model is available (API key is set)
            if self.model is None:
                logger.warning("Gemini model not available, using fallback topics")
                topics = self._get_diverse_fallback_topics()[:count]
                return {
                    "topics": topics,
                    "niche": niche,
                    "tone": tone,
                    "count": len(topics),
                    "generated_at": datetime.now().isoformat(),
                    "fallback": True
                }
                
            prompt = f"""
            Generate {count} compelling newsletter topic ideas for {niche} content with a {tone} tone.
            
            For each topic, provide:
            1. Title (catchy, engaging)
            2. Description (2-3 sentences explaining the topic)
            3. Target audience 
            4. Content angle (trending, educational, controversial, etc.)
            
            Make topics diverse, actionable, and relevant to current trends.
            
            Format as JSON array:
            [
              {{
                "title": "Topic Title",
                "description": "Brief description of the topic and why it matters",
                "audience": "Target audience description", 
                "angle": "Content angle/approach",
                "keywords": ["keyword1", "keyword2", "keyword3"]
              }}
            ]
            """
            
            response = self.model.generate_content(prompt)
            topics_text = response.text
              # Extract JSON from response
            topics = self._extract_json_from_response(topics_text)
            
            if not topics:
                # Fallback with predefined topics
                topics = self._get_diverse_fallback_topics()[:count]
            
            return {
                "topics": topics,
                "niche": niche,
                "tone": tone,
                "count": len(topics),
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in generate_random_topics_impl: {e}")
            # Return fallback topics
            return {
                "topics": self._get_diverse_fallback_topics()[:count],
                "niche": niche,
                "tone": tone,
                "count": count,
                "generated_at": datetime.now().isoformat(),
                "fallback": True
            }

    async def match_content_to_topics_impl(
        self,
        user_topics: List[str],
        content_data: List[Dict[str, Any]],
        relevance_threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Match API content to user-defined topics with relevance scoring
        
        Args:
            user_topics: List of user-specified topics
            content_data: Raw content from APIs
            relevance_threshold: Minimum relevance score (0-1)
        """
        try:
            matched_content = {}
            
            for topic in user_topics:
                matched_content[topic] = {
                    "high_relevance": [],  # >0.7
                    "medium_relevance": [], # 0.3-0.7
                    "low_relevance": [],   # <0.3
                    "total_matches": 0
                }
            
            # Score each piece of content against each topic
            for content in content_data:
                for topic in user_topics:
                    relevance_score = await self._calculate_relevance_score(content, topic)
                    
                    if relevance_score >= relevance_threshold:
                        content_with_score = {
                            **content,
                            "relevance_score": relevance_score,
                            "matched_topic": topic
                        }
                        
                        if relevance_score >= 0.7:
                            matched_content[topic]["high_relevance"].append(content_with_score)
                        elif relevance_score >= 0.3:
                            matched_content[topic]["medium_relevance"].append(content_with_score)
                        else:
                            matched_content[topic]["low_relevance"].append(content_with_score)
                        
                        matched_content[topic]["total_matches"] += 1
            
            # Sort matches by relevance score
            for topic in matched_content:
                for relevance_level in ["high_relevance", "medium_relevance", "low_relevance"]:
                    matched_content[topic][relevance_level].sort(
                        key=lambda x: x["relevance_score"], 
                        reverse=True
                    )
            
            return {
                "matched_content": matched_content,
                "user_topics": user_topics,
                "total_content_analyzed": len(content_data),
                "relevance_threshold": relevance_threshold,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in match_content_to_topics_impl: {e}")
            return {"error": f"Failed to match content to topics: {str(e)}"}

    async def _analyze_trending_topics(
        self, 
        content: List[Dict[str, Any]], 
        categories: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract and analyze trending topics from content"""
        
        # Extract keywords and phrases
        all_text = []
        topic_data = defaultdict(lambda: {
            "count": 0,
            "platforms": set(),
            "engagement": 0,
            "sample_content": []
        })
        
        for item in content:
            text = f"{item.get('title', '')} {item.get('content', '')} {item.get('text', '')}"
            all_text.append(text)
            
            # Extract key phrases (simple approach)
            words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
            
            # Common topic keywords
            topic_keywords = [
                'ai', 'artificial intelligence', 'machine learning', 'technology', 'crypto', 
                'bitcoin', 'blockchain', 'startup', 'innovation', 'climate', 'health',
                'economy', 'market', 'investing', 'remote work', 'productivity', 'social media'
            ]
            
            platform = item.get('platform', item.get('source_platform', 'unknown'))
            engagement = item.get('score', item.get('like_count', item.get('engagement_score', 0)))
            
            for keyword in topic_keywords:
                if keyword in text.lower():
                    topic_data[keyword]["count"] += 1
                    topic_data[keyword]["platforms"].add(platform)
                    topic_data[keyword]["engagement"] += engagement
                    if len(topic_data[keyword]["sample_content"]) < 3:
                        topic_data[keyword]["sample_content"].append({
                            "title": item.get('title', '')[:100],
                            "platform": platform
                        })
        
        # Convert to list and sort by relevance
        topics = []
        for topic, data in topic_data.items():
            if data["count"] >= 2:  # Minimum threshold
                topics.append({
                    "topic": topic.title(),
                    "frequency": data["count"],
                    "platforms": list(data["platforms"]),
                    "total_engagement": data["engagement"],
                    "avg_engagement": data["engagement"] / data["count"] if data["count"] > 0 else 0,
                    "sample_content": data["sample_content"]                })
        
        # Sort by frequency and engagement
        topics.sort(key=lambda x: (x["frequency"], x["total_engagement"]), reverse=True)
        
        return topics

    async def _generate_topic_suggestions(
        self, 
        trending_topics: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate enhanced topic suggestions with AI descriptions"""
        
        suggestions = []
        
        # If we have fewer trending topics than needed, generate diverse suggestions
        if len(trending_topics) < 5:
            # Use AI to generate 5 diverse newsletter topics
            return await self._generate_diverse_suggestions(trending_topics)
        
        for topic_data in trending_topics:
            topic = topic_data["topic"]
            
            try:
                # Check if AI model is available
                if self.model is None:
                    # Use fallback if no model available
                    suggestion = {
                        "title": f"The Rise of {topic}",
                        "description": f"{topic} is trending across multiple platforms with high engagement. This presents an opportunity to create timely, relevant content.",
                        "angles": ["trend analysis", "expert insights", "practical applications"],
                        "original_topic": topic,
                        "trend_data": {
                            "frequency": topic_data["frequency"],
                            "platforms": topic_data["platforms"],
                            "engagement": topic_data["total_engagement"]
                        }
                    }
                else:
                    # Generate AI description for topic
                    prompt = f"""
                    Based on the trending topic "{topic}" that appears {topic_data['frequency']} times across platforms {topic_data['platforms']}, create a compelling newsletter topic suggestion.
                    
                    Provide:
                    1. An engaging title
                    2. A 2-sentence description of why this topic matters now
                    3. Suggested content angles
                    
                    Format as JSON:
                    {{
                      "title": "Engaging Newsletter Title",
                      "description": "Why this topic is relevant and timely",
                      "angles": ["angle1", "angle2", "angle3"]
                    }}
                    """
                    
                    response = self.model.generate_content(prompt)
                    ai_suggestion = self._extract_json_from_response(response.text)
                    
                    if ai_suggestion:
                        suggestion = {
                            **ai_suggestion,
                            "original_topic": topic,
                            "trend_data": {
                                "frequency": topic_data["frequency"],
                                "platforms": topic_data["platforms"],
                                "engagement": topic_data["total_engagement"]
                            }
                        }
                    else:
                        # Fallback manual suggestion
                        suggestion = {
                            "title": f"The Rise of {topic}",
                            "description": f"{topic} is trending across multiple platforms with high engagement. This presents an opportunity to create timely, relevant content.",
                            "angles": ["trend analysis", "expert insights", "practical applications"],
                            "original_topic": topic,
                            "trend_data": topic_data
                        }
                
                suggestions.append(suggestion)
                
            except Exception as e:
                logger.error(f"Error generating suggestion for {topic}: {e}")
                # Add basic suggestion
                suggestions.append({
                    "title": f"Trending: {topic}",
                    "description": f"Content about {topic} is gaining traction",
                    "angles": ["analysis", "news", "opinion"],
                    "original_topic": topic,                "trend_data": topic_data
                })
        
        return suggestions
        
    async def _generate_diverse_suggestions(
        self, 
        trending_topics: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate 5 diverse newsletter topic suggestions using AI"""
        
        try:
            # Extract the trending topics we have
            topics_context = ", ".join([topic["topic"] for topic in trending_topics[:3]]) if trending_topics else "current market trends and innovative developments"
            
            if self.model is None:
                logger.error("Gemini model not available - API key not configured")
                # If no AI model, create simple dynamic topics instead of hardcoded ones
                return self._generate_simple_topics()
            
            prompt = f"""
            Generate exactly 5 diverse and compelling newsletter topic suggestions for content creators and business professionals. 
            
            Context: Consider these trending areas for inspiration: {topics_context}
            
            Requirements:
            - Each topic must be unique and cover different niches
            - Topics should be relevant to current market trends and consumer interests
            - Include a mix of: technology, business strategy, personal development, industry insights, and practical guides
            - Make titles engaging and click-worthy
            - Descriptions should explain immediate value and relevance
            
            For each topic, provide:
            - title: An engaging, professional newsletter title (5-10 words)
            - description: Two sentences explaining why this topic matters right now
            - angles: Three specific content angles or subtopics to explore
            
            Return ONLY a valid JSON array with exactly 5 topics:
            [
              {{
                "title": "Newsletter Title Here",
                "description": "First sentence explaining relevance. Second sentence about value proposition.",
                "angles": ["specific angle 1", "specific angle 2", "specific angle 3"]
              }}
            ]
            """
            
            logger.info("Generating AI-powered topic suggestions...")
            response = self.model.generate_content(prompt)
            logger.info(f"AI Response received: {response.text[:200]}...")
            
            suggestions = self._extract_json_from_response(response.text)
            
            if suggestions and isinstance(suggestions, list) and len(suggestions) >= 5:
                logger.info(f"Successfully generated {len(suggestions)} AI topic suggestions")
                # Add metadata to match expected format
                for i, suggestion in enumerate(suggestions[:5]):
                    suggestion["original_topic"] = f"AI_Generated_{i+1}"
                    suggestion["trend_data"] = {
                        "frequency": 1,
                        "platforms": ["AI Generated"],
                        "engagement": 100
                    }
                return suggestions[:5]
            else:
                logger.warning(f"AI returned invalid format or insufficient topics: {suggestions}")
                # Retry with simpler prompt
                return await self._retry_simple_generation()
                
        except Exception as e:
            logger.error(f"Error generating diverse suggestions: {e}")
            # Try one more time with a simpler approach
            return await self._retry_simple_generation()

    async def _retry_simple_generation(self) -> List[Dict[str, Any]]:
        """Retry topic generation with a simpler prompt"""
        try:
            if self.model is None:
                return self._generate_simple_topics()
                
            simple_prompt = """
            Create 5 different newsletter topics for business professionals. Return only JSON:
            [
              {"title": "Topic 1", "description": "Why it matters.", "angles": ["angle1", "angle2", "angle3"]},
              {"title": "Topic 2", "description": "Why it matters.", "angles": ["angle1", "angle2", "angle3"]},
              {"title": "Topic 3", "description": "Why it matters.", "angles": ["angle1", "angle2", "angle3"]},
              {"title": "Topic 4", "description": "Why it matters.", "angles": ["angle1", "angle2", "angle3"]},
              {"title": "Topic 5", "description": "Why it matters.", "angles": ["angle1", "angle2", "angle3"]}
            ]
            """
            
            response = self.model.generate_content(simple_prompt)
            suggestions = self._extract_json_from_response(response.text)
            
            if suggestions and isinstance(suggestions, list):
                for i, suggestion in enumerate(suggestions[:5]):
                    suggestion["original_topic"] = f"AI_Simple_{i+1}"
                    suggestion["trend_data"] = {
                        "frequency": 1,
                        "platforms": ["AI Generated"],
                        "engagement": 100
                    }
                return suggestions[:5]
            else:
                return self._generate_simple_topics()
                
        except Exception as e:
            logger.error(f"Simple generation also failed: {e}")
            return self._generate_simple_topics()

    def _generate_simple_topics(self) -> List[Dict[str, Any]]:
        """Generate simple topics without AI when all else fails"""
        topics = [
            ("AI and Automation", "artificial intelligence"),
            ("Business Strategy", "market trends"),
            ("Remote Work", "productivity"),
            ("Digital Marketing", "customer engagement"),
            ("Innovation", "technology trends")
        ]
        
        suggestions = []
        for i, (category, keyword) in enumerate(topics):
            suggestions.append({
                "title": f"{category} Weekly Update",
                "description": f"Latest developments in {keyword} and their impact on business. Insights and actionable strategies for professionals.",
                "angles": ["industry news", "practical tips", "case studies"],
                "original_topic": f"Simple_{category}",
                "trend_data": {
                    "frequency": 1,
                    "platforms": ["Generated"],
                    "engagement": 50
                }
            })
        
        return suggestions

    def _get_diverse_fallback_topics(self) -> List[Dict[str, Any]]:
        """Provide 5 diverse fallback topics when AI fails"""
        
        return [
            {
                "title": "The Future of Remote Work: What's Next in 2025",
                "description": "Remote work is evolving beyond video calls and home offices. Explore emerging trends in distributed teams, digital nomadism, and the tools reshaping how we collaborate.",
                "angles": ["emerging tools", "productivity hacks", "team management"],
                "original_topic": "Remote Work Trends",
                "trend_data": {"frequency": 5, "platforms": ["LinkedIn", "Twitter"], "engagement": 250}
            },
            {
                "title": "AI Tools That Actually Save Time (Not Hype)",
                "description": "Cut through the AI noise with practical tools that streamline daily workflows. From content creation to data analysis, discover which AI applications deliver real value.",
                "angles": ["tool reviews", "workflow optimization", "productivity metrics"],
                "original_topic": "AI Productivity",
                "trend_data": {"frequency": 8, "platforms": ["Reddit", "Twitter"], "engagement": 180}
            },
            {
                "title": "The Psychology of High-Converting Email Subject Lines",
                "description": "Why do some emails get opened while others get deleted? Dive into behavioral psychology and data-driven strategies that boost email engagement rates.",
                "angles": ["psychology insights", "A/B testing", "case studies"],
                "original_topic": "Email Marketing",
                "trend_data": {"frequency": 3, "platforms": ["LinkedIn"], "engagement": 120}
            },
            {
                "title": "Building Sustainable Business Models in 2025",
                "description": "Traditional business models are being disrupted by conscious consumers and climate concerns. Learn how companies are adapting and thriving with sustainable practices.",
                "angles": ["case studies", "implementation strategies", "market analysis"],
                "original_topic": "Sustainable Business",
                "trend_data": {"frequency": 4, "platforms": ["News", "LinkedIn"], "engagement": 200}
            },
            {
                "title": "The Creator Economy Reality Check",
                "description": "Behind the glamorous social media posts lies the real economics of content creation. Explore income diversity, platform dependencies, and sustainable creator strategies.",
                "angles": ["income analysis", "platform comparison", "diversification strategies"],
                "original_topic": "Creator Economy",
                "trend_data": {"frequency": 6, "platforms": ["Twitter", "Reddit"], "engagement": 300}
            }
        ]

    async def _calculate_relevance_score(
        self, 
        content: Dict[str, Any], 
        topic: str
    ) -> float:
        """Calculate relevance score between content and topic"""
        
        # Extract text for analysis
        text = f"{content.get('title', '')} {content.get('content', '')} {content.get('text', '')}"
        
        # Simple keyword matching (can be enhanced with AI)
        topic_lower = topic.lower()
        text_lower = text.lower()
        
        # Direct topic mention
        direct_match = 1.0 if topic_lower in text_lower else 0.0
        
        # Related keywords scoring
        topic_words = topic_lower.split()
        text_words = text_lower.split()
        
        word_matches = sum(1 for word in topic_words if word in text_words)
        word_score = word_matches / len(topic_words) if topic_words else 0
        
        # Content length factor (longer content might be more relevant)
        length_factor = min(1.0, len(text) / 500)  # Normalize to 500 chars
        
        # Engagement factor
        engagement = content.get('score', content.get('like_count', content.get('engagement_score', 0)))
        engagement_factor = min(1.0, engagement / 100) if engagement else 0.1
        
        # Combined score
        relevance_score = (
            direct_match * 0.4 +
            word_score * 0.3 +
            length_factor * 0.2 +
            engagement_factor * 0.1
        )
        
        return min(1.0, relevance_score)

    def _extract_json_from_response(self, text: str) -> Any:
        """Extract JSON from AI response text"""
        try:
            # Find JSON in the response
            import re
            json_match = re.search(r'\[.*\]|\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            return None
        except Exception as e:
            logger.error(f"Error extracting JSON: {e}")
            return None

    def _get_fallback_topics(self, count: int, niche: str) -> List[Dict[str, Any]]:
        """Generate fallback topics when AI fails"""
        
        fallback_topics = {
            "tech": [
                {
                    "title": "The Future of AI in Everyday Life",
                    "description": "Exploring how artificial intelligence is reshaping daily routines and business operations. From smart homes to automated workflows.",
                    "audience": "Tech enthusiasts and business professionals",
                    "angle": "educational",
                    "keywords": ["AI", "automation", "technology"]
                },
                {
                    "title": "Cybersecurity Trends to Watch",
                    "description": "Latest cybersecurity threats and protection strategies for individuals and businesses. Essential knowledge for the digital age.",
                    "audience": "Business owners and tech users",
                    "angle": "educational",
                    "keywords": ["cybersecurity", "privacy", "protection"]
                }
            ],
            "business": [
                {
                    "title": "Remote Work Revolution",
                    "description": "How distributed teams are changing the corporate landscape. Best practices for managing remote workforce effectively.",
                    "audience": "Business leaders and remote workers",
                    "angle": "trending",
                    "keywords": ["remote work", "productivity", "management"]
                }
            ],
            "general": [
                {
                    "title": "Productivity Hacks That Actually Work",
                    "description": "Science-backed methods to boost productivity and manage time more effectively. Practical tips for busy professionals.",
                    "audience": "Working professionals",
                    "angle": "educational",
                    "keywords": ["productivity", "time management", "efficiency"]
                }
            ]
        }
        
        topics = fallback_topics.get(niche, fallback_topics["general"])
        
        # Repeat topics if needed and shuffle
        while len(topics) < count:
            topics.extend(fallback_topics.get(niche, fallback_topics["general"]))
        
        random.shuffle(topics)
        return topics[:count]


# MCP Server setup
app = server.Server("topic-generator")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="fetch_trending_topics",
            description="Analyze trending content to generate topic suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "platforms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Platforms to analyze (reddit, twitter, news)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of topics to return",
                        "default": 20
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by categories"
                    }
                }
            }
        ),
        types.Tool(
            name="generate_random_topics",
            description="Generate random topic suggestions using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Number of topics to generate",
                        "default": 10
                    },
                    "niche": {
                        "type": "string",
                        "description": "Target niche (tech, business, health, etc.)",
                        "default": "general"
                    },
                    "tone": {
                        "type": "string",
                        "description": "Content tone (professional, casual, technical, etc.)",
                        "default": "professional"
                    }
                }
            }
        ),
        types.Tool(
            name="match_content_to_topics",
            description="Match API content to user topics with relevance scoring",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "User-defined topics"
                    },
                    "content_data": {
                        "type": "array",
                        "description": "Content from APIs"
                    },
                    "relevance_threshold": {
                        "type": "number",
                        "description": "Minimum relevance score (0-1)",
                        "default": 0.3
                    }
                },
                "required": ["user_topics", "content_data"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    
    topic_generator = TopicGeneratorServer()
    
    try:
        if name == "fetch_trending_topics":
            result = await topic_generator.fetch_trending_topics_impl(**arguments)
        elif name == "generate_random_topics":
            result = await topic_generator.generate_random_topics_impl(**arguments)
        elif name == "match_content_to_topics":
            result = await topic_generator.match_content_to_topics_impl(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="topic-generator",
                server_version="1.0.0"
            )
        )

def create_topic_generator_server():
    """Factory function to create topic generator server"""
    return TopicGeneratorServer()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
