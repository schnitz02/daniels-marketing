from unittest.mock import patch, MagicMock

FB_HTML = """
<html>
<head>
<title>Daniel's Donuts Australia | Facebook</title>
</head>
<body>
<div>8,500 people follow this</div>
</body>
</html>
"""

FB_HTML_NO_META = "<html><body><p>Nothing here</p></body></html>"


def _mock_response(html):
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def test_scrape_facebook_parses_followers():
    from src.core.scrapers.facebook import scrape_facebook
    with patch("httpx.get", return_value=_mock_response(FB_HTML)):
        result = scrape_facebook("DanielsDonutsAustralia")
    assert result["platform"] == "facebook"
    assert result["followers"] == 8500
    assert result["bio"] == "Daniel's Donuts Australia"
    assert result["handle"] == "DanielsDonutsAustralia"


def test_scrape_facebook_returns_zeros_when_no_meta():
    from src.core.scrapers.facebook import scrape_facebook
    with patch("httpx.get", return_value=_mock_response(FB_HTML_NO_META)):
        result = scrape_facebook("DanielsDonutsAustralia")
    assert result["followers"] == 0


def test_scrape_facebook_returns_none_on_error():
    from src.core.scrapers.facebook import scrape_facebook
    with patch("httpx.get", side_effect=Exception("blocked")):
        result = scrape_facebook("DanielsDonutsAustralia")
    assert result is None
