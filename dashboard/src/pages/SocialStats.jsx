import { useEffect, useState, useCallback } from "react"
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts"
import api from "../api"
import { formatDateTime, formatTime, formatDateShort, formatMonthYear } from "../utils/date"

const PLATFORMS = ["instagram", "tiktok", "facebook"]

const PLATFORM_META = {
  instagram: { label: "Instagram", color: "#E1306C", icon: "📸" },
  tiktok:    { label: "TikTok",    color: "#69C9D0", icon: "🎵" },
  facebook:  { label: "Facebook",  color: "#1877F2", icon: "👍" },
}

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-xl p-4 flex flex-col gap-1 border border-[#E8E4D9]">
      <span className="text-[#6B8A9A] text-xs uppercase tracking-wide">{label}</span>
      <span className="text-[#00395D] text-2xl font-bold">{value ?? "—"}</span>
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
  const dates = allScrapedAts.map(s => new Date(s))
  const minDate = new Date(Math.min(...dates))
  const maxDate = new Date(Math.max(...dates))
  const rangeMs = maxDate - minDate
  const ONE_DAY = 86_400_000

  if (rangeMs < ONE_DAY) return formatTime(scraped_at)
  if (rangeMs < ONE_DAY * 60) return formatDateShort(scraped_at)
  return formatMonthYear(scraped_at)
}

function TrendsChart({ history, color }) {
  if (!history || history.length < 2)
    return <p className="text-[#6B8A9A] text-sm">Not enough data yet. Run the Social Stats agent a few times to build history.</p>

  const allScrapedAts = history.map(s => s.scraped_at)
  const data = history.map(s => ({
    date: smartDateLabel(s.scraped_at, allScrapedAts),
    Followers: s.followers,
  }))

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E8E4D9" />
        <XAxis dataKey="date" stroke="#6B7280" tick={{ fontSize: 11 }} />
        <YAxis stroke="#6B7280" tick={{ fontSize: 11 }} tickFormatter={formatNum} />
        <Tooltip
          contentStyle={{ backgroundColor: "#00395D", border: "1px solid #1a5276", borderRadius: 8 }}
          labelStyle={{ color: "#F5F4EC" }}
          itemStyle={{ color: "white" }}
          formatter={v => [formatNum(v), "Followers"]}
        />
        <Line type="monotone" dataKey="Followers" stroke={color} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}

function PostsGrid({ posts, followers }) {
  if (!posts || posts.length === 0)
    return <p className="text-[#6B8A9A] text-sm">No posts cached yet.</p>

  return (
    <div className="grid grid-cols-3 gap-3">
      {posts.map(p => (
        <div key={p.post_id} className="bg-white rounded-xl p-3 border border-[#E8E4D9]">
          {p.thumbnail_url
            ? <img src={p.thumbnail_url} alt="" className="w-full h-28 object-cover rounded-lg mb-2" />
            : <div className="w-full h-28 bg-[#F5F4EC] rounded-lg mb-2 flex items-center justify-center text-[#6B8A9A] text-xs">No preview</div>
          }
          <p className="text-[#4A5568] text-xs line-clamp-2 mb-2">{p.caption || "—"}</p>
          <div className="flex justify-between text-xs text-[#6B8A9A]">
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
  const [analysis, setAnalysis] = useState(null)
  const [generating, setGenerating] = useState(false)

  const loadAnalysis = useCallback(() =>
    api.get(`/social-stats/analysis/${platform}`)
      .then(r => setAnalysis(r.data))
      .catch(() => {}),
  [platform])

  const generateAnalysis = async () => {
    setGenerating(true)
    try {
      const r = await api.post(`/social-stats/analysis/${platform}`)
      setAnalysis(r.data)
    } catch {}
    setGenerating(false)
  }

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
    loadAnalysis()
  }, [platform, loadAnalysis])

  // Re-fetch when parent signals a completed scrape
  useEffect(() => { if (reloadSignal > 0) load() }, [reloadSignal, load])

  useEffect(() => { load() }, [load])

  if (loading) return <div className="text-[#6B8A9A] text-sm py-8 text-center">Loading…</div>

  if (fetchError) return (
    <div className="text-center py-16">
      <p className="text-red-400 text-sm">Could not load {meta.label} data. Is the backend running?</p>
    </div>
  )

  if (!latest) return (
    <div className="text-center py-16">
      <p className="text-[#4A5568] text-sm mb-4">No data yet for {meta.label}.</p>
      <p className="text-[#6B8A9A] text-xs">Go to Agents and run "Social Stats" to scrape the profile.</p>
    </div>
  )

  return (
    <div className="space-y-8">
      {/* Surface stats */}
      <section>
        <h3 className="text-sm font-semibold text-[#6B8A9A] uppercase tracking-wide mb-3">Profile</h3>
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
        {latest.bio && <p className="text-[#4A5568] text-sm">{latest.bio}</p>}
        <p className="text-[#6B8A9A] text-xs mt-1">
          Last scraped: {latest.scraped_at ? formatDateTime(latest.scraped_at) : "unknown"}
        </p>
      </section>

      {/* AI Analysis section */}
      <div className="bg-white border border-[#E8E4D9] rounded-xl p-5 mb-6 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-[#00395D]">AI Analysis</h3>
          <button
            onClick={generateAnalysis}
            disabled={generating}
            className="text-xs bg-[#04D3C5] hover:bg-[#03bdb0] disabled:opacity-50 text-white px-3 py-1.5 rounded-lg transition-colors"
          >
            {generating ? "Generating..." : "✦ Generate Analysis"}
          </button>
        </div>

        {analysis ? (
          <div className="space-y-4">
            <p className="text-[#4A5568] text-sm leading-relaxed">{analysis.summary}</p>
            <div>
              <p className="text-xs text-[#6B8A9A] font-semibold uppercase tracking-wide mb-1">Benchmarks</p>
              <p className="text-[#4A5568] text-sm leading-relaxed">{analysis.benchmarks}</p>
            </div>
            <div>
              <p className="text-xs text-[#6B8A9A] font-semibold uppercase tracking-wide mb-2">Recommendations</p>
              <ol className="space-y-1">
                {(analysis.recommendations || []).map((r, i) => (
                  <li key={i} className="text-sm text-[#00395D] flex gap-2">
                    <span className="text-[#04D3C5] font-bold">{i + 1}.</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ol>
            </div>
            {analysis.generated_at && (
              <p className="text-xs text-[#6B8A9A]">Generated {formatDateTime(analysis.generated_at)}</p>
            )}
          </div>
        ) : (
          <p className="text-[#6B8A9A] text-sm">No analysis yet. Click "Generate Analysis" to get AI insights.</p>
        )}
      </div>

      {/* Trends */}
      <section>
        <h3 className="text-sm font-semibold text-[#6B8A9A] uppercase tracking-wide mb-3">Follower Trend</h3>
        <div className="bg-white border border-[#E8E4D9] rounded-xl p-4 shadow-sm">
          <TrendsChart history={history} color={meta.color} />
        </div>
      </section>

      {/* Posts */}
      <section>
        <h3 className="text-sm font-semibold text-[#6B8A9A] uppercase tracking-wide mb-3">Recent Posts</h3>
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
        <h1 className="text-2xl font-bold text-[#00395D]">Social Stats</h1>
        <button
          onClick={refresh}
          disabled={refreshing}
          className="bg-white border border-[#E8E4D9] text-[#00395D] text-sm px-4 py-2 rounded-lg hover:bg-[#F5F4EC] disabled:opacity-50 transition-colors"
        >
          {refreshing ? "Scraping…" : "🔄 Refresh Now"}
        </button>
      </div>

      {refreshMsg && (
        <div className={`mb-5 px-4 py-3 rounded-xl text-sm border ${refreshMsg.ok ? "bg-green-50 border-green-200 text-green-700" : "bg-red-50 border-red-200 text-red-600"}`}>
          {refreshMsg.text}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-white border border-[#E8E4D9] p-1 rounded-xl w-fit shadow-sm">
        {PLATFORMS.map(p => (
          <button
            key={p}
            onClick={() => setActive(p)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${active === p ? "bg-[#04D3C5] text-white" : "text-[#6B8A9A] hover:text-[#00395D]"}`}
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
