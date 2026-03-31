# Social Stats Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a Social Stats page that scrapes Daniel's Donuts' public Instagram, Facebook, and TikTok profiles, stores historical snapshots, and displays live stats + trend charts + recent posts in the dashboard.

**Architecture:** A new `SocialStatsAgent` scrapes all three platforms using `instaloader` (Instagram) and `httpx`+`bs4` (TikTok, Facebook), stores timestamped snapshots and post caches in two new DB tables, and exposes three REST endpoints consumed by a new React page with tabs, stat cards, Recharts line charts, and a post grid.

**Tech Stack:** Python `instaloader`, `httpx`, `beautifulsoup4` (backend scraping) · SQLAlchemy (new models) · FastAPI (new routes) · React 18 + Recharts + Tailwind CSS (frontend)

**Python binary:** `C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe`
**Run tests with:** `C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/ -v`
**Project root:** `C:\Users\natan.akoka1\Desktop\Claude Code\Daniels Marketing`

---

## Task 1: DB Models — `social_snapshots` + `social_posts_cache`

**Files:**
- Modify: `src/db/models.py`
- Test: `tests/test_social_models.py`

**Step 1: Write the failing test**

Create `tests/test_social_models.py`:

```python
from tests.conftest import *  # noqa — uses the db fixture
from src.db.models import SocialSnapshot, SocialPostCache
from datetime import datetime, timezone


def test_social_snapshot_created(db):
    snap = SocialSnapshot(
        platform="instagram",
        handle="danielsdonutsaustralia",
        followers=12000,
        following=300,
        posts_count=850,
        bio="Australia's best donuts 🍩",
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)
    assert snap.id is not None
    assert snap.scraped_at is not None


def test_social_post_cache_created(db):
    post = SocialPostCache(
        platform="instagram",
        post_id="abc123",
        likes=450,
        comments=22,
        caption="Fresh glazed just dropped!",
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    assert post.id is not None
    assert post.scraped_at is not None
```

**Step 2: Run test to verify it fails**

```
cd "C:\Users\natan.akoka1\Desktop\Claude Code\Daniels Marketing"
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_social_models.py -v
```
Expected: FAIL — `ImportError: cannot import name 'SocialSnapshot'`

**Step 3: Add models to `src/db/models.py`**

Add after the existing model classes (before the end of the file):

```python
class SocialSnapshot(Base):
    __tablename__ = "social_snapshots"
    id          = Column(Integer, primary_key=True, index=True)
    platform    = Column(String, nullable=False)       # instagram / facebook / tiktok
    handle      = Column(String, nullable=False)
    followers   = Column(Integer, default=0)
    following   = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    bio         = Column(String, default="")
    scraped_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SocialPostCache(Base):
    __tablename__ = "social_posts_cache"
    id            = Column(Integer, primary_key=True, index=True)
    platform      = Column(String, nullable=False)
    post_id       = Column(String, nullable=False, unique=True)
    likes         = Column(Integer, default=0)
    comments      = Column(Integer, default=0)
    thumbnail_url = Column(String, default="")
    caption       = Column(String, default="")
    posted_at     = Column(DateTime, nullable=True)
    scraped_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

Make sure `datetime` and `timezone` are imported at the top of `models.py` (check if already present).

**Step 4: Run test to verify it passes**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_social_models.py -v
```
Expected: 2 PASSED

**Step 5: Run full suite to check no regressions**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/ -q
```
Expected: 45 passed

**Step 6: Commit**

```bash
git add src/db/models.py tests/test_social_models.py
git commit -m "feat: add SocialSnapshot and SocialPostCache models"
```

---

## Task 2: Instagram Scraper

**Files:**
- Create: `src/core/scrapers/instagram.py`
- Test: `tests/test_scraper_instagram.py`

**Step 1: Write the failing test**

Create `tests/test_scraper_instagram.py`:

```python
import pytest
from unittest.mock import MagicMock, patch


def _make_mock_profile(followers=10000, followees=250, mediacount=800, biography="Donuts 🍩"):
    profile = MagicMock()
    profile.followers = followers
    profile.followees = followees
    profile.mediacount = mediacount
    profile.biography = biography
    return profile


def _make_mock_post(likes=200, comments=15, shortcode="abc123", caption="Fresh glazed"):
    post = MagicMock()
    post.likes = likes
    post.comments = comments
    post.shortcode = shortcode
    post.caption = caption
    post.date_utc = None
    post.url = "https://example.com/img.jpg"
    return post


def test_scrape_instagram_returns_snapshot_shape():
    from src.core.scrapers.instagram import scrape_instagram
    mock_profile = _make_mock_profile()
    mock_post = _make_mock_post()
    mock_profile.get_posts.return_value = [mock_post]

    with patch("src.core.scrapers.instagram.instaloader.Instaloader"), \
         patch("src.core.scrapers.instagram.instaloader.Profile.from_username",
               return_value=mock_profile):
        result = scrape_instagram("danielsdonutsaustralia")

    assert result["followers"] == 10000
    assert result["following"] == 250
    assert result["posts_count"] == 800
    assert result["bio"] == "Donuts 🍩"
    assert len(result["recent_posts"]) == 1
    assert result["recent_posts"][0]["post_id"] == "abc123"
    assert result["recent_posts"][0]["likes"] == 200


def test_scrape_instagram_returns_none_on_error():
    from src.core.scrapers.instagram import scrape_instagram
    with patch("src.core.scrapers.instagram.instaloader.Profile.from_username",
               side_effect=Exception("blocked")):
        result = scrape_instagram("danielsdonutsaustralia")
    assert result is None
```

**Step 2: Run test to verify it fails**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_scraper_instagram.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'src.core.scrapers'`

**Step 3: Create the scraper**

Create directory `src/core/scrapers/` and add `__init__.py` (empty).

Create `src/core/scrapers/instagram.py`:

```python
import logging
import instaloader

logger = logging.getLogger(__name__)
MAX_POSTS = 9


def scrape_instagram(handle: str) -> dict | None:
    """
    Scrape a public Instagram profile.
    Returns a dict with profile stats and recent posts, or None if scraping fails.
    """
    try:
        loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            compress_json=False,
            save_metadata=False,
            quiet=True,
        )
        profile = instaloader.Profile.from_username(loader.context, handle)

        recent_posts = []
        for post in profile.get_posts():
            if len(recent_posts) >= MAX_POSTS:
                break
            recent_posts.append({
                "post_id": post.shortcode,
                "likes": post.likes,
                "comments": post.comments,
                "caption": (post.caption or "")[:200],
                "thumbnail_url": post.url,
                "posted_at": post.date_utc,
            })

        return {
            "platform": "instagram",
            "handle": handle,
            "followers": profile.followers,
            "following": profile.followees,
            "posts_count": profile.mediacount,
            "bio": profile.biography or "",
            "recent_posts": recent_posts,
        }
    except Exception as e:
        logger.warning("Instagram scrape failed for %s: %s", handle, e)
        return None
```

**Step 4: Run test to verify it passes**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_scraper_instagram.py -v
```
Expected: 2 PASSED

**Step 5: Commit**

```bash
git add src/core/scrapers/ tests/test_scraper_instagram.py
git commit -m "feat: add Instagram scraper using instaloader"
```

---

## Task 3: TikTok Scraper

**Files:**
- Create: `src/core/scrapers/tiktok.py`
- Test: `tests/test_scraper_tiktok.py`

**Step 1: Write the failing test**

Create `tests/test_scraper_tiktok.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
import json


TIKTOK_HTML = """
<html><body>
<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">
{
  "__DEFAULT_SCOPE__": {
    "webapp.user-detail": {
      "userInfo": {
        "user": {"uniqueId": "danielsdonutsaus", "signature": "Official TikTok"},
        "stats": {"followerCount": 5000, "followingCount": 120, "heartCount": 45000, "videoCount": 95}
      }
    }
  }
}
</script>
</body></html>
"""


def _mock_response(html):
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def test_scrape_tiktok_returns_snapshot_shape():
    from src.core.scrapers.tiktok import scrape_tiktok
    with patch("httpx.get", return_value=_mock_response(TIKTOK_HTML)):
        result = scrape_tiktok("danielsdonutsaus")
    assert result["followers"] == 5000
    assert result["following"] == 120
    assert result["posts_count"] == 95
    assert result["platform"] == "tiktok"


def test_scrape_tiktok_returns_none_on_error():
    from src.core.scrapers.tiktok import scrape_tiktok
    with patch("httpx.get", side_effect=Exception("network error")):
        result = scrape_tiktok("danielsdonutsaus")
    assert result is None
```

**Step 2: Run test to verify it fails**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_scraper_tiktok.py -v
```
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Create `src/core/scrapers/tiktok.py`**

```python
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
```

**Step 4: Run test to verify it passes**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_scraper_tiktok.py -v
```
Expected: 2 PASSED

**Step 5: Commit**

```bash
git add src/core/scrapers/tiktok.py tests/test_scraper_tiktok.py
git commit -m "feat: add TikTok scraper using httpx"
```

---

## Task 4: Facebook Scraper

**Files:**
- Create: `src/core/scrapers/facebook.py`
- Test: `tests/test_scraper_facebook.py`

**Step 1: Write the failing test**

Create `tests/test_scraper_facebook.py`:

```python
from unittest.mock import patch, MagicMock

FB_HTML = """
<html>
<head>
<meta property="og:description" content="Daniel's Donuts Australia · 8,200 likes · 8,500 followers" />
<meta property="og:title" content="Daniel's Donuts Australia" />
</head>
<body></body>
</html>
"""

FB_HTML_NO_META = "<html><body><p>Nothing here</p></body></html>"


def _mock_response(html):
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def test_scrape_facebook_parses_followers():
    from src.core.scrapers.facebook import scrape_facebook
    with patch("httpx.get", return_value=_mock_response(FB_HTML)):
        result = scrape_facebook("DanielsDonutsAustralia")
    assert result["platform"] == "facebook"
    assert result["followers"] == 8500


def test_scrape_facebook_returns_zeros_when_no_meta():
    from src.core.scrapers.facebook import scrape_facebook
    with patch("httpx.get", return_value=_mock_response(FB_HTML_NO_META)):
        result = scrape_facebook("DanielsDonutsAustralia")
    assert result["followers"] == 0


def test_scrape_facebook_returns_none_on_error():
    from src.core.scrapers.facebook import scrape_facebook
    with patch("httpx.get", side_effect=Exception("blocked")):
        result = scrape_facebook("DanielsDonutsAustralia")
    assert result is None
```

**Step 2: Run test to verify it fails**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_scraper_facebook.py -v
```
Expected: FAIL

**Step 3: Create `src/core/scrapers/facebook.py`**

```python
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
    """Parse '8,500' or '8.5K' style numbers into int."""
    if not text:
        return 0
    text = text.replace(",", "").replace(".", "").strip()
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0


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
        likes = 0

        # Try og:description meta tag — often contains "X likes · Y followers"
        desc_meta = soup.find("meta", property="og:description")
        if desc_meta:
            desc = desc_meta.get("content", "")
            followers_match = re.search(r"([\d,]+)\s+follower", desc, re.IGNORECASE)
            likes_match = re.search(r"([\d,]+)\s+like", desc, re.IGNORECASE)
            if followers_match:
                followers = _parse_count(followers_match.group(1))
            if likes_match:
                likes = _parse_count(likes_match.group(1))

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
```

**Step 4: Run test to verify it passes**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_scraper_facebook.py -v
```
Expected: 3 PASSED

**Step 5: Commit**

```bash
git add src/core/scrapers/facebook.py tests/test_scraper_facebook.py
git commit -m "feat: add Facebook scraper using httpx + BeautifulSoup"
```

---

## Task 5: SocialStatsAgent

**Files:**
- Create: `src/agents/social_stats.py`
- Test: `tests/test_agent_social_stats.py`

**Step 1: Write the failing test**

Create `tests/test_agent_social_stats.py`:

```python
import pytest
from unittest.mock import patch, AsyncMock
from tests.conftest import *  # noqa
from src.db.models import SocialSnapshot, SocialPostCache

MOCK_IG = {
    "platform": "instagram", "handle": "danielsdonutsaustralia",
    "followers": 12000, "following": 300, "posts_count": 850, "bio": "Donuts",
    "recent_posts": [
        {"post_id": "abc1", "likes": 200, "comments": 10,
         "caption": "Fresh!", "thumbnail_url": "", "posted_at": None}
    ],
}
MOCK_TT = {
    "platform": "tiktok", "handle": "danielsdonutsaus",
    "followers": 5000, "following": 120, "posts_count": 95, "bio": "TT bio",
    "recent_posts": [],
}
MOCK_FB = {
    "platform": "facebook", "handle": "DanielsDonutsAustralia",
    "followers": 8500, "following": 0, "posts_count": 0, "bio": "FB bio",
    "recent_posts": [],
}


@pytest.mark.asyncio
async def test_social_stats_agent_stores_snapshots(db):
    from src.agents.social_stats import SocialStatsAgent
    with patch("src.agents.social_stats.scrape_instagram", return_value=MOCK_IG), \
         patch("src.agents.social_stats.scrape_tiktok", return_value=MOCK_TT), \
         patch("src.agents.social_stats.scrape_facebook", return_value=MOCK_FB):
        agent = SocialStatsAgent(db=db)
        result = await agent.run()

    assert result["snapshots_saved"] == 3
    snaps = db.query(SocialSnapshot).all()
    assert len(snaps) == 3
    platforms = {s.platform for s in snaps}
    assert platforms == {"instagram", "tiktok", "facebook"}


@pytest.mark.asyncio
async def test_social_stats_agent_stores_posts(db):
    from src.agents.social_stats import SocialStatsAgent
    with patch("src.agents.social_stats.scrape_instagram", return_value=MOCK_IG), \
         patch("src.agents.social_stats.scrape_tiktok", return_value=MOCK_TT), \
         patch("src.agents.social_stats.scrape_facebook", return_value=MOCK_FB):
        agent = SocialStatsAgent(db=db)
        await agent.run()

    posts = db.query(SocialPostCache).all()
    assert len(posts) == 1
    assert posts[0].post_id == "abc1"
    assert posts[0].likes == 200


@pytest.mark.asyncio
async def test_social_stats_agent_handles_failed_scrape(db):
    from src.agents.social_stats import SocialStatsAgent
    with patch("src.agents.social_stats.scrape_instagram", return_value=None), \
         patch("src.agents.social_stats.scrape_tiktok", return_value=MOCK_TT), \
         patch("src.agents.social_stats.scrape_facebook", return_value=None):
        agent = SocialStatsAgent(db=db)
        result = await agent.run()

    assert result["snapshots_saved"] == 1
```

**Step 2: Run test to verify it fails**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_agent_social_stats.py -v
```
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Create `src/agents/social_stats.py`**

```python
import logging
from sqlalchemy.orm import Session
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.core.scrapers.instagram import scrape_instagram
from src.core.scrapers.tiktok import scrape_tiktok
from src.core.scrapers.facebook import scrape_facebook
from src.db.models import SocialSnapshot, SocialPostCache
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

PROFILES = [
    ("instagram", "danielsdonutsaustralia", scrape_instagram),
    ("tiktok",    "danielsdonutsaus",       scrape_tiktok),
    ("facebook",  "DanielsDonutsAustralia", scrape_facebook),
]


@register_agent("social_stats")
class SocialStatsAgent(BaseAgent):
    name = "social_stats"

    async def run(self):
        snapshots_saved = 0
        posts_cached = 0

        for platform, handle, scrape_fn in PROFILES:
            data = scrape_fn(handle)
            if data is None:
                logger.warning("Skipping %s — scrape returned None", platform)
                continue

            snap = SocialSnapshot(
                platform=platform,
                handle=handle,
                followers=data.get("followers", 0),
                following=data.get("following", 0),
                posts_count=data.get("posts_count", 0),
                bio=data.get("bio", ""),
            )
            self.db.add(snap)
            snapshots_saved += 1

            for post in data.get("recent_posts", []):
                existing = self.db.query(SocialPostCache).filter_by(
                    post_id=post["post_id"]
                ).first()
                if existing:
                    existing.likes = post["likes"]
                    existing.comments = post["comments"]
                    existing.scraped_at = datetime.now(timezone.utc)
                else:
                    self.db.add(SocialPostCache(
                        platform=platform,
                        post_id=post["post_id"],
                        likes=post.get("likes", 0),
                        comments=post.get("comments", 0),
                        caption=post.get("caption", ""),
                        thumbnail_url=post.get("thumbnail_url", ""),
                        posted_at=post.get("posted_at"),
                    ))
                    posts_cached += 1

        self.db.commit()
        return {"snapshots_saved": snapshots_saved, "posts_cached": posts_cached}
```

**Step 4: Run test to verify it passes**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_agent_social_stats.py -v
```
Expected: 3 PASSED

**Step 5: Register agent + add to scheduler**

In `src/api/routes/agents.py`, add `"social_stats"` to `AGENT_NAMES`:
```python
AGENT_NAMES = ["orchestrator", "research", "strategy", "content",
               "post_production", "social", "social_stats", "website", "analytics"]
```

Also add the import inside `trigger_agent()`:
```python
import src.agents.social_stats  # noqa
```

In `src/core/scheduler.py`, find where jobs are added and add a daily 9:30am job:
```python
scheduler.add_job("social_stats", hour=9, minute=30)
```
(Use whatever pattern the other jobs follow in that file.)

**Step 6: Run full test suite**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/ -q
```
Expected: 51+ passed

**Step 7: Commit**

```bash
git add src/agents/social_stats.py src/api/routes/agents.py src/core/scheduler.py tests/test_agent_social_stats.py
git commit -m "feat: add SocialStatsAgent with Instagram/TikTok/Facebook scraping"
```

---

## Task 6: API Routes for Social Stats

**Files:**
- Create: `src/api/routes/social.py`
- Modify: `src/main.py`
- Test: `tests/test_api_social.py`

**Step 1: Write the failing test**

Create `tests/test_api_social.py`:

```python
from tests.conftest import *  # noqa
from src.db.models import SocialSnapshot, SocialPostCache
from datetime import datetime, timezone


def _seed_snapshot(db, platform="instagram", followers=10000):
    snap = SocialSnapshot(
        platform=platform, handle="testhandle",
        followers=followers, following=200, posts_count=500, bio="Test bio"
    )
    db.add(snap)
    db.commit()
    return snap


def _seed_post(db, platform="instagram", post_id="p1", likes=100):
    post = SocialPostCache(
        platform=platform, post_id=post_id,
        likes=likes, comments=5, caption="Test post"
    )
    db.add(post)
    db.commit()
    return post


def test_get_stats_returns_snapshots(client, db):
    _seed_snapshot(db, "instagram", followers=12000)
    _seed_snapshot(db, "instagram", followers=12500)
    resp = client.get("/api/social/stats/instagram")
    assert resp.status_code == 200
    data = resp.json()
    assert data["latest"]["followers"] == 12500
    assert len(data["history"]) == 2


def test_get_stats_empty_platform(client):
    resp = client.get("/api/social/stats/tiktok")
    assert resp.status_code == 200
    assert resp.json()["latest"] is None
    assert resp.json()["history"] == []


def test_get_posts_returns_cached(client, db):
    _seed_post(db, "instagram", "p1", 100)
    _seed_post(db, "instagram", "p2", 200)
    resp = client.get("/api/social/posts/instagram")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_invalid_platform_returns_400(client):
    resp = client.get("/api/social/stats/twitter")
    assert resp.status_code == 400
```

**Step 2: Run test to verify it fails**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_api_social.py -v
```
Expected: FAIL — 404 (routes don't exist yet)

**Step 3: Create `src/api/routes/social.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import SocialSnapshot, SocialPostCache

router = APIRouter()

VALID_PLATFORMS = {"instagram", "facebook", "tiktok"}


def _validate_platform(platform: str):
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}. Must be one of {VALID_PLATFORMS}")


@router.get("/stats/{platform}")
def get_social_stats(platform: str, db: Session = Depends(get_db)):
    _validate_platform(platform)
    snapshots = (
        db.query(SocialSnapshot)
        .filter_by(platform=platform)
        .order_by(SocialSnapshot.scraped_at.asc())
        .all()
    )
    latest = snapshots[-1] if snapshots else None
    return {
        "platform": platform,
        "latest": {
            "followers": latest.followers,
            "following": latest.following,
            "posts_count": latest.posts_count,
            "bio": latest.bio,
            "scraped_at": latest.scraped_at.isoformat(),
        } if latest else None,
        "history": [
            {
                "followers": s.followers,
                "following": s.following,
                "scraped_at": s.scraped_at.isoformat(),
            }
            for s in snapshots
        ],
    }


@router.get("/posts/{platform}")
def get_social_posts(platform: str, db: Session = Depends(get_db)):
    _validate_platform(platform)
    posts = (
        db.query(SocialPostCache)
        .filter_by(platform=platform)
        .order_by(SocialPostCache.scraped_at.desc())
        .limit(9)
        .all()
    )
    return [
        {
            "post_id": p.post_id,
            "likes": p.likes,
            "comments": p.comments,
            "caption": p.caption,
            "thumbnail_url": p.thumbnail_url,
            "posted_at": p.posted_at.isoformat() if p.posted_at else None,
            "engagement_rate": round((p.likes + p.comments) / max(p.likes, 1) * 100, 1),
        }
        for p in posts
    ]
```

**Step 4: Register the router in `src/main.py`**

Inside `create_app()`, find where other routers are included and add:
```python
from src.api.routes import approvals, agents, dashboard, social  # add social
app.include_router(social.router, prefix="/api/social")
```

**Step 5: Run test to verify it passes**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/test_api_social.py -v
```
Expected: 4 PASSED

**Step 6: Run full test suite**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/ -q
```
Expected: 55+ passed

**Step 7: Commit**

```bash
git add src/api/routes/social.py src/main.py tests/test_api_social.py
git commit -m "feat: add social stats API routes"
```

---

## Task 7: Frontend — SocialStats Page

**Files:**
- Create: `dashboard/src/pages/SocialStats.jsx`
- Modify: `dashboard/src/App.jsx`

No automated tests for frontend — visually verify in browser.

**Step 1: Create `dashboard/src/pages/SocialStats.jsx`**

```jsx
import { useEffect, useState, useCallback } from "react"
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from "recharts"
import api from "../api"

const PLATFORMS = ["instagram", "facebook", "tiktok"]

const PLATFORM_META = {
  instagram: { label: "Instagram", color: "#E1306C", icon: "📸" },
  facebook:  { label: "Facebook",  color: "#1877F2", icon: "👍" },
  tiktok:    { label: "TikTok",    color: "#69C9D0", icon: "🎵" },
}

function StatCard({ label, value, color }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex flex-col gap-1">
      <span className="text-gray-400 text-xs">{label}</span>
      <span className={`text-3xl font-bold ${color}`}>
        {typeof value === "number" ? value.toLocaleString() : value ?? "—"}
      </span>
    </div>
  )
}

function FollowerChart({ history, color }) {
  if (!history || history.length < 2) {
    return (
      <div className="h-40 flex items-center justify-center text-gray-600 text-sm">
        Not enough data for trend chart yet. Check back after more scrapes.
      </div>
    )
  }
  const data = history.map(h => ({
    date: new Date(h.scraped_at).toLocaleDateString("en-AU", { month: "short", day: "numeric" }),
    followers: h.followers,
  }))
  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="date" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
        <YAxis tick={{ fill: "#9CA3AF", fontSize: 11 }} width={60} />
        <Tooltip
          contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
          labelStyle={{ color: "#F9FAFB" }}
          itemStyle={{ color }}
        />
        <Line type="monotone" dataKey="followers" stroke={color} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}

function PostGrid({ posts }) {
  if (!posts || posts.length === 0) {
    return <p className="text-gray-600 text-sm">No recent posts cached yet.</p>
  }
  return (
    <div className="grid grid-cols-3 gap-3">
      {posts.map(post => (
        <div key={post.post_id} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          {post.thumbnail_url && (
            <img
              src={post.thumbnail_url}
              alt="post"
              className="w-full h-28 object-cover rounded-lg mb-3"
              onError={e => { e.target.style.display = "none" }}
            />
          )}
          <p className="text-gray-400 text-xs line-clamp-2 mb-2">{post.caption || "No caption"}</p>
          <div className="flex gap-3 text-xs text-gray-500">
            <span>❤️ {post.likes?.toLocaleString()}</span>
            <span>💬 {post.comments?.toLocaleString()}</span>
            <span className="text-green-400">{post.engagement_rate}%</span>
          </div>
        </div>
      ))}
    </div>
  )
}

function PlatformTab({ platform }) {
  const meta = PLATFORM_META[platform]
  const [stats, setStats] = useState(null)
  const [posts, setPosts] = useState([])
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)

  const load = useCallback(() => {
    return Promise.all([
      api.get(`/social/stats/${platform}`).then(r => setStats(r.data)),
      api.get(`/social/posts/${platform}`).then(r => setPosts(r.data)),
    ]).catch(() => setError("Could not load social stats. Make sure the backend is running."))
  }, [platform])

  useEffect(() => { load() }, [load])

  const refresh = async () => {
    setRefreshing(true)
    try {
      await api.post(`/agents/trigger/social_stats`)
      await load()
    } catch {
      setError("Refresh failed — the scraper may have been blocked. Showing cached data.")
    }
    setRefreshing(false)
  }

  const latest = stats?.latest
  const lastScraped = latest
    ? new Date(latest.scraped_at).toLocaleString("en-AU")
    : null

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold">{meta.icon} {meta.label}</h2>
          {lastScraped && (
            <p className="text-gray-500 text-xs mt-0.5">Last scraped: {lastScraped}</p>
          )}
        </div>
        <button
          onClick={refresh}
          disabled={refreshing}
          className="bg-gray-800 border border-gray-700 text-white text-xs px-4 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors"
        >
          {refreshing ? "Scraping…" : "↻ Refresh"}
        </button>
      </div>

      {error && (
        <div className="text-yellow-400 bg-yellow-900/20 border border-yellow-800 rounded-xl p-3 mb-4 text-xs">
          {error}
        </div>
      )}

      {!latest ? (
        <div className="text-center py-16 text-gray-600">
          <p className="text-4xl mb-3">📊</p>
          <p className="font-medium mb-1">No data yet</p>
          <p className="text-xs">Click Refresh to scrape {meta.label} now.</p>
        </div>
      ) : (
        <>
          {/* Surface stats */}
          <section className="mb-8">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Surface Stats</h3>
            <div className="grid grid-cols-4 gap-3">
              <StatCard label="Followers"  value={latest.followers}   color={`text-[${meta.color}]`} />
              <StatCard label="Following"  value={latest.following}   color="text-gray-200" />
              <StatCard label="Posts"      value={latest.posts_count} color="text-gray-200" />
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <span className="text-gray-400 text-xs block mb-1">Bio</span>
                <p className="text-gray-300 text-sm leading-relaxed line-clamp-3">
                  {latest.bio || "No bio available"}
                </p>
              </div>
            </div>
          </section>

          {/* Follower trend */}
          <section className="mb-8">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Follower Trend</h3>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <FollowerChart history={stats?.history} color={meta.color} />
            </div>
          </section>

          {/* Recent posts */}
          <section>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Recent Posts</h3>
            <PostGrid posts={posts} />
          </section>
        </>
      )}
    </div>
  )
}

export default function SocialStats() {
  const [activeTab, setActiveTab] = useState("instagram")

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Social Stats</h1>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-900 border border-gray-800 rounded-xl p-1 w-fit">
        {PLATFORMS.map(p => (
          <button
            key={p}
            onClick={() => setActiveTab(p)}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === p
                ? "bg-gray-700 text-white"
                : "text-gray-500 hover:text-gray-300"
            }`}
          >
            {PLATFORM_META[p].icon} {PLATFORM_META[p].label}
          </button>
        ))}
      </div>

      <PlatformTab key={activeTab} platform={activeTab} />
    </div>
  )
}
```

**Step 2: Add the route to `dashboard/src/App.jsx`**

Find the import block and add:
```jsx
import SocialStats from "./pages/SocialStats"
```

Find where routes are defined and add:
```jsx
<Route path="/social-stats" element={<SocialStats />} />
```

Find the sidebar navigation links and add:
```jsx
<NavLink to="/social-stats">📊 Social Stats</NavLink>
```
(Match the existing NavLink style in the sidebar.)

**Step 3: Verify in browser**

1. Restart backend (Ctrl+C + double-click `start_backend.bat`)
2. Vite should hot-reload automatically
3. Navigate to `http://localhost:5173` → click "Social Stats" in sidebar
4. You should see 3 tabs with "No data yet" states and a Refresh button
5. Click Refresh on Instagram tab — it triggers the social_stats agent
6. After ~10 seconds, stats should appear

**Step 4: Commit**

```bash
git add dashboard/src/pages/SocialStats.jsx dashboard/src/App.jsx
git commit -m "feat: add Social Stats dashboard page with tabs, trend charts, and post grid"
```

---

## Task 8: Final check

**Step 1: Run complete test suite**

```
C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests/ -v
```
Expected: 55+ passed, 0 failed

**Step 2: Also commit the JSON fix from earlier (if not yet committed)**

Check:
```bash
git status
```
If `src/agents/base.py`, `src/agents/strategy.py`, `src/agents/content.py`, `src/agents/research.py` show as modified, commit them:
```bash
git add src/agents/base.py src/agents/strategy.py src/agents/content.py src/agents/research.py
git commit -m "fix: strip markdown code fences from Claude JSON responses in all agents"
```

**Step 3: Push to remote**

```bash
git push origin master
```
