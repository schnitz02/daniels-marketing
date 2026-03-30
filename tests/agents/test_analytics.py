import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base, Post
from src.agents.analytics import AnalyticsAgent

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_analytics_updates_post_metrics(db):
    post = Post(content_id=1, platform="instagram", platform_post_id="ig_123", status="published")
    db.add(post)
    db.commit()

    with patch.object(AnalyticsAgent, "_fetch_metrics", return_value={"reach": 1500, "engagement": 230}):
        agent = AnalyticsAgent(db=db)
        result = await agent.execute()
        db.refresh(post)
        assert post.reach == 1500
        assert post.engagement == 230
        assert result["updated"] == 1

@pytest.mark.asyncio
async def test_analytics_skips_unpublished(db):
    post = Post(content_id=1, platform="instagram", status="scheduled")
    db.add(post)
    db.commit()

    agent = AnalyticsAgent(db=db)
    result = await agent.execute()
    assert result["updated"] == 0

@pytest.mark.asyncio
async def test_analytics_agent_registered(db):
    from src.agents.orchestrator import AGENT_REGISTRY
    assert "analytics" in AGENT_REGISTRY
