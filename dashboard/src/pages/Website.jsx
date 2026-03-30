import { useEffect, useState } from "react"
import api from "../api"

const TYPE_COLORS = {
  banner: "bg-orange-900 text-orange-300",
  blog_post: "bg-blue-900 text-blue-300",
  campaign_page: "bg-purple-900 text-purple-300",
  product: "bg-green-900 text-green-300",
}

export default function Website() {
  const [changes, setChanges] = useState([])
  const [approving, setApproving] = useState(null)

  const load = () => api.get("/approvals/website").then(r => setChanges(r.data)).catch(() => {})

  useEffect(() => { load() }, [])

  const approve = async (id) => {
    setApproving(id)
    await api.post(`/approvals/website/${id}/approve`).catch(() => {})
    await load()
    setApproving(null)
  }
  const reject = async (id) => {
    await api.post(`/approvals/website/${id}/reject`, { notes: "" }).catch(() => {})
    await load()
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Website Changes</h1>
      <p className="text-gray-500 text-sm mb-6">Pending updates to danielsdonuts.com.au</p>
      {changes.length === 0 ? (
        <p className="text-gray-600 text-sm">No pending website changes.</p>
      ) : changes.map(c => (
        <div key={c.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-3">
          <div className="flex items-start justify-between gap-4 mb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs px-2 py-0.5 rounded-full ${TYPE_COLORS[c.change_type] ?? "bg-gray-800 text-gray-400"}`}>
                  {c.change_type}
                </span>
              </div>
              <p className="font-semibold text-white">{c.description}</p>
            </div>
          </div>
          <pre className="bg-gray-950 rounded-lg p-3 text-xs text-gray-400 mb-4 overflow-x-auto">{JSON.stringify(c.payload, null, 2)}</pre>
          <div className="flex gap-2">
            <button onClick={() => approve(c.id)} disabled={approving === c.id}
              className="bg-green-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-600 disabled:opacity-50 transition-colors">
              {approving === c.id ? "Applying..." : "✓ Approve"}
            </button>
            <button onClick={() => reject(c.id)}
              className="bg-gray-800 text-red-400 border border-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-700 transition-colors">
              ✗ Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
