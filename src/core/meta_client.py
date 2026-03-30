import os
import uuid
import httpx
import logging

logger = logging.getLogger(__name__)
POC_MODE = os.getenv("POC_MODE", "false").lower() == "true"

class MetaClient:
    GRAPH_API = "https://graph.facebook.com/v21.0"

    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.ig_account_id = os.getenv("META_IG_ACCOUNT_ID")
        self.page_id = os.getenv("META_PAGE_ID")

    async def post_image(self, image_path: str, caption: str) -> str:
        if POC_MODE:
            post_id = f"poc_ig_{uuid.uuid4().hex[:8]}"
            logger.info("POC_MODE: stubbed Instagram image post → %s | caption: %s", post_id, caption[:60])
            return post_id
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

    async def post_to_facebook_page(self, message: str, image_path: str = None) -> str:
        if POC_MODE:
            post_id = f"poc_fb_{uuid.uuid4().hex[:8]}"
            logger.info("POC_MODE: stubbed Facebook page post → %s | message: %s", post_id, message[:60])
            return post_id
        """Post to Facebook Page feed (text + optional photo)."""
        if not self.page_id:
            logger.warning("MetaClient: META_PAGE_ID not set, skipping Facebook page post")
            return ""
        async with httpx.AsyncClient(timeout=60.0) as client:
            if image_path:
                with open(image_path, "rb") as f:
                    response = await client.post(
                        f"{self.GRAPH_API}/{self.page_id}/photos",
                        params={"access_token": self.access_token},
                        data={"caption": message},
                        files={"source": f},
                    )
            else:
                response = await client.post(
                    f"{self.GRAPH_API}/{self.page_id}/feed",
                    params={"access_token": self.access_token},
                    json={"message": message},
                )
            response.raise_for_status()
            return response.json().get("id", "")

    async def post_reel(self, video_path: str, caption: str) -> str:
        if POC_MODE:
            post_id = f"poc_reel_{uuid.uuid4().hex[:8]}"
            logger.info("POC_MODE: stubbed Instagram reel post → %s | caption: %s", post_id, caption[:60])
            return post_id
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
