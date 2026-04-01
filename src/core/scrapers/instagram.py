import os
import logging
import httpx

logger = logging.getLogger(__name__)
MAX_POSTS = 9
POC_MODE = os.getenv("POC_MODE", "false").lower() == "true"
_SESSION_ID = os.getenv("INSTAGRAM_SESSION_ID", "")

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


_POC_STUB = {
    "platform": "instagram",
    "handle": "danielsdonutsaustralia",
    "followers": 14_800,
    "following": 312,
    "posts_count": 934,
    "bio": "Australia's favourite donut shop 🍩 Fresh glazed daily. Order online ⬇️",
    "recent_posts": [
        {"post_id": "poc_ig_1", "likes": 420, "comments": 18, "caption": "Our new Strawberry Dream donut is here! 🍓 Come try it this weekend.", "thumbnail_url": "", "posted_at": None},
        {"post_id": "poc_ig_2", "likes": 387, "comments": 24, "caption": "Nothing beats a fresh glazed on a Monday morning ☀️", "thumbnail_url": "", "posted_at": None},
        {"post_id": "poc_ig_3", "likes": 511, "comments": 31, "caption": "Behind the scenes: how we make 500 donuts before 6am 🍩", "thumbnail_url": "", "posted_at": None},
    ],
}


def scrape_instagram(handle: str) -> dict | None:
    """
    Scrape a public Instagram profile via the web profile info API.
    Returns a dict with profile stats and recent posts, or None if scraping fails.
    """
    try:
        # Use session cookie if available — bypasses rate limiting on the API
        if _SESSION_ID:
            headers = {**HEADERS, "Cookie": f"sessionid={_SESSION_ID}"}
            logger.info("Instagram: using session cookie for %s", handle)
        elif POC_MODE:
            logger.info("POC_MODE: returning Instagram stub for %s", handle)
            return {**_POC_STUB, "handle": handle}
        else:
            headers = HEADERS

        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={handle}"
        resp = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
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
        if POC_MODE:
            logger.info("POC_MODE: falling back to Instagram stub after failed scrape")
            return {**_POC_STUB, "handle": handle}
        return None
