import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base, ResearchItem, Idea
from src.agents.strategy import StrategyAgent

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_strategy_creates_ideas(db):
    db.add(ResearchItem(source="instagram", competitor="Krispy Kreme", content="Strawberry glaze trending", raw_data={}))
    db.commit()

    mock_ideas = [
        {"title": "Strawberry Weekend Special", "body": "Launch a 3-day strawberry glazed campaign", "platform": "instagram", "content_type": "reel"},
        {"title": "Monday Morning Donut Drop", "body": "Post a reel each Monday at 7am", "platform": "tiktok", "content_type": "reel"},
    ]
    with patch.object(StrategyAgent, "_generate_ideas", return_value=mock_ideas):
        agent = StrategyAgent(db=db)
        result = await agent.execute()
        ideas = db.query(Idea).all()
        assert len(ideas) == 2
        assert all(i.status == "pending" for i in ideas)
        assert result["ideas_generated"] == 2

@pytest.mark.asyncio
async def test_strategy_agent_registered(db):
    from src.agents.orchestrator import AGENT_REGISTRY
    assert "strategy" in AGENT_REGISTRY

@pytest.mark.asyncio
async def test_strategy_skips_duplicate_ideas(db):
    mock_ideas = [{"title": "Same Idea", "body": "Same body", "platform": "instagram", "content_type": "image"}]
    with patch.object(StrategyAgent, "_generate_ideas", return_value=mock_ideas):
        agent = StrategyAgent(db=db)
        await agent.execute()
        await agent.execute()  # second run
        ideas = db.query(Idea).filter_by(title="Same Idea").all()
        assert len(ideas) == 1  # not duplicated
