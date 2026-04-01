import re
import json
import logging
from curl_cffi import requests as cffi_requests
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


def _scrape_socialblade(handle: str) -> dict | None:
    """Fetch Facebook stats from Social Blade's embedded tRPC data."""
    url = f"https://socialblade.com/facebook/user/{handle}"
    resp = cffi_requests.get(url, impersonate="chrome", timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag:
        return None

    data = json.loads(tag.string)
    queries = data["props"]["pageProps"]["trpcState"]["json"]["queries"]

    user_data = None
    for q in queries:
        key = str(q.get("queryKey", ""))
        d = q.get("state", {}).get("data")
        if "facebook" in key and "user" in key and isinstance(d, dict):
            user_data = d
            break

    if not user_data:
        return None

    # Social Blade exposes page likes as the follower equivalent for Facebook
    followers = user_data.get("likes", 0) or user_data.get("followers", 0)
    bio = user_data.get("display_name", "") or user_data.get("name", "")

    return {
        "platform": "facebook",
        "handle": handle,
        "followers": followers,
        "following": 0,
        "posts_count": 0,
        "bio": bio,
        "recent_posts": [],
    }


def scrape_facebook(handle: str) -> dict | None:
    """
    Scrape a public Facebook page via Social Blade (reliable, no login required).
    Falls back to None if scraping fails.
    """
    try:
        return _scrape_socialblade(handle)
    except Exception as e:
        logger.warning("Facebook scrape failed for %s: %s", handle, e)
        return None
