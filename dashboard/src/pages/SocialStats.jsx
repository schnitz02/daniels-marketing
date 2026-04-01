import { useEffect, useState, useCallback } from "react"
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts"
import api from "../api"

const PLATFORMS = ["instagram", "tiktok", "facebook"]

const PLATFORM_META = {
  instagram: { label: "Instagram", color: "#E1306C", icon: "📸" },
  tiktok:    { label: "TikTok",    color: "#69C9D0", icon: "🎵" },
  facebook:  { label: "Facebook",  color: "#1877F2", icon: "👍" },
}

function StatCard({ label, value }) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 flex flex-col gap-1">
      <span className="text-gray-500 text-xs uppercase tracking-wide">{label}</span>
      <span className="text-white text-2xl font-bold">{value ?? "—"}</span>
    </div>
  )
}

function formatNum(n) {
  if (n == null) return "—"
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M"
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K"
  return String(n)
}

function engagementRate(likes, comments, followers) {
  if (!followers) return "—"
  return (((likes + comments) / followers) * 100).toFixed(2) + "%"
}

function smartDateLabel(scraped_at, allScrapedAts) {
  const d = new Date(scraped_at)
  const dates = allScrapedAts.map(s => new Date(s))
  const minDate = new Date(Math.min(...dates))
  const maxDate = new Date(Math.max(...dates))
  const rangeMs = maxDate - minDate
  const ONE_DAY = 86_400_000

  if (rangeMs < ONE_DAY) {
    // All within same day — show time only
    return d.toLocaleTimeString("en-AU", { hour: "2-digit", minute: "2-digit" })
  }
  if (rangeMs < ONE_DAY * 60) {
    // Within ~2 months — show "1 Apr"
    return d.toLocaleDateString("en-AU", { day: "numeric", month: "short" })
  }
  // Longer range — show "Jan 25"
  return d.toLocaleDateString("en-AU", { month: "short", year: "2-digit" })
}

function TrendsChart({ history, color }) {
  if (!history || history.length < 2)
    return <p className="text-gray-600 text-sm">Not enough data yet. Run the Social Stats agent a few times to build history.</p>

  const allScrapedAts = history.map(s => s.scraped_at)
  const data = history.map(s => ({
    date: smartDateLabel(s.scraped_at, allScrapedAts),
    Followers: s.followers,
  }))

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="date" stroke="#6B7280" tick={{ fontSize: 11 }} />
        <YAxis stroke="#6B7280" tick={{ fontSize: 11 }} tickFormatter={formatNum} />
        <Tooltip
          contentStyle={{ backgroundColor: "#1F2937", border: "1px solid #374151", borderRadius: 8 }}
          labelStyle={{ color: "#9CA3AF" }}
          itemStyle={{ color: "#F9FAFB" }}
          formatter={v => [formatNum(v), "Followers"]}
        />
        <Line type="monotone" dataKey="Followers" stroke={color} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}

function PostsGrid({ posts, followers }) {
  if (!posts || posts.length === 0)
    return <p className="text-gray-600 text-sm">No posts cached yet.</p>

  return (
    <div className="grid grid-cols-3 gap-3">
      {posts.map(p => (
        <div key={p.post_id} className="bg-gray-800 rounded-xl p-3">
          {p.thumbnail_url
            ? <img src={p.thumbnail_url} alt="" className="w-full h-28 object-cover rounded-lg mb-2" />
            : <div className="w-full h-28 bg-gray-700 rounded-lg mb-2 flex items-center justify-center text-gray-600 text-xs">No preview</div>
          }
          <p className="text-gray-300 text-xs line-clamp-2 mb-2">{p.caption || "—"}</p>
          <div className="flex justify-between text-xs text-gray-500">
            <span>❤️ {formatNum(p.likes)}</span>
            <span>💬 {formatNum(p.comments)}</span>
            <span>{engagementRate(p.likes, p.comments, followers)}</span>
          </div>
        </div>
      ))}
    </div>
  )
}

function PlatformTab({ platform, reloadSignal }) {
  const meta = PLATFORM_META[platform]
  const [latest, setLatest] = useState(null)
  const [history, setHistory] = useState([])
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setFetchError(false)
    try {
      const [latestAll, hist, postsData] = await Promise.all([
        api.get("/social-stats/latest"),
        api.get(`/social-stats/history/${platform}`),
        api.get(`/social-stats/posts/${platform}?limit=9`),
      ])
      setLatest(latestAll.data.find(x => x.platform === platform) ?? null)
      setHistory(hist.data)
      setPosts(postsData.data)
    } catch (err) {
      console.error("SocialStats fetch failed", err)
      setFetchError(true)
    }
    setLoading(false)
  }, [platform])

  // Re-fetch when parent signals a completed scrape
  useEffect(() => { if (reloadSignal > 0) load() }, [reloadSignal, load])

  useEffect(() => { load() }, [load])

  if (loading) return <div className="text-gray-500 text-sm py-8 text-center">Loading…</div>

  if (fetchError) return (
    <div className="text-center py-16">
      <p className="text-red-400 text-sm">Could not load {meta.label} data. Is the backend running?</p>
    </div>
  )

  if (!latest) return (
    <div className="text-center py-16">
      <p className="text-gray-500 text-sm mb-4">No data yet for {meta.label}.</p>
      <p className="text-gray-600 text-xs">Go to Agents and run "Social Stats" to scrape the profile.</p>
    </div>
  )

  return (
    <div className="space-y-8">
      {/* Surface stats */}
      <section>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">Profile</h3>
        <div className="grid grid-cols-4 gap-3 mb-3">
          <StatCard label="Followers" value={formatNum(latest.followers)} />
          <StatCard label="Following" value={formatNum(latest.following)} />
          <StatCard label="Posts" value={formatNum(latest.posts_count)} />
          <StatCard label="Eng. Rate" value={posts.length ? engagementRate(
            posts.reduce((s, p) => s + p.likes, 0) / posts.length,
            posts.reduce((s, p) => s + p.comments, 0) / posts.length,
            latest.followers
          ) : "—"} />
        </div>
        {latest.bio && <p className="text-gray-400 text-sm">{latest.bio}</p>}
        <p className="text-gray-700 text-xs mt-1">
          Last scraped: {latest.scraped_at ? new Date(latest.scraped_at).toLocaleString("en-AU") : "unknown"}
        </p>
      </section>

      {/* Trends */}
      <section>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">Follower Trend</h3>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <TrendsChart history={history} color={meta.color} />
        </div>
      </section>

      {/* Posts */}
      <section>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">Recent Posts</h3>
        <PostsGrid posts={posts} followers={latest.followers} />
      </section>
    </div>
  )
}

export default function SocialStats() {
  const [active, setActive] = useState("instagram")
  const [refreshing, setRefreshing] = useState(false)
  const [refreshMsg, setRefreshMsg] = useState(null)
  const [reloadSignal, setReloadSignal] = useState(0)

  const refresh = async () => {
    setRefreshing(true)
    setRefreshMsg(null)
    try {
      await api.post("/agents/trigger/social_stats")
      setRefreshMsg({ ok: true, text: "Scrape complete — data updated below." })
      setReloadSignal(s => s + 1)  // tell active PlatformTab to re-fetch
    } catch {
      setRefreshMsg({ ok: false, text: "Scrape failed. Check that the backend is running." })
    }
    setRefreshing(false)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Social Stats</h1>
        <button
          onClick={refresh}
          disabled={refreshing}
          className="bg-gray-800 border border-gray-700 text-white text-sm px-4 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors"
        >
          {refreshing ? "Scraping…" : "🔄 Refresh Now"}
        </button>
      </div>

      {refreshMsg && (
        <div className={`mb-5 px-4 py-3 rounded-xl text-sm border ${refreshMsg.ok ? "bg-green-900/20 border-green-800 text-green-300" : "bg-red-900/20 border-red-800 text-red-300"}`}>
          {refreshMsg.text}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-900 p-1 rounded-xl w-fit">
        {PLATFORMS.map(p => (
          <button
            key={p}
            onClick={() => setActive(p)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${active === p ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >
            {PLATFORM_META[p].icon} {PLATFORM_META[p].label}
          </button>
        ))}
      </div>

      {/* key forces full remount on tab switch, resetting all state */}
      <PlatformTab key={active} platform={active} reloadSignal={reloadSignal} />
    </div>
  )
}
