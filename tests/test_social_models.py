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
