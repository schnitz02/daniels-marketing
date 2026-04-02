import { useEffect, useState } from "react"
import api from "../api"

const CARDS = [
  { key: "pending_ideas", label: "Pending Ideas", color: "text-[#04D3C5]", icon: "💡" },
  { key: "pending_content", label: "Pending Content", color: "text-blue-500", icon: "🎨" },
  { key: "pending_website_changes", label: "Website Changes", color: "text-purple-500", icon: "🌐" },
  { key: "published_posts", label: "Published Posts", color: "text-green-600", icon: "📤" },
  { key: "total_reach", label: "Total Reach", color: "text-[#04D3C5]", icon: "👁️" },
]

export default function Overview() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = () => api.get("/dashboard/overview")
      .then(r => setData(r.data))
      .catch(() => setError("Could not reach the backend. Make sure it's running on port 8000."))
    load()
    const t = setInterval(load, 8000)
    return () => clearInterval(t)
  }, [])

  if (error) return (
    <div className="text-red-600 bg-red-50 border border-red-200 rounded-xl p-6">{error}</div>
  )
  if (!data) return (
    <div className="text-[#6B8A9A] animate-pulse">Loading overview...</div>
  )

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2 text-[#00395D]">Overview</h1>
      <p className="text-[#6B8A9A] text-sm mb-6">Daniel's Donuts Marketing Agent</p>
      <div className="grid grid-cols-3 gap-4">
        {CARDS.map(({ key, label, color, icon }) => (
          <div key={key} className="bg-white border border-[#E8E4D9] rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-2 text-[#6B8A9A] text-sm mb-2">
              <span>{icon}</span>
              <span>{label}</span>
            </div>
            <div className={`text-3xl font-bold ${color}`}>
              {typeof data[key] === "number" ? data[key].toLocaleString() : data[key] ?? 0}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
