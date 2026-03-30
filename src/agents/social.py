import logging
from datetime import datetime, timezone
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.core.meta_client import MetaClient
from src.core.tiktok_client import TikTokClient
from src.db.models import Content, Post

logger = logging.getLogger(__name__)

@register_agent("social")
class SocialAgent(BaseAgent):
    name = "social"

    async def run(self):
        approved = self.db.query(Content).filter_by(status="approved").all()
        meta = MetaClient()
        tiktok = TikTokClient()
        published = 0

        for content in approved:
            platforms = ["instagram", "facebook", "tiktok"] if content.type == "reel" else ["instagram", "facebook"]
            # Only attempt platforms that haven't been successfully posted yet
            posted_platforms = {
                p.platform for p in self.db.query(Post).filter_by(content_id=content.id, status="published").all()
            }
            platforms = [p for p in platforms if p not in posted_platforms]
            if not platforms:
                continue

            for platform in platforms:
                try:
                    if platform in ("instagram", "facebook"):
                        if content.type == "image":
                            post_id = await meta.post_image(content.file_path, content.caption)
                        else:
                            post_id = await meta.post_reel(content.file_path, content.caption)
                    else:
                        post_id = await tiktok.post_video(content.file_path, content.caption)

                    post = Post(
                        content_id=content.id,
                        platform=platform,
                        platform_post_id=post_id,
                        published_at=datetime.now(timezone.utc),
                        status="published",
                    )
                    self.db.add(post)
                    published += 1
                except Exception as e:
                    logger.error("SocialAgent: failed to post to %s: %s", platform, e)
                    post = Post(content_id=content.id, platform=platform, status="failed")
                    self.db.add(post)

        self.db.commit()
        return {"published": published}
