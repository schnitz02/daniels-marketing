import os
import httpx
import logging
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.db.models import Post

logger = logging.getLogger(__name__)

@register_agent("analytics")
class AnalyticsAgent(BaseAgent):
    name = "analytics"

    async def run(self):
        published_posts = self.db.query(Post).filter_by(status="published").all()
        updated = 0
        for post in published_posts:
            try:
                metrics = await self._fetch_metrics(post)
                if metrics:
                    post.reach = metrics.get("reach", post.reach)
                    post.engagement = metrics.get("engagement", post.engagement)
                    updated += 1
            except Exception as e:
                logger.warning("AnalyticsAgent: failed to fetch metrics for post %d: %s", post.id, e)
        self.db.commit()
        return {"updated": updated}

    async def _fetch_metrics(self, post: Post) -> dict:
        if post.platform in ("instagram", "facebook") and post.platform_post_id:
            return await self._fetch_meta_metrics(post.platform_post_id)
        return {}

    async def _fetch_meta_metrics(self, post_id: str) -> dict:
        access_token = os.getenv("META_ACCESS_TOKEN")
        if not access_token:
            return {}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://graph.facebook.com/v21.0/{post_id}/insights",
                params={
                    "metric": "impressions,reach,engagement",
                    "access_token": access_token,
                },
            )
            if response.status_code != 200:
                logger.warning("AnalyticsAgent: Meta API returned %d for post %s", response.status_code, post_id)
                return {}
            data = response.json().get("data", [])
            metrics = {}
            for item in data:
                values = item.get("values", [])
                if not values:
                    continue
                if item["name"] == "reach":
                    metrics["reach"] = values[0].get("value", 0)
                elif item["name"] == "engagement":
                    metrics["engagement"] = values[0].get("value", 0)
            return metrics
