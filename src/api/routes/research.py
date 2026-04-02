from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import ResearchItem

router = APIRouter(prefix="/research", tags=["research"])


def _item_dict(item: ResearchItem) -> dict:
    return {
        "id": item.id,
        "source": item.source,
        "competitor": item.competitor,
        "content": item.content,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


@router.get("/items")
def get_research_items(
    competitor: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return research items, optionally filtered by competitor."""
    q = db.query(ResearchItem).order_by(ResearchItem.created_at.desc())
    if competitor:
        q = q.filter(ResearchItem.competitor == competitor)
    return [_item_dict(item) for item in q.limit(limit).all()]


@router.get("/competitors")
def get_competitors(db: Session = Depends(get_db)):
    """Return distinct competitor names for filter dropdown."""
    rows = db.query(ResearchItem.competitor).distinct().all()
    return sorted([r[0] for r in rows if r[0]])
