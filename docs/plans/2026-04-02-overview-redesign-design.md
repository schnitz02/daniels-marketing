# Overview Page Redesign — Design Document

**Date:** 2026-04-02
**Status:** Approved

## Goal

Transform the Overview page from a static summary into an interactive "morning briefing" that gives users the two things they need first each day: how the social channels performed, and what content is going out this week. All detail views open as slide-in drawer modals — no navigation away from the page.

---

## Layout (top to bottom)

### 1. Header Bar
- "Good morning" greeting + today's date in Melbourne time (`en-AU` locale)
- Subtle, full-width, sets context without taking much space

### 2. Social Health Strip
Three equal-width cards in a row: **Instagram · TikTok · Facebook**

Each card shows:
- Platform icon + name
- Follower count (formatted with commas)
- Delta since last scrape (e.g. `+12 since yesterday`) — positive in teal, negative in red, zero in gray
- Last updated timestamp (Melbourne time, relative if recent e.g. "2 hours ago")

**Click behaviour:** Opens a drawer modal with the full stat breakdown for that platform (all fields returned by `/api/social-stats/{platform}`).

### 3. This Week's Schedule
Largest section on the page. Grid of post cards spanning today + the next 6 days.

Each post card shows:
- Platform badge (colour-coded)
- Day + time (Melbourne timezone, Australian format)
- Content preview — truncated to 2 lines with ellipsis
- Status chip: Scheduled / Draft / Published

**Click behaviour:** Opens a drawer modal with full post content, platform, scheduled datetime, and status.

Empty state: friendly message with a link to the Calendar page if no posts are scheduled.

### 4. Bottom Row (2 columns)

**Left — Pending Approvals**
- Count badge showing total pending
- List of up to 3 pending ideas: title + 1-line snippet
- "+ N more" link navigates to Approvals page if more than 3
- **Click an idea:** Opens drawer modal with full body, evidence field, and **Approve / Reject** buttons that call the API in-place. On action, the idea disappears from the list and count updates.

**Right — Latest Research**
- Most recent research item from `/api/research/items?limit=1`
- Competitor name, source badge, key finding snippet
- **Click:** Opens drawer modal with full parsed insight (same rendering as Research page `InsightCard`)

---

## Modals / Drawers

- Shared `<Drawer>` component: slides in from the right, full viewport height, ~480px wide
- Dismissible by clicking the backdrop or pressing Escape
- Title bar with close button (×)
- Each section passes its own content as children

---

## Data Sources (all existing — no backend changes)

| Section | Endpoint |
|---|---|
| Social strip | `GET /api/social-stats/instagram`, `/tiktok`, `/facebook` |
| Schedule | `GET /api/dashboard/calendar` (filter next 7 days client-side) |
| Pending approvals | `GET /api/approvals/pending` |
| Approve in modal | `POST /api/approvals/{id}/approve` |
| Reject in modal | `POST /api/approvals/{id}/reject` |
| Latest research | `GET /api/research/items?limit=1` |

---

## Styling

Follows the Daniel's Donuts brand refresh already applied to all other pages:
- Page background: cream `#F5F4EC`
- Cards: white with `#E8E4D9` border and soft drop shadow
- Primary accent: teal `#04D3C5`
- Headings / text: navy `#00395D`
- Badges / highlights: gold `#F7CA5E`
- Drawer overlay: semi-transparent dark backdrop

---

## Out of Scope

- No new backend endpoints required
- No GA4 data on Overview (not connected yet — deferred to April 14th IT meeting)
- No drag-and-drop or customisable widgets
- No notifications/alerts system
