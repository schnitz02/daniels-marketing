import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import Base, AgentRun
from src.agents.base import BaseAgent

class ConcreteAgent(BaseAgent):
    name = "test_agent"
    async def run(self):
        return {"status": "ok"}

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_agent_execute_returns_result(db):
    agent = ConcreteAgent(db=db)
    result = await agent.execute()
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_agent_records_run_in_db(db):
    agent = ConcreteAgent(db=db)
    await agent.execute()
    run = db.query(AgentRun).filter_by(agent_name="test_agent").first()
    assert run is not None
    assert run.status == "completed"

@pytest.mark.asyncio
async def test_agent_records_failure(db):
    class FailingAgent(BaseAgent):
        name = "failing_agent"
        async def run(self):
            raise ValueError("Something went wrong")

    agent = FailingAgent(db=db)
    with pytest.raises(ValueError):
        await agent.execute()

    run = db.query(AgentRun).filter_by(agent_name="failing_agent").first()
    assert run.status == "failed"
    assert "Something went wrong" in run.log
