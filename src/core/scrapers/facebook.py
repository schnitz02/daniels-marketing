import re
import logging
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# mbasic.facebook.com is the stripped-down mobile version — no JS, no login redirect
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
    Scrape a public Facebook page via mbasic.facebook.com (no login redirect).
    Returns profile stats dict or None if scraping fails.
    """
    try:
        # mbasic serves a plain HTML page without auth redirect for public pages
        url = f"https://mbasic.facebook.com/{handle}"
        resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        full_text = soup.get_text(" ", strip=True)

        followers = 0
        # mbasic pages often have "X people follow this" or "X followers"
        for pattern in [
            r"([\d,\.]+[KkMm]?)\s+people\s+follow",
            r"([\d,\.]+[KkMm]?)\s+follower",
            r"([\d,\.]+[KkMm]?)\s+likes",
        ]:
            m = re.search(pattern, full_text, re.IGNORECASE)
            if m:
                followers = _parse_count(m.group(1))
                break

        # Page title as bio
        title_tag = soup.find("title")
        bio = title_tag.get_text(strip=True) if title_tag else ""
        # Remove " | Facebook" suffix
        bio = re.sub(r"\s*\|\s*Facebook$", "", bio, flags=re.IGNORECASE)

        return {
            "platform": "facebook",
            "handle": handle,
            "followers": followers,
            "following": 0,
            "posts_count": 0,
            "bio": bio,
            "recent_posts": [],
        }
    except Exception as e:
        logger.warning("Facebook scrape failed for %s: %s", handle, e)
        return None
