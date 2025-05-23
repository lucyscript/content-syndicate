"""
Personalization MCP Server
Adapts content to audience preferences and segments
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from collections import Counter

from mcp.server.fastmcp import FastMCP
from ..models import User, Subscriber, NewsletterAnalytics, ContentPreference


class PersonalizationServer:
    def __init__(self):
        self.mcp = FastMCP("personalization")
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.mcp.tool()
        async def analyze_audience_preferences(
            user_id: int,
            subscriber_data: List[Dict[str, Any]] = None,
            analytics_data: List[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Analyze audience preferences based on engagement data"""
            return await self.analyze_audience_preferences(user_id, subscriber_data, analytics_data)
        
        @self.mcp.tool()
        async def segment_audience(
            subscribers: List[Dict[str, Any]],
            segmentation_criteria: List[str] = None
        ) -> Dict[str, List[Dict[str, Any]]]:
            """Segment audience based on various criteria"""
            return await self.segment_audience(subscribers, segmentation_criteria)
        
        @self.mcp.tool()
        async def personalize_content(
            content: str,
            target_segment: Dict[str, Any],
            personalization_level: str = "medium"
        ) -> Dict[str, Any]:
            """Personalize content for a specific audience segment"""
            return await self.personalize_content(content, target_segment, personalization_level)
        
        @self.mcp.tool()
        async def recommend_send_time(
            user_id: int,
            subscriber_timezone_data: List[Dict[str, Any]] = None,
            historical_engagement: List[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Recommend optimal send time for newsletter"""
            return await self.recommend_send_time(user_id, subscriber_timezone_data, historical_engagement)
        
        @self.mcp.tool()
        async def generate_dynamic_subject_lines(
            base_subject: str,
            segments: Dict[str, List[Dict[str, Any]]]
        ) -> Dict[str, str]:
            """Generate dynamic subject lines for different segments"""
            return await self.generate_dynamic_subject_lines(base_subject, segments)
    
    async def analyze_audience_preferences(
        self,
        user_id: int,
        subscriber_data: List[Dict[str, Any]] = None,
        analytics_data: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze audience preferences based on engagement data
        
        Args:
            user_id: User ID to analyze
            subscriber_data: List of subscriber information
            analytics_data: List of engagement analytics
        """
        try:
            # Analyze engagement patterns
            engagement_patterns = self._analyze_engagement_patterns(analytics_data or [])
            
            # Analyze content preferences
            content_preferences = self._analyze_content_preferences(subscriber_data or [])
            
            # Analyze demographics
            demographics = self._analyze_demographics(subscriber_data or [])
            
            # Generate insights
            insights = self._generate_insights(engagement_patterns, content_preferences, demographics)
            
            return {
                "user_id": user_id,
                "engagement_patterns": engagement_patterns,
                "content_preferences": content_preferences,
                "demographics": demographics,
                "insights": insights,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze audience preferences: {str(e)}"}
    
    async def segment_audience(
        self,
        subscribers: List[Dict[str, Any]],
        segmentation_criteria: List[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Segment audience based on various criteria
        
        Args:
            subscribers: List of subscriber data
            segmentation_criteria: Criteria for segmentation
        """
        try:
            if not segmentation_criteria:
                segmentation_criteria = ["engagement_level", "preferences", "demographics"]
            
            segments = {}
            
            # Engagement-based segmentation
            if "engagement_level" in segmentation_criteria:
                engagement_segments = self._segment_by_engagement(subscribers)
                segments.update(engagement_segments)
            
            # Preference-based segmentation
            if "preferences" in segmentation_criteria:
                preference_segments = self._segment_by_preferences(subscribers)
                segments.update(preference_segments)
            
            # Demographic segmentation
            if "demographics" in segmentation_criteria:
                demographic_segments = self._segment_by_demographics(subscribers)
                segments.update(demographic_segments)
            
            # Behavioral segmentation
            if "behavior" in segmentation_criteria:
                behavioral_segments = self._segment_by_behavior(subscribers)
                segments.update(behavioral_segments)
            
            return segments
            
        except Exception as e:
            return {"error": f"Failed to segment audience: {str(e)}"}
    
    async def personalize_content(
        self,
        content: str,
        target_segment: Dict[str, Any],
        personalization_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Personalize content for a specific audience segment
        
        Args:
            content: Original content to personalize
            target_segment: Target audience segment data
            personalization_level: Level of personalization (low, medium, high)
        """
        try:
            # Extract segment characteristics
            segment_characteristics = self._extract_segment_characteristics(target_segment)
            
            # Generate personalization strategy
            strategy = self._create_personalization_strategy(
                segment_characteristics, 
                personalization_level
            )
            
            # Apply personalization
            personalized_content = self._apply_personalization(content, strategy)
            
            return {
                "original_content": content,
                "personalized_content": personalized_content,
                "target_segment": target_segment,
                "strategy": strategy,
                "personalization_level": personalization_level,
                "personalized_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to personalize content: {str(e)}"}
    
    async def recommend_send_time(
        self,
        user_id: int,
        subscriber_timezone_data: List[Dict[str, Any]] = None,
        historical_engagement: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recommend optimal send time for newsletter
        
        Args:
            user_id: User ID
            subscriber_timezone_data: Timezone data for subscribers
            historical_engagement: Historical engagement data by time
        """
        try:
            # Analyze timezone distribution
            timezone_analysis = self._analyze_timezones(subscriber_timezone_data or [])
            
            # Analyze engagement by time
            time_analysis = self._analyze_engagement_by_time(historical_engagement or [])
            
            # Recommend optimal times
            recommendations = self._generate_time_recommendations(
                timezone_analysis, 
                time_analysis
            )
            
            return {
                "user_id": user_id,
                "timezone_analysis": timezone_analysis,
                "engagement_analysis": time_analysis,
                "recommendations": recommendations,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to recommend send time: {str(e)}"}
    
    async def generate_dynamic_subject_lines(
        self,
        base_subject: str,
        segments: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, str]:
        """
        Generate dynamic subject lines for different segments
        
        Args:
            base_subject: Base subject line
            segments: Audience segments with their characteristics
        """
        try:
            personalized_subjects = {}
            
            for segment_name, segment_data in segments.items():
                # Analyze segment characteristics
                characteristics = self._extract_segment_characteristics({"subscribers": segment_data})
                
                # Personalize subject line
                personalized_subject = self._personalize_subject_line(base_subject, characteristics)
                
                personalized_subjects[segment_name] = personalized_subject
            
            return personalized_subjects
            
        except Exception as e:
            return {"error": f"Failed to generate dynamic subject lines: {str(e)}"}
    
    def _analyze_engagement_patterns(self, analytics_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement patterns from analytics data"""
        if not analytics_data:
            return {"open_rate": 0, "click_rate": 0, "engagement_score": 0}
        
        total_sent = len(analytics_data)
        opens = sum(1 for data in analytics_data if data.get("opened_at"))
        clicks = sum(1 for data in analytics_data if data.get("clicked_at"))
        
        # Analyze engagement by day of week
        day_engagement = {}
        hour_engagement = {}
        
        for data in analytics_data:
            if data.get("opened_at"):
                dt = datetime.fromisoformat(data["opened_at"].replace('Z', '+00:00'))
                day = dt.strftime('%A')
                hour = dt.hour
                
                day_engagement[day] = day_engagement.get(day, 0) + 1
                hour_engagement[hour] = hour_engagement.get(hour, 0) + 1
        
        return {
            "total_sent": total_sent,
            "total_opens": opens,
            "total_clicks": clicks,
            "open_rate": (opens / total_sent * 100) if total_sent > 0 else 0,
            "click_rate": (clicks / total_sent * 100) if total_sent > 0 else 0,
            "best_days": sorted(day_engagement.items(), key=lambda x: x[1], reverse=True)[:3],
            "best_hours": sorted(hour_engagement.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    def _analyze_content_preferences(self, subscriber_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content preferences from subscriber data"""
        if not subscriber_data:
            return {"top_topics": [], "content_types": []}
        
        all_tags = []
        all_preferences = []
        
        for subscriber in subscriber_data:
            tags = subscriber.get("tags", [])
            preferences = subscriber.get("preferences", {})
            
            if isinstance(tags, list):
                all_tags.extend(tags)
            
            if isinstance(preferences, dict):
                for key, value in preferences.items():
                    all_preferences.append((key, value))
        
        # Count tag frequency
        tag_counts = Counter(all_tags)
        
        # Analyze preferences
        preference_analysis = {}
        for key, value in all_preferences:
            if key not in preference_analysis:
                preference_analysis[key] = []
            preference_analysis[key].append(value)
        
        return {
            "top_topics": list(tag_counts.most_common(10)),
            "preference_distribution": preference_analysis,
            "total_subscribers": len(subscriber_data)
        }
    
    def _analyze_demographics(self, subscriber_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze demographic data"""
        if not subscriber_data:
            return {"total_subscribers": 0}
        
        # Analyze subscription dates to understand growth
        subscription_dates = []
        for subscriber in subscriber_data:
            if subscriber.get("subscription_date"):
                subscription_dates.append(subscriber["subscription_date"])
        
        # Analyze engagement scores
        engagement_scores = []
        for subscriber in subscriber_data:
            score = subscriber.get("engagement_score", 0)
            if isinstance(score, (int, float)):
                engagement_scores.append(score)
        
        avg_engagement = np.mean(engagement_scores) if engagement_scores else 0
        
        return {
            "total_subscribers": len(subscriber_data),
            "average_engagement_score": float(avg_engagement),
            "recent_subscribers": len([d for d in subscription_dates 
                                     if datetime.fromisoformat(d.replace('Z', '+00:00')) > 
                                     datetime.utcnow() - timedelta(days=30)]),
            "high_engagement_count": len([s for s in engagement_scores if s > 70])
        }
    
    def _generate_insights(self, engagement_patterns: Dict, content_preferences: Dict, demographics: Dict) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        # Engagement insights
        if engagement_patterns.get("open_rate", 0) > 25:
            insights.append("Above-average open rate indicates strong subject line performance")
        elif engagement_patterns.get("open_rate", 0) < 15:
            insights.append("Low open rate suggests need for better subject lines and send time optimization")
        
        # Content insights
        top_topics = content_preferences.get("top_topics", [])
        if top_topics:
            insights.append(f"Most popular topics: {', '.join([topic[0] for topic in top_topics[:3]])}")
        
        # Demographic insights
        if demographics.get("recent_subscribers", 0) > demographics.get("total_subscribers", 1) * 0.2:
            insights.append("Strong recent growth - focus on onboarding content")
        
        return insights
    
    def _segment_by_engagement(self, subscribers: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Segment subscribers by engagement level"""
        high_engagement = []
        medium_engagement = []
        low_engagement = []
        
        for subscriber in subscribers:
            score = subscriber.get("engagement_score", 0)
            if score >= 70:
                high_engagement.append(subscriber)
            elif score >= 30:
                medium_engagement.append(subscriber)
            else:
                low_engagement.append(subscriber)
        
        return {
            "high_engagement": high_engagement,
            "medium_engagement": medium_engagement,
            "low_engagement": low_engagement
        }
    
    def _segment_by_preferences(self, subscribers: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Segment subscribers by content preferences"""
        segments = {}
        
        for subscriber in subscribers:
            tags = subscriber.get("tags", [])
            for tag in tags:
                if tag not in segments:
                    segments[tag] = []
                segments[tag].append(subscriber)
        
        return segments
    
    def _segment_by_demographics(self, subscribers: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Segment subscribers by demographics"""
        new_subscribers = []
        long_time_subscribers = []
        
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        for subscriber in subscribers:
            sub_date = subscriber.get("subscription_date")
            if sub_date:
                if datetime.fromisoformat(sub_date.replace('Z', '+00:00')) > cutoff_date:
                    new_subscribers.append(subscriber)
                else:
                    long_time_subscribers.append(subscriber)
        
        return {
            "new_subscribers": new_subscribers,
            "long_time_subscribers": long_time_subscribers
        }
    
    def _segment_by_behavior(self, subscribers: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Segment subscribers by behavior patterns"""
        frequent_openers = []
        occasional_openers = []
        rare_openers = []
        
        for subscriber in subscribers:
            total_opens = subscriber.get("total_opens", 0)
            if total_opens >= 10:
                frequent_openers.append(subscriber)
            elif total_opens >= 3:
                occasional_openers.append(subscriber)
            else:
                rare_openers.append(subscriber)
        
        return {
            "frequent_openers": frequent_openers,
            "occasional_openers": occasional_openers,
            "rare_openers": rare_openers
        }
    
    def _extract_segment_characteristics(self, segment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key characteristics from segment data"""
        subscribers = segment_data.get("subscribers", [])
        
        if not subscribers:
            return {}
        
        # Calculate average engagement
        avg_engagement = np.mean([s.get("engagement_score", 0) for s in subscribers])
        
        # Most common tags
        all_tags = []
        for s in subscribers:
            all_tags.extend(s.get("tags", []))
        common_tags = Counter(all_tags).most_common(5)
        
        return {
            "size": len(subscribers),
            "avg_engagement": float(avg_engagement),
            "common_tags": [tag[0] for tag in common_tags],
            "characteristics": common_tags
        }
    
    def _create_personalization_strategy(self, characteristics: Dict[str, Any], level: str) -> Dict[str, Any]:
        """Create personalization strategy based on characteristics"""
        strategy = {
            "tone_adjustments": [],
            "content_focus": [],
            "call_to_action": "standard"
        }
        
        avg_engagement = characteristics.get("avg_engagement", 0)
        common_tags = characteristics.get("common_tags", [])
        
        # Adjust tone based on engagement
        if avg_engagement > 70:
            strategy["tone_adjustments"].append("enthusiastic")
            strategy["call_to_action"] = "strong"
        elif avg_engagement < 30:
            strategy["tone_adjustments"].append("gentle")
            strategy["call_to_action"] = "soft"
        
        # Focus content based on interests
        if common_tags:
            strategy["content_focus"] = common_tags[:3]
        
        # Adjust based on personalization level
        if level == "high":
            strategy["include_personal_elements"] = True
            strategy["dynamic_content"] = True
        elif level == "low":
            strategy["minimal_changes"] = True
        
        return strategy
    
    def _apply_personalization(self, content: str, strategy: Dict[str, Any]) -> str:
        """Apply personalization strategy to content"""
        personalized = content
        
        # Apply tone adjustments
        tone_adjustments = strategy.get("tone_adjustments", [])
        if "enthusiastic" in tone_adjustments:
            personalized = personalized.replace(".", "!")
            personalized = personalized.replace("interesting", "exciting")
        elif "gentle" in tone_adjustments:
            personalized = personalized.replace("must", "might want to")
            personalized = personalized.replace("should", "could")
        
        # Focus on specific topics
        content_focus = strategy.get("content_focus", [])
        if content_focus:
            # Add topic-specific callouts
            personalized += f"\n\n💡 Since you're interested in {', '.join(content_focus)}, you'll find this particularly relevant!"
        
        return personalized
    
    def _analyze_timezones(self, timezone_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze subscriber timezone distribution"""
        if not timezone_data:
            return {"primary_timezone": "UTC", "distribution": {}}
        
        timezone_counts = Counter([tz.get("timezone", "UTC") for tz in timezone_data])
        
        return {
            "primary_timezone": timezone_counts.most_common(1)[0][0],
            "distribution": dict(timezone_counts),
            "total_timezones": len(timezone_counts)
        }
    
    def _analyze_engagement_by_time(self, engagement_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement patterns by time"""
        if not engagement_data:
            return {"best_hour": 9, "best_day": "Tuesday"}
        
        hour_engagement = {}
        day_engagement = {}
        
        for data in engagement_data:
            if data.get("opened_at"):
                dt = datetime.fromisoformat(data["opened_at"].replace('Z', '+00:00'))
                hour = dt.hour
                day = dt.strftime('%A')
                
                hour_engagement[hour] = hour_engagement.get(hour, 0) + 1
                day_engagement[day] = day_engagement.get(day, 0) + 1
        
        best_hour = max(hour_engagement.items(), key=lambda x: x[1])[0] if hour_engagement else 9
        best_day = max(day_engagement.items(), key=lambda x: x[1])[0] if day_engagement else "Tuesday"
        
        return {
            "best_hour": best_hour,
            "best_day": best_day,
            "hour_distribution": hour_engagement,
            "day_distribution": day_engagement
        }
    
    def _generate_time_recommendations(self, timezone_analysis: Dict, time_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate send time recommendations"""
        recommendations = []
        
        primary_tz = timezone_analysis.get("primary_timezone", "UTC")
        best_hour = time_analysis.get("best_hour", 9)
        best_day = time_analysis.get("best_day", "Tuesday")
        
        recommendations.append({
            "type": "optimal",
            "day": best_day,
            "hour": best_hour,
            "timezone": primary_tz,
            "confidence": "high",
            "reason": "Based on historical engagement patterns"
        })
        
        # Add alternative recommendations
        alternative_hours = [best_hour - 2, best_hour + 2]
        for alt_hour in alternative_hours:
            if 6 <= alt_hour <= 22:  # Reasonable hours
                recommendations.append({
                    "type": "alternative",
                    "day": best_day,
                    "hour": alt_hour,
                    "timezone": primary_tz,
                    "confidence": "medium",
                    "reason": "Alternative time with good potential"
                })
        
        return recommendations
    
    def _personalize_subject_line(self, base_subject: str, characteristics: Dict[str, Any]) -> str:
        """Personalize subject line for segment characteristics"""
        personalized = base_subject
        
        common_tags = characteristics.get("common_tags", [])
        avg_engagement = characteristics.get("avg_engagement", 0)
        
        # Add engagement-based modifications
        if avg_engagement > 70:
            personalized = f"🔥 {personalized}"
        elif avg_engagement < 30:
            personalized = f"💡 {personalized}"
        
        # Add topic-specific elements
        if "tech" in common_tags:
            personalized = personalized.replace("news", "tech updates")
        elif "business" in common_tags:
            personalized = personalized.replace("insights", "business insights")
        
        return personalized


def create_personalization_server():
    """Factory function to create personalization server"""
    return PersonalizationServer()
