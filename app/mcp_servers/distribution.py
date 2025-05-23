"""
Distribution MCP Server
Handles email delivery and social media posting
"""
import json
from typing import List, Dict, Any, Optional
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
import tweepy
import requests
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP
from ..config import settings


class DistributionServer:
    def __init__(self):
        self.mcp = FastMCP("distribution")
        self._setup_clients()
        self._register_tools()
    
    def _setup_clients(self):
        """Initialize distribution clients"""
        # SendGrid client
        if settings.sendgrid_api_key:
            self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
        else:
            self.sendgrid_client = None
        
        # Twitter client
        if settings.twitter_api_key and settings.twitter_api_secret:
            self.twitter_client = tweepy.Client(
                consumer_key=settings.twitter_api_key,
                consumer_secret=settings.twitter_api_secret,
                access_token=settings.twitter_access_token,
                access_token_secret=settings.twitter_access_token_secret
            )
        else:
            self.twitter_client = None
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.mcp.tool()
        async def send_newsletter_email(
            recipients: List[str],
            subject: str,
            html_content: str,
            text_content: str = "",
            from_email: str = "",
            from_name: str = ""
        ) -> Dict[str, Any]:
            return await self.send_newsletter_email_impl(recipients, subject, html_content, text_content, from_email, from_name)
        
        @self.mcp.tool()
        async def post_to_social_media(
            posts: Dict[str, List[str]]
        ) -> Dict[str, Any]:
            return await self.post_to_social_media_impl(posts)
        
        @self.mcp.tool()
        async def schedule_newsletter(
            recipients: List[str],
            subject: str,
            content: str,
            send_time: str
        ) -> Dict[str, Any]:
            return await self.schedule_newsletter_impl(recipients, subject, content, send_time)
        
        @self.mcp.tool()
        async def send_sms(
            phone_numbers: List[str],
            message: str
        ) -> Dict[str, Any]:
            return await self.send_sms_impl(phone_numbers, message)

    async def send_newsletter_email_impl(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        text_content: str = "",
        from_email: str = "",
        from_name: str = ""
    ) -> Dict[str, Any]:
        """Send newsletter email to multiple recipients"""
        try:
            if not self.sendgrid_client:
                return {"error": "SendGrid client not configured"}
            
            if not recipients:
                return {"error": "No recipients provided"}
            
            # Use default sender if not provided
            if not from_email:
                from_email = settings.from_email
            if not from_name:
                from_name = settings.from_name
            
            successful_sends = []
            failed_sends = []
            
            for recipient in recipients:
                try:
                    # Create email
                    mail = Mail(
                        from_email=Email(from_email, from_name),
                        to_emails=To(recipient),
                        subject=subject,
                        html_content=Content("text/html", html_content)
                    )
                    
                    if text_content:
                        mail.add_content(Content("text/plain", text_content))
                    
                    # Send email
                    response = self.sendgrid_client.send(mail)
                    
                    if response.status_code in [200, 201, 202]:
                        successful_sends.append(recipient)
                    else:
                        failed_sends.append({
                            "email": recipient,
                            "error": f"HTTP {response.status_code}"
                        })
                
                except Exception as e:
                    failed_sends.append({
                        "email": recipient,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "successful_sends": len(successful_sends),
                "failed_sends": len(failed_sends),
                "successful_emails": successful_sends,
                "failed_emails": failed_sends,
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Email sending failed: {str(e)}"}

    async def post_to_social_media_impl(
        self,
        posts: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Post content to social media platforms"""
        try:
            results = {}
            
            # Twitter posts
            if "twitter" in posts and self.twitter_client:
                twitter_results = []
                for post_content in posts["twitter"]:
                    try:
                        response = self.twitter_client.create_tweet(text=post_content)
                        twitter_results.append({
                            "success": True,
                            "tweet_id": response.data['id'],
                            "content": post_content
                        })
                    except Exception as e:
                        twitter_results.append({
                            "success": False,
                            "error": str(e),
                            "content": post_content
                        })
                
                results["twitter"] = {
                    "total_posts": len(posts["twitter"]),
                    "successful_posts": len([r for r in twitter_results if r["success"]]),
                    "failed_posts": len([r for r in twitter_results if not r["success"]]),
                    "results": twitter_results
                }
            
            # LinkedIn posts (placeholder - requires LinkedIn API setup)
            if "linkedin" in posts:
                results["linkedin"] = {
                    "status": "not_implemented",
                    "message": "LinkedIn API integration not yet available"
                }
            
            # Facebook posts (placeholder - requires Facebook API setup)
            if "facebook" in posts:
                results["facebook"] = {
                    "status": "not_implemented",
                    "message": "Facebook API integration not yet available"
                }
            
            return {
                "success": True,
                "platforms": list(results.keys()),
                "results": results,
                "posted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Social media posting failed: {str(e)}"}

    async def schedule_newsletter_impl(
        self,
        recipients: List[str],
        subject: str,
        content: str,
        send_time: str
    ) -> Dict[str, Any]:
        """Schedule newsletter for future delivery"""
        try:
            # For now, this is a placeholder implementation
            # In production, this would integrate with a job queue like Celery or similar
            
            scheduled_time = datetime.fromisoformat(send_time)
            current_time = datetime.utcnow()
            
            if scheduled_time <= current_time:
                return {"error": "Scheduled time must be in the future"}
            
            # Mock scheduling
            return {
                "success": True,
                "scheduled": True,
                "recipients_count": len(recipients),
                "subject": subject,
                "send_time": send_time,
                "scheduled_at": current_time.isoformat(),
                "job_id": f"newsletter_{int(current_time.timestamp())}"
            }
            
        except Exception as e:
            return {"error": f"Newsletter scheduling failed: {str(e)}"}

    async def send_sms_impl(
        self,
        phone_numbers: List[str],
        message: str
    ) -> Dict[str, Any]:
        """Send SMS notifications"""
        try:
            # This is a placeholder implementation
            # In production, integrate with Twilio, AWS SNS, or similar SMS service
            
            return {
                "success": True,
                "service": "mock_sms",
                "recipients_count": len(phone_numbers),
                "message_length": len(message),
                "sent_at": datetime.utcnow().isoformat(),
                "note": "SMS service not yet implemented - this is a mock response"
            }
            
        except Exception as e:
            return {"error": f"SMS sending failed: {str(e)}"}

    def get_server(self):
        """Return the FastMCP server instance"""
        return self.mcp


def create_distribution_server():
    """Factory function to create distribution server"""
    return DistributionServer()
