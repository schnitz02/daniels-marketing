import pytest
from unittest.mock import MagicMock, patch


def _make_mock_profile(followers=10000, followees=250, mediacount=800, biography="Donuts 🍩"):
    profile = MagicMock()
    profile.followers = followers
    profile.followees = followees
    profile.mediacount = mediacount
    profile.biography = biography
    return profile


def _make_mock_post(likes=200, comments=15, shortcode="abc123", caption="Fresh glazed"):
    post = MagicMock()
    post.likes = likes
    post.comments = comments
    post.shortcode = shortcode
    post.caption = caption
    post.date_utc = None
    post.url = "https://example.com/img.jpg"
    return post


def test_scrape_instagram_returns_snapshot_shape():
    from src.core.scrapers.instagram import scrape_instagram
    mock_profile = _make_mock_profile()
    mock_post = _make_mock_post()
    mock_profile.get_posts.return_value = [mock_post]

    with patch("src.core.scrapers.instagram.instaloader.Instaloader"), \
         patch("src.core.scrapers.instagram.instaloader.Profile.from_username",
               return_value=mock_profile):
        result = scrape_instagram("danielsdonutsaustralia")

    assert result["followers"] == 10000
    assert result["following"] == 250
    assert result["posts_count"] == 800
    assert result["bio"] == "Donuts 🍩"
    assert len(result["recent_posts"]) == 1
    assert result["recent_posts"][0]["post_id"] == "abc123"
    assert result["recent_posts"][0]["likes"] == 200


def test_scrape_instagram_returns_none_on_error():
    from src.core.scrapers.instagram import scrape_instagram
    with patch("src.core.scrapers.instagram.instaloader.Profile.from_username",
               side_effect=Exception("blocked")):
        result = scrape_instagram("danielsdonutsaustralia")
    assert result is None
