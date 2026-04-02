import { useEffect, useState } from "react"
import api from "../api"
import { formatDateTime } from "../utils/date"

const STATUS_BADGE = {
  completed: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-600",
  running: "bg-[#F7CA5E]/30 text-[#00395D] animate-pulse",
  never_run: "bg-gray-100 text-gray-500",
}

export default function Agents() {
  const [status, setStatus] = useState({})
  const [triggering, setTriggering] = useState(null)
  const [lastResult, setLastResult] = useState(null)
  const [error, setError] = useState(null)

  const load = () => api.get("/agents/status").then(r => setStatus(r.data)).catch(() => setError(true))

  useEffect(() => { load(); const t = setInterval(load, 10000); return () => clearInterval(t) }, [])

  const trigger = async (name) => {
    setTriggering(name)
    setLastResult(null)
    try {
      const res = await api.post(`/agents/trigger/${name}`)
      const summary = Object.entries(res.data || {}).map(([k, v]) => `${k}: ${v}`).join(", ")
      setLastResult({ name, ok: true, msg: summary || "completed" })
    } catch (e) {
      const detail = e?.response?.data?.detail || e?.message || "unknown error"
      setLastResult({ name, ok: false, msg: detail })
    }
    await load()
    setTriggering(null)
  }

  if (error) return <div className="text-red-600 text-sm">Could not load agents. Is the backend running?</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2 text-[#00395D]">Agents</h1>
      <p className="text-[#6B8A9A] text-sm mb-6">Agents run automatically on schedule. Use "Run Now" to trigger manually.</p>

      {lastResult && (
        <div className={`mb-5 px-4 py-3 rounded-xl text-sm border ${lastResult.ok ? "bg-green-50 border-green-200 text-green-700" : "bg-red-50 border-red-200 text-red-600"}`}>
          <span className="font-semibold capitalize">{lastResult.name.replace(/_/g, " ")}</span>
          {" — "}{lastResult.msg}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        {Object.entries(status).map(([name, info]) => (
          <div key={name} className="bg-white border border-[#E8E4D9] rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-1">
              <h3 className="font-semibold capitalize text-sm text-[#00395D]">{name.replace(/_/g, " ")}</h3>
              <span className={`text-xs font-mono px-2 py-0.5 rounded-full ${STATUS_BADGE[info.status] ?? "bg-gray-100 text-gray-500"}`}>
                {info.status}
              </span>
            </div>
            <p className="text-[#6B8A9A] text-xs mb-3">
              {info.last_run ? `Last run: ${formatDateTime(info.last_run)}` : "Never run"}
            </p>
            <button
              onClick={() => trigger(name)}
              disabled={triggering !== null}
              className="bg-white border border-[#E8E4D9] text-[#00395D] text-xs px-3 py-1.5 rounded-lg hover:bg-[#F5F4EC] disabled:opacity-50 transition-colors"
            >
              {triggering === name ? "Running..." : "▶ Run Now"}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
