import pytest
from unittest.mock import patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base, Idea, Content
from src.agents.content import ContentAgent

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_content_agent_creates_content_for_approved_ideas(db):
    idea = Idea(title="Glazed Monday", body="Monday morning glazed donut reel", status="approved")
    db.add(idea)
    db.commit()

    with patch("src.core.higgsfield.HiggsFieldClient.generate_image", new_callable=AsyncMock, return_value="/tmp/test_image.jpg"), \
         patch("src.core.higgsfield.HiggsFieldClient.generate_video", new_callable=AsyncMock, return_value="/tmp/test_video.mp4"), \
         patch.object(ContentAgent, "_build_prompt", new_callable=AsyncMock, return_value={
             "image_prompt": "delicious glazed donut",
             "video_prompt": "glazed donut slow motion pour",
             "caption": "Start your week right 🍩 #DanielsDonutsAU"
         }):
        agent = ContentAgent(db=db)
        result = await agent.execute()
        contents = db.query(Content).all()
        assert len(contents) == 2  # one image + one reel
        assert all(c.idea_id == idea.id for c in contents)
        assert all(c.status == "pending" for c in contents)
        assert result["content_created"] == 2

@pytest.mark.asyncio
async def test_content_agent_skips_already_generated(db):
    idea = Idea(title="Already Done", body="Test", status="approved")
    db.add(idea)
    db.flush()
    existing = Content(idea_id=idea.id, type="image", file_path="/tmp/existing.jpg", caption="Already here", status="pending")
    db.add(existing)
    db.commit()

    with patch.object(ContentAgent, "_build_prompt", new_callable=AsyncMock, return_value={}):
        agent = ContentAgent(db=db)
        result = await agent.execute()
        assert result["content_created"] == 0

@pytest.mark.asyncio
async def test_content_agent_registered(db):
    from src.agents.orchestrator import AGENT_REGISTRY
    assert "content" in AGENT_REGISTRY
