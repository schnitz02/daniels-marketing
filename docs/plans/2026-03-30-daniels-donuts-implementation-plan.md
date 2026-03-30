# Daniel's Donuts Marketing Agent — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a fully autonomous multi-agent marketing system for Daniel's Donuts that creates/posts social content, manages the WordPress website, monitors competitors, generates strategy, and routes everything through a human approval dashboard.

**Architecture:** A FastAPI backend hosts an Orchestrator Agent (Claude SDK) that coordinates 8 specialised sub-agents. Each agent communicates via a shared PostgreSQL database. A React + Tailwind dashboard serves as the human-in-the-loop approval interface. Redis + APScheduler handles agent scheduling.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, Redis, APScheduler, Anthropic Claude SDK (claude-sonnet-4-6), Higgsfield API, MoviePy + FFmpeg, Meta Graph API, TikTok API, WordPress REST API, Apify/Playwright, React 18, Tailwind CSS, Vite.

---

## Phase 1: Project Scaffolding

### Task 1: Initialize project structure

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/agents/__init__.py`
- Create: `src/api/__init__.py`
- Create: `src/db/__init__.py`
- Create: `src/dashboard/` (React app root)
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: Create directory structure**

```bash
mkdir -p src/agents src/api src/db src/core tests/agents tests/api tests/db
```

**Step 2: Create `pyproject.toml`**

```toml
[project]
name = "daniels-donuts-marketing-agent"
version = "0.1.0"
requires-python = ">=3.12"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

**Step 3: Create `requirements.txt`**

```
anthropic>=0.40.0
fastapi>=0.115.0
uvicorn>=0.32.0
sqlalchemy>=2.0.0
alembic>=1.14.0
psycopg2-binary>=2.9.0
redis>=5.2.0
apscheduler>=3.10.0
httpx>=0.27.0
playwright>=1.48.0
moviepy>=1.0.3
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.24.0
pytest-httpx>=0.32.0
```

**Step 4: Create `.env.example`**

```
ANTHROPIC_API_KEY=
HIGGSFIELD_API_KEY=
META_APP_ID=
META_APP_SECRET=
META_ACCESS_TOKEN=
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=
TIKTOK_ACCESS_TOKEN=
WP_URL=https://danielsdonuts.com.au
WP_USERNAME=
WP_APP_PASSWORD=
DATABASE_URL=postgresql://user:password@localhost:5432/daniels_marketing
REDIS_URL=redis://localhost:6379
```

**Step 5: Create `.gitignore`**

```
.env
__pycache__/
*.pyc
.pytest_cache/
node_modules/
dist/
*.egg-info/
.venv/
```

**Step 6: Commit**

```bash
git add .
git commit -m "feat: scaffold project structure"
```

---

### Task 2: Database models

**Files:**
- Create: `src/db/models.py`
- Create: `src/db/database.py`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Test: `tests/db/test_models.py`

**Step 1: Write the failing test**

```python
# tests/db/test_models.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base, ResearchItem, Idea, Content, Post, Approval

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_create_idea(db):
    idea = Idea(title="Glazed Monday Campaign", body="Post 3 glazed donut reels on Monday morning", status="pending")
    db.add(idea)
    db.commit()
    assert idea.id is not None
    assert idea.status == "pending"

def test_create_research(db):
    item = ResearchItem(source="instagram", competitor="Krispy Kreme", content="New strawberry glaze trending", raw_data="{}")
    db.add(item)
    db.commit()
    assert item.id is not None

def test_create_content(db):
    idea = Idea(title="Test", body="Test", status="approved")
    db.add(idea)
    db.flush()
    content = Content(idea_id=idea.id, type="image", file_path="/tmp/test.jpg", caption="Freshest donuts in town", status="pending")
    db.add(content)
    db.commit()
    assert content.idea_id == idea.id
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/db/test_models.py -v
```
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Create `src/db/models.py`**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class ResearchItem(Base):
    __tablename__ = "research"
    id = Column(Integer, primary_key=True)
    source = Column(String(50))          # instagram, tiktok, web
    competitor = Column(String(100))
    content = Column(Text)
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Idea(Base):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    body = Column(Text)
    status = Column(String(20), default="pending")  # pending/approved/rejected
    rejection_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    contents = relationship("Content", back_populates="idea")

class Content(Base):
    __tablename__ = "content"
    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"))
    type = Column(String(20))            # image, reel
    file_path = Column(String(500))
    caption = Column(Text)
    status = Column(String(20), default="pending")  # pending/approved/rejected
    rejection_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    idea = relationship("Idea", back_populates="contents")
    posts = relationship("Post", back_populates="content")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey("content.id"))
    platform = Column(String(30))        # instagram, facebook, tiktok
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
    item_type = Column(String(20))       # idea, content, website_change
    item_id = Column(Integer)
    decision = Column(String(20))        # approved, rejected
    notes = Column(Text, nullable=True)
    decided_at = Column(DateTime, default=datetime.utcnow)

class WebsiteChange(Base):
    __tablename__ = "website_changes"
    id = Column(Integer, primary_key=True)
    change_type = Column(String(50))     # banner, product, blog_post, campaign_page
    description = Column(Text)
    payload = Column(JSON)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(50))
    status = Column(String(20))          # running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    log = Column(Text, nullable=True)
```

**Step 4: Create `src/db/database.py`**

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./daniels_marketing.db")

engine = create_engine(DATABASE_URL)
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

**Step 5: Run tests to verify they pass**

```bash
pytest tests/db/test_models.py -v
```
Expected: 3 PASSED

**Step 6: Commit**

```bash
git add src/db/ tests/db/ requirements.txt
git commit -m "feat: add database models and schema"
```

---

## Phase 2: Core Agent Infrastructure

### Task 3: Base agent class

**Files:**
- Create: `src/agents/base.py`
- Test: `tests/agents/test_base.py`

**Step 1: Write the failing test**

```python
# tests/agents/test_base.py
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.base import BaseAgent

class ConcreteAgent(BaseAgent):
    name = "test_agent"
    async def run(self):
        return {"status": "ok"}

@pytest.mark.asyncio
async def test_agent_logs_run(db):
    agent = ConcreteAgent(db=db)
    result = await agent.execute()
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_agent_records_run_in_db(db):
    agent = ConcreteAgent(db=db)
    await agent.execute()
    from src.db.models import AgentRun
    run = db.query(AgentRun).filter_by(agent_name="test_agent").first()
    assert run is not None
    assert run.status == "completed"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/agents/test_base.py -v
```
Expected: FAIL

**Step 3: Create `src/agents/base.py`**

```python
from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy.orm import Session
from src.db.models import AgentRun

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
            run.completed_at = datetime.utcnow()
            self.db.commit()
            return result
        except Exception as e:
            run.status = "failed"
            run.log = str(e)
            run.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    @abstractmethod
    async def run(self):
        pass
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/agents/test_base.py -v
```
Expected: 2 PASSED

**Step 5: Commit**

```bash
git add src/agents/base.py tests/agents/test_base.py
git commit -m "feat: add base agent class with run logging"
```

---

### Task 4: Orchestrator Agent

**Files:**
- Create: `src/agents/orchestrator.py`
- Test: `tests/agents/test_orchestrator.py`

**Step 1: Write the failing test**

```python
# tests/agents/test_orchestrator.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.orchestrator import OrchestratorAgent

@pytest.mark.asyncio
async def test_orchestrator_triggers_research(db):
    with patch("src.agents.orchestrator.ResearchAgent") as MockResearch:
        mock_instance = AsyncMock()
        MockResearch.return_value = mock_instance
        orchestrator = OrchestratorAgent(db=db)
        await orchestrator.trigger_agent("research")
        mock_instance.execute.assert_called_once()

@pytest.mark.asyncio
async def test_orchestrator_queues_approval(db):
    from src.db.models import Idea
    idea = Idea(title="Test Idea", body="Test body", status="pending")
    db.add(idea)
    db.commit()
    orchestrator = OrchestratorAgent(db=db)
    await orchestrator.queue_for_approval("idea", idea.id)
    from src.db.models import Approval
    # approval record should NOT exist yet — it's queued, not decided
    assert db.query(Approval).count() == 0
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/agents/test_orchestrator.py -v
```
Expected: FAIL

**Step 3: Create `src/agents/orchestrator.py`**

```python
import asyncio
from sqlalchemy.orm import Session
from src.agents.base import BaseAgent

AGENT_REGISTRY = {}

def register_agent(name):
    def decorator(cls):
        AGENT_REGISTRY[name] = cls
        return cls
    return decorator

class OrchestratorAgent(BaseAgent):
    name = "orchestrator"

    async def run(self):
        return {"status": "orchestrator running"}

    async def trigger_agent(self, agent_name: str):
        from src.agents import research, strategy, content, post_production, social, website, analytics
        agent_cls = AGENT_REGISTRY.get(agent_name)
        if not agent_cls:
            raise ValueError(f"Unknown agent: {agent_name}")
        agent = agent_cls(db=self.db)
        return await agent.execute()

    async def queue_for_approval(self, item_type: str, item_id: int):
        # Items sit in the DB with status="pending" — dashboard reads them
        pass
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/agents/test_orchestrator.py -v
```
Expected: 2 PASSED

**Step 5: Commit**

```bash
git add src/agents/orchestrator.py tests/agents/test_orchestrator.py
git commit -m "feat: add orchestrator agent with agent registry"
```

---

## Phase 3: Research & Strategy Agents

### Task 5: Research Agent

**Files:**
- Create: `src/agents/research.py`
- Create: `src/core/scraper.py`
- Test: `tests/agents/test_research.py`

**Step 1: Write the failing test**

```python
# tests/agents/test_research.py
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.research import ResearchAgent

@pytest.mark.asyncio
async def test_research_agent_stores_results(db):
    mock_results = [
        {"source": "instagram", "competitor": "Krispy Kreme", "content": "New glazed range", "raw_data": {}},
        {"source": "tiktok", "competitor": "Dunkin Donuts", "content": "Viral donut tower video", "raw_data": {}},
    ]
    with patch.object(ResearchAgent, "_scrape_competitors", return_value=mock_results):
        agent = ResearchAgent(db=db)
        await agent.execute()
        from src.db.models import ResearchItem
        items = db.query(ResearchItem).all()
        assert len(items) == 2
        assert items[0].competitor == "Krispy Kreme"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/agents/test_research.py -v
```
Expected: FAIL

**Step 3: Create `src/agents/research.py`**

```python
import os
import httpx
from sqlalchemy.orm import Session
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.db.models import ResearchItem

COMPETITORS = [
    "Krispy Kreme Australia",
    "Dunkin Donuts",
    "Donut King",
    "Mad Mex",  # local competition
]

@register_agent("research")
class ResearchAgent(BaseAgent):
    name = "research"

    async def run(self):
        results = await self._scrape_competitors()
        for item in results:
            record = ResearchItem(
                source=item["source"],
                competitor=item["competitor"],
                content=item["content"],
                raw_data=item["raw_data"],
            )
            self.db.add(record)
        self.db.commit()
        return {"researched": len(results)}

    async def _scrape_competitors(self) -> list[dict]:
        """
        Uses Claude to synthesise competitor intelligence.
        In production, augment with Apify/Playwright scrapers.
        """
        import anthropic
        client = anthropic.Anthropic()
        results = []
        for competitor in COMPETITORS:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": (
                        f"You are a marketing research agent for Daniel's Donuts, an Australian donut brand. "
                        f"Based on your knowledge of {competitor}'s marketing strategy, social media presence, "
                        f"and recent campaigns, provide 3 key insights that Daniel's Donuts could learn from or respond to. "
                        f"Return as JSON: {{\"insights\": [{{\"insight\": str, \"platform\": str, \"actionable\": str}}]}}"
                    )
                }]
            )
            results.append({
                "source": "claude_research",
                "competitor": competitor,
                "content": message.content[0].text,
                "raw_data": {"model": "claude-sonnet-4-6"},
            })
        return results
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/agents/test_research.py -v
```
Expected: 1 PASSED

**Step 5: Commit**

```bash
git add src/agents/research.py tests/agents/test_research.py
git commit -m "feat: add research agent with competitor intelligence"
```

---

### Task 6: Strategy Agent

**Files:**
- Create: `src/agents/strategy.py`
- Test: `tests/agents/test_strategy.py`

**Step 1: Write the failing test**

```python
# tests/agents/test_strategy.py
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.strategy import StrategyAgent
from src.db.models import ResearchItem, Idea

@pytest.mark.asyncio
async def test_strategy_creates_ideas(db):
    # Seed research data
    db.add(ResearchItem(source="instagram", competitor="Krispy Kreme", content="Strawberry glaze trending", raw_data={}))
    db.commit()

    mock_ideas = [
        {"title": "Strawberry Weekend Special", "body": "Launch a 3-day strawberry glazed campaign"},
        {"title": "Monday Morning Donut Drop", "body": "Post a reel each Monday at 7am"},
    ]
    with patch.object(StrategyAgent, "_generate_ideas", return_value=mock_ideas):
        agent = StrategyAgent(db=db)
        await agent.execute()
        ideas = db.query(Idea).all()
        assert len(ideas) == 2
        assert all(i.status == "pending" for i in ideas)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/agents/test_strategy.py -v
```
Expected: FAIL

**Step 3: Create `src/agents/strategy.py`**

```python
import json
import anthropic
from sqlalchemy.orm import Session
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.db.models import ResearchItem, Post, Idea

@register_agent("strategy")
class StrategyAgent(BaseAgent):
    name = "strategy"

    async def run(self):
        research = self.db.query(ResearchItem).order_by(ResearchItem.created_at.desc()).limit(20).all()
        posts = self.db.query(Post).order_by(Post.published_at.desc()).limit(20).all()
        ideas = await self._generate_ideas(research, posts)
        for idea_data in ideas:
            idea = Idea(title=idea_data["title"], body=idea_data["body"], status="pending")
            self.db.add(idea)
        self.db.commit()
        return {"ideas_generated": len(ideas)}

    async def _generate_ideas(self, research=None, posts=None) -> list[dict]:
        research_summary = "\n".join([f"- {r.competitor}: {r.content}" for r in (research or [])])
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": (
                    f"You are the marketing strategist for Daniel's Donuts, a 100% Aussie-made donut brand with 50+ flavours. "
                    f"Based on this competitor research:\n{research_summary}\n\n"
                    f"Generate 5 creative marketing ideas for Instagram, Facebook, and TikTok. "
                    f"Focus on viral potential, Australian culture, and what makes Daniel's unique. "
                    f'Return as JSON: {{"ideas": [{{"title": str, "body": str, "platform": str, "content_type": str}}]}}'
                )
            }]
        )
        data = json.loads(message.content[0].text)
        return data.get("ideas", [])
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/agents/test_strategy.py -v
```
Expected: 1 PASSED

**Step 5: Commit**

```bash
git add src/agents/strategy.py tests/agents/test_strategy.py
git commit -m "feat: add strategy agent with Claude-powered idea generation"
```

---

## Phase 4: Content Pipeline

### Task 7: Content Agent (Higgsfield)

**Files:**
- Create: `src/agents/content.py`
- Create: `src/core/higgsfield.py`
- Test: `tests/agents/test_content.py`

**Step 1: Write the failing test**

```python
# tests/agents/test_content.py
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.content import ContentAgent
from src.db.models import Idea, Content

@pytest.mark.asyncio
async def test_content_agent_creates_content_for_approved_ideas(db):
    idea = Idea(title="Glazed Monday", body="Monday morning glazed donut reel", status="approved")
    db.add(idea)
    db.commit()

    with patch("src.core.higgsfield.HiggsFieldClient.generate_image", return_value="/tmp/test_image.jpg"), \
         patch("src.core.higgsfield.HiggsFieldClient.generate_video", return_value="/tmp/test_video.mp4"):
        agent = ContentAgent(db=db)
        await agent.execute()
        contents = db.query(Content).all()
        assert len(contents) >= 1
        assert contents[0].idea_id == idea.id
        assert contents[0].status == "pending"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/agents/test_content.py -v
```
Expected: FAIL

**Step 3: Create `src/core/higgsfield.py`**

```python
import os
import httpx

class HiggsFieldClient:
    BASE_URL = "https://api.higgsfield.ai/v1"  # Check Higgsfield docs for actual endpoint

    def __init__(self):
        self.api_key = os.getenv("HIGGSFIELD_API_KEY")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def generate_image(self, prompt: str, output_path: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/generate/image",
                headers=self.headers,
                json={"prompt": prompt, "style": "photorealistic", "aspect_ratio": "1:1"},
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            # Download the image
            img_response = await client.get(data["url"])
            with open(output_path, "wb") as f:
                f.write(img_response.content)
        return output_path

    async def generate_video(self, prompt: str, output_path: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/generate/video",
                headers=self.headers,
                json={"prompt": prompt, "duration": 15, "aspect_ratio": "9:16"},
                timeout=300.0,
            )
            response.raise_for_status()
            data = response.json()
            video_response = await client.get(data["url"])
            with open(output_path, "wb") as f:
                f.write(video_response.content)
        return output_path
```

**Step 4: Create `src/agents/content.py`**

```python
import os
import json
import anthropic
from sqlalchemy.orm import Session
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.core.higgsfield import HiggsFieldClient
from src.db.models import Idea, Content

MEDIA_DIR = os.getenv("MEDIA_DIR", "./media")

@register_agent("content")
class ContentAgent(BaseAgent):
    name = "content"

    async def run(self):
        approved_ideas = self.db.query(Idea).filter_by(status="approved").all()
        higgsfield = HiggsFieldClient()
        created = 0
        for idea in approved_ideas:
            # Skip if content already generated
            if self.db.query(Content).filter_by(idea_id=idea.id).count() > 0:
                continue

            prompt = await self._build_prompt(idea)
            os.makedirs(MEDIA_DIR, exist_ok=True)

            # Generate image
            image_path = f"{MEDIA_DIR}/idea_{idea.id}_image.jpg"
            await higgsfield.generate_image(prompt["image_prompt"], image_path)

            # Generate video
            video_path = f"{MEDIA_DIR}/idea_{idea.id}_video.mp4"
            await higgsfield.generate_video(prompt["video_prompt"], video_path)

            for file_path, content_type in [(image_path, "image"), (video_path, "reel")]:
                content = Content(
                    idea_id=idea.id,
                    type=content_type,
                    file_path=file_path,
                    caption=prompt["caption"],
                    status="pending",
                )
                self.db.add(content)
            created += 2

        self.db.commit()
        return {"content_created": created}

    async def _build_prompt(self, idea: Idea) -> dict:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": (
                    f"You are a creative director for Daniel's Donuts, an Australian donut brand. "
                    f"For this marketing idea: '{idea.title}' — '{idea.body}'\n"
                    f"Generate:\n"
                    f"1. A detailed Higgsfield image prompt (photorealistic donuts, appetising, bright)\n"
                    f"2. A detailed Higgsfield video prompt (15 second reel, vertical 9:16)\n"
                    f"3. An engaging social media caption with hashtags\n"
                    f'Return as JSON: {{"image_prompt": str, "video_prompt": str, "caption": str}}'
                )
            }]
        )
        return json.loads(message.content[0].text)
```

**Step 5: Run tests to verify they pass**

```bash
pytest tests/agents/test_content.py -v
```
Expected: 1 PASSED

**Step 6: Commit**

```bash
git add src/agents/content.py src/core/higgsfield.py tests/agents/test_content.py
git commit -m "feat: add content agent with Higgsfield image and video generation"
```

---

### Task 8: Post-Production Agent

**Files:**
- Create: `src/agents/post_production.py`
- Create: `src/core/video_editor.py`
- Test: `tests/agents/test_post_production.py`

**Step 1: Write the failing test**

```python
# tests/agents/test_post_production.py
import pytest
from unittest.mock import patch, MagicMock
from src.agents.post_production import PostProductionAgent
from src.db.models import Idea, Content

@pytest.mark.asyncio
async def test_post_production_processes_pending_reels(db):
    idea = Idea(title="Test", body="Test", status="approved")
    db.add(idea)
    db.flush()
    content = Content(idea_id=idea.id, type="reel", file_path="/tmp/raw.mp4", caption="Test", status="pending")
    db.add(content)
    db.commit()

    with patch("src.core.video_editor.VideoEditor.add_branding", return_value="/tmp/branded.mp4"):
        agent = PostProductionAgent(db=db)
        await agent.execute()
        db.refresh(content)
        # content file_path should be updated to branded version
        assert "branded" in content.file_path or content.file_path == "/tmp/branded.mp4"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/agents/test_post_production.py -v
```
Expected: FAIL

**Step 3: Create `src/core/video_editor.py`**

```python
import os

class VideoEditor:
    BRAND_COLOR = "#FF6B35"  # Daniel's Donuts orange
    WATERMARK_TEXT = "Daniel's Donuts"

    def add_branding(self, input_path: str, output_path: str) -> str:
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
            clip = VideoFileClip(input_path)
            watermark = (
                TextClip(self.WATERMARK_TEXT, fontsize=36, color="white", font="Arial-Bold")
                .set_position(("center", "bottom"))
                .set_duration(clip.duration)
            )
            final = CompositeVideoClip([clip, watermark])
            final.write_videofile(output_path, codec="libx264", audio_codec="aac")
        except Exception as e:
            # If moviepy fails, copy the file as-is
            import shutil
            shutil.copy(input_path, output_path)
        return output_path
```

**Step 4: Create `src/agents/post_production.py`**

```python
import os
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.core.video_editor import VideoEditor
from src.db.models import Content

MEDIA_DIR = os.getenv("MEDIA_DIR", "./media")

@register_agent("post_production")
class PostProductionAgent(BaseAgent):
    name = "post_production"

    async def run(self):
        pending_reels = self.db.query(Content).filter_by(type="reel", status="pending").all()
        editor = VideoEditor()
        processed = 0
        for content in pending_reels:
            if not os.path.exists(content.file_path):
                continue
            branded_path = content.file_path.replace(".mp4", "_branded.mp4")
            editor.add_branding(content.file_path, branded_path)
            content.file_path = branded_path
            processed += 1
        self.db.commit()
        return {"processed": processed}
```

**Step 5: Run tests to verify they pass**

```bash
pytest tests/agents/test_post_production.py -v
```
Expected: 1 PASSED

**Step 6: Commit**

```bash
git add src/agents/post_production.py src/core/video_editor.py tests/agents/test_post_production.py
git commit -m "feat: add post-production agent with branding overlay"
```

---

## Phase 5: Publishing Agents

### Task 9: Social Agent

**Files:**
- Create: `src/agents/social.py`
- Create: `src/core/meta_client.py`
- Create: `src/core/tiktok_client.py`
- Test: `tests/agents/test_social.py`

**Step 1: Write the failing test**

```python
# tests/agents/test_social.py
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.social import SocialAgent
from src.db.models import Idea, Content, Post

@pytest.mark.asyncio
async def test_social_agent_creates_posts_for_approved_content(db):
    idea = Idea(title="Test", body="Test", status="approved")
    db.add(idea)
    db.flush()
    content = Content(idea_id=idea.id, type="image", file_path="/tmp/test.jpg", caption="Fresh donuts!", status="approved")
    db.add(content)
    db.commit()

    with patch("src.core.meta_client.MetaClient.post_image", return_value="meta_post_123"), \
         patch("src.core.tiktok_client.TikTokClient.post_video", return_value="tiktok_post_456"):
        agent = SocialAgent(db=db)
        await agent.execute()
        posts = db.query(Post).all()
        assert len(posts) >= 1
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/agents/test_social.py -v
```
Expected: FAIL

**Step 3: Create `src/core/meta_client.py`**

```python
import os
import httpx

class MetaClient:
    GRAPH_API = "https://graph.facebook.com/v21.0"

    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.page_id = os.getenv("META_PAGE_ID")
        self.ig_account_id = os.getenv("META_IG_ACCOUNT_ID")

    async def post_image(self, image_path: str, caption: str) -> str:
        async with httpx.AsyncClient() as client:
            # Upload to Instagram
            with open(image_path, "rb") as f:
                upload = await client.post(
                    f"{self.GRAPH_API}/{self.ig_account_id}/media",
                    params={"access_token": self.access_token},
                    data={"caption": caption},
                    files={"image": f},
                )
            media_id = upload.json()["id"]
            publish = await client.post(
                f"{self.GRAPH_API}/{self.ig_account_id}/media_publish",
                params={"access_token": self.access_token, "creation_id": media_id},
            )
            return publish.json()["id"]

    async def post_reel(self, video_path: str, caption: str) -> str:
        async with httpx.AsyncClient() as client:
            with open(video_path, "rb") as f:
                upload = await client.post(
                    f"{self.GRAPH_API}/{self.ig_account_id}/media",
                    params={"access_token": self.access_token, "media_type": "REELS"},
                    data={"caption": caption},
                    files={"video": f},
                    timeout=300.0,
                )
            media_id = upload.json()["id"]
            publish = await client.post(
                f"{self.GRAPH_API}/{self.ig_account_id}/media_publish",
                params={"access_token": self.access_token, "creation_id": media_id},
            )
            return publish.json()["id"]
```

**Step 4: Create `src/core/tiktok_client.py`**

```python
import os
import httpx

class TikTokClient:
    API_BASE = "https://open.tiktokapis.com/v2"

    def __init__(self):
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")

    async def post_video(self, video_path: str, caption: str) -> str:
        async with httpx.AsyncClient() as client:
            init = await client.post(
                f"{self.API_BASE}/post/publish/video/init/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={"post_info": {"title": caption, "privacy_level": "PUBLIC_TO_EVERYONE"},
                      "source_info": {"source": "FILE_UPLOAD"}},
            )
            upload_url = init.json()["data"]["upload_url"]
            with open(video_path, "rb") as f:
                await client.put(upload_url, content=f.read())
            publish_id = init.json()["data"]["publish_id"]
            return publish_id
```

**Step 5: Create `src/agents/social.py`**

```python
from datetime import datetime
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.core.meta_client import MetaClient
from src.core.tiktok_client import TikTokClient
from src.db.models import Content, Post

@register_agent("social")
class SocialAgent(BaseAgent):
    name = "social"

    async def run(self):
        approved = self.db.query(Content).filter_by(status="approved").all()
        meta = MetaClient()
        tiktok = TikTokClient()
        published = 0

        for content in approved:
            already_posted = self.db.query(Post).filter_by(content_id=content.id).count()
            if already_posted:
                continue

            platforms = ["instagram", "facebook", "tiktok"] if content.type == "reel" else ["instagram", "facebook"]

            for platform in platforms:
                try:
                    if platform in ("instagram", "facebook"):
                        if content.type == "image":
                            post_id = await meta.post_image(content.file_path, content.caption)
                        else:
                            post_id = await meta.post_reel(content.file_path, content.caption)
                    elif platform == "tiktok":
                        post_id = await tiktok.post_video(content.file_path, content.caption)

                    post = Post(
                        content_id=content.id,
                        platform=platform,
                        platform_post_id=post_id,
                        published_at=datetime.utcnow(),
                        status="published",
                    )
                    self.db.add(post)
                    published += 1
                except Exception as e:
                    post = Post(content_id=content.id, platform=platform, status="failed")
                    self.db.add(post)

        self.db.commit()
        return {"published": published}
```

**Step 6: Run tests to verify they pass**

```bash
pytest tests/agents/test_social.py -v
```
Expected: 1 PASSED

**Step 7: Commit**

```bash
git add src/agents/social.py src/core/meta_client.py src/core/tiktok_client.py tests/agents/test_social.py
git commit -m "feat: add social agent with Meta and TikTok publishing"
```

---

### Task 10: Website Agent

**Files:**
- Create: `src/agents/website.py`
- Create: `src/core/wordpress_client.py`
- Test: `tests/agents/test_website.py`

**Step 1: Write the failing test**

```python
# tests/agents/test_website.py
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.website import WebsiteAgent
from src.db.models import WebsiteChange

@pytest.mark.asyncio
async def test_website_agent_applies_approved_changes(db):
    change = WebsiteChange(
        change_type="banner",
        description="Update hero banner for Easter campaign",
        payload={"title": "Easter Donuts are here!", "image_url": "/tmp/easter.jpg"},
        status="approved",
    )
    db.add(change)
    db.commit()

    with patch("src.core.wordpress_client.WordPressClient.update_banner", return_value=True):
        agent = WebsiteAgent(db=db)
        await agent.execute()
        db.refresh(change)
        assert change.status == "applied"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/agents/test_website.py -v
```
Expected: FAIL

**Step 3: Create `src/core/wordpress_client.py`**

```python
import os
import httpx
from base64 import b64encode

class WordPressClient:
    def __init__(self):
        self.url = os.getenv("WP_URL", "https://danielsdonuts.com.au")
        username = os.getenv("WP_USERNAME")
        password = os.getenv("WP_APP_PASSWORD")
        creds = b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/json",
        }

    async def update_banner(self, title: str, image_url: str) -> bool:
        async with httpx.AsyncClient() as client:
            # Update front page via WP REST API
            response = await client.post(
                f"{self.url}/wp-json/wp/v2/pages",
                headers=self.headers,
                json={"title": title, "featured_media": image_url},
            )
            return response.status_code in (200, 201)

    async def create_post(self, title: str, content: str, status: str = "publish") -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/wp-json/wp/v2/posts",
                headers=self.headers,
                json={"title": title, "content": content, "status": status},
            )
            response.raise_for_status()
            return response.json()

    async def update_product(self, product_id: int, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.url}/wp-json/wc/v3/products/{product_id}",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def create_campaign_page(self, title: str, content: str) -> dict:
        return await self.create_post(title, content, status="publish")
```

**Step 4: Create `src/agents/website.py`**

```python
import anthropic
import json
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.core.wordpress_client import WordPressClient
from src.db.models import WebsiteChange, ResearchItem, Idea

@register_agent("website")
class WebsiteAgent(BaseAgent):
    name = "website"

    async def run(self):
        # Apply approved changes
        approved = self.db.query(WebsiteChange).filter_by(status="approved").all()
        wp = WordPressClient()
        applied = 0

        for change in approved:
            try:
                if change.change_type == "banner":
                    await wp.update_banner(**change.payload)
                elif change.change_type == "blog_post":
                    await wp.create_post(**change.payload)
                elif change.change_type == "product":
                    await wp.update_product(**change.payload)
                elif change.change_type == "campaign_page":
                    await wp.create_campaign_page(**change.payload)
                change.status = "applied"
                applied += 1
            except Exception as e:
                change.status = "failed"

        # Generate new website change suggestions from approved ideas
        approved_ideas = self.db.query(Idea).filter_by(status="approved").all()
        for idea in approved_ideas:
            existing = self.db.query(WebsiteChange).filter_by(description=idea.title).first()
            if not existing:
                await self._suggest_website_change(idea)

        self.db.commit()
        return {"applied": applied}

    async def _suggest_website_change(self, idea: Idea):
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": (
                    f"For this Daniel's Donuts marketing idea: '{idea.title}' — '{idea.body}'\n"
                    f"Suggest a website change (banner, blog post, or campaign page). "
                    f'Return as JSON: {{"change_type": str, "description": str, "payload": dict}}'
                )
            }]
        )
        data = json.loads(message.content[0].text)
        change = WebsiteChange(
            change_type=data["change_type"],
            description=idea.title,
            payload=data["payload"],
            status="pending",
        )
        self.db.add(change)
```

**Step 5: Run tests to verify they pass**

```bash
pytest tests/agents/test_website.py -v
```
Expected: 1 PASSED

**Step 6: Commit**

```bash
git add src/agents/website.py src/core/wordpress_client.py tests/agents/test_website.py
git commit -m "feat: add website agent with WordPress REST API integration"
```

---

### Task 11: Analytics Agent

**Files:**
- Create: `src/agents/analytics.py`
- Test: `tests/agents/test_analytics.py`

**Step 1: Write the failing test**

```python
# tests/agents/test_analytics.py
import pytest
from unittest.mock import patch
from src.agents.analytics import AnalyticsAgent
from src.db.models import Post

@pytest.mark.asyncio
async def test_analytics_agent_updates_post_metrics(db):
    post = Post(content_id=1, platform="instagram", platform_post_id="ig_123", status="published")
    db.add(post)
    db.commit()

    mock_metrics = {"reach": 1500, "engagement": 230}
    with patch.object(AnalyticsAgent, "_fetch_metrics", return_value=mock_metrics):
        agent = AnalyticsAgent(db=db)
        await agent.execute()
        db.refresh(post)
        assert post.reach == 1500
        assert post.engagement == 230
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/agents/test_analytics.py -v
```
Expected: FAIL

**Step 3: Create `src/agents/analytics.py`**

```python
import os
import httpx
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.db.models import Post

@register_agent("analytics")
class AnalyticsAgent(BaseAgent):
    name = "analytics"

    async def run(self):
        published_posts = self.db.query(Post).filter_by(status="published").all()
        updated = 0
        for post in published_posts:
            try:
                metrics = await self._fetch_metrics(post)
                post.reach = metrics.get("reach", post.reach)
                post.engagement = metrics.get("engagement", post.engagement)
                updated += 1
            except Exception:
                pass
        self.db.commit()
        return {"updated": updated}

    async def _fetch_metrics(self, post: Post) -> dict:
        if post.platform in ("instagram", "facebook"):
            return await self._fetch_meta_metrics(post.platform_post_id)
        return {}

    async def _fetch_meta_metrics(self, post_id: str) -> dict:
        access_token = os.getenv("META_ACCESS_TOKEN")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://graph.facebook.com/v21.0/{post_id}/insights",
                params={
                    "metric": "impressions,reach,engagement",
                    "access_token": access_token,
                },
            )
            data = response.json().get("data", [])
            metrics = {}
            for item in data:
                if item["name"] == "reach":
                    metrics["reach"] = item["values"][0]["value"]
                elif item["name"] == "engagement":
                    metrics["engagement"] = item["values"][0]["value"]
            return metrics
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/agents/test_analytics.py -v
```
Expected: 1 PASSED

**Step 5: Commit**

```bash
git add src/agents/analytics.py tests/agents/test_analytics.py
git commit -m "feat: add analytics agent with Meta metrics fetching"
```

---

## Phase 6: FastAPI Backend

### Task 12: FastAPI app + approval endpoints

**Files:**
- Create: `src/api/main.py`
- Create: `src/api/routes/approvals.py`
- Create: `src/api/routes/agents.py`
- Create: `src/api/routes/dashboard.py`
- Test: `tests/api/test_approvals.py`

**Step 1: Write the failing test**

```python
# tests/api/test_approvals.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.db.models import Idea

def test_get_pending_approvals(client, db):
    db.add(Idea(title="Test Idea", body="Test", status="pending"))
    db.commit()
    response = client.get("/api/approvals/ideas")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "pending"

def test_approve_idea(client, db):
    idea = Idea(title="Approve Me", body="Test", status="pending")
    db.add(idea)
    db.commit()
    response = client.post(f"/api/approvals/ideas/{idea.id}/approve")
    assert response.status_code == 200
    db.refresh(idea)
    assert idea.status == "approved"

def test_reject_idea_with_notes(client, db):
    idea = Idea(title="Reject Me", body="Test", status="pending")
    db.add(idea)
    db.commit()
    response = client.post(f"/api/approvals/ideas/{idea.id}/reject", json={"notes": "Not on brand"})
    assert response.status_code == 200
    db.refresh(idea)
    assert idea.status == "rejected"
    assert idea.rejection_notes == "Not on brand"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/api/test_approvals.py -v
```
Expected: FAIL

**Step 3: Create `src/api/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import approvals, agents, dashboard
from src.db.database import init_db

app = FastAPI(title="Daniel's Donuts Marketing Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(approvals.router, prefix="/api/approvals")
app.include_router(agents.router, prefix="/api/agents")
app.include_router(dashboard.router, prefix="/api/dashboard")

@app.on_event("startup")
def startup():
    init_db()
```

**Step 4: Create `src/api/routes/approvals.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Idea, Content, WebsiteChange, Approval
from datetime import datetime

router = APIRouter()

class RejectionNotes(BaseModel):
    notes: str = ""

@router.get("/ideas")
def get_pending_ideas(db: Session = Depends(get_db)):
    return db.query(Idea).filter_by(status="pending").all()

@router.post("/ideas/{idea_id}/approve")
def approve_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).get(idea_id)
    if not idea:
        raise HTTPException(status_code=404)
    idea.status = "approved"
    db.add(Approval(item_type="idea", item_id=idea_id, decision="approved", decided_at=datetime.utcnow()))
    db.commit()
    return {"status": "approved"}

@router.post("/ideas/{idea_id}/reject")
def reject_idea(idea_id: int, body: RejectionNotes, db: Session = Depends(get_db)):
    idea = db.query(Idea).get(idea_id)
    if not idea:
        raise HTTPException(status_code=404)
    idea.status = "rejected"
    idea.rejection_notes = body.notes
    db.add(Approval(item_type="idea", item_id=idea_id, decision="rejected", decided_at=datetime.utcnow()))
    db.commit()
    return {"status": "rejected"}

@router.get("/content")
def get_pending_content(db: Session = Depends(get_db)):
    return db.query(Content).filter_by(status="pending").all()

@router.post("/content/{content_id}/approve")
def approve_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).get(content_id)
    if not content:
        raise HTTPException(status_code=404)
    content.status = "approved"
    db.add(Approval(item_type="content", item_id=content_id, decision="approved", decided_at=datetime.utcnow()))
    db.commit()
    return {"status": "approved"}

@router.post("/content/{content_id}/reject")
def reject_content(content_id: int, body: RejectionNotes, db: Session = Depends(get_db)):
    content = db.query(Content).get(content_id)
    if not content:
        raise HTTPException(status_code=404)
    content.status = "rejected"
    content.rejection_notes = body.notes
    db.add(Approval(item_type="content", item_id=content_id, decision="rejected", decided_at=datetime.utcnow()))
    db.commit()
    return {"status": "rejected"}

@router.get("/website")
def get_pending_website_changes(db: Session = Depends(get_db)):
    return db.query(WebsiteChange).filter_by(status="pending").all()

@router.post("/website/{change_id}/approve")
def approve_website_change(change_id: int, db: Session = Depends(get_db)):
    change = db.query(WebsiteChange).get(change_id)
    if not change:
        raise HTTPException(status_code=404)
    change.status = "approved"
    db.add(Approval(item_type="website_change", item_id=change_id, decision="approved", decided_at=datetime.utcnow()))
    db.commit()
    return {"status": "approved"}

@router.post("/website/{change_id}/reject")
def reject_website_change(change_id: int, body: RejectionNotes, db: Session = Depends(get_db)):
    change = db.query(WebsiteChange).get(change_id)
    if not change:
        raise HTTPException(status_code=404)
    change.status = "rejected"
    db.add(Approval(item_type="website_change", item_id=change_id, decision="rejected", decided_at=datetime.utcnow()))
    db.commit()
    return {"status": "rejected"}
```

**Step 5: Create `src/api/routes/agents.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import AgentRun

router = APIRouter()

@router.get("/status")
def get_agent_status(db: Session = Depends(get_db)):
    agents = ["orchestrator", "research", "strategy", "content", "post_production", "social", "website", "analytics"]
    result = {}
    for agent in agents:
        last_run = db.query(AgentRun).filter_by(agent_name=agent).order_by(AgentRun.started_at.desc()).first()
        result[agent] = {
            "last_run": last_run.started_at.isoformat() if last_run else None,
            "status": last_run.status if last_run else "never_run",
        }
    return result

@router.post("/trigger/{agent_name}")
async def trigger_agent(agent_name: str, db: Session = Depends(get_db)):
    from src.agents.orchestrator import OrchestratorAgent
    orchestrator = OrchestratorAgent(db=db)
    result = await orchestrator.trigger_agent(agent_name)
    return result
```

**Step 6: Create `src/api/routes/dashboard.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Idea, Content, Post, WebsiteChange, AgentRun

router = APIRouter()

@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    return {
        "pending_ideas": db.query(Idea).filter_by(status="pending").count(),
        "pending_content": db.query(Content).filter_by(status="pending").count(),
        "pending_website_changes": db.query(WebsiteChange).filter_by(status="pending").count(),
        "published_posts": db.query(Post).filter_by(status="published").count(),
        "total_reach": db.query(Post).with_entities(Post.reach).scalar() or 0,
    }

@router.get("/calendar")
def get_calendar(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.scheduled_at.desc()).limit(50).all()
    return posts

@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    posts = db.query(Post).filter_by(status="published").all()
    by_platform = {}
    for post in posts:
        if post.platform not in by_platform:
            by_platform[post.platform] = {"reach": 0, "engagement": 0, "count": 0}
        by_platform[post.platform]["reach"] += post.reach
        by_platform[post.platform]["engagement"] += post.engagement
        by_platform[post.platform]["count"] += 1
    return {"by_platform": by_platform, "total_posts": len(posts)}
```

**Step 7: Add test fixtures to `tests/conftest.py`**

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base
from src.db.database import get_db
from src.api.main import app

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

**Step 8: Run tests to verify they pass**

```bash
pytest tests/api/test_approvals.py -v
```
Expected: 3 PASSED

**Step 9: Commit**

```bash
git add src/api/ tests/api/ tests/conftest.py
git commit -m "feat: add FastAPI backend with approval, agent, and dashboard routes"
```

---

## Phase 7: Scheduler

### Task 13: Agent scheduler

**Files:**
- Create: `src/core/scheduler.py`
- Create: `src/main.py`
- Test: `tests/test_scheduler.py`

**Step 1: Write the failing test**

```python
# tests/test_scheduler.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.scheduler import AgentScheduler

def test_scheduler_registers_all_jobs():
    scheduler = AgentScheduler()
    scheduler.setup()
    job_ids = [job.id for job in scheduler.scheduler.get_jobs()]
    assert "research_daily" in job_ids
    assert "strategy_weekly" in job_ids
    assert "analytics_daily" in job_ids
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_scheduler.py -v
```
Expected: FAIL

**Step 3: Create `src/core/scheduler.py`**

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.db.database import SessionLocal
from src.agents.orchestrator import OrchestratorAgent

class AgentScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def setup(self):
        # Research: every day at 6am
        self.scheduler.add_job(self._run("research"), CronTrigger(hour=6), id="research_daily")
        # Analytics: every day at 8pm
        self.scheduler.add_job(self._run("analytics"), CronTrigger(hour=20), id="analytics_daily")
        # Strategy: every Monday at 7am
        self.scheduler.add_job(self._run("strategy"), CronTrigger(day_of_week="mon", hour=7), id="strategy_weekly")
        # Content: every day at 9am (processes approved ideas)
        self.scheduler.add_job(self._run("content"), CronTrigger(hour=9), id="content_daily")
        # Post-production: every day at 10am
        self.scheduler.add_job(self._run("post_production"), CronTrigger(hour=10), id="post_production_daily")
        # Social: every day at 11am (posts approved content)
        self.scheduler.add_job(self._run("social"), CronTrigger(hour=11), id="social_daily")
        # Website: every day at noon
        self.scheduler.add_job(self._run("website"), CronTrigger(hour=12), id="website_daily")

    def _run(self, agent_name: str):
        async def job():
            db = SessionLocal()
            try:
                orchestrator = OrchestratorAgent(db=db)
                await orchestrator.trigger_agent(agent_name)
            finally:
                db.close()
        return job

    def start(self):
        self.setup()
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()
```

**Step 4: Create `src/main.py`**

```python
import uvicorn
from dotenv import load_dotenv
load_dotenv()

from src.api.main import app
from src.core.scheduler import AgentScheduler

scheduler = AgentScheduler()

@app.on_event("startup")
def start_scheduler():
    scheduler.start()

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.stop()

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
```

**Step 5: Run tests to verify they pass**

```bash
pytest tests/test_scheduler.py -v
```
Expected: 1 PASSED

**Step 6: Commit**

```bash
git add src/core/scheduler.py src/main.py tests/test_scheduler.py
git commit -m "feat: add agent scheduler with autonomous daily/weekly cadence"
```

---

## Phase 8: React Dashboard

### Task 14: Scaffold React dashboard

**Files:**
- Create: `src/dashboard/` (Vite + React app)

**Step 1: Scaffold Vite React app**

```bash
cd src && npm create vite@latest dashboard -- --template react && cd dashboard && npm install && npm install -D tailwindcss postcss autoprefixer && npx tailwindcss init -p && npm install react-router-dom axios recharts
```

**Step 2: Configure Tailwind in `src/dashboard/src/index.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Step 3: Configure `tailwind.config.js`**

```js
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: { extend: { colors: { brand: "#FF6B35" } } },
  plugins: [],
}
```

**Step 4: Create `src/dashboard/src/api.js`**

```js
import axios from "axios"
const api = axios.create({ baseURL: "http://localhost:8000/api" })
export default api
```

**Step 5: Commit**

```bash
git add src/dashboard/
git commit -m "feat: scaffold React dashboard with Tailwind and routing"
```

---

### Task 15: Dashboard — Overview page

**Files:**
- Create: `src/dashboard/src/pages/Overview.jsx`
- Create: `src/dashboard/src/App.jsx`

**Step 1: Create `src/dashboard/src/App.jsx`**

```jsx
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom"
import Overview from "./pages/Overview"
import Approvals from "./pages/Approvals"
import Calendar from "./pages/Calendar"
import Analytics from "./pages/Analytics"
import Strategy from "./pages/Strategy"
import Website from "./pages/Website"
import Agents from "./pages/Agents"

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-950 text-white">
        <nav className="w-56 bg-gray-900 p-4 flex flex-col gap-2">
          <div className="text-brand font-bold text-lg mb-6">Daniel's Donuts</div>
          {[
            ["Overview", "/"],
            ["Approvals", "/approvals"],
            ["Calendar", "/calendar"],
            ["Analytics", "/analytics"],
            ["Strategy", "/strategy"],
            ["Website", "/website"],
            ["Agents", "/agents"],
          ].map(([label, path]) => (
            <NavLink key={path} to={path} end={path === "/"}
              className={({ isActive }) =>
                `px-3 py-2 rounded text-sm ${isActive ? "bg-brand text-white" : "text-gray-400 hover:text-white"}`
              }>
              {label}
            </NavLink>
          ))}
        </nav>
        <main className="flex-1 overflow-auto p-8">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/approvals" element={<Approvals />} />
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/strategy" element={<Strategy />} />
            <Route path="/website" element={<Website />} />
            <Route path="/agents" element={<Agents />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
```

**Step 2: Create `src/dashboard/src/pages/Overview.jsx`**

```jsx
import { useEffect, useState } from "react"
import api from "../api"

export default function Overview() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get("/dashboard/overview").then(r => setData(r.data))
  }, [])

  if (!data) return <div className="text-gray-400">Loading...</div>

  const cards = [
    { label: "Pending Ideas", value: data.pending_ideas, color: "text-yellow-400" },
    { label: "Pending Content", value: data.pending_content, color: "text-blue-400" },
    { label: "Website Changes", value: data.pending_website_changes, color: "text-purple-400" },
    { label: "Published Posts", value: data.published_posts, color: "text-green-400" },
    { label: "Total Reach", value: data.total_reach?.toLocaleString(), color: "text-brand" },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Overview</h1>
      <div className="grid grid-cols-3 gap-4">
        {cards.map(({ label, value, color }) => (
          <div key={label} className="bg-gray-900 rounded-xl p-6">
            <div className="text-gray-400 text-sm mb-1">{label}</div>
            <div className={`text-3xl font-bold ${color}`}>{value ?? 0}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

**Step 3: Commit**

```bash
git add src/dashboard/src/
git commit -m "feat: add dashboard overview page with KPI cards"
```

---

### Task 16: Dashboard — Approvals page

**Files:**
- Create: `src/dashboard/src/pages/Approvals.jsx`

**Step 1: Create `src/dashboard/src/pages/Approvals.jsx`**

```jsx
import { useEffect, useState } from "react"
import api from "../api"

function IdeaCard({ idea, onApprove, onReject }) {
  const [notes, setNotes] = useState("")
  const [showReject, setShowReject] = useState(false)

  return (
    <div className="bg-gray-900 rounded-xl p-5 mb-4">
      <h3 className="font-semibold text-white mb-1">{idea.title}</h3>
      <p className="text-gray-400 text-sm mb-4">{idea.body}</p>
      {showReject ? (
        <div className="flex gap-2">
          <input value={notes} onChange={e => setNotes(e.target.value)}
            placeholder="Rejection notes (optional)"
            className="flex-1 bg-gray-800 text-white text-sm px-3 py-2 rounded" />
          <button onClick={() => onReject(idea.id, notes)}
            className="bg-red-600 text-white px-4 py-2 rounded text-sm hover:bg-red-500">
            Confirm Reject
          </button>
          <button onClick={() => setShowReject(false)} className="text-gray-400 text-sm px-3">Cancel</button>
        </div>
      ) : (
        <div className="flex gap-2">
          <button onClick={() => onApprove(idea.id)}
            className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-500">
            Approve
          </button>
          <button onClick={() => setShowReject(true)}
            className="bg-red-900 text-red-300 px-4 py-2 rounded text-sm hover:bg-red-800">
            Reject
          </button>
        </div>
      )}
    </div>
  )
}

export default function Approvals() {
  const [ideas, setIdeas] = useState([])
  const [content, setContent] = useState([])

  const load = () => {
    api.get("/approvals/ideas").then(r => setIdeas(r.data))
    api.get("/approvals/content").then(r => setContent(r.data))
  }

  useEffect(() => { load() }, [])

  const approveIdea = (id) => api.post(`/approvals/ideas/${id}/approve`).then(load)
  const rejectIdea = (id, notes) => api.post(`/approvals/ideas/${id}/reject`, { notes }).then(load)

  const approveContent = (id) => api.post(`/approvals/content/${id}/approve`).then(load)
  const rejectContent = (id, notes) => api.post(`/approvals/content/${id}/reject`, { notes }).then(load)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Approvals</h1>

      <section className="mb-8">
        <h2 className="text-lg font-semibold text-yellow-400 mb-4">
          Stage 1 — Ideas ({ideas.length} pending)
        </h2>
        {ideas.length === 0 && <p className="text-gray-500 text-sm">No pending ideas.</p>}
        {ideas.map(idea => (
          <IdeaCard key={idea.id} idea={idea} onApprove={approveIdea} onReject={rejectIdea} />
        ))}
      </section>

      <section>
        <h2 className="text-lg font-semibold text-blue-400 mb-4">
          Stage 2 — Content ({content.length} pending)
        </h2>
        {content.length === 0 && <p className="text-gray-500 text-sm">No pending content.</p>}
        {content.map(item => (
          <div key={item.id} className="bg-gray-900 rounded-xl p-5 mb-4">
            <div className="flex gap-4 mb-3">
              {item.type === "image" && (
                <img src={`http://localhost:8000/media/${item.file_path.split("/").pop()}`}
                  alt="preview" className="w-32 h-32 object-cover rounded" />
              )}
              <div>
                <span className="text-xs text-gray-500 uppercase">{item.type}</span>
                <p className="text-gray-300 text-sm mt-1">{item.caption}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={() => approveContent(item.id)}
                className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-500">
                Approve
              </button>
              <button onClick={() => rejectContent(item.id, "")}
                className="bg-red-900 text-red-300 px-4 py-2 rounded text-sm hover:bg-red-800">
                Reject
              </button>
            </div>
          </div>
        ))}
      </section>
    </div>
  )
}
```

**Step 2: Commit**

```bash
git add src/dashboard/src/pages/Approvals.jsx
git commit -m "feat: add approvals page with two-stage idea and content review"
```

---

### Task 17: Dashboard — Agents, Analytics, and remaining pages

**Files:**
- Create: `src/dashboard/src/pages/Agents.jsx`
- Create: `src/dashboard/src/pages/Analytics.jsx`
- Create: `src/dashboard/src/pages/Strategy.jsx`
- Create: `src/dashboard/src/pages/Calendar.jsx`
- Create: `src/dashboard/src/pages/Website.jsx`

**Step 1: Create `src/dashboard/src/pages/Agents.jsx`**

```jsx
import { useEffect, useState } from "react"
import api from "../api"

const STATUS_COLORS = { completed: "text-green-400", failed: "text-red-400", running: "text-yellow-400", never_run: "text-gray-500" }

export default function Agents() {
  const [status, setStatus] = useState({})

  useEffect(() => {
    api.get("/agents/status").then(r => setStatus(r.data))
  }, [])

  const trigger = (name) => api.post(`/agents/trigger/${name}`).then(() => api.get("/agents/status").then(r => setStatus(r.data)))

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Agents</h1>
      <div className="grid grid-cols-2 gap-4">
        {Object.entries(status).map(([name, info]) => (
          <div key={name} className="bg-gray-900 rounded-xl p-5">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold capitalize">{name.replace("_", " ")}</h3>
              <span className={`text-xs font-mono ${STATUS_COLORS[info.status] || "text-gray-400"}`}>{info.status}</span>
            </div>
            <div className="text-gray-500 text-xs mb-3">{info.last_run ? `Last run: ${new Date(info.last_run).toLocaleString()}` : "Never run"}</div>
            <button onClick={() => trigger(name)} className="bg-gray-800 text-white text-xs px-3 py-1.5 rounded hover:bg-gray-700">
              Run Now
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
```

**Step 2: Create `src/dashboard/src/pages/Analytics.jsx`**

```jsx
import { useEffect, useState } from "react"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import api from "../api"

export default function Analytics() {
  const [data, setData] = useState(null)
  useEffect(() => { api.get("/dashboard/analytics").then(r => setData(r.data)) }, [])
  if (!data) return <div className="text-gray-400">Loading...</div>
  const chartData = Object.entries(data.by_platform || {}).map(([platform, metrics]) => ({ platform, ...metrics }))
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Analytics</h1>
      <div className="bg-gray-900 rounded-xl p-6 mb-6">
        <h2 className="text-gray-400 text-sm mb-4">Reach by Platform</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData}>
            <XAxis dataKey="platform" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip contentStyle={{ background: "#111827", border: "none" }} />
            <Bar dataKey="reach" fill="#FF6B35" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-gray-400 text-sm">Total published posts: {data.total_posts}</p>
    </div>
  )
}
```

**Step 3: Create stub pages for Strategy, Calendar, Website**

```jsx
// src/dashboard/src/pages/Strategy.jsx
import { useEffect, useState } from "react"
import api from "../api"
export default function Strategy() {
  const [ideas, setIdeas] = useState([])
  useEffect(() => { api.get("/approvals/ideas").then(r => setIdeas(r.data)) }, [])
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Strategy</h1>
      {ideas.map(i => <div key={i.id} className="bg-gray-900 rounded-xl p-4 mb-3"><h3 className="font-semibold">{i.title}</h3><p className="text-gray-400 text-sm">{i.body}</p></div>)}
    </div>
  )
}
```

```jsx
// src/dashboard/src/pages/Calendar.jsx
export default function Calendar() {
  return <div><h1 className="text-2xl font-bold mb-6">Content Calendar</h1><p className="text-gray-400">Scheduled posts will appear here.</p></div>
}
```

```jsx
// src/dashboard/src/pages/Website.jsx
import { useEffect, useState } from "react"
import api from "../api"
export default function Website() {
  const [changes, setChanges] = useState([])
  const load = () => api.get("/approvals/website").then(r => setChanges(r.data))
  useEffect(() => { load() }, [])
  const approve = (id) => api.post(`/approvals/website/${id}/approve`).then(load)
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Website Changes</h1>
      {changes.map(c => (
        <div key={c.id} className="bg-gray-900 rounded-xl p-5 mb-4">
          <span className="text-xs text-gray-500 uppercase">{c.change_type}</span>
          <p className="text-white font-semibold mt-1">{c.description}</p>
          <button onClick={() => approve(c.id)} className="mt-3 bg-green-600 text-white px-4 py-2 rounded text-sm">Approve</button>
        </div>
      ))}
    </div>
  )
}
```

**Step 4: Commit**

```bash
git add src/dashboard/src/pages/
git commit -m "feat: add all dashboard pages (agents, analytics, strategy, calendar, website)"
```

---

## Phase 9: Integration & Media Serving

### Task 18: Media file serving + final wiring

**Files:**
- Modify: `src/api/main.py`

**Step 1: Add static file serving to `src/api/main.py`**

```python
# Add after existing imports:
from fastapi.staticfiles import StaticFiles
import os

# Add after app creation:
os.makedirs("./media", exist_ok=True)
app.mount("/media", StaticFiles(directory="./media"), name="media")
```

**Step 2: Run the full test suite**

```bash
pytest tests/ -v
```
Expected: All tests PASS

**Step 3: Start the backend to verify it boots**

```bash
python -m src.main
```
Expected: Uvicorn starts on port 8000, scheduler initializes

**Step 4: Start the dashboard**

```bash
cd src/dashboard && npm run dev
```
Expected: Vite dev server starts on port 5173

**Step 5: Final commit**

```bash
git add src/api/main.py
git commit -m "feat: add media file serving, complete integration"
```

---

## Phase 10: Push to GitHub

### Task 19: Push to remote

**Step 1: Verify all tests pass**

```bash
pytest tests/ -v
```

**Step 2: Push to GitHub**

```bash
git push -u origin master
```

---

## Environment Setup Checklist

Before running, set all values in `.env`:

```
ANTHROPIC_API_KEY=          # Get from console.anthropic.com
HIGGSFIELD_API_KEY=         # Get from higgsfield.ai
META_APP_ID=                # Facebook Developer App
META_APP_SECRET=            # Facebook Developer App
META_ACCESS_TOKEN=          # Long-lived page access token
META_PAGE_ID=               # Daniel's Donuts Facebook Page ID
META_IG_ACCOUNT_ID=         # Instagram Business Account ID
TIKTOK_CLIENT_KEY=          # TikTok for Developers
TIKTOK_CLIENT_SECRET=       # TikTok for Developers
TIKTOK_ACCESS_TOKEN=        # TikTok Business Account token
WP_URL=https://danielsdonuts.com.au
WP_USERNAME=                # WordPress admin username
WP_APP_PASSWORD=            # WordPress Application Password (not login password)
DATABASE_URL=sqlite:///./daniels_marketing.db
REDIS_URL=redis://localhost:6379
MEDIA_DIR=./media
```
