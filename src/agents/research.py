from anthropic import AsyncAnthropic
from sqlalchemy.orm import Session
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.db.models import ResearchItem

COMPETITORS = [
    "Krispy Kreme Australia",
    "Dunkin Donuts",
    "Donut King",
    "Mad Mex",
]

@register_agent("research")
class ResearchAgent(BaseAgent):
    name = "research"

    async def run(self):
        results = await self._scrape_competitors()
        for item in results:
            record = ResearchItem(
                source=item["source"],
                competitor=item["competitor"],
                content=item["content"],
                raw_data=item.get("raw_data", {}),
            )
            self.db.add(record)
        self.db.commit()
        return {"researched": len(results)}

    async def _scrape_competitors(self) -> list[dict]:
        client = AsyncAnthropic()
        results = []
        for competitor in COMPETITORS:
            message = await client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": (
                        f"You are a marketing research agent for Daniel's Donuts, an Australian donut brand. "
                        f"Based on your knowledge of {competitor}'s marketing strategy, social media presence, "
                        f"and recent campaigns, provide 3 key insights that Daniel's Donuts could learn from or respond to. "
                        f'Return ONLY valid JSON: {{"insights": [{{"insight": "str", "platform": "str", "actionable": "str"}}]}}'
                    )
                }]
            )
            results.append({
                "source": "claude_research",
                "competitor": competitor,
                "content": message.content[0].text,
                "raw_data": {"model": "claude-sonnet-4-6"},
            })
        return results
