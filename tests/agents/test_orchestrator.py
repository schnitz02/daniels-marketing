import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base, Idea
from src.agents.orchestrator import OrchestratorAgent, AGENT_REGISTRY

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_orchestrator_runs(db):
    orchestrator = OrchestratorAgent(db=db)
    result = await orchestrator.execute()
    assert result["status"] == "orchestrator running"

@pytest.mark.asyncio
async def test_orchestrator_triggers_registered_agent(db):
    from src.agents.base import BaseAgent
    from src.agents.orchestrator import register_agent

    @register_agent("mock_test_agent")
    class MockAgent(BaseAgent):
        name = "mock_test_agent"
        async def run(self):
            return {"ran": True}

    orchestrator = OrchestratorAgent(db=db)
    result = await orchestrator.trigger_agent("mock_test_agent")
    assert result["ran"] is True

@pytest.mark.asyncio
async def test_orchestrator_raises_for_unknown_agent(db):
    orchestrator = OrchestratorAgent(db=db)
    with pytest.raises(ValueError, match="Unknown agent"):
        await orchestrator.trigger_agent("nonexistent_agent")
