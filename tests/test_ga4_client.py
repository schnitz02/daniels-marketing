# tests/test_ga4_client.py
import os
from unittest.mock import patch, MagicMock

def test_ga4_client_returns_none_when_no_credentials():
    """Client degrades gracefully when env vars not set."""
    with patch.dict(os.environ, {}, clear=False):
        # Ensure vars are absent
        os.environ.pop("GOOGLE_ANALYTICS_PROPERTY_ID", None)
        os.environ.pop("GOOGLE_SERVICE_ACCOUNT_JSON", None)
        # Force re-import with clean env
        import importlib
        import src.core.ga4_client as mod
        importlib.reload(mod)
        client = mod.GA4Client()
        assert client.connected is False
        assert client.get_seo_metrics() is None
        assert client.get_sem_metrics() is None
        assert client.get_status() == {"connected": False}

def test_ga4_client_status_connected_when_credentials_present(tmp_path):
    """Client reports connected=True when env vars are set (even if file doesn't exist — just checking init)."""
    fake_json = tmp_path / "sa.json"
    fake_json.write_text('{"type": "service_account"}')
    env = {
        "GOOGLE_ANALYTICS_PROPERTY_ID": "123456789",
        "GOOGLE_SERVICE_ACCOUNT_JSON": str(fake_json),
    }
    with patch.dict(os.environ, env):
        import importlib
        import src.core.ga4_client as mod
        with patch("src.core.ga4_client.BetaAnalyticsDataClient"):
            with patch("src.core.ga4_client.service_account.Credentials.from_service_account_file"):
                importlib.reload(mod)
                client = mod.GA4Client()
                assert client.connected is True
                assert client.get_status() == {"connected": True}
