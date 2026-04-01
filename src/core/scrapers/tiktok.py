import json
import logging
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-AU,en;q=0.9",
}


def scrape_tiktok(handle: str) -> dict | None:
    """
    Scrape a public TikTok profile page.
    Returns profile stats dict or None if scraping fails.
    """
    try:
        url = f"https://www.tiktok.com/@{handle}"
        resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        script = soup.find("script", {"id": "__UNIVERSAL_DATA_FOR_REHYDRATION__"})
        if not script:
            logger.warning("TikTok: rehydration script not found for %s", handle)
            return None

        data = json.loads(script.string)
        user_info = (
            data.get("__DEFAULT_SCOPE__", {})
                .get("webapp.user-detail", {})
                .get("userInfo", {})
        )
        stats = user_info.get("stats", {})
        user = user_info.get("user", {})

        return {
            "platform": "tiktok",
            "handle": handle,
            "followers": stats.get("followerCount", 0),
            "following": stats.get("followingCount", 0),
            "posts_count": stats.get("videoCount", 0),
            "bio": user.get("signature", ""),
            "recent_posts": [],  # TikTok post-level data requires heavier scraping
        }
    except Exception as e:
        logger.warning("TikTok scrape failed for %s: %s", handle, e)
        return None
