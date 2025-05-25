"""
AI Writer MCP Server
Creates human-like newsletter content using Gemini API
"""
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from ..config import settings


class AIWriterServer:
    def __init__(self):
        self.mcp = FastMCP("ai-writer")
        self._setup_ai()
        self._register_tools()
      def _setup_ai(self):
        """Initialize Gemini AI"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.mcp.tool()
        async def generate_newsletter_content(
            source_articles: List[Dict[str, Any]],
            newsletter_topic: str = "",
            target_audience: str = "general",
            tone: str = "professional",
            length: str = "medium",
            include_sections: List[str] = None,
            topic_matching_data: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            """Generate newsletter content from source articles"""
            return await self.generate_newsletter_content(
                source_articles, newsletter_topic, target_audience, tone, length, include_sections, topic_matching_data
            )
        
        @self.mcp.tool()
        async def generate_social_media_posts(
            newsletter_content: str,
            platforms: List[str] = None,
            max_posts_per_platform: int = 3
        ) -> Dict[str, List[Dict[str, Any]]]:
            """Generate social media posts from newsletter content"""
            return await self.generate_social_media_posts(newsletter_content, platforms, max_posts_per_platform)
        
        @self.mcp.tool()
        async def improve_content(
            content: str,
            improvement_type: str = "readability",
            specific_instructions: str = ""
        ) -> Dict[str, Any]:
            """Improve existing content based on specific criteria"""
            return await self.improve_content(content, improvement_type, specific_instructions)        
        @self.mcp.tool()
        async def generate_subject_lines(
            newsletter_content: str,
            count: int = 5,
            style: str = "engaging"
        ) -> List[str]:
            """Generate email subject lines for newsletter"""
            return await self.generate_subject_lines(newsletter_content, count, style)
    
    async def generate_newsletter_content(
        self,
        source_articles: List[Dict[str, Any]],
        newsletter_topic: str = "",
        target_audience: str = "general",
        tone: str = "professional",
        length: str = "medium",
        include_sections: List[str] = None,
        topic_matching_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate newsletter content from source articles
        
        Args:
            source_articles: List of source articles/content
            newsletter_topic: Main topic/theme for the newsletter
            target_audience: Target audience description
            tone: Writing tone (professional, casual, friendly, authoritative)
            length: Content length (short, medium, long)
            include_sections: Specific sections to include
            topic_matching_data: Enhanced data from topic generator including relevance scores
        """
        try:
            if not include_sections:
                include_sections = ["introduction", "main_content", "conclusion", "call_to_action"]
            
            # Prepare content summary from source articles
            content_summaries = []
            for i, article in enumerate(source_articles[:10], 1):  # Limit to 10 articles
                summary = {
                    "index": i,
                    "title": article.get("title", ""),
                    "content": article.get("content", article.get("text", article.get("summary", "")))[:500],
                    "source": article.get("source_type", "unknown"),
                    "url": article.get("url", "")
                }
                content_summaries.append(summary)
              # Generate newsletter prompt with enhanced topic matching
            prompt = self._create_newsletter_prompt(
                content_summaries=content_summaries,
                newsletter_topic=newsletter_topic,
                target_audience=target_audience,
                tone=tone,
                length=length,
                include_sections=include_sections,
                topic_matching_data=topic_matching_data
            )
            
            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return {"error": "Failed to generate content"}
            
            # Parse the response to extract different sections
            newsletter_content = self._parse_newsletter_response(response.text)
            
            return {
                "success": True,
                "content": newsletter_content,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "source_count": len(source_articles),
                    "topic": newsletter_topic,
                    "audience": target_audience,
                    "tone": tone,
                    "length": length
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to generate newsletter content: {str(e)}"}
    
    async def generate_social_media_posts(
        self,
        newsletter_content: str,
        platforms: List[str] = None,
        max_posts_per_platform: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate social media posts from newsletter content
        
        Args:
            newsletter_content: The newsletter content to transform
            platforms: List of platforms (twitter, linkedin, facebook)
            max_posts_per_platform: Maximum posts per platform
        """
        try:
            if not platforms:
                platforms = ["twitter", "linkedin", "facebook"]
            
            social_posts = {}
            
            for platform in platforms:
                prompt = self._create_social_media_prompt(
                    newsletter_content=newsletter_content,
                    platform=platform,
                    max_posts=max_posts_per_platform
                )
                
                response = self.model.generate_content(prompt)
                
                if response.text:
                    posts = self._parse_social_media_response(response.text, platform)
                    social_posts[platform] = posts
                else:
                    social_posts[platform] = []
            
            return social_posts
            
        except Exception as e:
            return {"error": f"Failed to generate social media posts: {str(e)}"}
    
    async def improve_content(
        self,
        content: str,
        improvement_type: str = "readability",
        specific_instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Improve existing content based on specific criteria
        
        Args:
            content: Content to improve
            improvement_type: Type of improvement (readability, engagement, seo, clarity)
            specific_instructions: Additional specific instructions
        """
        try:
            prompt = self._create_improvement_prompt(
                content=content,
                improvement_type=improvement_type,
                specific_instructions=specific_instructions
            )
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return {"error": "Failed to improve content"}
            
            return {
                "success": True,
                "original_content": content,
                "improved_content": response.text,
                "improvement_type": improvement_type,
                "instructions": specific_instructions
            }
            
        except Exception as e:
            return {"error": f"Failed to improve content: {str(e)}"}
    
    async def generate_subject_lines(
        self,
        newsletter_content: str,
        count: int = 5,
        style: str = "engaging"
    ) -> List[str]:
        """
        Generate email subject lines for newsletter
        
        Args:
            newsletter_content: Newsletter content to base subject lines on
            count: Number of subject lines to generate
            style: Style of subject lines (engaging, professional, curiosity, urgent)
        """
        try:
            prompt = f"""
            Generate {count} compelling email subject lines for this newsletter content.
            Style: {style}
            
            Newsletter content preview:
            {newsletter_content[:500]}...
            
            Requirements:
            - Keep subject lines under 50 characters
            - Make them {style} and compelling
            - Avoid spam trigger words
            - Create urgency or curiosity where appropriate
            - Make them mobile-friendly
            
            Return only the subject lines, one per line, without numbering or bullets.
            """
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return []
            
            subject_lines = [line.strip() for line in response.text.split('\n') if line.strip()]
            return subject_lines[:count]
              except Exception as e:
            return []
    
    def _create_newsletter_prompt(
        self,
        content_summaries: List[Dict],
        newsletter_topic: str,
        target_audience: str,
        tone: str,
        length: str,
        include_sections: List[str],
        topic_matching_data: Dict[str, Any] = None
    ) -> str:
        """Create enhanced prompt for newsletter generation with topic matching data"""
        
        length_guidelines = {
            "short": "500-800 words",
            "medium": "800-1500 words", 
            "long": "1500-2500 words"
        }
        
        tone_guidelines = {
            "professional": "formal, authoritative, and informative",
            "casual": "conversational, friendly, and approachable",
            "friendly": "warm, personal, and engaging",
            "authoritative": "expert, confident, and comprehensive"
        }
          source_content = "\n".join([
            f"Source {s['index']}: {s['title']}\nContent: {s['content']}\nFrom: {s['source']}\nURL: {s['url']}\n"
            for s in content_summaries
        ])
        
        # Build enhanced prompt with topic matching data
        topic_insights = ""
        relevance_guidance = ""
        
        if topic_matching_data:
            # Extract topic analysis insights
            if "topic_analysis" in topic_matching_data:
                analysis = topic_matching_data["topic_analysis"]
                topic_insights = f"""
        TOPIC ANALYSIS INSIGHTS:
        - Primary Topic: {analysis.get('primary_topic', 'Not specified')}
        - Confidence Score: {analysis.get('confidence_score', 'N/A')}
        - Key Themes: {', '.join(analysis.get('key_themes', []))}
        - Content Categories: {', '.join(analysis.get('categories', []))}
        """
                
            # Extract content relevance information
            if "content_matches" in topic_matching_data:
                matches = topic_matching_data["content_matches"]
                high_relevance = [m for m in matches if m.get('relevance_score', 0) >= 0.7]
                medium_relevance = [m for m in matches if 0.4 <= m.get('relevance_score', 0) < 0.7]
                
                relevance_guidance = f"""
        CONTENT RELEVANCE GUIDANCE:
        - High relevance content ({len(high_relevance)} items): Focus heavily on these sources
        - Medium relevance content ({len(medium_relevance)} items): Use as supporting information
        - Prioritize sources with higher relevance scores for main points
        - Use topic categories to organize content sections logically
        """
        
        prompt = f"""
        Create a high-quality newsletter from the following source content with enhanced topic matching guidance.
        
        NEWSLETTER REQUIREMENTS:
        - Topic: {newsletter_topic if newsletter_topic else "Current trends and insights"}
        - Target Audience: {target_audience}
        - Tone: {tone_guidelines.get(tone, tone)}
        - Length: {length_guidelines.get(length, length)}
        - Include sections: {', '.join(include_sections)}
        {topic_insights}
        {relevance_guidance}
        
        SOURCE CONTENT:
        {source_content}
        
        ENHANCED STRUCTURE REQUIREMENTS:
        1. Compelling headline that reflects the primary topic theme
        2. Engaging introduction that hooks the reader and establishes topic relevance
        3. Main content organized by topic categories and relevance scores
        4. Key insights prioritized by content relevance
        5. Actionable recommendations based on high-relevance sources
        6. Strong conclusion with call-to-action aligned with topic focus
        
        ENHANCED STYLE GUIDELINES:
        - Write in {tone} tone
        - Prioritize content with higher relevance scores
        - Use topic themes to create coherent narrative flow
        - Include relevant quotes or statistics from high-relevance sources
        - Add smooth transitions between topic categories
        - Make it scannable with subheadings based on content themes
        - Include actionable insights from most relevant content
        - End with a compelling call-to-action that aligns with the primary topic
        - Reference topic categories when organizing information
        
        Format the output as structured text with clear section headers.
        """
        
        return prompt
    
    def _create_social_media_prompt(
        self,
        newsletter_content: str,
        platform: str,
        max_posts: int
    ) -> str:
        """Create prompt for social media post generation"""
        
        platform_specs = {
            "twitter": {
                "char_limit": 280,
                "style": "concise, engaging, use hashtags, thread-friendly",
                "format": "Short punchy posts with relevant hashtags"
            },
            "linkedin": {
                "char_limit": 3000,
                "style": "professional, insightful, industry-focused",
                "format": "Professional insights with business value"
            },
            "facebook": {
                "char_limit": 2000,
                "style": "engaging, personal, community-focused",
                "format": "Engaging posts that encourage discussion"
            }
        }
        
        specs = platform_specs.get(platform, platform_specs["twitter"])
        
        prompt = f"""
        Create {max_posts} {platform} posts from this newsletter content:
        
        Newsletter content:
        {newsletter_content[:1000]}...
        
        Platform: {platform}
        Requirements:
        - Character limit: {specs['char_limit']}
        - Style: {specs['style']}
        - Format: {specs['format']}
        
        For each post:
        1. Extract the most engaging points
        2. Make it platform-appropriate
        3. Include relevant hashtags (if applicable)
        4. Add engaging hooks
        5. Include call-to-action where appropriate
        
        Return each post separated by "---"
        """
        
        return prompt
    
    def _create_improvement_prompt(
        self,
        content: str,
        improvement_type: str,
        specific_instructions: str
    ) -> str:
        """Create prompt for content improvement"""
        
        improvement_guidelines = {
            "readability": "improve clarity, simplify complex sentences, enhance flow",
            "engagement": "add hooks, improve storytelling, increase emotional connection",
            "seo": "optimize for search engines, improve keyword usage, enhance structure",
            "clarity": "eliminate ambiguity, improve precision, enhance understanding"
        }
        
        guidelines = improvement_guidelines.get(improvement_type, improvement_type)
        
        prompt = f"""
        Improve the following content focusing on: {improvement_type}
        
        Improvement focus: {guidelines}
        Additional instructions: {specific_instructions}
        
        Original content:
        {content}
        
        Requirements:
        1. Maintain the original meaning and key points
        2. Improve {improvement_type} significantly
        3. Keep the same approximate length
        4. Enhance overall quality
        5. Make it more compelling for readers
        
        Return only the improved content.
        """
        
        return prompt
    
    def _parse_newsletter_response(self, response_text: str) -> Dict[str, str]:
        """Parse newsletter response into structured sections"""
        sections = {}
        current_section = "content"
        current_text = []
        
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            if any(keyword in line.lower() for keyword in ['headline', 'title', 'subject']):
                if current_text:
                    sections[current_section] = '\n'.join(current_text)
                current_section = "headline"
                current_text = []
                if ':' in line:
                    current_text.append(line.split(':', 1)[1].strip())
            elif any(keyword in line.lower() for keyword in ['introduction', 'intro']):
                if current_text:
                    sections[current_section] = '\n'.join(current_text)
                current_section = "introduction"
                current_text = []
            elif any(keyword in line.lower() for keyword in ['conclusion', 'summary']):
                if current_text:
                    sections[current_section] = '\n'.join(current_text)
                current_section = "conclusion"
                current_text = []
            elif any(keyword in line.lower() for keyword in ['call-to-action', 'call to action', 'cta']):
                if current_text:
                    sections[current_section] = '\n'.join(current_text)
                current_section = "call_to_action"
                current_text = []
            else:
                current_text.append(line)
          # Add the last section
        if current_text:
            sections[current_section] = '\n'.join(current_text)
        
        # Always create a full_content field by combining all sections
        if len(sections) > 1:
            # Combine sections in a logical order
            full_content_parts = []
            if "headline" in sections:
                full_content_parts.append(f"# {sections['headline']}")
            if "introduction" in sections:
                full_content_parts.append(sections['introduction'])
            if "content" in sections:
                full_content_parts.append(sections['content'])
            if "conclusion" in sections:
                full_content_parts.append(sections['conclusion'])
            if "call_to_action" in sections:
                full_content_parts.append(sections['call_to_action'])
            
            sections["full_content"] = '\n\n'.join(full_content_parts)
        elif len(sections) == 1 and "content" in sections:
            sections["full_content"] = sections["content"]
        else:
            sections["full_content"] = response_text
        
        return sections
    
    def _parse_social_media_response(self, response_text: str, platform: str) -> List[Dict[str, Any]]:
        """Parse social media response into individual posts"""
        posts = []
        post_texts = response_text.split('---')
        
        for i, post_text in enumerate(post_texts, 1):
            post_text = post_text.strip()
            if post_text:
                posts.append({
                    "platform": platform,
                    "content": post_text,
                    "post_number": i,
                    "character_count": len(post_text)
                })
        
        return posts


def create_ai_writer_server():
    """Factory function to create AI writer server"""
    return AIWriterServer()
