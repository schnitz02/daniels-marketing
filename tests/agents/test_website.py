import pytest
from unittest.mock import patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base, WebsiteChange, Idea
from src.agents.website import WebsiteAgent

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_website_agent_applies_approved_banner(db):
    change = WebsiteChange(
        change_type="banner",
        description="Easter campaign banner",
        payload={"title": "Easter Donuts!", "image_url": "/tmp/easter.jpg"},
        status="approved",
    )
    db.add(change)
    db.commit()

    with patch("src.core.wordpress_client.WordPressClient.update_banner", new_callable=AsyncMock, return_value=True):
        agent = WebsiteAgent(db=db)
        result = await agent.execute()
        db.refresh(change)
        assert change.status == "applied"
        assert result["applied"] == 1

@pytest.mark.asyncio
async def test_website_agent_marks_failed_on_error(db):
    change = WebsiteChange(
        change_type="banner",
        description="Failing banner",
        payload={"title": "Fail"},
        status="approved",
    )
    db.add(change)
    db.commit()

    with patch("src.core.wordpress_client.WordPressClient.update_banner", new_callable=AsyncMock, side_effect=Exception("WP down")):
        agent = WebsiteAgent(db=db)
        await agent.execute()
        db.refresh(change)
        assert change.status == "failed"

@pytest.mark.asyncio
async def test_website_agent_registered(db):
    from src.agents.orchestrator import AGENT_REGISTRY
    assert "website" in AGENT_REGISTRY
