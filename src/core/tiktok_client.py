import os
import httpx
import logging

logger = logging.getLogger(__name__)

class TikTokClient:
    API_BASE = "https://open.tiktokapis.com/v2"

    def __init__(self):
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")

    async def post_video(self, video_path: str, caption: str) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            if len(caption) > 150:
                logger.warning("TikTokClient: caption truncated from %d to 150 chars for TikTok", len(caption))
            truncated_caption = caption[:150]
            init = await client.post(
                f"{self.API_BASE}/post/publish/video/init/",
                headers={"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"},
                json={
                    "post_info": {"title": truncated_caption, "privacy_level": "PUBLIC_TO_EVERYONE"},
                    "source_info": {"source": "FILE_UPLOAD"},
                },
            )
            init.raise_for_status()
            data = init.json()["data"]
            upload_url = data["upload_url"]
            with open(video_path, "rb") as f:
                video_bytes = f.read()
            upload_resp = await client.put(
                upload_url,
                content=video_bytes,
                headers={"Content-Type": "video/mp4", "Content-Length": str(len(video_bytes))},
            )
            upload_resp.raise_for_status()
            return data["publish_id"]
