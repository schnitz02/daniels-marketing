import logging
import httpx
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)
MAX_POSTS = 9

# Instagram's internal app ID required for the web profile API
_IG_APP_ID = "936619743392459"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-AU,en;q=0.9",
    "x-ig-app-id": _IG_APP_ID,
    "Referer": "https://www.instagram.com/",
}


def scrape_instagram(handle: str) -> dict | None:
    """
    Scrape a public Instagram profile via the web profile info API.
    Returns a dict with profile stats and recent posts, or None if scraping fails.
    """
    try:
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={handle}"
        resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()

        data = resp.json()
        user = data["data"]["user"]

        recent_posts = []
        edges = (
            user.get("edge_owner_to_timeline_media", {})
                .get("edges", [])
        )
        for edge in edges[:MAX_POSTS]:
            node = edge.get("node", {})
            recent_posts.append({
                "post_id": node.get("shortcode", ""),
                "likes": node.get("edge_liked_by", {}).get("count", 0),
                "comments": node.get("edge_media_to_comment", {}).get("count", 0),
                "caption": (
                    node.get("edge_media_to_caption", {})
                        .get("edges", [{}])[0]
                        .get("node", {})
                        .get("text", "")
                )[:200],
                "thumbnail_url": node.get("thumbnail_src", node.get("display_url", "")),
                "posted_at": None,
            })

        return {
            "platform": "instagram",
            "handle": handle,
            "followers": user.get("edge_followed_by", {}).get("count", 0),
            "following": user.get("edge_follow", {}).get("count", 0),
            "posts_count": user.get("edge_owner_to_timeline_media", {}).get("count", 0),
            "bio": user.get("biography", ""),
            "recent_posts": recent_posts,
        }
    except Exception as e:
        logger.warning("Instagram scrape failed for %s: %s", handle, e)
        return None
