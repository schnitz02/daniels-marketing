import os
import httpx
import logging
from base64 import b64encode

logger = logging.getLogger(__name__)

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
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.url}/wp-json/wp/v2/pages",
                headers=self.headers,
                json={"title": title, "featured_media": image_url},
            )
            return response.status_code in (200, 201)

    async def create_post(self, title: str, content: str, status: str = "publish", **kwargs) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.url}/wp-json/wp/v2/posts",
                headers=self.headers,
                json={"title": title, "content": content, "status": status},
            )
            response.raise_for_status()
            return response.json()

    async def update_product(self, product_id: int, data: dict, **kwargs) -> dict:
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
