from unittest.mock import patch, MagicMock
import json


TIKTOK_HTML = """
<html><body>
<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">
{
  "__DEFAULT_SCOPE__": {
    "webapp.user-detail": {
      "userInfo": {
        "user": {"uniqueId": "danielsdonutsaus", "signature": "Official TikTok"},
        "stats": {"followerCount": 5000, "followingCount": 120, "heartCount": 45000, "videoCount": 95}
      }
    }
  }
}
</script>
</body></html>
"""


def _mock_response(html):
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def test_scrape_tiktok_returns_snapshot_shape():
    from src.core.scrapers.tiktok import scrape_tiktok
    with patch("httpx.get", return_value=_mock_response(TIKTOK_HTML)):
        result = scrape_tiktok("danielsdonutsaus")
    assert result["followers"] == 5000
    assert result["following"] == 120
    assert result["posts_count"] == 95
    assert result["platform"] == "tiktok"


def test_scrape_tiktok_returns_none_on_error():
    from src.core.scrapers.tiktok import scrape_tiktok
    with patch("httpx.get", side_effect=Exception("network error")):
        result = scrape_tiktok("danielsdonutsaus")
    assert result is None
