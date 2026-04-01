import logging
import instaloader

logger = logging.getLogger(__name__)
MAX_POSTS = 9


def scrape_instagram(handle: str) -> dict | None:
    """
    Scrape a public Instagram profile.
    Returns a dict with profile stats and recent posts, or None if scraping fails.
    """
    try:
        loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            compress_json=False,
            save_metadata=False,
            quiet=True,
        )
        profile = instaloader.Profile.from_username(loader.context, handle)

        recent_posts = []
        for post in profile.get_posts():
            if len(recent_posts) >= MAX_POSTS:
                break
            recent_posts.append({
                "post_id": post.shortcode,
                "likes": post.likes,
                "comments": post.comments,
                "caption": (post.caption or "")[:200],
                "thumbnail_url": post.url,
                "posted_at": post.date_utc.isoformat() if post.date_utc else None,
            })

        return {
            "platform": "instagram",
            "handle": handle,
            "followers": profile.followers,
            "following": profile.followees,
            "posts_count": profile.mediacount,
            "bio": profile.biography or "",
            "recent_posts": recent_posts,
        }
    except Exception as e:
        logger.warning("Instagram scrape failed for %s: %s", handle, e)
        return None
