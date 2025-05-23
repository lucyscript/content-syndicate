"""
Analytics MCP Server
Tracks performance and engagement metrics
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, Counter

from mcp.server.fastmcp import FastMCP


class AnalyticsServer:
    def __init__(self):
        self.mcp = FastMCP("analytics")
        self._register_tools()
      def _register_tools(self):
        """Register MCP tools"""
        
        @self.mcp.tool()
        async def track_newsletter_performance(
            newsletter_id: int,
            engagement_data: List[Dict[str, Any]],
            time_period: str = "7d"
        ) -> Dict[str, Any]:
            """Track newsletter performance metrics"""
            return await self.track_newsletter_performance_impl(newsletter_id, engagement_data, time_period)
        
        @self.mcp.tool()
        async def analyze_content_performance(
            content_data: List[Dict[str, Any]],
            comparison_period: str = "30d"
        ) -> Dict[str, Any]:
            """Analyze content performance across newsletters"""
            return await self.analyze_content_performance_impl(content_data, comparison_period)
        
        @self.mcp.tool()
        async def generate_audience_insights(
            subscriber_data: List[Dict[str, Any]],
            engagement_history: List[Dict[str, Any]]
        ) -> Dict[str, Any]:
            """Generate comprehensive audience insights"""
            return await self.generate_audience_insights_impl(subscriber_data, engagement_history)
        
        @self.mcp.tool()
        async def create_performance_dashboard(
            user_id: int,
            dashboard_type: str = "overview",
            date_range: Dict[str, str] = None
        ) -> Dict[str, Any]:
            """Create performance dashboard data"""
            return await self.create_performance_dashboard_impl(user_id, dashboard_type, date_range)
        
        @self.mcp.tool()
        async def predict_engagement(
            historical_data: List[Dict[str, Any]],
            content_features: Dict[str, Any] = None,
            prediction_horizon: str = "7d"
        ) -> Dict[str, Any]:
            """Predict engagement for future content"""
            return await self.predict_engagement_impl(historical_data, content_features, prediction_horizon)
        
        @self.mcp.tool()
        async def analyze_ab_test_results(
            test_data: Dict[str, List[Dict[str, Any]]],
            test_metric: str = "open_rate",
            confidence_level: float = 0.95
        ) -> Dict[str, Any]:
            """Analyze A/B test results for newsletters"""
            return await self.analyze_ab_test_results_impl(test_data, test_metric, confidence_level)
    
    async def track_newsletter_performance_impl(
        self,
        newsletter_id: int,
        engagement_data: List[Dict[str, Any]],
        time_period: str = "7d"
    ) -> Dict[str, Any]:
        """
        Track newsletter performance metrics
        
        Args:
            newsletter_id: Newsletter ID to track
            engagement_data: List of engagement events
            time_period: Time period for analysis (1d, 7d, 30d)
        """
        try:
            # Calculate basic metrics
            metrics = self._calculate_basic_metrics(engagement_data)
            
            # Calculate engagement trends
            trends = self._calculate_engagement_trends(engagement_data, time_period)
            
            # Analyze reader behavior
            behavior = self._analyze_reader_behavior(engagement_data)
            
            # Generate insights
            insights = self._generate_performance_insights(metrics, trends, behavior)
            
            return {
                "newsletter_id": newsletter_id,
                "metrics": metrics,
                "trends": trends,
                "behavior_analysis": behavior,
                "insights": insights,
                "analyzed_at": datetime.utcnow().isoformat(),
                "time_period": time_period
            }
            
        except Exception as e:
            return {"error": f"Failed to track newsletter performance: {str(e)}"}
    
    async def analyze_content_performance_impl(
        self,
        content_data: List[Dict[str, Any]],
        comparison_period: str = "30d"
    ) -> Dict[str, Any]:
        """
        Analyze content performance across newsletters
        
        Args:
            content_data: List of content performance data
            comparison_period: Period for comparison analysis
        """
        try:
            # Analyze top performing content
            top_content = self._analyze_top_content(content_data)
            
            # Analyze content trends
            content_trends = self._analyze_content_trends(content_data, comparison_period)
            
            # Topic performance analysis
            topic_performance = self._analyze_topic_performance(content_data)
            
            # Content optimization recommendations
            recommendations = self._generate_content_recommendations(
                top_content, content_trends, topic_performance
            )
            
            return {
                "top_performing_content": top_content,
                "content_trends": content_trends,
                "topic_performance": topic_performance,
                "recommendations": recommendations,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze content performance: {str(e)}"}
    
    async def generate_audience_insights_impl(
        self,
        subscriber_data: List[Dict[str, Any]],
        engagement_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive audience insights
        
        Args:
            subscriber_data: List of subscriber information
            engagement_history: Historical engagement data
        """
        try:
            # Audience demographics
            demographics = self._analyze_audience_demographics(subscriber_data)
            
            # Engagement patterns
            engagement_patterns = self._analyze_engagement_patterns(engagement_history)
            
            # Subscriber lifecycle analysis
            lifecycle = self._analyze_subscriber_lifecycle(subscriber_data, engagement_history)
            
            # Churn analysis
            churn_analysis = self._analyze_churn_risk(subscriber_data, engagement_history)
            
            # Growth analysis
            growth_analysis = self._analyze_audience_growth(subscriber_data)
            
            return {
                "demographics": demographics,
                "engagement_patterns": engagement_patterns,
                "lifecycle_analysis": lifecycle,
                "churn_analysis": churn_analysis,
                "growth_analysis": growth_analysis,
                "total_subscribers": len(subscriber_data),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to generate audience insights: {str(e)}"}
    
    async def create_performance_dashboard_impl(
        self,
        user_id: int,
        dashboard_type: str = "overview",
        date_range: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Create performance dashboard data
        
        Args:
            user_id: User ID for dashboard
            dashboard_type: Type of dashboard (overview, detailed, comparison)
            date_range: Date range for dashboard data
        """
        try:
            if not date_range:
                date_range = {
                    "start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                    "end": datetime.utcnow().isoformat()
                }
            
            # Get dashboard data based on type
            if dashboard_type == "overview":
                dashboard_data = self._create_overview_dashboard(user_id, date_range)
            elif dashboard_type == "detailed":
                dashboard_data = self._create_detailed_dashboard(user_id, date_range)
            elif dashboard_type == "comparison":
                dashboard_data = self._create_comparison_dashboard(user_id, date_range)
            else:
                dashboard_data = self._create_overview_dashboard(user_id, date_range)
            
            return {
                "user_id": user_id,
                "dashboard_type": dashboard_type,
                "date_range": date_range,
                "data": dashboard_data,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to create dashboard: {str(e)}"}
    
    async def predict_engagement_impl(
        self,
        historical_data: List[Dict[str, Any]],
        content_features: Dict[str, Any] = None,
        prediction_horizon: str = "7d"
    ) -> Dict[str, Any]:
        """
        Predict engagement for future content
        
        Args:
            historical_data: Historical engagement data
            content_features: Features of the content to predict for
            prediction_horizon: How far ahead to predict
        """
        try:
            # Analyze historical patterns
            patterns = self._extract_engagement_patterns(historical_data)
            
            # Calculate baseline metrics
            baseline = self._calculate_baseline_metrics(historical_data)
            
            # Generate predictions
            predictions = self._generate_engagement_predictions(
                patterns, baseline, content_features, prediction_horizon
            )
            
            # Calculate confidence intervals
            confidence = self._calculate_prediction_confidence(historical_data, predictions)
            
            return {
                "predictions": predictions,
                "confidence_intervals": confidence,
                "baseline_metrics": baseline,
                "prediction_horizon": prediction_horizon,
                "predicted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to predict engagement: {str(e)}"}
    
    async def analyze_ab_test_results_impl(
        self,
        test_data: Dict[str, List[Dict[str, Any]]],
        test_metric: str = "open_rate",
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Analyze A/B test results for newsletters
        
        Args:
            test_data: Test data with variant A and B
            test_metric: Metric to analyze (open_rate, click_rate, engagement_score)
            confidence_level: Statistical confidence level
        """
        try:
            # Extract metrics for each variant
            variant_a_metrics = self._extract_test_metrics(test_data.get("variant_a", []), test_metric)
            variant_b_metrics = self._extract_test_metrics(test_data.get("variant_b", []), test_metric)
            
            # Calculate statistical significance
            significance = self._calculate_statistical_significance(
                variant_a_metrics, variant_b_metrics, confidence_level
            )
            
            # Determine winner
            winner = self._determine_test_winner(variant_a_metrics, variant_b_metrics, significance)
            
            # Generate recommendations
            recommendations = self._generate_test_recommendations(
                variant_a_metrics, variant_b_metrics, winner, significance
            )
            
            return {
                "variant_a": {
                    "metrics": variant_a_metrics,
                    "sample_size": len(test_data.get("variant_a", []))
                },
                "variant_b": {
                    "metrics": variant_b_metrics,
                    "sample_size": len(test_data.get("variant_b", []))
                },
                "statistical_analysis": significance,
                "winner": winner,
                "recommendations": recommendations,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze A/B test: {str(e)}"}
    
    def _calculate_basic_metrics(self, engagement_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic engagement metrics"""
        if not engagement_data:
            return {"sent": 0, "opened": 0, "clicked": 0, "open_rate": 0, "click_rate": 0}
        
        total_sent = len(engagement_data)
        total_opened = sum(1 for data in engagement_data if data.get("opened_at"))
        total_clicked = sum(1 for data in engagement_data if data.get("clicked_at"))
        total_unsubscribed = sum(1 for data in engagement_data if data.get("unsubscribed_at"))
        
        open_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0
        click_rate = (total_clicked / total_sent * 100) if total_sent > 0 else 0
        click_to_open_rate = (total_clicked / total_opened * 100) if total_opened > 0 else 0
        unsubscribe_rate = (total_unsubscribed / total_sent * 100) if total_sent > 0 else 0
        
        return {
            "sent": total_sent,
            "opened": total_opened,
            "clicked": total_clicked,
            "unsubscribed": total_unsubscribed,
            "open_rate": round(open_rate, 2),
            "click_rate": round(click_rate, 2),
            "click_to_open_rate": round(click_to_open_rate, 2),
            "unsubscribe_rate": round(unsubscribe_rate, 2)
        }
    
    def _calculate_engagement_trends(self, engagement_data: List[Dict[str, Any]], time_period: str) -> Dict[str, Any]:
        """Calculate engagement trends over time"""
        if not engagement_data:
            return {"trend": "stable", "change_percentage": 0}
        
        # Group data by time periods
        time_groups = defaultdict(list)
        
        for data in engagement_data:
            if data.get("opened_at"):
                date = datetime.fromisoformat(data["opened_at"].replace('Z', '+00:00'))
                # Group by day for trend analysis
                day_key = date.strftime('%Y-%m-%d')
                time_groups[day_key].append(data)
        
        # Calculate daily open rates
        daily_rates = []
        for day, day_data in time_groups.items():
            day_opens = sum(1 for d in day_data if d.get("opened_at"))
            day_total = len(day_data)
            day_rate = (day_opens / day_total * 100) if day_total > 0 else 0
            daily_rates.append(day_rate)
        
        if len(daily_rates) < 2:
            return {"trend": "insufficient_data", "change_percentage": 0}
        
        # Calculate trend
        first_half = daily_rates[:len(daily_rates)//2]
        second_half = daily_rates[len(daily_rates)//2:]
        
        avg_first = np.mean(first_half)
        avg_second = np.mean(second_half)
        
        change_percentage = ((avg_second - avg_first) / avg_first * 100) if avg_first > 0 else 0
        
        if change_percentage > 5:
            trend = "improving"
        elif change_percentage < -5:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_percentage": round(change_percentage, 2),
            "daily_rates": daily_rates,
            "average_first_half": round(avg_first, 2),
            "average_second_half": round(avg_second, 2)
        }
    
    def _analyze_reader_behavior(self, engagement_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze reader behavior patterns"""
        if not engagement_data:
            return {}
        
        # Analyze time to open
        time_to_open = []
        for data in engagement_data:
            if data.get("opened_at") and data.get("sent_at"):
                opened = datetime.fromisoformat(data["opened_at"].replace('Z', '+00:00'))
                sent = datetime.fromisoformat(data["sent_at"].replace('Z', '+00:00'))
                hours_to_open = (opened - sent).total_seconds() / 3600
                time_to_open.append(hours_to_open)
        
        # Analyze reading time
        reading_times = [data.get("time_spent_reading", 0) for data in engagement_data 
                        if data.get("time_spent_reading")]
        
        # Analyze click patterns
        clicked_links = []
        for data in engagement_data:
            if data.get("clicked_links"):
                clicked_links.extend(data["clicked_links"])
        
        link_popularity = Counter(clicked_links)
        
        return {
            "avg_time_to_open_hours": round(np.mean(time_to_open), 2) if time_to_open else 0,
            "median_time_to_open_hours": round(np.median(time_to_open), 2) if time_to_open else 0,
            "avg_reading_time_seconds": round(np.mean(reading_times), 2) if reading_times else 0,
            "popular_links": list(link_popularity.most_common(5)),
            "quick_readers": len([t for t in reading_times if t < 30]),
            "engaged_readers": len([t for t in reading_times if t > 120])
        }
    
    def _generate_performance_insights(self, metrics: Dict, trends: Dict, behavior: Dict) -> List[str]:
        """Generate actionable performance insights"""
        insights = []
        
        # Open rate insights
        open_rate = metrics.get("open_rate", 0)
        if open_rate > 25:
            insights.append("Excellent open rate! Your subject lines are performing well.")
        elif open_rate > 20:
            insights.append("Good open rate. Consider A/B testing subject lines for improvement.")
        elif open_rate > 15:
            insights.append("Average open rate. Focus on improving subject lines and send times.")
        else:
            insights.append("Low open rate. Review subject lines, sender reputation, and timing.")
        
        # Click rate insights
        click_rate = metrics.get("click_rate", 0)
        if click_rate > 5:
            insights.append("High engagement! Your content is resonating with readers.")
        elif click_rate > 2:
            insights.append("Good click rate. Consider adding more compelling calls-to-action.")
        else:
            insights.append("Low click rate. Review content relevance and call-to-action placement.")
        
        # Trend insights
        trend = trends.get("trend", "stable")
        if trend == "improving":
            insights.append("Engagement is trending upward. Keep up the good work!")
        elif trend == "declining":
            insights.append("Engagement is declining. Consider refreshing your content strategy.")
        
        # Behavior insights
        avg_reading_time = behavior.get("avg_reading_time_seconds", 0)
        if avg_reading_time > 120:
            insights.append("Readers are spending good time with your content.")
        elif avg_reading_time < 30:
            insights.append("Short reading times suggest content may be too long or not engaging enough.")
        
        return insights
    
    def _analyze_top_content(self, content_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze top performing content"""
        if not content_data:
            return []
        
        # Sort by engagement metrics
        sorted_content = sorted(
            content_data,
            key=lambda x: x.get("engagement_score", 0),
            reverse=True
        )
        
        top_content = []
        for content in sorted_content[:10]:
            top_content.append({
                "title": content.get("title", "Untitled"),
                "engagement_score": content.get("engagement_score", 0),
                "open_rate": content.get("open_rate", 0),
                "click_rate": content.get("click_rate", 0),
                "topic": content.get("topic", "General"),
                "publish_date": content.get("publish_date", "")
            })
        
        return top_content
    
    def _analyze_content_trends(self, content_data: List[Dict[str, Any]], period: str) -> Dict[str, Any]:
        """Analyze content performance trends"""
        if not content_data:
            return {}
        
        # Group by topic
        topic_performance = defaultdict(list)
        for content in content_data:
            topic = content.get("topic", "General")
            topic_performance[topic].append(content.get("engagement_score", 0))
        
        # Calculate average performance by topic
        topic_averages = {}
        for topic, scores in topic_performance.items():
            topic_averages[topic] = round(np.mean(scores), 2)
        
        # Sort topics by performance
        sorted_topics = sorted(topic_averages.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "best_performing_topics": sorted_topics[:5],
            "worst_performing_topics": sorted_topics[-3:],
            "topic_performance": topic_averages
        }
    
    def _analyze_topic_performance(self, content_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detailed topic performance analysis"""
        if not content_data:
            return {}
        
        topic_stats = defaultdict(lambda: {
            "count": 0,
            "total_engagement": 0,
            "total_opens": 0,
            "total_clicks": 0
        })
        
        for content in content_data:
            topic = content.get("topic", "General")
            stats = topic_stats[topic]
            
            stats["count"] += 1
            stats["total_engagement"] += content.get("engagement_score", 0)
            stats["total_opens"] += content.get("opens", 0)
            stats["total_clicks"] += content.get("clicks", 0)
        
        # Calculate averages
        topic_analysis = {}
        for topic, stats in topic_stats.items():
            count = stats["count"]
            topic_analysis[topic] = {
                "content_count": count,
                "avg_engagement": round(stats["total_engagement"] / count, 2),
                "avg_opens": round(stats["total_opens"] / count, 2),
                "avg_clicks": round(stats["total_clicks"] / count, 2),
                "total_performance": stats["total_engagement"]
            }
        
        return topic_analysis
    
    def _generate_content_recommendations(self, top_content: List, trends: Dict, topic_performance: Dict) -> List[str]:
        """Generate content optimization recommendations"""
        recommendations = []
        
        # Topic recommendations
        best_topics = trends.get("best_performing_topics", [])
        if best_topics:
            recommendations.append(
                f"Focus more on {best_topics[0][0]} content - it's your best performing topic"
            )
        
        # Content frequency recommendations
        if len(top_content) > 0:
            avg_engagement = np.mean([c.get("engagement_score", 0) for c in top_content])
            if avg_engagement > 70:
                recommendations.append("Your content quality is high - consider increasing frequency")
            elif avg_engagement < 30:
                recommendations.append("Focus on content quality over quantity")
        
        # Diversification recommendations
        topic_count = len(topic_performance)
        if topic_count < 3:
            recommendations.append("Consider diversifying your content topics")
        elif topic_count > 10:
            recommendations.append("Focus on your top-performing topics")
        
        return recommendations
    
    def _analyze_audience_demographics(self, subscriber_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze audience demographics"""
        if not subscriber_data:
            return {}
        
        # Analyze subscription dates
        subscription_months = defaultdict(int)
        for subscriber in subscriber_data:
            if subscriber.get("subscription_date"):
                date = datetime.fromisoformat(subscriber["subscription_date"].replace('Z', '+00:00'))
                month_key = date.strftime('%Y-%m')
                subscription_months[month_key] += 1
        
        # Analyze engagement levels
        engagement_distribution = {"high": 0, "medium": 0, "low": 0}
        for subscriber in subscriber_data:
            score = subscriber.get("engagement_score", 0)
            if score >= 70:
                engagement_distribution["high"] += 1
            elif score >= 30:
                engagement_distribution["medium"] += 1
            else:
                engagement_distribution["low"] += 1
        
        return {
            "total_subscribers": len(subscriber_data),
            "subscription_trend": dict(subscription_months),
            "engagement_distribution": engagement_distribution,
            "active_subscribers": sum(1 for s in subscriber_data if s.get("is_active", True))
        }
    
    def _analyze_engagement_patterns(self, engagement_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement patterns over time"""
        if not engagement_history:
            return {}
        
        # Analyze by day of week
        day_engagement = defaultdict(int)
        hour_engagement = defaultdict(int)
        
        for event in engagement_history:
            if event.get("opened_at"):
                dt = datetime.fromisoformat(event["opened_at"].replace('Z', '+00:00'))
                day_engagement[dt.strftime('%A')] += 1
                hour_engagement[dt.hour] += 1
        
        best_day = max(day_engagement.items(), key=lambda x: x[1])[0] if day_engagement else "Unknown"
        best_hour = max(hour_engagement.items(), key=lambda x: x[1])[0] if hour_engagement else 9
        
        return {
            "best_day": best_day,
            "best_hour": best_hour,
            "day_distribution": dict(day_engagement),
            "hour_distribution": dict(hour_engagement)
        }
    
    def _analyze_subscriber_lifecycle(self, subscriber_data: List[Dict], engagement_history: List[Dict]) -> Dict[str, Any]:
        """Analyze subscriber lifecycle stages"""
        lifecycle_stages = {"new": 0, "active": 0, "at_risk": 0, "churned": 0}
        
        current_date = datetime.utcnow()
        
        for subscriber in subscriber_data:
            sub_date = subscriber.get("subscription_date")
            last_engagement = subscriber.get("last_engagement")
            
            if sub_date:
                sub_datetime = datetime.fromisoformat(sub_date.replace('Z', '+00:00'))
                days_subscribed = (current_date - sub_datetime).days
                
                if days_subscribed <= 30:
                    lifecycle_stages["new"] += 1
                elif last_engagement:
                    last_eng_datetime = datetime.fromisoformat(last_engagement.replace('Z', '+00:00'))
                    days_since_engagement = (current_date - last_eng_datetime).days
                    
                    if days_since_engagement <= 14:
                        lifecycle_stages["active"] += 1
                    elif days_since_engagement <= 60:
                        lifecycle_stages["at_risk"] += 1
                    else:
                        lifecycle_stages["churned"] += 1
                else:
                    lifecycle_stages["at_risk"] += 1
        
        return lifecycle_stages
    
    def _analyze_churn_risk(self, subscriber_data: List[Dict], engagement_history: List[Dict]) -> Dict[str, Any]:
        """Analyze churn risk factors"""
        high_risk = []
        medium_risk = []
        low_risk = []
        
        current_date = datetime.utcnow()
        
        for subscriber in subscriber_data:
            risk_score = 0
            
            # Check engagement score
            engagement_score = subscriber.get("engagement_score", 50)
            if engagement_score < 20:
                risk_score += 3
            elif engagement_score < 40:
                risk_score += 1
            
            # Check last engagement
            last_engagement = subscriber.get("last_engagement")
            if last_engagement:
                last_eng_datetime = datetime.fromisoformat(last_engagement.replace('Z', '+00:00'))
                days_since = (current_date - last_eng_datetime).days
                
                if days_since > 30:
                    risk_score += 2
                elif days_since > 14:
                    risk_score += 1
            else:
                risk_score += 3
            
            # Categorize risk
            if risk_score >= 4:
                high_risk.append(subscriber)
            elif risk_score >= 2:
                medium_risk.append(subscriber)
            else:
                low_risk.append(subscriber)
        
        return {
            "high_risk_count": len(high_risk),
            "medium_risk_count": len(medium_risk),
            "low_risk_count": len(low_risk),
            "churn_risk_percentage": round(len(high_risk) / len(subscriber_data) * 100, 2) if subscriber_data else 0
        }
    
    def _analyze_audience_growth(self, subscriber_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze audience growth patterns"""
        if not subscriber_data:
            return {"growth_rate": 0, "trend": "stable"}
        
        # Group subscriptions by month
        monthly_subscriptions = defaultdict(int)
        for subscriber in subscriber_data:
            if subscriber.get("subscription_date"):
                date = datetime.fromisoformat(subscriber["subscription_date"].replace('Z', '+00:00'))
                month_key = date.strftime('%Y-%m')
                monthly_subscriptions[month_key] += 1
        
        # Calculate growth rate
        months = sorted(monthly_subscriptions.keys())
        if len(months) >= 2:
            current_month = monthly_subscriptions[months[-1]]
            previous_month = monthly_subscriptions[months[-2]]
            growth_rate = ((current_month - previous_month) / previous_month * 100) if previous_month > 0 else 0
            
            if growth_rate > 10:
                trend = "strong_growth"
            elif growth_rate > 0:
                trend = "growing"
            elif growth_rate > -10:
                trend = "stable"
            else:
                trend = "declining"
        else:
            growth_rate = 0
            trend = "insufficient_data"
        
        return {
            "growth_rate": round(growth_rate, 2),
            "trend": trend,
            "monthly_subscriptions": dict(monthly_subscriptions),
            "total_subscribers": len(subscriber_data)
        }
    
    def _create_overview_dashboard(self, user_id: int, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Create overview dashboard data"""
        return {
            "summary_metrics": {
                "total_newsletters": 12,
                "total_subscribers": 1250,
                "avg_open_rate": 24.5,
                "avg_click_rate": 3.2,
                "growth_rate": 8.5
            },
            "recent_performance": {
                "last_newsletter": {
                    "title": "Latest Industry Insights",
                    "sent_date": "2025-05-20",
                    "open_rate": 26.8,
                    "click_rate": 4.1
                }
            },
            "trends": {
                "subscriber_growth": [120, 135, 148, 162, 175, 189, 201],
                "engagement_trend": [22.1, 23.5, 24.2, 25.1, 24.8, 25.3, 24.5]
            },
            "top_content": [
                {"title": "AI Revolution Update", "engagement": 89},
                {"title": "Market Analysis Q2", "engagement": 84},
                {"title": "Tech Trends 2025", "engagement": 82}
            ]
        }
    
    def _create_detailed_dashboard(self, user_id: int, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Create detailed dashboard data"""
        return {
            "detailed_metrics": {
                "newsletters_sent": 12,
                "total_opens": 3678,
                "total_clicks": 482,
                "total_unsubscribes": 23,
                "bounce_rate": 2.1,
                "spam_complaints": 1
            },
            "segmentation_performance": {
                "high_engagement": {"count": 450, "open_rate": 45.2, "click_rate": 8.1},
                "medium_engagement": {"count": 600, "open_rate": 28.4, "click_rate": 3.8},
                "low_engagement": {"count": 200, "open_rate": 12.1, "click_rate": 1.2}
            },
            "content_analysis": {
                "best_topics": ["Technology", "Business", "Marketing"],
                "optimal_length": "800-1200 words",
                "best_send_time": {"day": "Tuesday", "hour": 10}
            }
        }
    
    def _create_comparison_dashboard(self, user_id: int, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Create comparison dashboard data"""
        return {
            "period_comparison": {
                "current_period": {
                    "open_rate": 24.5,
                    "click_rate": 3.2,
                    "subscribers": 1250,
                    "newsletters": 12
                },
                "previous_period": {
                    "open_rate": 22.8,
                    "click_rate": 2.9,
                    "subscribers": 1150,
                    "newsletters": 11
                },
                "changes": {
                    "open_rate": "+7.5%",
                    "click_rate": "+10.3%",
                    "subscribers": "+8.7%",
                    "newsletters": "+9.1%"
                }
            },
            "benchmark_comparison": {
                "industry_average": {"open_rate": 21.3, "click_rate": 2.6},
                "your_performance": {"open_rate": 24.5, "click_rate": 3.2},
                "percentile": {"open_rate": 75, "click_rate": 80}
            }
        }
    
    def _extract_engagement_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract patterns from historical engagement data"""
        if not historical_data:
            return {}
        
        # Analyze seasonal patterns
        monthly_engagement = defaultdict(list)
        for data in historical_data:
            if data.get("date"):
                date = datetime.fromisoformat(data["date"].replace('Z', '+00:00'))
                month = date.month
                monthly_engagement[month].append(data.get("engagement_score", 0))
        
        # Calculate monthly averages
        monthly_averages = {}
        for month, scores in monthly_engagement.items():
            monthly_averages[month] = np.mean(scores)
        
        return {
            "monthly_patterns": monthly_averages,
            "seasonal_trends": self._identify_seasonal_trends(monthly_averages),
            "data_points": len(historical_data)
        }
    
    def _calculate_baseline_metrics(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate baseline metrics from historical data"""
        if not historical_data:
            return {"baseline_engagement": 0, "baseline_open_rate": 0}
        
        engagement_scores = [d.get("engagement_score", 0) for d in historical_data]
        open_rates = [d.get("open_rate", 0) for d in historical_data]
        
        return {
            "baseline_engagement": round(np.mean(engagement_scores), 2),
            "baseline_open_rate": round(np.mean(open_rates), 2),
            "engagement_std": round(np.std(engagement_scores), 2),
            "open_rate_std": round(np.std(open_rates), 2)
        }
    
    def _generate_engagement_predictions(self, patterns: Dict, baseline: Dict, content_features: Dict, horizon: str) -> Dict[str, Any]:
        """Generate engagement predictions"""
        base_engagement = baseline.get("baseline_engagement", 50)
        base_open_rate = baseline.get("baseline_open_rate", 20)
        
        # Apply seasonal adjustments
        current_month = datetime.utcnow().month
        monthly_patterns = patterns.get("monthly_patterns", {})
        seasonal_adjustment = monthly_patterns.get(current_month, base_engagement) / base_engagement if base_engagement > 0 else 1
        
        # Apply content feature adjustments
        content_adjustment = 1.0
        if content_features:
            if content_features.get("topic") in ["Technology", "Business"]:
                content_adjustment += 0.1
            if content_features.get("length", 1000) > 1500:
                content_adjustment -= 0.05
        
        predicted_engagement = base_engagement * seasonal_adjustment * content_adjustment
        predicted_open_rate = base_open_rate * seasonal_adjustment * content_adjustment
        
        return {
            "predicted_engagement": round(predicted_engagement, 2),
            "predicted_open_rate": round(predicted_open_rate, 2),
            "seasonal_adjustment": round(seasonal_adjustment, 3),
            "content_adjustment": round(content_adjustment, 3)
        }
    
    def _calculate_prediction_confidence(self, historical_data: List[Dict], predictions: Dict) -> Dict[str, Any]:
        """Calculate confidence intervals for predictions"""
        if not historical_data:
            return {"confidence": "low", "interval": [0, 0]}
        
        # Simple confidence calculation based on historical variance
        engagement_scores = [d.get("engagement_score", 0) for d in historical_data]
        std_dev = np.std(engagement_scores)
        
        predicted_value = predictions.get("predicted_engagement", 50)
        
        # 95% confidence interval
        lower_bound = predicted_value - (1.96 * std_dev)
        upper_bound = predicted_value + (1.96 * std_dev)
        
        confidence_level = "high" if std_dev < 10 else "medium" if std_dev < 20 else "low"
        
        return {
            "confidence": confidence_level,
            "interval": [round(lower_bound, 2), round(upper_bound, 2)],
            "standard_deviation": round(std_dev, 2)
        }
    
    def _identify_seasonal_trends(self, monthly_averages: Dict[int, float]) -> List[str]:
        """Identify seasonal trends from monthly data"""
        trends = []
        
        if not monthly_averages:
            return trends
        
        # Find peak months
        max_month = max(monthly_averages, key=monthly_averages.get)
        min_month = min(monthly_averages, key=monthly_averages.get)
        
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        
        trends.append(f"Peak engagement in {month_names.get(max_month, 'Unknown')}")
        trends.append(f"Lowest engagement in {month_names.get(min_month, 'Unknown')}")
        
        return trends
    
    def _extract_test_metrics(self, test_data: List[Dict[str, Any]], metric: str) -> Dict[str, Any]:
        """Extract metrics for A/B test analysis"""
        if not test_data:
            return {"mean": 0, "count": 0, "std": 0}
        
        values = [data.get(metric, 0) for data in test_data]
        
        return {
            "mean": round(np.mean(values), 4),
            "count": len(values),
            "std": round(np.std(values), 4),
            "min": round(min(values), 4),
            "max": round(max(values), 4)
        }
    
    def _calculate_statistical_significance(self, variant_a: Dict, variant_b: Dict, confidence_level: float) -> Dict[str, Any]:
        """Calculate statistical significance between variants"""
        # Simple t-test calculation (would use scipy.stats in production)
        mean_a = variant_a.get("mean", 0)
        mean_b = variant_b.get("mean", 0)
        std_a = variant_a.get("std", 0)
        std_b = variant_b.get("std", 0)
        n_a = variant_a.get("count", 1)
        n_b = variant_b.get("count", 1)
        
        # Calculate pooled standard error
        pooled_se = np.sqrt((std_a**2 / n_a) + (std_b**2 / n_b))
        
        # Calculate t-statistic
        t_stat = abs(mean_b - mean_a) / pooled_se if pooled_se > 0 else 0
        
        # Simple significance check (would use proper t-distribution in production)
        is_significant = t_stat > 1.96  # Approximate for 95% confidence
        
        return {
            "t_statistic": round(t_stat, 4),
            "is_significant": is_significant,
            "confidence_level": confidence_level,
            "p_value_estimate": round(max(0.001, 0.05 - (t_stat * 0.01)), 4)
        }
    
    def _determine_test_winner(self, variant_a: Dict, variant_b: Dict, significance: Dict) -> Dict[str, Any]:
        """Determine the winning variant"""
        mean_a = variant_a.get("mean", 0)
        mean_b = variant_b.get("mean", 0)
        is_significant = significance.get("is_significant", False)
        
        if not is_significant:
            return {
                "winner": "inconclusive",
                "reason": "No statistically significant difference",
                "lift": 0
            }
        
        if mean_b > mean_a:
            lift = ((mean_b - mean_a) / mean_a * 100) if mean_a > 0 else 0
            return {
                "winner": "variant_b",
                "reason": f"Variant B performed {lift:.2f}% better",
                "lift": round(lift, 2)
            }
        else:
            lift = ((mean_a - mean_b) / mean_b * 100) if mean_b > 0 else 0
            return {
                "winner": "variant_a",
                "reason": f"Variant A performed {lift:.2f}% better",
                "lift": round(lift, 2)
            }
    
    def _generate_test_recommendations(self, variant_a: Dict, variant_b: Dict, winner: Dict, significance: Dict) -> List[str]:
        """Generate recommendations based on A/B test results"""
        recommendations = []
        
        if winner["winner"] == "inconclusive":
            recommendations.append("Run the test longer to gather more data")
            recommendations.append("Consider testing more dramatically different variants")
        else:
            recommendations.append(f"Implement {winner['winner']} as it shows {winner['lift']:.1f}% improvement")
            recommendations.append("Test other elements using the winning variant as baseline")
        
        # Sample size recommendations
        total_sample = variant_a.get("count", 0) + variant_b.get("count", 0)
        if total_sample < 1000:
            recommendations.append("Increase sample size for more reliable results")
        
        return recommendations


    def get_server(self):
        """Return the FastMCP server instance"""
        return self.mcp


def create_analytics_server():
    """Factory function to create analytics server"""
    return AnalyticsServer()
