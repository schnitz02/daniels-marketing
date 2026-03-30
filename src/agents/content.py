import os
import json
import logging
from anthropic import AsyncAnthropic
from sqlalchemy.orm import Session
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.core.higgsfield import HiggsFieldClient
from src.db.models import Idea, Content

logger = logging.getLogger(__name__)
MEDIA_DIR = os.getenv("MEDIA_DIR", "./media")

@register_agent("content")
class ContentAgent(BaseAgent):
    name = "content"

    async def run(self):
        approved_ideas = self.db.query(Idea).filter_by(status="approved").all()
        higgsfield = HiggsFieldClient()
        created = 0

        for idea in approved_ideas:
            if self.db.query(Content).filter_by(idea_id=idea.id).count() > 0:
                continue

            try:
                prompt = await self._build_prompt(idea)
                os.makedirs(MEDIA_DIR, exist_ok=True)

                image_path = os.path.join(MEDIA_DIR, f"idea_{idea.id}_image.jpg")
                await higgsfield.generate_image(prompt["image_prompt"], image_path)

                video_path = os.path.join(MEDIA_DIR, f"idea_{idea.id}_video.mp4")
                await higgsfield.generate_video(prompt["video_prompt"], video_path)

                for file_path, content_type in [(image_path, "image"), (video_path, "reel")]:
                    content = Content(
                        idea_id=idea.id,
                        type=content_type,
                        file_path=file_path,
                        caption=prompt.get("caption", ""),
                        status="pending",
                    )
                    self.db.add(content)
                    created += 1

            except Exception as e:
                logger.error("ContentAgent: failed to generate content for idea %d: %s", idea.id, e)

        self.db.commit()
        return {"content_created": created}

    async def _build_prompt(self, idea: Idea) -> dict:
        client = AsyncAnthropic()
        message = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": (
                    f"You are a creative director for Daniel's Donuts, an Australian donut brand. "
                    f"For this marketing idea: '{idea.title}' — '{idea.body}'\n"
                    f"Generate:\n"
                    f"1. A detailed Higgsfield image prompt (photorealistic donuts, appetising, bright)\n"
                    f"2. A detailed Higgsfield video prompt (15 second reel, vertical 9:16)\n"
                    f"3. An engaging social media caption with relevant Australian hashtags\n"
                    f'Return ONLY valid JSON: {{"image_prompt": "str", "video_prompt": "str", "caption": "str"}}'
                )
            }]
        )
        raw = message.content[0].text
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error("ContentAgent: failed to parse prompt JSON: %s\nRaw: %s", e, raw[:300])
            return {"image_prompt": idea.title, "video_prompt": idea.body, "caption": idea.title}
