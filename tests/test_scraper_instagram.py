import json
from unittest.mock import MagicMock, patch

# Minimal IG web_profile_info API response shape
IG_API_RESPONSE = {
    "data": {
        "user": {
            "biography": "Donuts 🍩",
            "edge_followed_by": {"count": 10000},
            "edge_follow": {"count": 250},
            "edge_owner_to_timeline_media": {
                "count": 800,
                "edges": [
                    {
                        "node": {
                            "shortcode": "abc123",
                            "edge_liked_by": {"count": 200},
                            "edge_media_to_comment": {"count": 15},
                            "edge_media_to_caption": {
                                "edges": [{"node": {"text": "Fresh glazed"}}]
                            },
                            "thumbnail_src": "https://example.com/img.jpg",
                            "display_url": "https://example.com/img.jpg",
                        }
                    }
                ],
            },
        }
    }
}


def _mock_response(data: dict, status_code: int = 200):
    resp = MagicMock()
    resp.json.return_value = data
    resp.raise_for_status = MagicMock()
    return resp


def test_scrape_instagram_returns_snapshot_shape():
    from src.core.scrapers.instagram import scrape_instagram
    with patch("httpx.get", return_value=_mock_response(IG_API_RESPONSE)):
        result = scrape_instagram("danielsdonutsaustralia")

    assert result["followers"] == 10000
    assert result["following"] == 250
    assert result["posts_count"] == 800
    assert result["bio"] == "Donuts 🍩"
    assert result["handle"] == "danielsdonutsaustralia"
    assert result["platform"] == "instagram"
    assert len(result["recent_posts"]) == 1
    assert result["recent_posts"][0]["post_id"] == "abc123"
    assert result["recent_posts"][0]["likes"] == 200


def test_scrape_instagram_returns_none_on_error():
    from src.core.scrapers.instagram import scrape_instagram
    with patch("httpx.get", side_effect=Exception("blocked")):
        result = scrape_instagram("danielsdonutsaustralia")
    assert result is None
