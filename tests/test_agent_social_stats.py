import pytest
from unittest.mock import patch
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
    with patch("src.core.scrapers.instagram.scrape_instagram", return_value=MOCK_IG), \
         patch("src.core.scrapers.tiktok.scrape_tiktok", return_value=MOCK_TT), \
         patch("src.core.scrapers.facebook.scrape_facebook", return_value=MOCK_FB):
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
    with patch("src.core.scrapers.instagram.scrape_instagram", return_value=MOCK_IG), \
         patch("src.core.scrapers.tiktok.scrape_tiktok", return_value=MOCK_TT), \
         patch("src.core.scrapers.facebook.scrape_facebook", return_value=MOCK_FB):
        agent = SocialStatsAgent(db=db)
        await agent.run()

    posts = db.query(SocialPostCache).all()
    assert len(posts) == 1
    assert posts[0].post_id == "abc1"
    assert posts[0].likes == 200


@pytest.mark.asyncio
async def test_social_stats_agent_handles_failed_scrape(db):
    from src.agents.social_stats import SocialStatsAgent
    with patch("src.core.scrapers.instagram.scrape_instagram", return_value=None), \
         patch("src.core.scrapers.tiktok.scrape_tiktok", return_value=MOCK_TT), \
         patch("src.core.scrapers.facebook.scrape_facebook", return_value=None):
        agent = SocialStatsAgent(db=db)
        result = await agent.run()

    assert result["snapshots_saved"] == 1
