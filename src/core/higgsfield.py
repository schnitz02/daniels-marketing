import os
import httpx

class HiggsFieldClient:
    BASE_URL = "https://api.higgsfield.ai/v1"

    def __init__(self):
        self.api_key = os.getenv("HIGGSFIELD_API_KEY")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def generate_image(self, prompt: str, output_path: str) -> str:
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
            img_response = await client.get(img_url)
            os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
            with open(output_path, "wb") as f:
                f.write(img_response.content)
        return output_path

    async def generate_video(self, prompt: str, output_path: str) -> str:
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
            video_response = await client.get(video_url)
            os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
            with open(output_path, "wb") as f:
                f.write(video_response.content)
        return output_path
