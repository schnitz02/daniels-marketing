import os
import httpx
import logging

logger = logging.getLogger(__name__)

class MetaClient:
    GRAPH_API = "https://graph.facebook.com/v21.0"

    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.ig_account_id = os.getenv("META_IG_ACCOUNT_ID")

    async def post_image(self, image_path: str, caption: str) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(image_path, "rb") as f:
                upload = await client.post(
                    f"{self.GRAPH_API}/{self.ig_account_id}/media",
                    params={"access_token": self.access_token},
                    data={"caption": caption},
                    files={"image": f},
                )
            upload.raise_for_status()
            media_id = upload.json()["id"]
            publish = await client.post(
                f"{self.GRAPH_API}/{self.ig_account_id}/media_publish",
                params={"access_token": self.access_token, "creation_id": media_id},
            )
            publish.raise_for_status()
            return publish.json()["id"]

    async def post_reel(self, video_path: str, caption: str) -> str:
        async with httpx.AsyncClient(timeout=300.0) as client:
            with open(video_path, "rb") as f:
                upload = await client.post(
                    f"{self.GRAPH_API}/{self.ig_account_id}/media",
                    params={"access_token": self.access_token, "media_type": "REELS"},
                    data={"caption": caption},
                    files={"video": f},
                )
            upload.raise_for_status()
            media_id = upload.json()["id"]
            publish = await client.post(
                f"{self.GRAPH_API}/{self.ig_account_id}/media_publish",
                params={"access_token": self.access_token, "creation_id": media_id},
            )
            publish.raise_for_status()
            return publish.json()["id"]
