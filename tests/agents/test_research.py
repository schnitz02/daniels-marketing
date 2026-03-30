import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base, ResearchItem
from src.agents.research import ResearchAgent

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_research_agent_stores_results(db):
    mock_results = [
        {"source": "instagram", "competitor": "Krispy Kreme", "content": "New glazed range", "raw_data": {}},
        {"source": "tiktok", "competitor": "Dunkin Donuts", "content": "Viral donut tower video", "raw_data": {}},
    ]
    with patch.object(ResearchAgent, "_scrape_competitors", return_value=mock_results):
        agent = ResearchAgent(db=db)
        result = await agent.execute()
        items = db.query(ResearchItem).all()
        assert len(items) == 2
        assert items[0].competitor == "Krispy Kreme"
        assert result["researched"] == 2

@pytest.mark.asyncio
async def test_research_agent_registered(db):
    from src.agents.orchestrator import AGENT_REGISTRY
    assert "research" in AGENT_REGISTRY
