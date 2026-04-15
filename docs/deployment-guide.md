# Deployment Guide — Daniel's Donuts Marketing Dashboard

**Repo:** https://github.com/schnitz02/daniels-marketing.git

**Architecture:**
- **Frontend** (React/Vite) → Vercel (free tier)
- **Backend** (FastAPI) → Railway ($5/month hobby plan)
- **Database** → Railway PostgreSQL (included with backend)

---

## Step 1: Deploy the Backend on Railway

Railway runs the FastAPI server and hosts a PostgreSQL database.

### 1.1 — Create a Railway account
1. Go to [railway.com](https://railway.com)
2. Click **"Start a New Project"**
3. Sign in with your **GitHub account** (schnitz02)

### 1.2 — Create a new project from the GitHub repo
1. Click **"Deploy from GitHub Repo"**
2. Select **schnitz02/daniels-marketing**
3. Railway will auto-detect the project — **don't deploy yet**, we need to configure it first

### 1.3 — Set the root directory and start command
1. Click on the service that was created
2. Go to **Settings** tab
3. Set **Root Directory** to: `/` (leave blank/default — the backend is at the repo root)
4. Set **Start Command** to:
   ```
   python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```
5. Set **Build Command** to:
   ```
   pip install -r requirements.txt
   ```

### 1.4 — Add a PostgreSQL database
1. In your Railway project, click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway will create the database and auto-inject a `DATABASE_URL` environment variable into your service
3. **Important:** Your code currently uses SQLite. The `DATABASE_URL` from Railway will point to PostgreSQL, which SQLAlchemy supports automatically if `psycopg2-binary` is installed (it's already in requirements.txt)

### 1.5 — Set environment variables
1. Click your service → **Variables** tab
2. Add these variables:

| Variable | Value | Required? |
|----------|-------|-----------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Yes |
| `POC_MODE` | `true` | Yes (until you get real API keys on April 14th) |
| `AGENT_API_KEY` | Any random string (protects `/agents/trigger`) | Recommended |
| `MEDIA_DIR` | `./media` | Optional (default) |

**After April 14th IT meeting, add:**
| Variable | Value |
|----------|-------|
| `META_ACCESS_TOKEN` | From Daniel's Meta Business account |
| `META_IG_ACCOUNT_ID` | Instagram Business account ID |
| `META_PAGE_ID` | Facebook Page ID |
| `TIKTOK_ACCESS_TOKEN` | TikTok OAuth token |
| `WP_URL` | Daniel's WordPress site URL |
| `WP_USERNAME` | WordPress admin username |
| `WP_APP_PASSWORD` | WordPress application password |
| `HIGGSFIELD_API_KEY` | Higgsfield API key |

### 1.6 — Deploy
1. Click **"Deploy"** — Railway will build and start the service
2. Once deployed, go to **Settings** → **Networking** → **Generate Domain**
3. Railway will give you a public URL like: `https://daniels-marketing-production.up.railway.app`
4. **Copy this URL** — you'll need it for the frontend

### 1.7 — Verify
Open your browser and visit:
```
https://YOUR-RAILWAY-URL/health
```
You should see: `{"status": "ok", "service": "daniels-donuts-marketing"}`

---

## Step 2: Deploy the Frontend on Vercel

Vercel builds and hosts the React dashboard as a static site.

### 2.1 — Create a Vercel account
1. Go to [vercel.com](https://vercel.com)
2. Sign in with your **GitHub account** (schnitz02)

### 2.2 — Import the project
1. Click **"Add New..."** → **"Project"**
2. Find and select **schnitz02/daniels-marketing**
3. Click **"Import"**

### 2.3 — Configure the build
On the configuration screen, set these fields:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `dashboard` |
| **Build Command** | `npm run build` (auto-detected) |
| **Output Directory** | `dist` (auto-detected) |

### 2.4 — Set the environment variable
In the **Environment Variables** section, add:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://YOUR-RAILWAY-URL` (the URL from Step 1.6) |

**Example:** `VITE_API_URL=https://daniels-marketing-production.up.railway.app`

### 2.5 — Deploy
1. Click **"Deploy"**
2. Vercel will build the React app and give you a URL like: `https://daniels-marketing.vercel.app`
3. **Copy this URL** — you need it for the next step

### 2.6 — Set up rewrites (API proxy)
Since the frontend calls `/api/*` and the backend is on a different domain, you need a rewrite rule.

Create a file `dashboard/vercel.json`:
```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://YOUR-RAILWAY-URL/api/:path*" },
    { "source": "/media/:path*", "destination": "https://YOUR-RAILWAY-URL/media/:path*" }
  ]
}
```

Replace `YOUR-RAILWAY-URL` with your actual Railway URL.

Commit and push this file — Vercel will auto-redeploy.

---

## Step 3: Connect the Two Services

### 3.1 — Update CORS on Railway
Go back to your Railway service → **Variables** → add:

| Variable | Value |
|----------|-------|
| `ALLOWED_ORIGINS` | `https://daniels-marketing.vercel.app` (your Vercel URL) |

**Note:** The code currently has a hardcoded CORS list in `src/main.py`. Before deploying, you should update it to read from this environment variable. See the "Code Changes Required" section below.

### 3.2 — Verify end-to-end
1. Open your Vercel URL in a browser
2. The dashboard should load and display data from the Railway backend
3. Check the browser console (F12) for any CORS or network errors

---

## Code Changes Required Before Deploying

Two small changes are needed to make the app production-ready:

### Change 1: Frontend API base URL (`dashboard/src/api.js`)

**Current:**
```js
const api = axios.create({
  baseURL: "/api",
})
```

**Change to:**
```js
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL}/api`
    : "/api",
})
```

This uses the Railway URL in production, and falls back to `/api` in local dev (where Vite proxies it).

**Note:** If you use the `vercel.json` rewrite approach from Step 2.6, you do NOT need this change — the rewrites handle the proxy. Choose one approach or the other:
- **Option A (simpler):** Use `vercel.json` rewrites — no code change needed
- **Option B:** Use `VITE_API_URL` env var — no `vercel.json` needed

### Change 2: Dynamic CORS origins (`src/main.py`)

**Current:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:3000", "http://127.0.0.1:3000",
    ],
    ...
)
```

**Change to:**
```python
import os

origins = [
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:3000", "http://127.0.0.1:3000",
]
extra = os.getenv("ALLOWED_ORIGINS", "")
if extra:
    origins.extend([o.strip() for o in extra.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    ...
)
```

This lets you add production domains via the `ALLOWED_ORIGINS` env var on Railway without changing code.

---

## Custom Domain (Optional)

### Vercel (frontend)
1. Go to your Vercel project → **Settings** → **Domains**
2. Add your custom domain (e.g. `marketing.danielsdonuts.com.au`)
3. Follow DNS instructions (add CNAME record pointing to `cname.vercel-dns.com`)

### Railway (backend)
1. Go to your Railway service → **Settings** → **Networking** → **Custom Domain**
2. Add a subdomain (e.g. `api.danielsdonuts.com.au`)
3. Follow DNS instructions

---

## Checklist

- [ ] Railway account created and linked to GitHub
- [ ] PostgreSQL database provisioned on Railway
- [ ] Backend environment variables set
- [ ] Railway deploy successful — `/health` returns OK
- [ ] Vercel account created and linked to GitHub
- [ ] Root directory set to `dashboard`
- [ ] `vercel.json` rewrites added and pushed
- [ ] Vercel deploy successful — dashboard loads
- [ ] CORS updated to allow Vercel domain
- [ ] End-to-end: dashboard talks to backend without errors

---

## Costs

| Service | Plan | Cost |
|---------|------|------|
| Vercel | Hobby (free) | $0/month |
| Railway | Hobby | ~$5/month |
| Railway PostgreSQL | Included | usage-based (~$1-3/month for this app) |
| **Total** | | **~$5-8/month** |
