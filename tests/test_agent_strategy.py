# tests/test_agent_strategy.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from tests.conftest import *  # noqa
from src.db.models import Idea, ResearchItem


def _make_research(db):
    item = ResearchItem(
        source="instagram",
        competitor="Krispy Kreme",
        content="KK saw 40% engagement uplift on limited edition posts"
    )
    db.add(item)
    db.commit()


@pytest.mark.asyncio
async def test_strategy_agent_stores_evidence(db):
    from src.agents.strategy import StrategyAgent
    _make_research(db)

    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text='{"ideas": [{"title": "Limited Edition Drop", "body": "Create a limited edition donut", "platform": "instagram", "content_type": "post", "evidence": "KK saw 40% uplift on limited edition posts"}]}')]

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_msg)

    with patch("src.agents.strategy.AsyncAnthropic", return_value=mock_client):
        agent = StrategyAgent(db=db)
        result = await agent.run()

    idea = db.query(Idea).first()
    assert idea is not None
    assert idea.evidence == "KK saw 40% uplift on limited edition posts"
    assert result["ideas_generated"] >= 1
