import { useEffect, useState } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import api from "../api"

const SETUP_GUIDE = `To enable GA4 analytics:
1. Go to console.cloud.google.com → Create a service account
2. Grant it "Viewer" access to your GA4 property
3. Download the JSON key file
4. Add to .env:
   GOOGLE_ANALYTICS_PROPERTY_ID=your_property_id
   GOOGLE_SERVICE_ACCOUNT_JSON=./credentials/ga4-service-account.json
5. Restart the backend`

export default function Analytics() {
  const [tab, setTab] = useState("seo")
  const [connected, setConnected] = useState(null)
  const [seo, setSeo] = useState(null)
  const [sem, setSem] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get("/ga4/status").then(r => {
      setConnected(r.data.connected)
      if (r.data.connected) {
        Promise.all([
          api.get("/ga4/seo").then(r => setSeo(r.data)),
          api.get("/ga4/sem").then(r => setSem(r.data)),
        ]).finally(() => setLoading(false))
      } else {
        setLoading(false)
      }
    }).catch(() => { setConnected(false); setLoading(false) })
  }, [])

  if (loading) return <div className="text-gray-500 text-sm">Loading analytics...</div>

  if (!connected) return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Analytics</h1>
      <div className="bg-gray-900 border border-yellow-800 rounded-xl p-6">
        <h2 className="text-yellow-400 font-semibold mb-2">⚡ GA4 Not Connected</h2>
        <p className="text-gray-400 text-sm mb-4">Connect Google Analytics 4 to track SEO and SEM performance.</p>
        <pre className="text-xs text-gray-500 bg-gray-800 rounded-lg p-4 whitespace-pre-wrap">{SETUP_GUIDE}</pre>
      </div>
    </div>
  )

  const data = tab === "seo" ? seo : sem

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Analytics</h1>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-900 border border-gray-800 rounded-xl p-1 w-fit">
        {["seo", "sem"].map(t => (
          <button key={t}
            onClick={() => setTab(t)}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors uppercase tracking-wide ${tab === t ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >
            {t}
          </button>
        ))}
      </div>

      {!data ? (
        <p className="text-gray-600 text-sm">No {tab.toUpperCase()} data available.</p>
      ) : (
        <div className="space-y-6">
          {/* Summary cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(data.summary || {}).map(([key, val]) => (
              <div key={key} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
                  {key.replace(/_/g, " ")}
                </p>
                <p className="text-2xl font-bold text-white">
                  {typeof val === "number" && key.includes("rate") ? `${val}%` : val?.toLocaleString()}
                </p>
              </div>
            ))}
          </div>

          {/* Trend chart */}
          {data.trend && data.trend.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h3 className="text-sm font-semibold mb-4">Sessions — Last 30 Days</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={data.trend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" tick={{ fill: "#6B7280", fontSize: 11 }}
                    tickFormatter={d => d ? `${d.slice(4,6)}/${d.slice(6,8)}` : ""} />
                  <YAxis tick={{ fill: "#6B7280", fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: 8 }} />
                  <Line type="monotone" dataKey="sessions" stroke="#EAB308" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Top pages (SEO only) */}
          {tab === "seo" && data.top_pages && data.top_pages.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h3 className="text-sm font-semibold mb-4">Top Organic Landing Pages</h3>
              <div className="space-y-2">
                {data.top_pages.map((p, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
                    <span className="text-gray-300 text-sm font-mono truncate max-w-xs">{p.page}</span>
                    <div className="flex gap-4 text-xs text-gray-500 shrink-0 ml-4">
                      <span>{p.sessions?.toLocaleString()} sessions</span>
                      <span>{p.engagement_rate}% engaged</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
