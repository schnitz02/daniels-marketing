import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base, Idea, Content, Post
from src.agents.social import SocialAgent

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_social_agent_posts_approved_image(db):
    idea = Idea(title="Test", body="Test", status="approved")
    db.add(idea)
    db.flush()
    content = Content(idea_id=idea.id, type="image", file_path="/tmp/test.jpg", caption="Fresh donuts!", status="approved")
    db.add(content)
    db.commit()

    with patch("src.core.meta_client.MetaClient.post_image", new_callable=AsyncMock, return_value="meta_post_123"):
        agent = SocialAgent(db=db)
        result = await agent.execute()
        posts = db.query(Post).all()
        assert any(p.platform in ("instagram", "facebook") for p in posts)
        assert result["published"] >= 1

@pytest.mark.asyncio
async def test_social_agent_skips_already_posted(db):
    idea = Idea(title="Test", body="Test", status="approved")
    db.add(idea)
    db.flush()
    content = Content(idea_id=idea.id, type="image", file_path="/tmp/test.jpg", caption="Test", status="approved")
    db.add(content)
    db.flush()
    post = Post(content_id=content.id, platform="instagram", status="published")
    db.add(post)
    db.commit()

    agent = SocialAgent(db=db)
    result = await agent.execute()
    assert result["published"] == 0

@pytest.mark.asyncio
async def test_social_agent_registered(db):
    from src.agents.orchestrator import AGENT_REGISTRY
    assert "social" in AGENT_REGISTRY
