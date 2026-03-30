# tests/db/test_models.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base, ResearchItem, Idea, Content, Post, Approval, WebsiteChange, AgentRun

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
    item = ResearchItem(source="instagram", competitor="Krispy Kreme", content="New strawberry glaze trending", raw_data={})
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

def test_create_website_change(db):
    change = WebsiteChange(change_type="banner", description="Easter campaign", payload={"title": "Easter!"}, status="pending")
    db.add(change)
    db.commit()
    assert change.id is not None
    assert change.status == "pending"

def test_create_agent_run(db):
    run = AgentRun(agent_name="research", status="running")
    db.add(run)
    db.commit()
    assert run.id is not None
    assert run.agent_name == "research"

def test_idea_content_relationship(db):
    idea = Idea(title="Relationship Test", body="Testing back_populates", status="pending")
    db.add(idea)
    db.flush()
    content = Content(idea_id=idea.id, type="image", file_path="/tmp/test.jpg", caption="Test", status="pending")
    db.add(content)
    db.commit()
    db.refresh(idea)
    assert len(idea.contents) == 1
    assert idea.contents[0].idea == idea

def test_create_approval(db):
    approval = Approval(item_type="idea", item_id=1, decision="approved", notes="Looks great")
    db.add(approval)
    db.commit()
    assert approval.id is not None
    assert approval.decision == "approved"

def test_rejection_notes_defaults_none(db):
    idea = Idea(title="No Rejection Notes", body="Test", status="pending")
    db.add(idea)
    db.commit()
    assert idea.rejection_notes is None
