import { useEffect, useState } from "react"
import api from "../api"

const STATUS_BADGE = {
  completed: "bg-green-900 text-green-300",
  failed: "bg-red-900 text-red-300",
  running: "bg-yellow-900 text-yellow-300 animate-pulse",
  never_run: "bg-gray-800 text-gray-500",
}

export default function Agents() {
  const [status, setStatus] = useState({})
  const [triggering, setTriggering] = useState(null)
  const [lastResult, setLastResult] = useState(null) // { name, ok, msg }
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

  if (error) return <div className="text-red-400 text-sm">Could not load agents. Is the backend running?</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Agents</h1>
      <p className="text-gray-500 text-sm mb-6">Agents run automatically on schedule. Use "Run Now" to trigger manually.</p>

      {lastResult && (
        <div className={`mb-5 px-4 py-3 rounded-xl text-sm border ${lastResult.ok ? "bg-green-900/20 border-green-800 text-green-300" : "bg-red-900/20 border-red-800 text-red-300"}`}>
          <span className="font-semibold capitalize">{lastResult.name.replace(/_/g, " ")}</span>
          {" — "}{lastResult.msg}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        {Object.entries(status).map(([name, info]) => (
          <div key={name} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-1">
              <h3 className="font-semibold capitalize text-sm">{name.replace(/_/g, " ")}</h3>
              <span className={`text-xs font-mono px-2 py-0.5 rounded-full ${STATUS_BADGE[info.status] ?? "bg-gray-800 text-gray-400"}`}>
                {info.status}
              </span>
            </div>
            <p className="text-gray-600 text-xs mb-3">
              {info.last_run ? `Last run: ${new Date(info.last_run).toLocaleString()}` : "Never run"}
            </p>
            <button
              onClick={() => trigger(name)}
              disabled={triggering !== null}
              className="bg-gray-800 border border-gray-700 text-white text-xs px-3 py-1.5 rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors"
            >
              {triggering === name ? "Running..." : "▶ Run Now"}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
