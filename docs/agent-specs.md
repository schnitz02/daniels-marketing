# Daniel's Donuts — Sub-Agent Specifications

> Portable specs for each autonomous agent in the marketing system.
> Paste into Hermes, Claude Agent SDK, or any orchestration platform.

---

## System Architecture

```
Research (daily 6am UTC)
    |
    v
Strategy (weekly Mon 7am UTC)
    |
    v
Content (daily 9am UTC)  ------>  Website (daily 12pm UTC)
    |
    v
Post Production (daily 10am UTC)
    |
    v
Social (daily 11am UTC)
    |
    v
Analytics (daily 8pm UTC)

Social Stats (daily 9:30am UTC)  [independent]
Social Analysis (on-demand)       [independent]
```

### Shared Infrastructure

**Database:** SQLite (dev) / PostgreSQL (prod)

**Base Agent Contract:** Every agent records its execution in the `agent_runs` table (`agent_name`, `status: running|completed|failed`, `started_at`, `completed_at`, `log`).

**JSON Parsing:** Claude responses may be wrapped in ` ```json ``` ` fences. Strip fences before parsing. Regex: `^```(?:json)?\s*` and `\s*```$`.

---

## Agent 1: Research

**Purpose:** Competitive intelligence — analyses 4 donut-market competitors using Claude's knowledge and stores structured insights.

**Model:** `claude-sonnet-4-6` · max_tokens: `1024`

**Schedule:** Daily at 06:00 UTC

**Dependencies:** None (first in pipeline)

**Competitors:**
- Krispy Kreme Australia
- Dunkin Donuts
- Donut King
- Mad Mex

**System Prompt:**
```
You are a marketing research agent for Daniel's Donuts, an Australian donut brand.
Based on your knowledge of {competitor}'s marketing strategy, social media presence,
and recent campaigns, provide 3 key insights that Daniel's Donuts could learn from
or respond to.

Return ONLY valid JSON:
{"insights": [{"insight": "str", "platform": "str", "actionable": "str"}]}
```

**Input:** None (stateless per-competitor analysis — iterates over COMPETITORS list)

**Output Schema:**
```json
{
  "insights": [
    {
      "insight": "string — what the competitor is doing",
      "platform": "string — which platform (instagram/tiktok/facebook/website)",
      "actionable": "string — specific recommendation for Daniel's Donuts"
    }
  ]
}
```

**Writes to DB:**
| Table | Column | Value |
|-------|--------|-------|
| `research` | `source` | `"claude_research"` |
| `research` | `competitor` | competitor name |
| `research` | `content` | stringified parsed JSON |
| `research` | `raw_data` | `{"model": "claude-sonnet-4-6"}` |
| `research` | `created_at` | UTC timestamp |

**Environment Variables:** `ANTHROPIC_API_KEY`

**Edge Cases:**
- If Claude returns unparseable JSON, store the raw text as `content` (fallback)
- Runs once per competitor (4 API calls per execution)

---

## Agent 2: Strategy

**Purpose:** Marketing ideation — consumes research insights and post history, generates 5 creative campaign ideas.

**Model:** `claude-sonnet-4-6` · max_tokens: `2048`

**Schedule:** Weekly on Monday at 07:00 UTC

**Dependencies:** Research agent (consumes `research` table)

**System Prompt:**
```
You are the marketing strategist for Daniel's Donuts, a 100% Aussie-made donut
brand with 50+ flavours. Based on this competitor research:
{research_summary}

Generate 5 creative marketing ideas for Instagram, Facebook, and TikTok.
Focus on viral potential, Australian culture, and what makes Daniel's unique.

Return ONLY valid JSON:
{"ideas": [{"title": "str", "body": "str", "platform": "str", "content_type": "str", "evidence": "str"}]}
```

**Input:**
- Last 20 rows from `research` table (ordered by `created_at` DESC), formatted as:
  `- {competitor}: {content}` (one line per row, joined with newlines)
- Last 20 rows from `posts` table (ordered by `published_at` DESC) — available as context

**Output Schema:**
```json
{
  "ideas": [
    {
      "title": "string — short campaign title",
      "body": "string — detailed description of the idea",
      "platform": "string — target platform (instagram/facebook/tiktok)",
      "content_type": "string — type of content (reel/image/carousel/story)",
      "evidence": "string — reasoning and data supporting this idea"
    }
  ]
}
```

**Writes to DB:**
| Table | Column | Value |
|-------|--------|-------|
| `ideas` | `title` | idea title (unique — skips duplicates) |
| `ideas` | `body` | idea description |
| `ideas` | `evidence` | supporting reasoning |
| `ideas` | `status` | `"pending"` (awaits human approval) |

**Environment Variables:** `ANTHROPIC_API_KEY`

**Edge Cases:**
- Skips ideas with titles that already exist in the `ideas` table
- If JSON parse fails, logs error and returns empty list (no crash)

---

## Agent 3: Content

**Purpose:** Creative production — generates image and video prompts for approved ideas, then calls Higgsfield API to produce the media.

**Model:** `claude-sonnet-4-6` · max_tokens: `1024`

**Schedule:** Daily at 09:00 UTC

**Dependencies:** Strategy agent (consumes `ideas` table where `status="approved"`)

**System Prompt:**
```
You are a creative director for Daniel's Donuts, an Australian donut brand.
For this marketing idea: '{idea.title}' — '{idea.body}'

Generate:
1. A detailed Higgsfield image prompt (photorealistic donuts, appetising, bright)
2. A detailed Higgsfield video prompt (15 second reel, vertical 9:16)
3. An engaging social media caption with relevant Australian hashtags

Return ONLY valid JSON:
{"image_prompt": "str", "video_prompt": "str", "caption": "str"}
```

**Input:** All rows from `ideas` where `status="approved"`, filtered to exclude ideas that already have `content` records.

**Output Schema:**
```json
{
  "image_prompt": "string — detailed prompt for Higgsfield image generation",
  "video_prompt": "string — detailed prompt for Higgsfield video generation",
  "caption": "string — social media caption with hashtags"
}
```

**Writes to DB (2 rows per idea):**
| Table | Column | Value |
|-------|--------|-------|
| `content` | `idea_id` | FK to approved idea |
| `content` | `type` | `"image"` or `"reel"` |
| `content` | `file_path` | `./media/idea_{id}_image.jpg` or `./media/idea_{id}_video.mp4` |
| `content` | `caption` | generated caption |
| `content` | `status` | `"pending"` (awaits human approval) |

**Writes to Filesystem:** Downloaded images and videos in `MEDIA_DIR` (default `./media`)

**External API — Higgsfield:**
- Image: `POST https://api.higgsfield.ai/v1/generate/image`
  - Params: `prompt`, `style: "photorealistic"`, `aspect_ratio: "1:1"`
- Video: `POST https://api.higgsfield.ai/v1/generate/video`
  - Params: `prompt`, `duration: 15`, `aspect_ratio: "9:16"`
- Auth: `Authorization: Bearer {HIGGSFIELD_API_KEY}`

**Environment Variables:** `ANTHROPIC_API_KEY`, `HIGGSFIELD_API_KEY`, `MEDIA_DIR` (optional)

**Edge Cases:**
- Skips ideas that already have content records (prevents duplicates)
- On Higgsfield failure, logs error and continues to next idea
- If Claude JSON parse fails, falls back to using idea title/body as raw prompts

---

## Agent 4: Post Production

**Purpose:** Branding — adds "Daniel's Donuts" watermark to generated video reels.

**Model:** None (no AI — pure video processing)

**Schedule:** Daily at 10:00 UTC

**Dependencies:** Content agent (consumes `content` table where `type="reel"` and `status="pending"`)

**Input:** All `content` rows where `type="reel"` and `status="pending"`

**Processing:**
1. Read video from `content.file_path`
2. Overlay "Daniel's Donuts" text watermark
3. Write branded video to `{original_stem}_branded.mp4`
4. Update `content.file_path` to point to branded version

**Library:** `moviepy` (with fallback to file copy if moviepy unavailable)

**Writes to DB:**
| Table | Column | Value |
|-------|--------|-------|
| `content` | `file_path` | updated to branded path |

**Environment Variables:** None

**Edge Cases:**
- If source video file not found, logs warning and skips
- If moviepy fails, logs error and skips

---

## Agent 5: Social

**Purpose:** Publishing — posts approved content to Instagram, Facebook, and TikTok.

**Model:** None (no AI — API integration only)

**Schedule:** Daily at 11:00 UTC

**Dependencies:** Post Production agent (consumes `content` where `status="approved"`)

**Input:** All `content` rows where `status="approved"`, filtered to exclude platforms that already have a `posts` record with `status="published"`.

**Platform Logic:**
- Images → Instagram + Facebook
- Reels → Instagram + Facebook + TikTok

**External APIs:**

**Meta (Instagram + Facebook):**
- `post_image(file_path, caption)` → Instagram image post via Graph API v21.0
- `post_reel(file_path, caption)` → Instagram reel via Graph API v21.0
- `post_to_facebook_page(caption, image_path?)` → Facebook Page post
- Auth: `META_ACCESS_TOKEN`
- Accounts: `META_IG_ACCOUNT_ID` (Instagram), `META_PAGE_ID` (Facebook)

**TikTok:**
- `post_video(file_path, caption)` → TikTok Open API v2
- Caption truncated to 150 characters
- Auth: `TIKTOK_ACCESS_TOKEN`

**Writes to DB:**
| Table | Column | Value |
|-------|--------|-------|
| `posts` | `content_id` | FK to content |
| `posts` | `platform` | `"instagram"` / `"facebook"` / `"tiktok"` |
| `posts` | `platform_post_id` | ID returned by platform API |
| `posts` | `published_at` | UTC timestamp |
| `posts` | `status` | `"published"` or `"failed"` |

**Environment Variables:** `META_ACCESS_TOKEN`, `META_IG_ACCOUNT_ID`, `META_PAGE_ID`, `TIKTOK_ACCESS_TOKEN`

**Edge Cases:**
- If platform credentials missing, `post_id` returns `None` → skip (don't record)
- On failure, records a `Post` with `status="failed"` (won't retry that platform)
- Checks `posted_platforms` set to avoid double-posting

---

## Agent 6: Website

**Purpose:** Website management — applies approved website changes to WordPress AND suggests new changes from approved ideas.

**Model:** `claude-sonnet-4-6` · max_tokens: `512`

**Schedule:** Daily at 12:00 UTC

**Dependencies:** Strategy agent (consumes `ideas` where `status="approved"`)

**Part A — Apply Changes:**
Processes all `website_changes` where `status="approved"`:
| `change_type` | WordPress Action |
|----------------|-----------------|
| `banner` | `PUT /wp-json/wp/v2/pages` |
| `blog_post` | `POST /wp-json/wp/v2/posts` |
| `product` | `PUT /wp-json/wc/v3/products/{id}` |
| `campaign_page` | `POST /wp-json/wp/v2/posts` |

**Part B — Suggest Changes (AI):**

**System Prompt:**
```
For this Daniel's Donuts marketing idea: '{idea.title}' — '{idea.body}'
Suggest a website change (banner, blog_post, or campaign_page).

Return ONLY valid JSON:
{"change_type": "str", "description": "str", "payload": {}}
```

**Output Schema:**
```json
{
  "change_type": "banner | blog_post | campaign_page",
  "description": "string — what the change does",
  "payload": {
    "title": "string",
    "content": "string (HTML)",
    "image_url": "string (optional)"
  }
}
```

**Writes to DB:**
| Table | Column | Value |
|-------|--------|-------|
| `website_changes` | `change_type` | from Claude response |
| `website_changes` | `description` | set to idea title (used for dedup) |
| `website_changes` | `payload` | JSON object from Claude |
| `website_changes` | `status` | `"pending"` / `"applied"` / `"failed"` |

**External API — WordPress:**
- Base URL: `WP_URL`
- Auth: HTTP Basic (`WP_USERNAME:WP_APP_PASSWORD`, base64 encoded)
- Endpoints: WordPress REST API v2 + WooCommerce v3

**Environment Variables:** `ANTHROPIC_API_KEY`, `WP_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`

**Edge Cases:**
- Skips ideas that already have a `website_changes` record with matching description
- On WordPress API failure, sets `status="failed"` and continues
- If Claude JSON parse fails, logs error and skips that idea

---

## Agent 7: Analytics

**Purpose:** Metrics collection — fetches reach and engagement data for published posts from Meta's Graph API.

**Model:** None (no AI — API integration only)

**Schedule:** Daily at 20:00 UTC

**Dependencies:** Social agent (consumes `posts` where `status="published"`)

**Input:** All `posts` rows where `status="published"`

**External API — Meta Graph API:**
```
GET https://graph.facebook.com/v21.0/{platform_post_id}/insights
  ?metric=impressions,reach,engagement
  &access_token={META_ACCESS_TOKEN}
```

**Updates to DB:**
| Table | Column | Value |
|-------|--------|-------|
| `posts` | `reach` | from API `reach` metric |
| `posts` | `engagement` | from API `engagement` metric |

**Environment Variables:** `META_ACCESS_TOKEN`

**Edge Cases:**
- Only fetches for `instagram` and `facebook` posts (TikTok not yet supported)
- If `META_ACCESS_TOKEN` is missing, returns empty metrics (no crash)
- If API returns non-200, logs warning and skips that post
- Overwrites existing values (latest fetch wins)

---

## Agent 8: Social Stats

**Purpose:** Social media monitoring — scrapes public profiles to track follower counts and cache recent posts.

**Model:** None (no AI — web scraping only)

**Schedule:** Daily at 09:30 UTC

**Dependencies:** None (independent)

**Profiles:**
| Platform | Handle | Scraper |
|----------|--------|---------|
| Instagram | `danielsdonutsaustralia` | Instagram private API |
| TikTok | `danielsdonutsaus` | TikTok page HTML parser |
| Facebook | `DanielsDonutsAustralia` | Social Blade scraper |

**Scraper Details:**

**Instagram:**
- URL: `https://i.instagram.com/api/v1/users/web_profile_info/?username={handle}`
- Headers: `User-Agent: Instagram 275.0.0.27.98 Android`, `x-ig-app-id: 936619743392459`
- Optional: `INSTAGRAM_SESSION_ID` cookie for rate limit bypass
- Returns: followers, following, posts_count, bio, recent_posts

**TikTok:**
- URL: `https://www.tiktok.com/@{handle}`
- Parses `__UNIVERSAL_DATA_FOR_REHYDRATION__` script tag from HTML
- Returns: followers, following, posts_count, bio, recent_posts

**Facebook:**
- URL: `https://socialblade.com/facebook/user/{handle}` (via Social Blade)
- Uses `curl_cffi` to impersonate Chrome browser
- Parses tRPC JSON data from page
- Returns: followers, following, posts_count

**Writes to DB:**

*Snapshots (1 per platform per day):*
| Table | Column | Value |
|-------|--------|-------|
| `social_snapshots` | `platform` | instagram/tiktok/facebook |
| `social_snapshots` | `handle` | profile handle |
| `social_snapshots` | `followers` | integer |
| `social_snapshots` | `following` | integer |
| `social_snapshots` | `posts_count` | integer |
| `social_snapshots` | `bio` | string |
| `social_snapshots` | `scraped_at` | UTC timestamp |

*Post cache (deduped on post_id):*
| Table | Column | Value |
|-------|--------|-------|
| `social_posts_cache` | `platform` | platform name |
| `social_posts_cache` | `post_id` | unique platform post ID |
| `social_posts_cache` | `likes` | integer |
| `social_posts_cache` | `comments` | integer |
| `social_posts_cache` | `caption` | string |
| `social_posts_cache` | `thumbnail_url` | URL |
| `social_posts_cache` | `posted_at` | datetime |

**Environment Variables:** `INSTAGRAM_SESSION_ID` (optional)

**Edge Cases:**
- Skips platform if scrape returns `None` (site down, blocked, etc.)
- Skips platform if a snapshot already exists for today (prevents duplicates)
- For existing posts in cache, updates likes/comments/scraped_at instead of inserting

---

## Agent 9: Social Analysis (On-Demand)

**Purpose:** AI performance analysis — generates benchmarks and recommendations from the latest social snapshot data.

**Model:** `claude-sonnet-4-6` · max_tokens: `800`

**Schedule:** On-demand only (triggered via `POST /api/social-stats/analysis/{platform}`)

**Dependencies:** Social Stats agent (consumes `social_snapshots` table)

**System Prompt:**
```
You are a social media analyst for Daniel's Donuts, an Australian donut brand.

Platform: {platform}
Current stats:
- Followers: {followers}
- Following: {following}
- Posts: {posts_count}
- Bio: {bio}

Provide a JSON response with exactly these keys:
- "summary": 2-3 sentence plain-English summary of current performance
- "benchmarks": How these numbers compare to typical Australian food/hospitality brand benchmarks
- "recommendations": List of exactly 3 specific, actionable improvements

Return ONLY valid JSON, no markdown.
```

**Input:** Latest `social_snapshots` row for the given platform.

**Output Schema:**
```json
{
  "summary": "string — 2-3 sentence performance summary",
  "benchmarks": "string — comparison to Australian food/hospitality benchmarks",
  "recommendations": ["string", "string", "string"],
  "generated_at": "ISO 8601 datetime"
}
```

**Writes to DB:**
| Table | Column | Value |
|-------|--------|-------|
| `social_analysis` | `platform` | instagram/tiktok/facebook |
| `social_analysis` | `analysis` | JSON string of response |
| `social_analysis` | `generated_at` | UTC timestamp |

**API Endpoints:**
- `GET /api/social-stats/analysis/{platform}` — returns latest stored analysis
- `POST /api/social-stats/analysis/{platform}` — generates fresh analysis

**Environment Variables:** `ANTHROPIC_API_KEY`

**Edge Cases:**
- Returns 404 if no snapshot data exists for the platform
- Returns 500 if Claude returns invalid JSON
- Stores each analysis (doesn't overwrite — history preserved)

---

## Environment Variables Summary

| Variable | Required By | Description |
|----------|-------------|-------------|
| `ANTHROPIC_API_KEY` | Research, Strategy, Content, Website, Social Analysis | Claude API access |
| `HIGGSFIELD_API_KEY` | Content | Image/video generation |
| `META_ACCESS_TOKEN` | Social, Analytics | Facebook Graph API |
| `META_IG_ACCOUNT_ID` | Social | Instagram Business account ID |
| `META_PAGE_ID` | Social | Facebook Page ID |
| `META_APP_ID` | Social | Meta App ID |
| `META_APP_SECRET` | Social | Meta App Secret |
| `TIKTOK_CLIENT_KEY` | Social | TikTok app key |
| `TIKTOK_CLIENT_SECRET` | Social | TikTok app secret |
| `TIKTOK_ACCESS_TOKEN` | Social | TikTok OAuth token |
| `WP_URL` | Website | WordPress site URL |
| `WP_USERNAME` | Website | WordPress admin username |
| `WP_APP_PASSWORD` | Website | WordPress application password |
| `INSTAGRAM_SESSION_ID` | Social Stats (optional) | Instagram session cookie |
| `MEDIA_DIR` | Content, Post Production | Media output directory (default `./media`) |
| `DATABASE_URL` | All | DB connection string |
| `AGENT_API_KEY` | API trigger endpoint (optional) | Protects `/agents/trigger` |
| `POC_MODE` | All external integrations | `true` = stub Higgsfield/Meta/TikTok/WordPress |

---

## Database Schema (all tables)

```sql
-- Pipeline tables
research          (id, source, competitor, content, raw_data, created_at)
ideas             (id, title, body, evidence, status, rejection_notes, created_at)
content           (id, idea_id FK, type, file_path, caption, status, rejection_notes, created_at)
posts             (id, content_id FK, platform, platform_post_id, scheduled_at, published_at, status, reach, engagement)
approvals         (id, item_type, item_id, decision, notes, decided_at)
website_changes   (id, change_type, description, payload, status, created_at)

-- Monitoring tables
agent_runs        (id, agent_name, status, started_at, completed_at, log)
social_snapshots  (id, platform, handle, followers, following, posts_count, bio, scraped_at)
social_posts_cache(id, platform, post_id UNIQUE, likes, comments, thumbnail_url, caption, posted_at, scraped_at)
social_analysis   (id, platform, analysis, generated_at)
```

---

## Orchestration Schedule

| Time (UTC) | Agent | Frequency | Human Gate? |
|------------|-------|-----------|-------------|
| 06:00 | Research | Daily | No |
| 07:00 Mon | Strategy | Weekly | Ideas → "pending" (need approval) |
| 09:00 | Content | Daily | Reads "approved" ideas only |
| 09:30 | Social Stats | Daily | No |
| 10:00 | Post Production | Daily | No |
| 11:00 | Social | Daily | Reads "approved" content only |
| 12:00 | Website | Daily | Changes → "pending" (need approval) |
| 20:00 | Analytics | Daily | No |
| On-demand | Social Analysis | Manual | No |

**Human approval gates:** Strategy → Approvals → Content → Approvals → Social/Website. The pipeline won't auto-publish without human sign-off at two checkpoints (ideas + content).
