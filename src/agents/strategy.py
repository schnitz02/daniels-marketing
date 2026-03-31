from anthropic import AsyncAnthropic
from sqlalchemy.orm import Session
from src.agents.base import BaseAgent, parse_claude_json
from src.agents.orchestrator import register_agent
from src.db.models import ResearchItem, Post, Idea

@register_agent("strategy")
class StrategyAgent(BaseAgent):
    name = "strategy"

    async def run(self):
        research = self.db.query(ResearchItem).order_by(ResearchItem.created_at.desc()).limit(20).all()
        posts = self.db.query(Post).order_by(Post.published_at.desc()).limit(20).all()
        ideas = await self._generate_ideas(research, posts)
        added = 0
        for idea_data in ideas:
            existing = self.db.query(Idea).filter_by(title=idea_data["title"]).first()
            if not existing:
                idea = Idea(title=idea_data["title"], body=idea_data["body"], status="pending")
                self.db.add(idea)
                added += 1
        self.db.commit()
        return {"ideas_generated": added}

    async def _generate_ideas(self, research=None, posts=None) -> list[dict]:
        research_summary = "\n".join([f"- {r.competitor}: {r.content}" for r in (research or [])])
        client = AsyncAnthropic()
        message = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": (
                    f"You are the marketing strategist for Daniel's Donuts, a 100% Aussie-made donut brand with 50+ flavours. "
                    f"Based on this competitor research:\n{research_summary}\n\n"
                    f"Generate 5 creative marketing ideas for Instagram, Facebook, and TikTok. "
                    f"Focus on viral potential, Australian culture, and what makes Daniel's unique. "
                    f'Return ONLY valid JSON: {{"ideas": [{{"title": "str", "body": "str", "platform": "str", "content_type": "str"}}]}}'
                )
            }]
        )
        raw = message.content[0].text
        try:
            data = parse_claude_json(raw)
            return data.get("ideas", [])
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                "StrategyAgent: failed to parse Claude response as JSON. Error: %s\nRaw response: %s",
                e, raw[:500]
            )
            return []
