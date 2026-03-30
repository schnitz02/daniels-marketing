import os
import httpx
import logging

logger = logging.getLogger(__name__)
POC_MODE = os.getenv("POC_MODE", "false").lower() == "true"

class HiggsFieldClient:
    BASE_URL = "https://api.higgsfield.ai/v1"

    def __init__(self):
        self.api_key = os.getenv("HIGGSFIELD_API_KEY")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def generate_image(self, prompt: str, output_path: str) -> str:
        if POC_MODE:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            # Write a minimal 1x1 white PNG as placeholder
            PNG_1X1 = bytes([137,80,78,71,13,10,26,10,0,0,0,13,73,72,68,82,0,0,0,1,0,0,0,1,8,2,0,0,0,144,119,83,222,0,0,0,12,73,68,65,84,8,215,99,248,255,255,63,0,5,254,2,254,220,204,89,231,0,0,0,0,73,69,78,68,174,66,96,130])
            with open(output_path, "wb") as f:
                f.write(PNG_1X1)
            logger.info("POC_MODE: stubbed image saved to %s | prompt: %s", output_path, prompt[:80])
            return output_path
        """Generate an image via Higgsfield API and save to output_path."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/generate/image",
                headers=self.headers,
                json={"prompt": prompt, "style": "photorealistic", "aspect_ratio": "1:1"},
            )
            response.raise_for_status()
            data = response.json()
            img_url = data.get("url") or data.get("image_url")
            if not img_url:
                raise ValueError(f"Higgsfield API returned no image URL. Response: {data}")
            img_response = await client.get(img_url)
            img_response.raise_for_status()
            if os.path.dirname(output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(img_response.content)
        return output_path

    async def generate_video(self, prompt: str, output_path: str) -> str:
        if POC_MODE:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(b"POC_VIDEO_STUB")
            logger.info("POC_MODE: stubbed video saved to %s | prompt: %s", output_path, prompt[:80])
            return output_path
        """Generate a video via Higgsfield API and save to output_path."""
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/generate/video",
                headers=self.headers,
                json={"prompt": prompt, "duration": 15, "aspect_ratio": "9:16"},
            )
            response.raise_for_status()
            data = response.json()
            video_url = data.get("url") or data.get("video_url")
            if not video_url:
                raise ValueError(f"Higgsfield API returned no video URL. Response: {data}")
            video_response = await client.get(video_url)
            video_response.raise_for_status()
            if os.path.dirname(output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(video_response.content)
        return output_path
