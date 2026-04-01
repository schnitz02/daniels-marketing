import os
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import AgentRun

router = APIRouter()

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    expected = os.getenv("AGENT_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=403, detail="Invalid API key")

AGENT_NAMES = ["orchestrator", "research", "strategy", "content",
               "post_production", "social", "social_stats", "website", "analytics"]

@router.get("/status")
def get_agent_status(db: Session = Depends(get_db)):
    result = {}
    for agent in AGENT_NAMES:
        last_run = db.query(AgentRun).filter_by(agent_name=agent).order_by(AgentRun.started_at.desc()).first()
        result[agent] = {
            "last_run": last_run.started_at.isoformat() if last_run else None,
            "status": last_run.status if last_run else "never_run",
        }
    return result

@router.post("/trigger/{agent_name}", dependencies=[Depends(verify_api_key)])
async def trigger_agent(agent_name: str, db: Session = Depends(get_db)):
    if agent_name not in AGENT_NAMES:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_name}")
    # Import all agent modules to ensure they are registered
    import src.agents.research  # noqa
    import src.agents.strategy  # noqa
    import src.agents.content   # noqa
    import src.agents.post_production  # noqa
    import src.agents.social    # noqa
    import src.agents.website   # noqa
    import src.agents.analytics # noqa
    import src.agents.social_stats  # noqa
    from src.agents.orchestrator import OrchestratorAgent
    orchestrator = OrchestratorAgent(db=db)
    result = await orchestrator.trigger_agent(agent_name)
    return result
