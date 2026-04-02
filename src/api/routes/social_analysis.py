import json
import logging
import anthropic
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import SocialSnapshot, SocialAnalysis

logger = logging.getLogger(__name__)
router = APIRouter(tags=["social-analysis"])

VALID_PLATFORMS = {"instagram", "tiktok", "facebook"}


def _get_latest_analysis(platform: str, db: Session):
    row = (
        db.query(SocialAnalysis)
        .filter_by(platform=platform)
        .order_by(SocialAnalysis.generated_at.desc())
        .first()
    )
    if not row:
        return None
    try:
        return {**json.loads(row.analysis), "generated_at": row.generated_at.isoformat()}
    except Exception:
        return None


@router.get("/social-stats/analysis/{platform}")
def get_analysis(platform: str, db: Session = Depends(get_db)):
    """Return latest stored analysis for a platform."""
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
    return _get_latest_analysis(platform, db)


@router.post("/social-stats/analysis/{platform}")
def generate_analysis(platform: str, db: Session = Depends(get_db)):
    """Generate a fresh AI analysis for a platform using latest snapshot data."""
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")

    # Gather latest snapshot
    snap = (
        db.query(SocialSnapshot)
        .filter_by(platform=platform)
        .order_by(SocialSnapshot.scraped_at.desc())
        .first()
    )
    if not snap:
        raise HTTPException(status_code=404, detail="No snapshot data available for this platform")

    # Build prompt
    prompt = f"""You are a social media analyst for Daniel's Donuts, an Australian donut brand.

Platform: {platform}
Current stats:
- Followers: {snap.followers:,}
- Following: {snap.following:,}
- Posts: {snap.posts_count:,}
- Bio: {snap.bio or 'N/A'}

Provide a JSON response with exactly these keys:
- "summary": 2-3 sentence plain-English summary of current performance
- "benchmarks": How these numbers compare to typical Australian food/hospitality brand benchmarks
- "recommendations": List of exactly 3 specific, actionable improvements

Return ONLY valid JSON, no markdown."""

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text

    # Validate JSON
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON")

    # Store result
    record = SocialAnalysis(platform=platform, analysis=json.dumps(parsed))
    db.add(record)
    db.commit()
    db.refresh(record)

    return {**parsed, "generated_at": record.generated_at.isoformat()}
