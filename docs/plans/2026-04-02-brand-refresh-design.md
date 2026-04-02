# Brand Refresh Design — Daniel's Donuts Dashboard

**Date:** 2026-04-02
**Goal:** Replace the generic dark-gray theme with Daniel's Donuts official brand colours, logo, and a lighter warm feel matching their public website.

---

## Colour Palette

| Role | Token | Hex |
|------|-------|-----|
| Primary action / teal accent | `--color-teal` | `#04D3C5` |
| Sidebar / headings | `--color-navy` | `#00395D` |
| Highlight / gold accent | `--color-gold` | `#F7CA5E` |
| Tags / badges / decorative | `--color-pink` | `#FFA1C7` |
| Page background | `--color-cream` | `#F5F4EC` |
| Card background | `--color-white` | `#FFFFFF` |
| Muted text | `--color-slate` | `#6B8A9A` |
| Card border | `--color-border` | `#E8E4D9` |

---

## Structural Changes

### Sidebar (`App.jsx`)
- Background: navy `#00395D`
- Logo: `Master_Logo_300x108.png` centered at top, replacing emoji + text
- Nav items: white text, teal active pill, white/10% hover
- Bottom: version/env indicator if desired

### Main Content Area
- Page background: cream `#F5F4EC`
- Cards: white `#FFFFFF`, 1px `#E8E4D9` border, `shadow-sm`
- Page headings (`h1`): navy `#00395D`, `font-bold`
- Body/secondary text: `#4A5568`
- Muted/label text: slate `#6B8A9A`

### Interactive Elements
- All primary buttons (was `bg-yellow-600`): → `bg-[#04D3C5] text-white hover:bg-[#03bdb0]`
- Text accent links (was `text-yellow-400`): → `text-[#04D3C5]`
- Numbered list markers (was `text-yellow-500`): → `text-[#04D3C5]`
- Reasoning toggle buttons: → teal

### Badges & Tags
- Social source badges: keep existing social brand colours (pink/blue/purple)
- `claude_research` badge: `bg-[#F7CA5E] text-[#00395D]` (gold + navy)
- Agent status running: amber/yellow pulse — keep as-is (status indicator, not brand)

### Charts
- Line stroke (was `#EAB308`): → `#04D3C5`
- Grid lines (was `#374151`): → `#E8E4D9`
- Tooltip background (was `#111827`): → `#00395D`
- Tooltip border (was `#374151`): → `#1a5276`

---

## File-by-File Change Map

### `dashboard/src/index.css`
- Add brand colour tokens to `@theme`
- `body`: `background-color: #F5F4EC`, `color: #00395D`

### `dashboard/public/` (assets)
- Copy `Master_Logo_300x108.png` → `dashboard/public/logo.png`

### `dashboard/src/App.jsx`
- Sidebar: `bg-[#00395D]` border `border-[#1a5276]`
- Logo: `<img src="/logo.png">` replacing emoji + text span
- Active nav: `bg-[#04D3C5] text-white`
- Hover nav: `hover:bg-white/10 text-white`
- Inactive nav: `text-white/70`
- Main area: `bg-[#F5F4EC]`

### All page `.jsx` files — class replacements

| Old (dark) | New (light) |
|---|---|
| `bg-gray-950` / `bg-gray-900` (cards) | `bg-white` |
| `bg-gray-800` (inner sections) | `bg-[#F5F4EC]` |
| `bg-gray-700` (deepest inner) | `bg-gray-100` |
| `border-gray-800` / `border-gray-700` | `border-[#E8E4D9]` |
| `text-white` (headings) | `text-[#00395D]` |
| `text-gray-300` / `text-gray-400` | `text-[#4A5568]` |
| `text-gray-500` / `text-gray-600` | `text-[#6B8A9A]` |
| `bg-yellow-600 hover:bg-yellow-500` (buttons) | `bg-[#04D3C5] hover:bg-[#03bdb0]` |
| `text-yellow-400 hover:text-yellow-300` | `text-[#04D3C5] hover:text-[#03bdb0]` |
| `text-yellow-500` | `text-[#04D3C5]` |
| `border-yellow-600` | `border-[#04D3C5]` |
| `bg-yellow-600 border-yellow-600` (active pill) | `bg-[#04D3C5] border-[#04D3C5]` |
| `stroke="#EAB308"` (chart line) | `stroke="#04D3C5"` |
| `stroke="#374151"` (chart grid) | `stroke="#E8E4D9"` |
| Chart tooltip `backgroundColor: "#111827"` | `backgroundColor: "#00395D"` |
| Chart tooltip `border: "1px solid #374151"` | `border: "1px solid #1a5276"` |
| `bg-gray-900 border-yellow-800` (GA4 warning) | `bg-[#FFF8E1] border-[#F7CA5E]` |
| `text-yellow-400` (GA4 heading) | `text-[#00395D]` |

### Pages affected
- `Overview.jsx`
- `Approvals.jsx`
- `Agents.jsx`
- `SocialStats.jsx`
- `Research.jsx`
- `Analytics.jsx`
- `Strategy.jsx`
- `Website.jsx`
- `Calendar.jsx`

---

## Logo Asset
- Source: `Master_Logo_300x108.png` (root of project)
- Destination: `dashboard/public/logo.png`
- Usage: `<img src="/logo.png" alt="Daniel's Donuts" className="w-40 mx-auto mb-6" />`

---

## Non-Goals
- No layout/structure changes (widths, grid columns, component hierarchy)
- No font changes
- No animation additions
- No mobile/responsive changes
