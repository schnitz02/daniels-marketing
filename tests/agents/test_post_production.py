import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base, Idea, Content
from src.agents.post_production import PostProductionAgent

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_post_production_processes_pending_reels(db):
    idea = Idea(title="Test", body="Test", status="approved")
    db.add(idea)
    db.flush()
    content = Content(idea_id=idea.id, type="reel", file_path="/tmp/raw_video.mp4", caption="Test", status="pending")
    db.add(content)
    db.commit()

    with patch("src.core.video_editor.VideoEditor.add_branding", return_value="/tmp/raw_video_branded.mp4"):
        agent = PostProductionAgent(db=db)
        result = await agent.execute()
        db.refresh(content)
        assert "branded" in content.file_path
        assert result["processed"] == 1

@pytest.mark.asyncio
async def test_post_production_skips_nonexistent_files(db):
    idea = Idea(title="Test", body="Test", status="approved")
    db.add(idea)
    db.flush()
    content = Content(idea_id=idea.id, type="reel", file_path="/tmp/does_not_exist_xyz.mp4", caption="Test", status="pending")
    db.add(content)
    db.commit()

    agent = PostProductionAgent(db=db)
    result = await agent.execute()
    assert result["processed"] == 0

@pytest.mark.asyncio
async def test_post_production_agent_registered(db):
    from src.agents.orchestrator import AGENT_REGISTRY
    assert "post_production" in AGENT_REGISTRY
