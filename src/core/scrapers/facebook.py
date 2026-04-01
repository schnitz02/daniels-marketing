import re
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


def _parse_count(text: str) -> int:
    """Parse '8,500', '8.5K', or '12M' style numbers into int."""
    if not text:
        return 0
    text = text.strip()
    multiplier = 1
    upper = text.upper()
    if upper.endswith("K"):
        multiplier = 1_000
        text = text[:-1]
    elif upper.endswith("M"):
        multiplier = 1_000_000
        text = text[:-1]
    text = text.replace(",", "").replace(".", "")
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) * multiplier if match else 0


def scrape_facebook(handle: str) -> dict | None:
    """
    Scrape a public Facebook page.
    Returns profile stats dict or None if scraping fails.
    """
    try:
        url = f"https://www.facebook.com/{handle}"
        resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        followers = 0

        # Try og:description meta tag — often contains "X likes · Y followers"
        # Note: likes are present in the description but not surfaced here since
        # SocialSnapshot has no likes column.
        desc_meta = soup.find("meta", property="og:description")
        if desc_meta:
            desc = desc_meta.get("content", "")
            followers_match = re.search(r"([\d,]+)\s+follower", desc, re.IGNORECASE)
            if followers_match:
                followers = _parse_count(followers_match.group(1))

        title_meta = soup.find("meta", property="og:title")
        bio = title_meta.get("content", "") if title_meta else ""

        return {
            "platform": "facebook",
            "handle": handle,
            "followers": followers,
            "following": 0,   # Facebook pages don't have a following count
            "posts_count": 0,  # Not reliably available without API
            "bio": bio,
            "recent_posts": [],
        }
    except Exception as e:
        logger.warning("Facebook scrape failed for %s: %s", handle, e)
        return None
