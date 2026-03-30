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
        # Ensure all agent modules are imported so they register themselves
        import src.agents.research      # noqa: F401
        import src.agents.strategy      # noqa: F401
        import src.agents.content       # noqa: F401
        import src.agents.post_production  # noqa: F401
        import src.agents.social        # noqa: F401
        import src.agents.website       # noqa: F401
        import src.agents.analytics     # noqa: F401
        agent_cls = AGENT_REGISTRY.get(agent_name)
        if not agent_cls:
            raise ValueError(f"Unknown agent: {agent_name}")
        agent = agent_cls(db=self.db)
        return await agent.execute()
