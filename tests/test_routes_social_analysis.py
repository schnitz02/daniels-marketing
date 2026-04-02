# tests/test_routes_social_analysis.py
from unittest.mock import patch, MagicMock
from tests.conftest import *  # noqa
from src.db.models import SocialSnapshot, SocialAnalysis

def _add_snapshot(db, platform="instagram", followers=50000):
    db.add(SocialSnapshot(platform=platform, handle="test", followers=followers,
                          following=100, posts_count=500, bio="test"))
    db.commit()

def test_get_analysis_empty(client):
    resp = client.get("/api/social-stats/analysis/instagram")
    assert resp.status_code == 200
    assert resp.json() is None

def test_generate_analysis_stores_result(client, db):
    _add_snapshot(db)
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text='{"summary": "Good growth", "benchmarks": "Above average", "recommendations": ["Post more reels", "Use hashtags", "Run giveaway"]}')]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_msg

    with patch("src.api.routes.social_analysis.anthropic.Anthropic", return_value=mock_client):
        resp = client.post("/api/social-stats/analysis/instagram")
    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"] == "Good growth"
    assert len(data["recommendations"]) == 3

def test_generate_analysis_invalid_platform(client):
    resp = client.post("/api/social-stats/analysis/myspace")
    assert resp.status_code == 400

def test_get_analysis_returns_latest(client, db):
    _add_snapshot(db)
    db.add(SocialAnalysis(platform="instagram", analysis='{"summary":"old","benchmarks":"","recommendations":[]}'))
    db.add(SocialAnalysis(platform="instagram", analysis='{"summary":"new","benchmarks":"","recommendations":[]}'))
    db.commit()
    resp = client.get("/api/social-stats/analysis/instagram")
    assert resp.status_code == 200
    assert resp.json()["summary"] == "new"
