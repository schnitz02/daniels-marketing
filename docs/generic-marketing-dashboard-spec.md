# Autonomous Marketing Dashboard — Generic Template Spec

> **For Claude Code:** This is a complete specification for building an autonomous marketing dashboard from scratch. Follow it step by step. All code, architecture, and patterns are proven — this spec was extracted from a working production system (Daniel's Donuts).

---

## Quick Start — What You're Building

A full-stack marketing dashboard that:
- Monitors social media accounts (Instagram, TikTok, Facebook) with daily scraping
- Runs AI-powered competitor research using Claude
- Displays analytics (GA4 integration ready)
- **[OPTIONAL]** Generates content ideas, creates media, publishes to social platforms, and updates a WordPress website — all autonomously with human approval gates

The system is designed for **Australian businesses** with Melbourne timezone formatting throughout.

---

## Company Configuration

**Before writing any code, the user MUST provide these values.** Ask for them if not given.

```yaml
# ─── Required ───────────────────────────────────────────────────────
company_name: "Company Name"              # e.g. "Daniel's Donuts"
company_tagline: "Short description"      # e.g. "100% Aussie-made donuts with 50+ flavours"
industry: "food_and_beverage"             # For benchmark context in AI prompts

# Brand colours (6 values)
color_primary: "#04D3C5"      # Primary accent — buttons, active states
color_sidebar: "#00395D"      # Sidebar background, headings
color_secondary: "#F7CA5E"    # Badges, highlights
color_tertiary: "#FFA1C7"     # Decorative accents
color_background: "#F5F4EC"   # Page background
color_border: "#E8E4D9"       # Card borders

# Social media handles
instagram_handle: "companyhandle"
tiktok_handle: "companyhandle"
facebook_handle: "CompanyHandle"

# Competitors (for research agent)
competitors:
  - "Competitor A"
  - "Competitor B"
  - "Competitor C"
  - "Competitor D"

# Logo file — user must provide a logo image file
logo_file: "logo.png"        # Will be placed at dashboard/public/logo.png

# ─── Optional (enable content pipeline) ─────────────────────────────
enable_content_pipeline: false   # true = include Strategy, Content, Post Production, Social, Website agents
enable_wordpress: false          # true = include WordPress integration
wordpress_url: ""
```

---

## Tech Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | >=0.135.0 |
| Server | Uvicorn | >=0.32.0 |
| Database | SQLAlchemy + SQLite (dev) / PostgreSQL (prod) | >=2.0.0 |
| Scheduler | APScheduler | >=3.10.0 |
| AI | Anthropic Claude API | >=0.40.0 |
| HTTP Client | httpx | >=0.27.0 |
| Scraping | Playwright (optional), httpx, curl_cffi | |
| Environment | python-dotenv | >=1.0.0 |

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | >=19 |
| Build Tool | Vite | >=6 |
| Styling | Tailwind CSS v4 | via @tailwindcss/vite |
| Routing | React Router | >=7 |
| Charts | Recharts | >=3 |
| HTTP Client | Axios | >=1 |

### Deployment
| Component | Platform |
|-----------|----------|
| Frontend | Vercel (free tier) |
| Backend | Railway (~$5/month) |
| Database | Railway PostgreSQL (included) |

---

## Project Structure

```
project-root/
├── src/
│   ├── __init__.py
│   ├── main.py                          # FastAPI entry point — uvicorn runs this
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                      # BaseAgent ABC + parse_claude_json helper
│   │   ├── orchestrator.py              # Agent registry + dispatcher
│   │   ├── research.py                  # CORE — competitive intelligence via Claude
│   │   ├── social_stats.py              # CORE — social media profile scraping
│   │   ├── analytics.py                 # CORE — fetch post engagement metrics
│   │   ├── strategy.py                  # OPTIONAL — idea generation
│   │   ├── content.py                   # OPTIONAL — media generation
│   │   ├── post_production.py           # OPTIONAL — video branding
│   │   ├── social.py                    # OPTIONAL — publish to platforms
│   │   └── website.py                   # OPTIONAL — WordPress management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                      # NOT the entry point (legacy, can be removed)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── dashboard.py             # CORE — /overview, /calendar, /analytics
│   │       ├── agents.py                # CORE — /status, /trigger/{name}
│   │       ├── research.py              # CORE — /research/items, /competitors
│   │       ├── social_stats.py          # CORE — /social-stats/latest, /history, /posts
│   │       ├── social_analysis.py       # CORE — AI analysis of social stats
│   │       ├── ga4.py                   # CORE — Google Analytics integration
│   │       └── approvals.py             # OPTIONAL — idea/content/website approval workflow
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scheduler.py                 # APScheduler cron job setup
│   │   ├── ga4_client.py                # Google Analytics client (graceful degradation)
│   │   ├── scrapers/
│   │   │   ├── __init__.py
│   │   │   ├── instagram.py             # Instagram profile scraper
│   │   │   ├── tiktok.py                # TikTok profile scraper
│   │   │   └── facebook.py              # Facebook profile scraper (via Social Blade)
│   │   ├── higgsfield.py                # OPTIONAL — image/video generation
│   │   ├── meta_client.py               # OPTIONAL — Meta Graph API posting
│   │   ├── tiktok_client.py             # OPTIONAL — TikTok posting
│   │   ├── wordpress_client.py          # OPTIONAL — WordPress REST API
│   │   └── video_editor.py              # OPTIONAL — moviepy watermarking
│   └── db/
│       ├── __init__.py
│       ├── database.py                  # Engine, session, init_db
│       └── models.py                    # All SQLAlchemy models
├── dashboard/
│   ├── package.json
│   ├── vite.config.js                   # Vite + Tailwind + /api proxy
│   ├── vercel.json                      # Vercel rewrites for production API proxy
│   ├── public/
│   │   └── logo.png                     # Company logo
│   └── src/
│       ├── main.jsx                     # React entry point
│       ├── App.jsx                      # Router + sidebar nav
│       ├── App.css                      # Minimal/empty
│       ├── index.css                    # Tailwind + brand colour tokens
│       ├── api.js                       # Axios instance (baseURL: "/api")
│       ├── utils/
│       │   └── date.js                  # Melbourne timezone formatters
│       └── pages/
│           ├── Overview.jsx             # CORE — KPI cards, social strip, schedule
│           ├── SocialStats.jsx          # CORE — platform tabs, follower charts, post grid
│           ├── Research.jsx             # CORE — competitor insights, run agent button
│           ├── Analytics.jsx            # CORE — GA4 SEO/SEM tabs (setup banner if not connected)
│           ├── Agents.jsx               # CORE — agent status + manual trigger buttons
│           ├── Calendar.jsx             # CORE/OPTIONAL — scheduled post timeline
│           ├── Strategy.jsx             # OPTIONAL — idea generation
│           ├── Approvals.jsx            # OPTIONAL — approve/reject workflow
│           └── Website.jsx              # OPTIONAL — WordPress changes
├── tests/                               # Mirrors src/ structure — TDD throughout
│   ├── conftest.py                      # Test app fixture with all routers
│   ├── agents/                          # One test file per agent
│   ├── api/                             # Route tests
│   └── db/                              # Model tests
├── requirements.txt
├── .env.example
└── docs/
```

---

## Database Schema

### CORE tables (always created)

```python
class ResearchItem(Base):
    __tablename__ = "research"
    id = Column(Integer, primary_key=True)
    source = Column(String(50))              # "claude_research"
    competitor = Column(String(100))
    content = Column(Text)                   # JSON string — use json.dumps(), NOT str()
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SocialSnapshot(Base):
    __tablename__ = "social_snapshots"
    __table_args__ = (Index("ix_social_snapshots_platform_handle", "platform", "handle"),)
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(30), nullable=False)       # instagram / facebook / tiktok
    handle = Column(String(100), nullable=False)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    bio = Column(String(500), default="")
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SocialPostCache(Base):
    __tablename__ = "social_posts_cache"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(30), nullable=False, index=True)
    post_id = Column(String(200), nullable=False, unique=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    thumbnail_url = Column(String(500), default="")
    caption = Column(String(1000), default="")
    posted_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SocialAnalysis(Base):
    __tablename__ = "social_analysis"
    id = Column(Integer, primary_key=True)
    platform = Column(String(20), nullable=False)
    analysis = Column(Text, nullable=False)            # JSON string
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(50))
    status = Column(String(20))                        # running / completed / failed
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    log = Column(Text, nullable=True)
```

### OPTIONAL tables (only if content pipeline enabled)

```python
class Idea(Base):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    body = Column(Text)
    evidence = Column(Text, nullable=True)
    status = Column(String(20), default="pending")     # pending / approved / rejected
    rejection_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    contents = relationship("Content", back_populates="idea")

class Content(Base):
    __tablename__ = "content"
    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"))
    type = Column(String(20))                          # image / reel
    file_path = Column(String(500))
    caption = Column(Text)
    status = Column(String(20), default="pending")
    rejection_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    idea = relationship("Idea", back_populates="contents")
    posts = relationship("Post", back_populates="content")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey("content.id"))
    platform = Column(String(30))
    platform_post_id = Column(String(200), nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="scheduled")
    reach = Column(Integer, default=0)
    engagement = Column(Integer, default=0)
    content = relationship("Content", back_populates="posts")

class Approval(Base):
    __tablename__ = "approvals"
    id = Column(Integer, primary_key=True)
    item_type = Column(String(20))
    item_id = Column(Integer)
    decision = Column(String(20))
    notes = Column(Text, nullable=True)
    decided_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class WebsiteChange(Base):
    __tablename__ = "website_changes"
    id = Column(Integer, primary_key=True)
    change_type = Column(String(50))
    description = Column(Text)
    payload = Column(JSON)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

---

## API Endpoints

### CORE endpoints

```
GET  /api/dashboard/overview      — KPI summary (pending counts, published posts, total reach)
GET  /api/dashboard/calendar      — Scheduled/published posts timeline
GET  /api/dashboard/analytics     — Engagement by platform

GET  /api/agents/status           — Last run status for all agents
POST /api/agents/trigger/{name}   — Manually trigger an agent (optional X-API-Key header)

GET  /api/research/items          — Research insights (?competitor=X&limit=50)
GET  /api/research/competitors    — Distinct competitor names

GET  /api/social-stats/latest     — Latest snapshot per platform
GET  /api/social-stats/history/{platform}  — Historical snapshots (for charts)
GET  /api/social-stats/posts/{platform}    — Cached recent posts

GET  /api/social-stats/analysis/{platform}  — Latest AI analysis
POST /api/social-stats/analysis/{platform}  — Generate fresh AI analysis

GET  /api/ga4/status              — GA4 connection status
GET  /api/ga4/seo                 — Organic search metrics
GET  /api/ga4/sem                 — Paid search metrics

GET  /health                      — Health check
```

### OPTIONAL endpoints (content pipeline)

```
GET  /api/approvals/ideas         — Pending ideas
POST /api/approvals/ideas/{id}/approve
POST /api/approvals/ideas/{id}/reject

GET  /api/approvals/content       — Pending content
POST /api/approvals/content/{id}/approve
POST /api/approvals/content/{id}/reject

GET  /api/approvals/website       — Pending website changes
POST /api/approvals/website/{id}/approve
POST /api/approvals/website/{id}/reject
```

---

## Core Agents

### Research Agent
Runs daily at 06:00 UTC. Iterates over the configured competitors list and asks Claude for 3 marketing insights per competitor.

**Claude model:** `claude-sonnet-4-6` · max_tokens: `1024`

**Prompt template:**
```
You are a marketing research agent for {company_name}, an Australian {industry} brand.
Based on your knowledge of {competitor}'s marketing strategy, social media presence,
and recent campaigns, provide 3 key insights that {company_name} could learn from or respond to.

Return ONLY valid JSON:
{"insights": [{"insight": "str", "platform": "str", "actionable": "str"}]}
```

**CRITICAL:** Store content as `json.dumps(parsed)`, NEVER `str(parsed)`. Python's `str()` produces single-quoted dicts that break frontend JSON parsing when values contain apostrophes.

**Output:** Writes to `research` table with `source="claude_research"`.

### Social Stats Agent
Runs daily at 09:30 UTC. Scrapes public social media profiles to track follower counts.

**Scraper details:**

- **Instagram:** `GET https://i.instagram.com/api/v1/users/web_profile_info/?username={handle}`
  - Headers: `User-Agent: Instagram 275.0.0.27.98 Android`, `x-ig-app-id: 936619743392459`
  - Optional: `INSTAGRAM_SESSION_ID` cookie
- **TikTok:** `GET https://www.tiktok.com/@{handle}` — parse `__UNIVERSAL_DATA_FOR_REHYDRATION__` script tag
- **Facebook:** `GET https://socialblade.com/facebook/user/{handle}` — uses `curl_cffi` to impersonate Chrome

**Note:** Scrapers work reliably from residential IPs (local dev) but may be blocked from cloud server IPs. Real API keys resolve this.

**Dedup:** Skips platform if a snapshot already exists for today.

### Social Analysis Agent
On-demand (triggered via `POST /api/social-stats/analysis/{platform}`). Reads latest snapshot and asks Claude for performance analysis.

**Claude model:** `claude-sonnet-4-6` · max_tokens: `800`

**Prompt template:**
```
You are a social media analyst for {company_name}, an Australian {industry} brand.

Platform: {platform}
Current stats:
- Followers: {followers}
- Following: {following}
- Posts: {posts_count}
- Bio: {bio}

Provide a JSON response with exactly these keys:
- "summary": 2-3 sentence plain-English summary of current performance
- "benchmarks": How these numbers compare to typical Australian {industry} brand benchmarks
- "recommendations": List of exactly 3 specific, actionable improvements

Return ONLY valid JSON, no markdown.
```

### Analytics Agent
Runs daily at 20:00 UTC. Fetches engagement metrics for published posts from Meta Graph API.

---

## Optional Agents (Content Pipeline)

Only build these if `enable_content_pipeline: true`.

### Strategy Agent
Weekly (Monday 07:00 UTC). Reads latest research + post history, generates 5 marketing ideas. Ideas enter "pending" status requiring human approval.

### Content Agent
Daily (09:00 UTC). For approved ideas, generates image/video prompts via Claude, then calls Higgsfield API to create media. Content enters "pending" status requiring human approval.

### Post Production Agent
Daily (10:00 UTC). Adds company watermark to generated video reels using moviepy.

### Social Agent
Daily (11:00 UTC). Publishes approved content to Instagram, Facebook, TikTok via Meta Graph API and TikTok Open API.

### Website Agent
Daily (12:00 UTC). Applies approved website changes to WordPress and generates new suggestions from approved ideas via Claude.

---

## Frontend Pages

### CORE pages

**Overview (`/`):**
- KPI stat cards (pending ideas, pending content, website changes, published posts, total reach)
- Social health strip (3 platform cards with follower count)
- This week's schedule
- Pending approvals summary
- All dates in Melbourne time, `en-AU` locale

**Social Stats (`/social-stats`):**
- Tab per platform (Instagram, TikTok, Facebook)
- Profile card (handle, followers, following, posts, bio)
- Follower trend chart (Recharts line chart from historical snapshots)
- Recent posts grid (thumbnail, likes, comments)
- "Generate Analysis" button → AI analysis card (summary, benchmarks, 3 recommendations)

**Research (`/research`):**
- Competitor filter buttons
- "Run Research Agent" button
- Insight cards with expand/collapse
- Each insight: platform badge, insight text, "Recommended Action" block
- Parser handles both JSON and markdown-fenced JSON (strip ` ```json ``` ` fences)

**Analytics (`/analytics`):**
- GA4 connection status check on load
- Setup banner when not connected (shows required env vars)
- SEO tab: organic search metrics, 30-day sessions chart, top landing pages
- SEM tab: paid search metrics

**Agents (`/agents`):**
- Card per agent showing last run time, status (completed/failed/running/never_run)
- Manual "Trigger" button per agent
- Status auto-refreshes every 5 seconds

**Calendar (`/calendar`):**
- Timeline of scheduled and published posts
- Platform badge, datetime, status chip

### OPTIONAL pages (content pipeline only)

**Strategy (`/strategy`):** — Idea generation view
**Approvals (`/approvals`):** — Approve/reject ideas, content, website changes
**Website (`/website`):** — WordPress change queue

---

## Frontend Patterns

### Date/Time Formatting
All dates displayed in **Melbourne time** with Australian formatting. Create `dashboard/src/utils/date.js`:

```javascript
const TZ = "Australia/Melbourne"
const LOCALE = "en-AU"

export function formatDate(value) {       // "1 Jan 2026"
  if (!value) return ""
  return new Date(value).toLocaleDateString(LOCALE, {
    day: "numeric", month: "short", year: "numeric", timeZone: TZ,
  })
}

export function formatDateTime(value) {   // "1 Jan 2026, 3:45 pm"
  if (!value) return ""
  return new Date(value).toLocaleString(LOCALE, {
    day: "numeric", month: "short", year: "numeric",
    hour: "numeric", minute: "2-digit", hour12: true, timeZone: TZ,
  })
}

export function formatTime(value) {       // "3:45 pm"
  if (!value) return ""
  return new Date(value).toLocaleTimeString(LOCALE, {
    hour: "numeric", minute: "2-digit", hour12: true, timeZone: TZ,
  })
}

export function formatDateShort(value) {  // "1 Apr"
  if (!value) return ""
  return new Date(value).toLocaleDateString(LOCALE, {
    day: "numeric", month: "short", timeZone: TZ,
  })
}

export function formatMonthYear(value) {  // "Apr '26"
  if (!value) return ""
  return new Date(value).toLocaleDateString(LOCALE, {
    month: "short", year: "2-digit", timeZone: TZ,
  })
}
```

### Brand Colours via Tailwind Arbitrary Values
Since each company has different colours, apply them as inline Tailwind arbitrary values:

```jsx
// Sidebar
<nav className="bg-[#00395D]">

// Active nav item
<NavLink className={isActive ? "bg-[#04D3C5] text-white" : "text-white/70"}>

// Cards
<div className="bg-white border border-[#E8E4D9] rounded-xl p-6 shadow-sm">

// Page background
<main className="bg-[#F5F4EC]">

// Headings
<h1 className="text-[#00395D]">

// Muted text
<p className="text-[#6B8A9A]">

// Primary button
<button className="bg-[#04D3C5] hover:bg-[#03bdb0] text-white">
```

Replace hex values with the company's configured colours. Define CSS tokens in `index.css`:

```css
@import "tailwindcss";

@theme {
  --color-brand: #04D3C5;     /* color_primary */
  --color-navy: #00395D;      /* color_sidebar */
  --color-gold: #F7CA5E;      /* color_secondary */
  --color-pink: #FFA1C7;      /* color_tertiary */
  --color-cream: #F5F4EC;     /* color_background */
}

body {
  margin: 0;
  background-color: #F5F4EC;  /* color_background */
  color: #00395D;             /* color_sidebar */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

### API Client
Simple Axios instance:
```javascript
import axios from "axios"
const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
})
export default api
```

### Vite Config
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/media': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
```

---

## Backend Patterns

### Entry Point (`src/main.py`)

```python
import os, logging
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from src.db.database import init_db
from src.core.scheduler import AgentScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles

    _scheduler = AgentScheduler()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db()
        _scheduler.start()
        logger.info("Application started")
        yield
        _scheduler.stop()

    app = FastAPI(title="{company_name} Marketing Agent", lifespan=lifespan)

    os.makedirs("./media", exist_ok=True)
    app.mount("/media", StaticFiles(directory="./media"), name="media")

    extra_origins = os.getenv("ALLOWED_ORIGINS", "")
    allowed_origins = [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:3000", "http://127.0.0.1:3000",
    ]
    if extra_origins:
        allowed_origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["*"], allow_headers=["*"], allow_credentials=True,
    )

    # CORE routers — always register
    from src.api.routes import agents, dashboard
    from src.api.routes.social_stats import router as social_stats_router
    from src.api.routes.research import router as research_router
    from src.api.routes.social_analysis import router as social_analysis_router
    from src.api.routes.ga4 import router as ga4_router
    app.include_router(agents.router, prefix="/api/agents")
    app.include_router(dashboard.router, prefix="/api/dashboard")
    app.include_router(social_stats_router, prefix="/api")
    app.include_router(research_router, prefix="/api")
    app.include_router(social_analysis_router, prefix="/api")
    app.include_router(ga4_router, prefix="/api")

    # OPTIONAL routers — only if content pipeline enabled
    # from src.api.routes import approvals
    # app.include_router(approvals.router, prefix="/api/approvals")

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "{company_name}-marketing"}

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
```

**CRITICAL:** `src/main.py` is the ONLY entry point. All routers MUST be registered here. There may be a `src/api/main.py` — that is NOT the entry point. Ignore it.

### Base Agent

```python
import json, re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.db.models import AgentRun

def parse_claude_json(raw: str) -> dict | list:
    """Parse JSON from Claude responses, stripping markdown code fences if present."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned.strip())

class BaseAgent(ABC):
    name: str = "base_agent"

    def __init__(self, db: Session):
        self.db = db

    async def execute(self):
        run = AgentRun(agent_name=self.name, status="running")
        self.db.add(run)
        self.db.commit()
        try:
            result = await self.run()
            run.status = "completed"
            run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            return result
        except Exception as e:
            run.status = "failed"
            run.log = str(e)
            run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            raise

    @abstractmethod
    async def run(self):
        pass
```

### Database (`src/db/database.py`)

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./marketing.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Note:** `create_all` only creates missing tables. It does NOT add columns to existing tables. If you add a column to a model after the table exists, you must run a manual `ALTER TABLE` migration.

---

## Deployment

### Vercel (Frontend)
1. Connect GitHub repo
2. Set **Root Directory** to `dashboard`
3. Framework preset: **Vite**
4. No environment variables needed

Create `dashboard/vercel.json`:
```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://YOUR-RAILWAY-URL/api/:path*" },
    { "source": "/media/:path*", "destination": "https://YOUR-RAILWAY-URL/media/:path*" }
  ]
}
```

### Railway (Backend)
1. Connect GitHub repo
2. Add PostgreSQL database
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Generate a public domain
6. Set environment variables:
   - `ANTHROPIC_API_KEY` — required
   - `POC_MODE` — `true` until real API keys available
   - `ALLOWED_ORIGINS` — Vercel URL

---

## Testing Approach

**TDD throughout.** Every backend feature: write failing test → implement → pass → full suite → commit.

Test fixture in `tests/conftest.py` creates an in-memory SQLite database and registers all routers on a test FastAPI app. Use `TestClient` from Starlette.

All agent tests mock external API calls (Anthropic, scrapers, Meta, TikTok, WordPress, Higgsfield).

---

## Known Gotchas

1. **`str()` vs `json.dumps()`** — NEVER use `str()` to serialize Python dicts for storage. It produces single-quoted notation that breaks JSON parsing when values contain apostrophes. Always use `json.dumps()`.

2. **Dual main.py** — `src/main.py` is the entry point. `src/api/main.py` exists but is NOT used. All router registrations go in `src/main.py`.

3. **SQLAlchemy `create_all`** — Only creates new tables. Adding a column to an existing model requires a manual `ALTER TABLE` SQL migration.

4. **Cloud scraping** — Instagram, TikTok, and Facebook scrapers work from residential IPs but get blocked from cloud server IPs (Railway). Real API keys resolve this.

5. **Railway `$PORT`** — Railway dynamically assigns a port. Use `--port $PORT` in the start command, not a hardcoded number.

6. **FastAPI + Starlette versions** — Pin `fastapi>=0.135.0`. Older versions (0.115.x) are incompatible with Starlette 1.0.0 which gets pulled in by the `mcp` package.

7. **Vercel default branch** — Vercel deploys from the GitHub default branch, not the "production branch" setting. Make sure the GitHub default branch is set to `master`/`main`.

---

## Implementation Order

Build in this order. Each step should be a commit.

1. Project scaffolding (requirements.txt, .env.example, src/db/database.py, src/db/models.py)
2. Base agent framework (base.py, orchestrator.py)
3. FastAPI entry point with health check (src/main.py)
4. Dashboard route (overview, calendar, analytics endpoints)
5. Social stats scrapers + agent + routes
6. Research agent + routes
7. Social analysis route (on-demand Claude analysis)
8. GA4 client + routes
9. Agent status + trigger routes
10. Scheduler setup
11. Frontend: Vite + React + Tailwind scaffolding
12. Frontend: App.jsx with sidebar nav + routing
13. Frontend: Overview page
14. Frontend: Social Stats page (tabs, charts, analysis)
15. Frontend: Research page (insights, filters, run button)
16. Frontend: Analytics page (GA4, setup banner)
17. Frontend: Agents page (status, trigger buttons)
18. Frontend: Calendar page
19. **[OPTIONAL]** Strategy agent + Approvals route + pages
20. **[OPTIONAL]** Content agent + Higgsfield client
21. **[OPTIONAL]** Post Production agent + video editor
22. **[OPTIONAL]** Social agent + Meta/TikTok clients
23. **[OPTIONAL]** Website agent + WordPress client + page
24. Deployment config (vercel.json, CORS, requirements pinning)
25. Brand polish pass (logo, colours, spacing)
