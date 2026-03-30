import pytest
from src.db.models import Idea, Content, WebsiteChange

def test_get_pending_ideas(client, db):
    db.add(Idea(title="Test Idea", body="Test body", status="pending"))
    db.commit()
    response = client.get("/api/approvals/ideas")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Idea"

def test_approve_idea(client, db):
    idea = Idea(title="Approve Me", body="Test", status="pending")
    db.add(idea)
    db.commit()
    response = client.post(f"/api/approvals/ideas/{idea.id}/approve")
    assert response.status_code == 200
    db.refresh(idea)
    assert idea.status == "approved"

def test_reject_idea_with_notes(client, db):
    idea = Idea(title="Reject Me", body="Test", status="pending")
    db.add(idea)
    db.commit()
    response = client.post(f"/api/approvals/ideas/{idea.id}/reject", json={"notes": "Not on brand"})
    assert response.status_code == 200
    db.refresh(idea)
    assert idea.status == "rejected"
    assert idea.rejection_notes == "Not on brand"

def test_get_pending_content(client, db):
    idea = Idea(title="Test", body="Test", status="approved")
    db.add(idea)
    db.flush()
    db.add(Content(idea_id=idea.id, type="image", file_path="/tmp/test.jpg", caption="Fresh!", status="pending"))
    db.commit()
    response = client.get("/api/approvals/content")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_approve_content(client, db):
    idea = Idea(title="Test", body="Test", status="approved")
    db.add(idea)
    db.flush()
    content = Content(idea_id=idea.id, type="image", file_path="/tmp/test.jpg", caption="Fresh!", status="pending")
    db.add(content)
    db.commit()
    response = client.post(f"/api/approvals/content/{content.id}/approve")
    assert response.status_code == 200
    db.refresh(content)
    assert content.status == "approved"

def test_get_pending_website_changes(client, db):
    db.add(WebsiteChange(change_type="banner", description="Easter", payload={}, status="pending"))
    db.commit()
    response = client.get("/api/approvals/website")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_dashboard_overview(client, db):
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "pending_ideas" in data
    assert "pending_content" in data
    assert "published_posts" in data
