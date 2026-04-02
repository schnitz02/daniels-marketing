# tests/test_routes_research.py
from tests.conftest import *  # noqa
from src.db.models import ResearchItem

def test_get_research_items_empty(client):
    resp = client.get("/api/research/items")
    assert resp.status_code == 200
    assert resp.json() == []

def test_get_research_items_returns_data(client, db):
    item = ResearchItem(source="instagram", competitor="Krispy Kreme",
                        content="KK ran a BOGO promotion")
    db.add(item)
    db.commit()
    resp = client.get("/api/research/items")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["competitor"] == "Krispy Kreme"
    assert data[0]["content"] == "KK ran a BOGO promotion"
    assert data[0]["source"] == "instagram"

def test_get_research_items_filter_by_competitor(client, db):
    db.add(ResearchItem(source="web", competitor="Krispy Kreme", content="KK news"))
    db.add(ResearchItem(source="web", competitor="Dunkin Donuts", content="DD news"))
    db.commit()
    resp = client.get("/api/research/items?competitor=Krispy+Kreme")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["competitor"] == "Krispy Kreme"
