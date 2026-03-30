import { useEffect, useState } from "react"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts"
import api from "../api"

export default function Analytics() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get("/dashboard/analytics").then(r => setData(r.data)).catch(() => {})
  }, [])

  if (!data) return <div className="text-gray-500 animate-pulse">Loading analytics...</div>

  const chartData = Object.entries(data.by_platform || {}).map(([platform, metrics]) => ({
    platform: platform.charAt(0).toUpperCase() + platform.slice(1),
    Reach: metrics.reach,
    Engagement: metrics.engagement,
    Posts: metrics.count,
  }))

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Analytics</h1>
      <div className="grid grid-cols-1 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-sm text-gray-400 mb-4">Reach by Platform</h2>
          {chartData.length === 0 ? (
            <p className="text-gray-600 text-sm">No published posts yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="platform" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }} />
                <Bar dataKey="Reach" fill="#FF6B35" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Engagement" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="text-gray-500 text-sm">Total published posts: <span className="text-white font-semibold">{data.total_posts}</span></div>
      </div>
    </div>
  )
}
