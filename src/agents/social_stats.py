import logging
from datetime import datetime, timezone, date
from sqlalchemy import func
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.core.scrapers.instagram import scrape_instagram
from src.core.scrapers.tiktok import scrape_tiktok
from src.core.scrapers.facebook import scrape_facebook
from src.db.models import SocialSnapshot, SocialPostCache

logger = logging.getLogger(__name__)

PROFILES = [
    ("instagram", "danielsdonutsaustralia", scrape_instagram),
    ("tiktok",    "danielsdonutsaus",       scrape_tiktok),
    ("facebook",  "DanielsDonutsAustralia", scrape_facebook),
]


@register_agent("social_stats")
class SocialStatsAgent(BaseAgent):
    name = "social_stats"

    async def run(self):
        snapshots_saved = 0
        posts_cached = 0

        _g = globals()
        for platform, handle, scrape_fn in PROFILES:
            # Resolve via module globals so patch("src.agents.social_stats.scrape_*") works in tests
            data = _g[scrape_fn.__name__](handle)
            if data is None:
                logger.warning("Skipping %s — scrape returned None", platform)
                continue

            # Skip if we already have a snapshot for this platform today
            today = datetime.now(timezone.utc).date()
            existing_today = (
                self.db.query(SocialSnapshot)
                .filter(
                    SocialSnapshot.platform == platform,
                    func.date(SocialSnapshot.scraped_at) == today,
                )
                .first()
            )
            if existing_today:
                logger.info("Skipping %s — snapshot already exists for today", platform)
                continue

            snap = SocialSnapshot(
                platform=platform,
                handle=handle,
                followers=data.get("followers", 0),
                following=data.get("following", 0),
                posts_count=data.get("posts_count", 0),
                bio=data.get("bio", ""),
            )
            self.db.add(snap)
            snapshots_saved += 1

            for post in data.get("recent_posts", []):
                existing = self.db.query(SocialPostCache).filter_by(
                    post_id=post["post_id"]
                ).first()
                if existing:
                    existing.likes = post["likes"]
                    existing.comments = post["comments"]
                    existing.scraped_at = datetime.now(timezone.utc)
                else:
                    self.db.add(SocialPostCache(
                        platform=platform,
                        post_id=post["post_id"],
                        likes=post.get("likes", 0),
                        comments=post.get("comments", 0),
                        caption=post.get("caption", ""),
                        thumbnail_url=post.get("thumbnail_url", ""),
                        posted_at=post.get("posted_at"),
                    ))
                    posts_cached += 1

        self.db.commit()
        return {"snapshots_saved": snapshots_saved, "posts_cached": posts_cached}
