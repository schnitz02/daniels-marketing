from tests.conftest import *  # noqa
from src.db.models import SocialSnapshot, SocialPostCache
from datetime import datetime, timezone


def _snap(db, platform, followers=1000, following=50, posts=10):
    s = SocialSnapshot(
        platform=platform,
        handle=f"{platform}_handle",
        followers=followers,
        following=following,
        posts_count=posts,
        bio=f"{platform} bio",
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _post(db, platform, post_id, likes=100, comments=5):
    p = SocialPostCache(
        platform=platform,
        post_id=post_id,
        likes=likes,
        comments=comments,
        caption="Test caption",
        thumbnail_url="",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_get_latest_returns_most_recent_per_platform(client, db):
    _snap(db, "instagram", followers=500)
    _snap(db, "instagram", followers=1200)  # most recent
    _snap(db, "tiktok", followers=300)
    response = client.get("/api/social-stats/latest")
    assert response.status_code == 200
    data = response.json()
    ig = next(x for x in data if x["platform"] == "instagram")
    assert ig["followers"] == 1200


def test_get_history_returns_snapshots_for_platform(client, db):
    _snap(db, "instagram", followers=800)
    _snap(db, "instagram", followers=900)
    _snap(db, "tiktok", followers=200)
    response = client.get("/api/social-stats/history/instagram")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(x["platform"] == "instagram" for x in data)


def test_get_posts_returns_posts_for_platform(client, db):
    _post(db, "instagram", "post_1", likes=50)
    _post(db, "instagram", "post_2", likes=80)
    _post(db, "tiktok", "post_3", likes=200)
    response = client.get("/api/social-stats/posts/instagram")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(x["platform"] == "instagram" for x in data)


def test_get_latest_empty_returns_empty_list(client, db):
    response = client.get("/api/social-stats/latest")
    assert response.status_code == 200
    assert response.json() == []
