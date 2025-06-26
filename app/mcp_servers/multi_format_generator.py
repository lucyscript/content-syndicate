"""
Multi-Format Content Generator
Generates content for all platforms from a single source with platform-specific optimization
"""
import json
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
import google.generativeai as genai
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from ..config import settings


class ContentFormat(Enum):
    """Supported content formats"""
    NEWSLETTER = "newsletter"
    TWITTER_THREAD = "twitter_thread"
    TWITTER_POST = "twitter_post"
    LINKEDIN_POST = "linkedin_post"
    LINKEDIN_ARTICLE = "linkedin_article"
    REDDIT_POST = "reddit_post"
    MEDIUM_ARTICLE = "medium_article"
    INSTAGRAM_CAPTION = "instagram_caption"
    FACEBOOK_POST = "facebook_post"
    BLOG_POST = "blog_post"
    YOUTUBE_SCRIPT = "youtube_script"
    TIKTOK_CAPTION = "tiktok_caption"


@dataclass
class ContentSpec:
    """Specification for content generation"""
    format: ContentFormat
    character_limit: Optional[int] = None
    word_limit: Optional[int] = None
    style_notes: str = ""
    include_hashtags: bool = True
    include_call_to_action: bool = True
    platform_specific_features: Dict[str, Any] = None


class MultiFormatContentGenerator:
    """Generates optimized content for multiple platforms from single source"""
    
    # Platform specifications
    PLATFORM_SPECS = {
        ContentFormat.NEWSLETTER: ContentSpec(
            format=ContentFormat.NEWSLETTER,
            word_limit=800,
            style_notes="Professional, informative, structured with sections",
            include_call_to_action=True
        ),
        ContentFormat.TWITTER_THREAD: ContentSpec(
            format=ContentFormat.TWITTER_THREAD,
            character_limit=280,
            style_notes="Conversational, hook in first tweet, numbered threads",
            include_hashtags=True,
            platform_specific_features={"max_tweets": 10, "thread_style": True}
        ),
        ContentFormat.TWITTER_POST: ContentSpec(
            format=ContentFormat.TWITTER_POST,
            character_limit=280,
            style_notes="Punchy, engaging, single focused message",
            include_hashtags=True
        ),
        ContentFormat.LINKEDIN_POST: ContentSpec(
            format=ContentFormat.LINKEDIN_POST,
            character_limit=3000,
            style_notes="Professional, thought leadership, industry insights",
            include_hashtags=True,
            platform_specific_features={"professional_tone": True}
        ),
        ContentFormat.LINKEDIN_ARTICLE: ContentSpec(
            format=ContentFormat.LINKEDIN_ARTICLE,
            word_limit=1200,
            style_notes="In-depth analysis, professional insights, structured",
            include_call_to_action=True
        ),
        ContentFormat.REDDIT_POST: ContentSpec(
            format=ContentFormat.REDDIT_POST,
            word_limit=500,
            style_notes="Authentic, conversational, community-focused",
            include_hashtags=False,
            platform_specific_features={"reddit_etiquette": True}
        ),
        ContentFormat.MEDIUM_ARTICLE: ContentSpec(
            format=ContentFormat.MEDIUM_ARTICLE,
            word_limit=1500,
            style_notes="Storytelling, detailed analysis, personal insights",
            include_call_to_action=True
        ),
        ContentFormat.INSTAGRAM_CAPTION: ContentSpec(
            format=ContentFormat.INSTAGRAM_CAPTION,
            character_limit=2200,
            style_notes="Visual-first, engaging, story-driven",
            include_hashtags=True,
            platform_specific_features={"visual_references": True}
        ),
        ContentFormat.FACEBOOK_POST: ContentSpec(
            format=ContentFormat.FACEBOOK_POST,
            character_limit=500,
            style_notes="Community-focused, discussion-starting",
            include_hashtags=False
        ),
        ContentFormat.BLOG_POST: ContentSpec(
            format=ContentFormat.BLOG_POST,
            word_limit=1000,
            style_notes="SEO-optimized, structured, informative",
            include_call_to_action=True
        ),
        ContentFormat.YOUTUBE_SCRIPT: ContentSpec(
            format=ContentFormat.YOUTUBE_SCRIPT,
            word_limit=800,
            style_notes="Conversational, engaging, visual cues included",
            platform_specific_features={"script_format": True}
        ),
        ContentFormat.TIKTOK_CAPTION: ContentSpec(
            format=ContentFormat.TIKTOK_CAPTION,
            character_limit=150,
            style_notes="Trendy, engaging, youth-focused",
            include_hashtags=True
        )
    }

    def __init__(self):
        self.mcp = FastMCP("multi-format-generator")
        self._setup_ai()
        self._register_tools()
    
    def _setup_ai(self):
        """Initialize Gemini AI"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.mcp.tool()
        async def generate_all_formats(
            source_content: Union[str, List[Dict[str, Any]]],
            topic: str = "",
            target_audience: str = "general",
            tone: str = "professional",
            selected_formats: List[str] = None,
            custom_instructions: str = ""
        ) -> Dict[str, Any]:
            """Generate content in all specified formats from source material"""
            return await self.generate_all_formats(
                source_content, topic, target_audience, tone, selected_formats, custom_instructions
            )
        
        @self.mcp.tool()
        async def generate_single_format(
            source_content: Union[str, List[Dict[str, Any]]],
            format_name: str,
            topic: str = "",
            target_audience: str = "general",
            tone: str = "professional",
            custom_instructions: str = ""
        ) -> Dict[str, Any]:
            """Generate content in a single specified format"""
            return await self.generate_single_format(
                source_content, format_name, topic, target_audience, tone, custom_instructions
            )
        
        @self.mcp.tool()
        async def repurpose_content(
            source_format: str,
            target_formats: List[str],
            content: str,
            preserve_core_message: bool = True
        ) -> Dict[str, Any]:
            """Repurpose existing content from one format to others"""
            return await self.repurpose_content(source_format, target_formats, content, preserve_core_message)
    
    async def generate_all_formats(
        self,
        source_content: Union[str, List[Dict[str, Any]]],
        topic: str = "",
        target_audience: str = "general", 
        tone: str = "professional",
        selected_formats: List[str] = None,
        custom_instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Generate content in all specified formats
        
        Args:
            source_content: Source material (text or article list)
            topic: Main topic/theme
            target_audience: Target audience description
            tone: Writing tone
            selected_formats: List of formats to generate (if None, generates all)
            custom_instructions: Additional instructions
        """
        try:
            # Default to all formats if none specified
            if not selected_formats:
                selected_formats = [f.value for f in ContentFormat]
            
            # Validate formats
            valid_formats = []
            for format_name in selected_formats:
                try:
                    format_enum = ContentFormat(format_name)
                    valid_formats.append(format_enum)
                except ValueError:
                    continue
            
            if not valid_formats:
                return {"error": "No valid formats specified"}
            
            # Process source content
            processed_source = self._process_source_content(source_content)
            
            # Generate content for each format
            generated_content = {}
            generation_metadata = {}
            
            for content_format in valid_formats:
                try:
                    result = await self._generate_format_specific_content(
                        processed_source, content_format, topic, target_audience, tone, custom_instructions
                    )
                    
                    if result.get("success"):
                        generated_content[content_format.value] = result["content"]
                        generation_metadata[content_format.value] = result.get("metadata", {})
                    else:
                        generated_content[content_format.value] = {"error": result.get("error", "Generation failed")}
                        
                except Exception as e:
                    generated_content[content_format.value] = {"error": f"Failed to generate {content_format.value}: {str(e)}"}
            
            return {
                "success": True,
                "generated_content": generated_content,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "source_type": "text" if isinstance(source_content, str) else "articles",
                    "topic": topic,
                    "audience": target_audience,
                    "tone": tone,
                    "formats_generated": len([f for f in generated_content.values() if "error" not in f]),
                    "formats_requested": len(valid_formats),
                    "generation_details": generation_metadata
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to generate multi-format content: {str(e)}"}
    
    async def generate_single_format(
        self,
        source_content: Union[str, List[Dict[str, Any]]],
        format_name: str,
        topic: str = "",
        target_audience: str = "general",
        tone: str = "professional", 
        custom_instructions: str = ""
    ) -> Dict[str, Any]:
        """Generate content in a single specified format"""
        try:
            # Validate format
            try:
                content_format = ContentFormat(format_name)
            except ValueError:
                return {"error": f"Invalid format: {format_name}"}
            
            # Process source content
            processed_source = self._process_source_content(source_content)
            
            # Generate content
            result = await self._generate_format_specific_content(
                processed_source, content_format, topic, target_audience, tone, custom_instructions
            )
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to generate {format_name} content: {str(e)}"}
    
    async def _generate_format_specific_content(
        self,
        processed_source: str,
        content_format: ContentFormat,
        topic: str,
        target_audience: str,
        tone: str,
        custom_instructions: str
    ) -> Dict[str, Any]:
        """Generate content for a specific format"""
        
        spec = self.PLATFORM_SPECS[content_format]
        
        # Create format-specific prompt
        prompt = self._create_format_prompt(
            processed_source, spec, topic, target_audience, tone, custom_instructions
        )
        
        # Generate content
        response = self.model.generate_content(prompt)
        
        if not response.text:
            return {"error": f"Failed to generate {content_format.value} content"}
        
        # Parse and structure the response
        structured_content = self._parse_format_response(response.text, content_format)
        
        return {
            "success": True,
            "content": structured_content,
            "metadata": {
                "format": content_format.value,
                "character_count": len(response.text),
                "word_count": len(response.text.split()),
                "generated_at": datetime.utcnow().isoformat(),
                "spec_used": {
                    "character_limit": spec.character_limit,
                    "word_limit": spec.word_limit,
                    "style_notes": spec.style_notes
                }
            }
        }
    
    def _process_source_content(self, source_content: Union[str, List[Dict[str, Any]]]) -> str:
        """Process source content into a unified string"""
        if isinstance(source_content, str):
            return source_content
        
        # If it's a list of articles, combine them
        processed_parts = []
        for item in source_content:
            if isinstance(item, dict):
                title = item.get("title", "")
                content = item.get("content", item.get("text", item.get("summary", "")))
                if title and content:
                    processed_parts.append(f"**{title}**\n{content}")
                elif content:
                    processed_parts.append(content)
        
        return "\n\n".join(processed_parts)
    
    def _create_format_prompt(
        self,
        source_content: str,
        spec: ContentSpec,
        topic: str,
        target_audience: str,
        tone: str,
        custom_instructions: str
    ) -> str:
        """Create a format-specific generation prompt"""
        
        base_prompt = f"""
        Create {spec.format.value.replace('_', ' ')} content based on the following source material.
        
        SOURCE MATERIAL:
        {source_content[:3000]}  # Limit source content to prevent token overflow
        
        REQUIREMENTS:
        - Topic focus: {topic if topic else "Extract main themes from source"}
        - Target audience: {target_audience}
        - Tone: {tone}
        - Style: {spec.style_notes}
        """
        
        if spec.character_limit:
            base_prompt += f"\n- Character limit: {spec.character_limit} characters"
        
        if spec.word_limit:
            base_prompt += f"\n- Word limit: {spec.word_limit} words"
        
        if spec.include_hashtags:
            base_prompt += "\n- Include relevant hashtags"
        
        if spec.include_call_to_action:
            base_prompt += "\n- Include a clear call-to-action"
        
        # Add platform-specific instructions
        if spec.format == ContentFormat.TWITTER_THREAD:
            base_prompt += "\n- Format as numbered thread (1/n, 2/n, etc.)"
            base_prompt += "\n- Each tweet should be under 280 characters"
            base_prompt += "\n- Start with a hook tweet"
        
        elif spec.format == ContentFormat.REDDIT_POST:
            base_prompt += "\n- Use authentic, community-friendly language"
            base_prompt += "\n- Avoid overly promotional tone"
            base_prompt += "\n- Consider adding a TL;DR if lengthy"
        
        elif spec.format == ContentFormat.LINKEDIN_ARTICLE:
            base_prompt += "\n- Include professional insights and industry perspective"
            base_prompt += "\n- Structure with clear headings"
            base_prompt += "\n- End with thought-provoking question"
        
        elif spec.format == ContentFormat.YOUTUBE_SCRIPT:
            base_prompt += "\n- Include [PAUSE], [SHOW SCREEN], [B-ROLL] cues"
            base_prompt += "\n- Write conversationally for speaking"
            base_prompt += "\n- Include intro hook and outro CTA"
        
        if custom_instructions:
            base_prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}"
        
        base_prompt += f"\n\nGenerate engaging, high-quality {spec.format.value.replace('_', ' ')} content now:"
        
        return base_prompt
    
    def _parse_format_response(self, response_text: str, content_format: ContentFormat) -> Dict[str, Any]:
        """Parse and structure the AI response for the specific format"""
        
        structured_content = {
            "raw_content": response_text,
            "format": content_format.value
        }
        
        # Format-specific parsing
        if content_format == ContentFormat.TWITTER_THREAD:
            # Extract individual tweets
            tweets = []
            lines = response_text.split('\n')
            current_tweet = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith(('1/', '2/', '3/', '4/', '5/', '6/', '7/', '8/', '9/')):
                    if current_tweet:
                        tweets.append(current_tweet.strip())
                    current_tweet = line
                elif current_tweet and line:
                    current_tweet += " " + line
            
            if current_tweet:
                tweets.append(current_tweet.strip())
            
            structured_content["tweets"] = tweets
            structured_content["thread_count"] = len(tweets)
        
        elif content_format == ContentFormat.NEWSLETTER:
            # Extract sections if formatted
            sections = {}
            current_section = "main"
            content_parts = response_text.split('\n\n')
            
            for part in content_parts:
                if part.lower().startswith(('subject:', 'title:')):
                    sections['subject'] = part.split(':', 1)[1].strip()
                elif part.lower().startswith('introduction'):
                    current_section = "introduction"
                    sections[current_section] = part
                elif part.lower().startswith('conclusion'):
                    current_section = "conclusion"  
                    sections[current_section] = part
                else:
                    if current_section not in sections:
                        sections[current_section] = part
                    else:
                        sections[current_section] += "\n\n" + part
            
            structured_content["sections"] = sections
        
        # Extract hashtags if present
        hashtags = []
        for word in response_text.split():
            if word.startswith('#') and len(word) > 1:
                hashtags.append(word)
        
        if hashtags:
            structured_content["hashtags"] = hashtags
        
        # Calculate metrics
        structured_content["character_count"] = len(response_text)
        structured_content["word_count"] = len(response_text.split())
        
        return structured_content

    async def repurpose_content(
        self,
        source_format: str,
        target_formats: List[str], 
        content: str,
        preserve_core_message: bool = True
    ) -> Dict[str, Any]:
        """Repurpose existing content from one format to others"""
        
        try:
            # Validate formats
            try:
                source_format_enum = ContentFormat(source_format)
            except ValueError:
                return {"error": f"Invalid source format: {source_format}"}
            
            valid_target_formats = []
            for format_name in target_formats:
                try:
                    target_format_enum = ContentFormat(format_name)
                    valid_target_formats.append(target_format_enum)
                except ValueError:
                    continue
            
            if not valid_target_formats:
                return {"error": "No valid target formats specified"}
            
            # Generate repurposed content
            repurposed_content = {}
            
            for target_format in valid_target_formats:
                prompt = f"""
                Repurpose the following {source_format.replace('_', ' ')} content into {target_format.value.replace('_', ' ')} format.
                
                ORIGINAL CONTENT:
                {content}
                
                REQUIREMENTS:
                - Preserve core message: {preserve_core_message}
                - Adapt to {target_format.value.replace('_', ' ')} style and constraints
                - {self.PLATFORM_SPECS[target_format].style_notes}
                """
                
                if self.PLATFORM_SPECS[target_format].character_limit:
                    prompt += f"\n- Stay within {self.PLATFORM_SPECS[target_format].character_limit} characters"
                
                if self.PLATFORM_SPECS[target_format].word_limit:
                    prompt += f"\n- Stay within {self.PLATFORM_SPECS[target_format].word_limit} words"
                
                response = self.model.generate_content(prompt)
                
                if response.text:
                    structured = self._parse_format_response(response.text, target_format)
                    repurposed_content[target_format.value] = structured
            
            return {
                "success": True,
                "repurposed_content": repurposed_content,
                "metadata": {
                    "source_format": source_format,
                    "target_formats": [f.value for f in valid_target_formats],
                    "repurposed_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to repurpose content: {str(e)}"}


# Initialize the server
def create_multi_format_generator():
    return MultiFormatContentGenerator()
