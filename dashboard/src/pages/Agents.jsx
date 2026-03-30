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
  const [error, setError] = useState(null)

  const load = () => api.get("/agents/status").then(r => setStatus(r.data)).catch(() => setError(true))

  useEffect(() => { load(); const t = setInterval(load, 10000); return () => clearInterval(t) }, [])

  const trigger = async (name) => {
    setTriggering(name)
    try { await api.post(`/agents/trigger/${name}`) } catch {}
    await load()
    setTriggering(null)
  }

  if (error) return <div className="text-red-400 text-sm">Could not load agents. Is the backend running?</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Agents</h1>
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
              disabled={triggering === name}
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
