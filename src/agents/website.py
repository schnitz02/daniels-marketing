import json
import logging
import anthropic
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.core.wordpress_client import WordPressClient
from src.db.models import WebsiteChange, Idea

logger = logging.getLogger(__name__)

@register_agent("website")
class WebsiteAgent(BaseAgent):
    name = "website"

    async def run(self):
        approved = self.db.query(WebsiteChange).filter_by(status="approved").all()
        wp = WordPressClient()
        applied = 0

        for change in approved:
            try:
                if change.change_type == "banner":
                    await wp.update_banner(**change.payload)
                elif change.change_type == "blog_post":
                    await wp.create_post(**change.payload)
                elif change.change_type == "product":
                    await wp.update_product(**change.payload)
                elif change.change_type == "campaign_page":
                    await wp.create_campaign_page(**change.payload)
                change.status = "applied"
                applied += 1
            except Exception as e:
                logger.error("WebsiteAgent: failed to apply change %d (%s): %s", change.id, change.change_type, e)
                change.status = "failed"

        # Generate website change suggestions from approved ideas
        approved_ideas = self.db.query(Idea).filter_by(status="approved").all()
        for idea in approved_ideas:
            existing = self.db.query(WebsiteChange).filter_by(description=idea.title).first()
            if not existing:
                await self._suggest_website_change(idea)

        self.db.commit()
        return {"applied": applied}

    async def _suggest_website_change(self, idea: Idea):
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": (
                    f"For this Daniel's Donuts marketing idea: '{idea.title}' — '{idea.body}'\n"
                    f"Suggest a website change (banner, blog_post, or campaign_page). "
                    f'Return ONLY valid JSON: {{"change_type": "str", "description": "str", "payload": {{}}}}'
                )
            }]
        )
        raw = message.content[0].text
        try:
            data = json.loads(raw)
            change = WebsiteChange(
                change_type=data["change_type"],
                description=idea.title,
                payload=data.get("payload", {}),
                status="pending",
            )
            self.db.add(change)
        except json.JSONDecodeError as e:
            logger.error("WebsiteAgent: failed to parse suggestion JSON: %s\nRaw: %s", e, raw[:300])
