from unittest.mock import patch, MagicMock

FB_HTML = """
<html>
<head>
<meta property="og:description" content="Daniel's Donuts Australia · 8,200 likes · 8,500 followers" />
<meta property="og:title" content="Daniel's Donuts Australia" />
</head>
<body></body>
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
