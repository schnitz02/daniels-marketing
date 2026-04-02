# tests/test_routes_ga4.py
from unittest.mock import patch
from tests.conftest import *  # noqa

def test_ga4_status_not_connected(client):
    with patch("src.api.routes.ga4._ga4_client") as mock:
        mock.get_status.return_value = {"connected": False}
        resp = client.get("/api/ga4/status")
    assert resp.status_code == 200
    assert resp.json() == {"connected": False}

def test_ga4_seo_returns_none_when_not_connected(client):
    with patch("src.api.routes.ga4._ga4_client") as mock:
        mock.get_seo_metrics.return_value = None
        resp = client.get("/api/ga4/seo")
    assert resp.status_code == 200
    assert resp.json() is None

def test_ga4_seo_returns_data_when_connected(client):
    fake = {"summary": {"sessions": 1200}, "trend": [], "top_pages": []}
    with patch("src.api.routes.ga4._ga4_client") as mock:
        mock.get_seo_metrics.return_value = fake
        resp = client.get("/api/ga4/seo")
    assert resp.status_code == 200
    assert resp.json()["summary"]["sessions"] == 1200

def test_ga4_sem_returns_data_when_connected(client):
    fake = {"summary": {"sessions": 300, "conversions": 45}, "trend": []}
    with patch("src.api.routes.ga4._ga4_client") as mock:
        mock.get_sem_metrics.return_value = fake
        resp = client.get("/api/ga4/sem")
    assert resp.status_code == 200
    assert resp.json()["summary"]["conversions"] == 45
