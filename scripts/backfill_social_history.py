"""
One-time script to backfill SocialSnapshot history from Social Blade.
Run once: python -m scripts.backfill_social_history
"""
import json
import sys
import os
import logging
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests

# Allow running as: python -m scripts.backfill_social_history
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.database import SessionLocal, init_db
from src.db.models import SocialSnapshot

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROFILES = [
    {
        "url": "https://socialblade.com/instagram/user/danielsdonutsaustralia",
        "platform": "instagram",
        "handle": "danielsdonutsaustralia",
        "map": lambda row: {
            "followers": row.get("followers", 0),
            "following": row.get("following", 0),
            "posts_count": row.get("media_count", 0),
            "bio": "",
        },
    },
    {
        "url": "https://socialblade.com/tiktok/user/danielsdonutsaus",
        "platform": "tiktok",
        "handle": "danielsdonutsaus",
        "map": lambda row: {
            "followers": row.get("followers", 0),
            "following": row.get("following", 0),
            "posts_count": row.get("videos", 0),
            "bio": "",
        },
    },
    {
        "url": "https://socialblade.com/facebook/user/DanielsDonutsAustralia",
        "platform": "facebook",
        "handle": "DanielsDonutsAustralia",
        "map": lambda row: {
            "followers": row.get("likes", 0),   # page likes = followers
            "following": 0,
            "posts_count": 0,
            "bio": "",
        },
    },
]


def fetch_history(url: str) -> list:
    """Fetch Social Blade page and extract embedded tRPC history query."""
    logger.info("Fetching %s", url)
    resp = cffi_requests.get(url, impersonate="chrome", timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag:
        raise ValueError("No __NEXT_DATA__ found on page")

    data = json.loads(tag.string)
    queries = data["props"]["pageProps"]["trpcState"]["json"]["queries"]

    for q in queries:
        key = str(q.get("queryKey", ""))
        rows = q.get("state", {}).get("data")
        if "history" in key and isinstance(rows, list) and rows:
            logger.info("Found %d history rows", len(rows))
            return rows

    raise ValueError("No history query found in page data")


def backfill(db, profile: dict) -> int:
    platform = profile["platform"]
    handle = profile["handle"]
    rows = fetch_history(profile["url"])

    inserted = 0
    for row in rows:
        raw_date = row.get("date", "")
        if not raw_date:
            continue

        scraped_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))

        # Skip if we already have a snapshot for this platform+date
        existing = (
            db.query(SocialSnapshot)
            .filter(
                SocialSnapshot.platform == platform,
                SocialSnapshot.scraped_at >= scraped_at.replace(hour=0, minute=0, second=0),
                SocialSnapshot.scraped_at < scraped_at.replace(hour=23, minute=59, second=59),
            )
            .first()
        )
        if existing:
            logger.debug("Skipping %s %s — already exists", platform, raw_date[:10])
            continue

        fields = profile["map"](row)
        snap = SocialSnapshot(
            platform=platform,
            handle=handle,
            scraped_at=scraped_at,
            **fields,
        )
        db.add(snap)
        inserted += 1

    db.commit()
    logger.info("%s: inserted %d snapshots", platform, inserted)
    return inserted


def main():
    init_db()
    db = SessionLocal()
    total = 0
    errors = []

    for profile in PROFILES:
        try:
            total += backfill(db, profile)
        except Exception as e:
            logger.error("Failed %s: %s", profile["platform"], e)
            errors.append(profile["platform"])

    db.close()
    print(f"\nDone — {total} snapshots inserted across {len(PROFILES) - len(errors)} platforms.")
    if errors:
        print(f"Failed platforms: {', '.join(errors)}")


if __name__ == "__main__":
    main()
