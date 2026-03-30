# Daniel's Donuts — Autonomous Marketing Agent Design
**Date:** 2026-03-30
**Status:** Approved

---

## Overview

An autonomous multi-agent marketing system for Daniel's Donuts. The system runs the full marketing operation: social media content creation and posting, website management, competitor research, and strategic planning — all with a human-in-the-loop approval gate before any execution.

---

## Platforms

- Instagram
- Facebook
- TikTok

---

## Agent Roster

| Agent | Responsibility | Schedule |
|---|---|---|
| **Orchestrator** | Coordinates all agents, manages task queue, triggers approvals | Always running |
| **Research Agent** | Monitors Krispy Kreme, Dunkin Donuts, local competitors, TikTok/Instagram trends | Daily |
| **Strategy Agent** | Analyzes research, generates marketing ideas, campaign briefs, weekly strategy reports | Weekly + on-demand |
| **Content Agent** | Generates AI images and video via Higgsfield, writes captions | Per approved idea |
| **Post-Production Agent** | Edits/assembles reels, adds music, captions, branding overlays (MoviePy + FFmpeg) | Per content batch |
| **Social Agent** | Schedules and posts to Instagram, Facebook, TikTok | Per approved content |
| **Website Agent** | Manages WordPress via REST API — banners, products, campaigns, blog posts | Per approved campaign |
| **Analytics Agent** | Tracks post performance, website traffic, campaign ROI, feeds data back to Strategy Agent | Daily |
| **Approval Gateway** | Manages review queue, surfaces items to dashboard, waits for sign-off | Event-driven |

---

## Tech Stack

### Core
- **Python** — all agents built with Anthropic Claude Agent SDK (`claude-sonnet-4-6`)
- **FastAPI** — backend API + orchestrator host
- **React + Tailwind CSS** — approval dashboard frontend
- **SQLite** (dev) → **PostgreSQL** (prod) — shared agent state
- **Redis + APScheduler** — task queue and agent scheduling

### Integrations
- **Claude API (claude-sonnet-4-6)** — agent reasoning, copywriting, strategy
- **Higgsfield API** — AI image and video generation
- **MoviePy + FFmpeg** — reel post-production pipeline
- **Meta Graph API** — Instagram + Facebook posting
- **TikTok API** — TikTok posting
- **WordPress REST API** — full site management (danielsdonuts.com.au — WordPress + WooCommerce + Avada)
- **Apify / Playwright** — competitor scraping and trend monitoring

---

## Approval Flow

```
Agent generates idea or content
        ↓
Approval Gateway adds to review queue
        ↓
Dashboard notifies user
        ↓
User reviews → Approve / Reject (with optional notes)
        ↓
Orchestrator triggers execution agents
```

Two-stage approval:
1. **Stage 1 — Ideas:** Strategy Agent ideas reviewed before any content is created
2. **Stage 2 — Content:** Finished images/reels reviewed before publishing or site updates

---

## Data Flow

### Daily Autonomous Cycle
1. Research Agent scrapes competitors + trends → stores insights in DB
2. Analytics Agent pulls performance data → updates DB
3. Strategy Agent reads insights + analytics → generates ideas/campaign briefs
4. Approval Gateway queues ideas → dashboard notification sent
5. User approves/rejects each idea (with optional notes)
6. Approved ideas → Content Agent generates assets via Higgsfield
7. Post-Production Agent assembles reels, adds branding/music/captions
8. Approval Gateway queues finished content → user reviews again
9. User approves → Social Agent schedules + posts | Website Agent updates site
10. Analytics Agent begins tracking performance

### Weekly Cycle
Strategy Agent generates full marketing report including:
- Competitor analysis summary
- Best/worst performing content
- Recommended campaigns for next week
- New product/flavour ideas based on trends

Report lands in dashboard for review.

---

## Database Schema (Key Tables)

| Table | Contents |
|---|---|
| `research` | Competitor data, trend snapshots, timestamps |
| `ideas` | Strategy-generated ideas with status (pending/approved/rejected) |
| `content` | Generated assets (images, videos, captions) linked to ideas |
| `posts` | Scheduled/published social posts with platform + analytics |
| `approvals` | Full audit trail of every user decision |

---

## Dashboard Pages

| Route | Purpose |
|---|---|
| `/dashboard` | Overview: pending approvals, scheduled posts, performance metrics, agent status |
| `/approvals` | Two-stage review queue (ideas → content) with preview and approve/reject |
| `/calendar` | Content calendar across Instagram, Facebook, TikTok |
| `/analytics` | Reach, engagement, follower growth, best content, campaign ROI |
| `/strategy` | Weekly reports, campaign briefs, competitor insights, trend summaries |
| `/website` | Pending website changes queued for approval |
| `/agents` | Agent status panel: last run, next run, health indicators, logs |

### Dashboard UX Principles
- One-click approvals with optional rejection notes fed back to the agent
- Content previewed in native platform format (Instagram card, TikTok vertical, etc.)
- Captions editable directly before approving
- Email/push notifications when new items need review

---

## Scheduling

The system runs fully autonomously on a fixed cadence:
- Research + Analytics: daily
- Content generation: triggered by approved ideas
- Strategy report: weekly
- Social posting: per approved content schedule
- Website updates: per approved campaign

---

## Target Website

**danielsdonuts.com.au** — WordPress + WooCommerce + Avada theme
The Website Agent has full management scope: content, products, banners, layout/design changes via WP REST API.
