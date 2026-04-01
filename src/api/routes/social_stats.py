import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.db.database import get_db
from src.db.models import SocialSnapshot, SocialPostCache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/social-stats", tags=["social-stats"])

VALID_PLATFORMS = {"instagram", "tiktok", "facebook"}
HISTORY_LIMIT = 90  # ~3 months of daily snapshots


def _snap_dict(s: SocialSnapshot) -> dict:
    return {
        "id": s.id,
        "platform": s.platform,
        "handle": s.handle,
        "followers": s.followers,
        "following": s.following,
        "posts_count": s.posts_count,
        "bio": s.bio,
        "scraped_at": s.scraped_at.isoformat() if s.scraped_at else None,
    }


def _post_dict(p: SocialPostCache) -> dict:
    return {
        "id": p.id,
        "platform": p.platform,
        "post_id": p.post_id,
        "likes": p.likes,
        "comments": p.comments,
        "caption": p.caption,
        "thumbnail_url": p.thumbnail_url,
        "posted_at": p.posted_at.isoformat() if p.posted_at else None,
        "scraped_at": p.scraped_at.isoformat() if p.scraped_at else None,
    }


@router.get("/latest")
def get_latest(db: Session = Depends(get_db)):
    """Return the most recent snapshot for each platform."""
    results = []
    for platform in VALID_PLATFORMS:
        snap = (
            db.query(SocialSnapshot)
            .filter_by(platform=platform)
            .order_by(desc(SocialSnapshot.scraped_at))
            .first()
        )
        if snap:
            results.append(_snap_dict(snap))
    return results


@router.get("/history/{platform}")
def get_history(platform: str, db: Session = Depends(get_db)):
    """Return snapshots for a platform ordered oldest-first (for charts). Max 90 entries."""
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform. Must be one of: {sorted(VALID_PLATFORMS)}")
    snaps = (
        db.query(SocialSnapshot)
        .filter_by(platform=platform)
        .order_by(SocialSnapshot.scraped_at)
        .limit(HISTORY_LIMIT)
        .all()
    )
    return [_snap_dict(s) for s in snaps]


@router.get("/posts/{platform}")
def get_posts(
    platform: str,
    limit: int = Query(default=9, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Return most recent cached posts for a platform (max 50)."""
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform. Must be one of: {sorted(VALID_PLATFORMS)}")
    posts = (
        db.query(SocialPostCache)
        .filter_by(platform=platform)
        .order_by(desc(SocialPostCache.scraped_at))
        .limit(limit)
        .all()
    )
    return [_post_dict(p) for p in posts]
