from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Idea, Content, WebsiteChange, Approval

router = APIRouter()

class RejectionBody(BaseModel):
    notes: str = ""

# ── Ideas ──────────────────────────────────────────────────────────────────

@router.get("/ideas")
def get_pending_ideas(db: Session = Depends(get_db)):
    ideas = db.query(Idea).filter_by(status="pending").all()
    return [{"id": i.id, "title": i.title, "body": i.body, "evidence": i.evidence, "status": i.status, "created_at": str(i.created_at)} for i in ideas]

@router.post("/ideas/{idea_id}/approve")
def approve_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).get(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.status = "approved"
    db.add(Approval(item_type="idea", item_id=idea_id, decision="approved", decided_at=datetime.now(timezone.utc)))
    db.commit()
    return {"status": "approved", "id": idea_id}

@router.post("/ideas/{idea_id}/reject")
def reject_idea(idea_id: int, body: RejectionBody, db: Session = Depends(get_db)):
    idea = db.query(Idea).get(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.status = "rejected"
    idea.rejection_notes = body.notes
    db.add(Approval(item_type="idea", item_id=idea_id, decision="rejected", notes=body.notes, decided_at=datetime.now(timezone.utc)))
    db.commit()
    return {"status": "rejected", "id": idea_id}

# ── Content ────────────────────────────────────────────────────────────────

@router.get("/content")
def get_pending_content(db: Session = Depends(get_db)):
    items = db.query(Content).filter_by(status="pending").all()
    return [{"id": c.id, "idea_id": c.idea_id, "type": c.type, "file_path": c.file_path, "caption": c.caption, "status": c.status} for c in items]

@router.post("/content/{content_id}/approve")
def approve_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).get(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    content.status = "approved"
    db.add(Approval(item_type="content", item_id=content_id, decision="approved", decided_at=datetime.now(timezone.utc)))
    db.commit()
    return {"status": "approved", "id": content_id}

@router.post("/content/{content_id}/reject")
def reject_content(content_id: int, body: RejectionBody, db: Session = Depends(get_db)):
    content = db.query(Content).get(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    content.status = "rejected"
    content.rejection_notes = body.notes
    db.add(Approval(item_type="content", item_id=content_id, decision="rejected", notes=body.notes, decided_at=datetime.now(timezone.utc)))
    db.commit()
    return {"status": "rejected", "id": content_id}

# ── Website Changes ─────────────────────────────────────────────────────────

@router.get("/website")
def get_pending_website_changes(db: Session = Depends(get_db)):
    changes = db.query(WebsiteChange).filter_by(status="pending").all()
    return [{"id": c.id, "change_type": c.change_type, "description": c.description, "payload": c.payload, "status": c.status} for c in changes]

@router.post("/website/{change_id}/approve")
def approve_website_change(change_id: int, db: Session = Depends(get_db)):
    change = db.query(WebsiteChange).get(change_id)
    if not change:
        raise HTTPException(status_code=404, detail="Website change not found")
    change.status = "approved"
    db.add(Approval(item_type="website_change", item_id=change_id, decision="approved", decided_at=datetime.now(timezone.utc)))
    db.commit()
    return {"status": "approved", "id": change_id}

@router.post("/website/{change_id}/reject")
def reject_website_change(change_id: int, body: RejectionBody, db: Session = Depends(get_db)):
    change = db.query(WebsiteChange).get(change_id)
    if not change:
        raise HTTPException(status_code=404, detail="Website change not found")
    change.status = "rejected"
    db.add(Approval(item_type="website_change", item_id=change_id, decision="rejected", notes=body.notes, decided_at=datetime.now(timezone.utc)))
    db.commit()
    return {"status": "rejected", "id": change_id}
