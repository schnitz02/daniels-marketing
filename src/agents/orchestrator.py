from sqlalchemy.orm import Session
from src.agents.base import BaseAgent

AGENT_REGISTRY: dict = {}

def register_agent(name: str):
    def decorator(cls):
        AGENT_REGISTRY[name] = cls
        return cls
    return decorator

class OrchestratorAgent(BaseAgent):
    name = "orchestrator"

    async def run(self):
        return {"status": "orchestrator running"}

    async def trigger_agent(self, agent_name: str):
        agent_cls = AGENT_REGISTRY.get(agent_name)
        if not agent_cls:
            raise ValueError(f"Unknown agent: {agent_name}")
        agent = agent_cls(db=self.db)
        return await agent.execute()
