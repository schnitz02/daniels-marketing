from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Idea, Content, Post, WebsiteChange

router = APIRouter()

@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    total_reach = db.query(Post).with_entities(Post.reach).all()
    reach_sum = sum(r[0] for r in total_reach if r[0]) if total_reach else 0
    return {
        "pending_ideas": db.query(Idea).filter_by(status="pending").count(),
        "pending_content": db.query(Content).filter_by(status="pending").count(),
        "pending_website_changes": db.query(WebsiteChange).filter_by(status="pending").count(),
        "published_posts": db.query(Post).filter_by(status="published").count(),
        "total_reach": reach_sum,
    }

@router.get("/calendar")
def get_calendar(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.scheduled_at.desc()).limit(50).all()
    return [{"id": p.id, "platform": p.platform, "status": p.status, "scheduled_at": str(p.scheduled_at), "published_at": str(p.published_at)} for p in posts]

@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    posts = db.query(Post).filter_by(status="published").all()
    by_platform: dict = {}
    for post in posts:
        if post.platform not in by_platform:
            by_platform[post.platform] = {"reach": 0, "engagement": 0, "count": 0}
        by_platform[post.platform]["reach"] += post.reach or 0
        by_platform[post.platform]["engagement"] += post.engagement or 0
        by_platform[post.platform]["count"] += 1
    return {"by_platform": by_platform, "total_posts": len(posts)}
