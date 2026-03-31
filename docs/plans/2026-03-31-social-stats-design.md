# Social Stats Dashboard — Design Document
**Date:** 2026-03-31
**Project:** Daniel's Donuts Marketing Agent

---

## Overview

Add a Social Stats page to the marketing dashboard that scrapes Daniel's Donuts' public social media profiles (Instagram, Facebook, TikTok) without using official API keys. Data is stored as timestamped snapshots to enable historical trend charts alongside live stats.

---

## Platforms & Handles

| Platform  | Handle                        | URL                                                   |
|-----------|-------------------------------|-------------------------------------------------------|
| Instagram | danielsdonutsaustralia        | https://www.instagram.com/danielsdonutsaustralia/     |
| Facebook  | DanielsDonutsAustralia        | https://www.facebook.com/DanielsDonutsAustralia/      |
| TikTok    | danielsdonutsaus              | https://www.tiktok.com/@danielsdonutsaus              |

---

## Database Schema

### `social_snapshots`
| Column        | Type     | Notes                                      |
|---------------|----------|--------------------------------------------|
| id            | Integer  | Primary key                                |
| platform      | String   | "instagram" / "facebook" / "tiktok"        |
| handle        | String   | Account handle                             |
| followers     | Integer  | Follower count at time of scrape           |
| following     | Integer  | Following count                            |
| posts_count   | Integer  | Total posts/videos                         |
| bio           | String   | Profile bio text                           |
| scraped_at    | DateTime | UTC timestamp of this snapshot             |

### `social_posts_cache`
| Column        | Type     | Notes                                      |
|---------------|----------|--------------------------------------------|
| id            | Integer  | Primary key                                |
| platform      | String   | Platform name                              |
| post_id       | String   | Platform-native post ID                    |
| likes         | Integer  | Like count                                 |
| comments      | Integer  | Comment count                              |
| thumbnail_url | String   | URL or local path to thumbnail             |
| caption       | String   | Post caption (truncated)                   |
| posted_at     | DateTime | When post was published                    |
| scraped_at    | DateTime | When this was last scraped                 |

---

## Scraping Strategy

### Instagram — `instaloader`
- Python library that scrapes public profiles without authentication
- Gets: followers, following, post count, bio, recent posts (likes, comments, thumbnails)
- Installed via pip, no API key required

### TikTok — `httpx` + HTML parsing
- Request public profile page with browser-like headers
- Parse JSON embedded in `<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">` tag
- Gets: followers, following, total likes, recent video stats

### Facebook — `httpx` + HTML parsing
- Request public page with browser-like headers
- Parse meta tags and structured data for page likes/followers
- Recent posts have limited public data; show available fields gracefully

### Fallback behaviour
- If a live scrape fails (bot detection, network error), return the most recent cached snapshot
- Show "last scraped" timestamp so the user knows how fresh the data is
- Never show an error that blocks the whole page — degrade gracefully per platform

---

## New Agent: `SocialStatsAgent`

Registered as `"social_stats"` in the agent registry.

**`run()` behaviour:**
1. Scrape all three platforms concurrently
2. Store a new `social_snapshot` row for each platform
3. Store/update `social_posts_cache` rows for recent posts (upsert by post_id)
4. Return `{"snapshots_saved": 3, "posts_cached": N}`

**Scheduled:** daily at 9am (alongside existing jobs)
**Manual trigger:** available via Agents page "Run Now" button

---

## API Endpoints

| Method | Path                              | Description                                 |
|--------|-----------------------------------|---------------------------------------------|
| GET    | `/api/social/stats/{platform}`    | Latest snapshot + all historical snapshots  |
| GET    | `/api/social/posts/{platform}`    | Cached recent posts for platform            |
| POST   | `/api/social/refresh/{platform}`  | Trigger live scrape for one platform        |

---

## Dashboard Page: Social Stats

**Route:** `/social-stats`
**File:** `dashboard/src/pages/SocialStats.jsx`

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  Social Stats                    [Refresh All]           │
│  Last scraped: 2 hours ago                               │
├──────────────┬──────────────┬────────────────────────────┤
│  Instagram   │   Facebook   │        TikTok              │  ← tabs
├──────────────┴──────────────┴────────────────────────────┤
│                                                           │
│  SURFACE STATS                                            │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌───────────┐  │
│  │ Followers│ │ Following │ │  Posts   │  │    Bio    │  │
│  │  12,400  │ │    342    │ │   891    │  │  text...  │  │
│  └──────────┘ └───────────┘ └──────────┘ └───────────┘  │
│                                                           │
│  FOLLOWER TREND                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │  [line chart — one point per snapshot]            │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│  RECENT POSTS                                             │
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐      │
│  │ post  │ │ post  │ │ post  │ │ post  │ │ post  │      │
│  │ 💙 234│ │ 💙 189│ │ 💙 421│ │ 💙 98 │ │ 💙 312│      │
│  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘      │
└─────────────────────────────────────────────────────────┘
```

### Charts
- **Follower trend:** Recharts `LineChart` — x-axis is date, y-axis is follower count
- **Engagement rate trend:** Recharts `LineChart` — engagement rate = (likes + comments) / followers × 100

### Graceful degradation
- No snapshots yet → show "No data yet. Click Refresh to scrape." with a prominent refresh button
- Scrape in progress → show skeleton loaders
- Platform blocked → show last cached data with "data may be stale" warning badge

---

## Dependencies

```
instaloader          # Instagram scraping
httpx                # HTTP client for TikTok + Facebook
beautifulsoup4       # HTML parsing fallback
recharts             # Charts (already likely available via npm)
```

---

## POC Mode

`POC_MODE=true` does **not** stub the social stats scraper — this agent uses real public scraping, no API key needed. If scraping fails in POC mode, the snapshot is skipped and a warning is logged.

---

## Testing

- Unit test `parse_instagram_profile()`, `parse_tiktok_profile()`, `parse_facebook_page()` with fixture HTML
- Unit test snapshot deduplication (don't double-insert if same platform + same hour)
- Integration test: full agent run with mocked HTTP responses stores correct DB rows
- API endpoint tests: GET returns snapshots in correct shape
