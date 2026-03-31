import json
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.db.models import AgentRun


def parse_claude_json(raw: str) -> dict | list:
    """Parse JSON from Claude responses, stripping markdown code fences if present."""
    cleaned = raw.strip()
    # Strip ```json ... ``` or ``` ... ``` wrappers
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned.strip())

class BaseAgent(ABC):
    name: str = "base_agent"

    def __init__(self, db: Session):
        self.db = db

    async def execute(self):
        run = AgentRun(agent_name=self.name, status="running")
        self.db.add(run)
        self.db.commit()
        try:
            result = await self.run()
            run.status = "completed"
            run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            return result
        except Exception as e:
            run.status = "failed"
            run.log = str(e)
            run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            raise

    @abstractmethod
    async def run(self):
        pass
