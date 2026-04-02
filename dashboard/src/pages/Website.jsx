import { useEffect, useState } from "react"
import api from "../api"

const TYPE_COLORS = {
  banner: "bg-orange-100 text-orange-700",
  blog_post: "bg-blue-100 text-blue-700",
  campaign_page: "bg-purple-100 text-purple-700",
  product: "bg-green-100 text-green-700",
}

export default function Website() {
  const [changes, setChanges] = useState([])
  const [approving, setApproving] = useState(null)
  const [error, setError] = useState(null)

  const load = () => api.get("/approvals/website").then(r => setChanges(r.data)).catch(() => setError(true))

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

  if (error) return <div className="text-red-600 text-sm">Could not load website changes. Is the backend running?</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2 text-[#00395D]">Website Changes</h1>
      <p className="text-[#6B8A9A] text-sm mb-6">Pending updates to danielsdonuts.com.au</p>
      {changes.length === 0 ? (
        <p className="text-[#6B8A9A] text-sm">No pending website changes.</p>
      ) : changes.map(c => (
        <div key={c.id} className="bg-white border border-[#E8E4D9] rounded-xl p-5 mb-3 shadow-sm">
          <div className="flex items-start justify-between gap-4 mb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TYPE_COLORS[c.change_type] ?? "bg-gray-100 text-gray-600"}`}>
                  {c.change_type}
                </span>
              </div>
              <p className="font-semibold text-[#00395D]">{c.description}</p>
            </div>
          </div>
          <pre className="bg-[#F5F4EC] rounded-lg p-3 text-xs text-[#4A5568] mb-4 overflow-x-auto border border-[#E8E4D9]">{JSON.stringify(c.payload, null, 2)}</pre>
          <div className="flex gap-2">
            <button onClick={() => approve(c.id)} disabled={approving === c.id}
              className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-500 disabled:opacity-50 transition-colors">
              {approving === c.id ? "Applying..." : "✓ Approve"}
            </button>
            <button onClick={() => reject(c.id)}
              className="bg-white text-red-500 border border-red-200 px-4 py-2 rounded-lg text-sm hover:bg-red-50 transition-colors">
              ✗ Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
