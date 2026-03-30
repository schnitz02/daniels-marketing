import os
import httpx
import logging
from base64 import b64encode

logger = logging.getLogger(__name__)
POC_MODE = os.getenv("POC_MODE", "false").lower() == "true"

class WordPressClient:
    def __init__(self):
        self.url = os.getenv("WP_URL", "https://danielsdonuts.com.au")
        username = os.getenv("WP_USERNAME", "")
        password = os.getenv("WP_APP_PASSWORD", "")
        creds = b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/json",
        }

    async def update_banner(self, title: str, image_url: str = "", **kwargs) -> bool:
        if POC_MODE:
            logger.info("POC_MODE: stubbed WP banner update → title: %s", title)
            return True
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.url}/wp-json/wp/v2/pages",
                headers=self.headers,
                json={"title": title, "featured_media": image_url},
            )
            response.raise_for_status()
            return True

    async def create_post(self, title: str, content: str, status: str = "publish", **kwargs) -> dict:
        if POC_MODE:
            logger.info("POC_MODE: stubbed WP post → title: %s", title)
            return {"id": 9999, "link": "https://danielsdonuts.com.au/?p=9999", "status": status}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.url}/wp-json/wp/v2/posts",
                headers=self.headers,
                json={"title": title, "content": content, "status": status},
            )
            response.raise_for_status()
            return response.json()

    async def update_product(self, product_id: int, data: dict, **kwargs) -> dict:
        if POC_MODE:
            logger.info("POC_MODE: stubbed WP product update → id: %s", product_id)
            return {"id": product_id, "status": "publish"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(
                f"{self.url}/wp-json/wc/v3/products/{product_id}",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def create_campaign_page(self, title: str, content: str, **kwargs) -> dict:
        return await self.create_post(title, content, status="publish")
