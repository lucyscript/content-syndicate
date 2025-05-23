# ContentSyndicate - Technical Architecture

## 🏗 System Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Web Frontend  │───▶│   API Gateway    │───▶│   Master Agent      │
│   (React/Next)  │    │   (FastAPI)      │    │   (Gemini AI)       │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────────┐
                                                │   MCP Orchestrator  │
                                                └─────────────────────┘
                                                         │
                        ┌────────────────────────────────┼────────────────────────────────┐
                        ▼                                ▼                                ▼
            ┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────────┐
            │ Content Aggregator  │          │    AI Writer       │          │  Personalization   │
            │    MCP Server       │          │   MCP Server       │          │    MCP Server      │
            └─────────────────────┘          └─────────────────────┘          └─────────────────────┘
                        │                                │                                │
                        ▼                                ▼                                ▼
            ┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────────┐
            │   External APIs     │          │   Content Database  │          │   User Profiles    │
            │ Reddit│Twitter│News │          │   (PostgreSQL)     │          │   (PostgreSQL)     │
            └─────────────────────┘          └─────────────────────┘          └─────────────────────┘
```

## 🤖 MCP Server Specifications

### 1. Content Aggregator Server
**Purpose**: Fetch trending content from multiple platforms
**Port**: 5001

```python
# Example MCP Tool
@mcp.tool()
def fetch_trending_content(platform: str, niche: str, limit: int = 10) -> list:
    """Fetch trending content from specified platform and niche"""
    # Implementation details in server code
```

### 2. AI Writer Server  
**Purpose**: Generate human-like newsletter content
**Port**: 5002

```python
@mcp.tool()
def generate_newsletter(content_data: list, tone: str, length: int) -> str:
    """Generate newsletter from aggregated content with specified tone and length"""
```

### 3. Personalization Server
**Purpose**: Customize content based on user preferences
**Port**: 5003

```python
@mcp.tool()
def personalize_content(content: str, user_profile: dict) -> str:
    """Personalize content based on user demographics and preferences"""
```

### 4. Distribution Server
**Purpose**: Handle email delivery and social media posting
**Port**: 5004

```python
@mcp.tool()
def send_newsletter(content: str, subscriber_list: list, template: str) -> dict:
    """Send newsletter to subscriber list with tracking"""
```

### 5. Analytics Server
**Purpose**: Track performance metrics and user engagement
**Port**: 5005

```python
@mcp.tool()
def track_engagement(newsletter_id: str, metrics: dict) -> dict:
    """Track newsletter performance and user engagement"""
```

## 🔄 Workflow Process

### 1. Content Generation Workflow
```
User Request → Master Agent → Content Aggregator → AI Writer → Personalization → Distribution
```

### 2. Scheduled Automation
```
Cron Job → Content Aggregator → AI Writer → User Approval → Distribution
```

### 3. Real-time Analytics
```
User Interaction → Analytics Server → Dashboard Update → Optimization Suggestions
```

## 🗄 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    subscription_tier VARCHAR(50),
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Newsletters Table
```sql
CREATE TABLE newsletters (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255),
    content TEXT,
    status VARCHAR(50),
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Content Sources Table
```sql
CREATE TABLE content_sources (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(100),
    content_data JSONB,
    trending_score FLOAT,
    fetched_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Configuration Management

### Environment Variables
```bash
# API Keys
GEMINI_API_KEY=your_gemini_key
REDDIT_CLIENT_ID=your_reddit_id
TWITTER_BEARER_TOKEN=your_twitter_token
SENDGRID_API_KEY=your_sendgrid_key

# Database
DATABASE_URL=postgresql://user:pass@localhost/contentsyndicate

# MCP Server Ports
CONTENT_AGGREGATOR_PORT=5001
AI_WRITER_PORT=5002
PERSONALIZATION_PORT=5003
DISTRIBUTION_PORT=5004
ANALYTICS_PORT=5005

# Rate Limiting
GEMINI_REQUESTS_PER_MINUTE=15
CONTENT_FETCH_INTERVAL=300
```

## 🚀 Deployment Strategy

### Development Environment
- Docker Compose for local development
- All MCP servers running locally
- SQLite for quick testing

### Production Environment
- **Frontend**: Vercel
- **Backend API**: Railway/Render
- **MCP Servers**: Docker containers on Railway
- **Database**: PostgreSQL on Railway
- **Redis**: For caching and rate limiting

### Scaling Considerations
- Load balancer for MCP servers
- Database read replicas
- CDN for static content
- Queue system for background tasks

## 📊 Performance Metrics

### API Response Times
- Content Aggregation: < 5 seconds
- AI Generation: < 30 seconds
- Newsletter Delivery: < 2 minutes

### Scalability Targets
- 1000 concurrent users
- 10,000 newsletters/day
- 100,000 API calls/day

## 🔒 Security & Compliance

### Data Protection
- API key encryption
- User data anonymization
- GDPR compliance for EU users
- SOC 2 Type I for enterprise clients

### Rate Limiting
- Per-user API limits based on subscription tier
- Graceful degradation when limits exceeded
- Priority queuing for premium users
