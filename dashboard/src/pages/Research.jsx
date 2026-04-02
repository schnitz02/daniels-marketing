import { useEffect, useState } from "react"
import api from "../api"

const SOURCE_BADGE = {
  instagram: "bg-pink-900 text-pink-300",
  facebook: "bg-blue-900 text-blue-300",
  tiktok: "bg-purple-900 text-purple-300",
  web: "bg-gray-700 text-gray-300",
}

export default function Research() {
  const [items, setItems] = useState([])
  const [competitors, setCompetitors] = useState([])
  const [filter, setFilter] = useState("")
  const [expanded, setExpanded] = useState({})
  const [triggering, setTriggering] = useState(false)
  const [error, setError] = useState(null)

  const load = () => {
    const url = filter ? `/research/items?competitor=${encodeURIComponent(filter)}` : "/research/items"
    return Promise.all([
      api.get(url).then(r => setItems(r.data)),
      api.get("/research/competitors").then(r => setCompetitors(r.data)),
    ]).catch(() => setError("Could not load research data."))
  }

  useEffect(() => { load() }, [filter])

  const runResearch = async () => {
    setTriggering(true)
    try { await api.post("/agents/trigger/research") } catch {}
    await load()
    setTriggering(false)
  }

  const toggle = id => setExpanded(e => ({ ...e, [id]: !e[id] }))

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Competitor Research</h1>
          <p className="text-gray-500 text-sm mt-1">Intelligence gathered by the research agent</p>
        </div>
        <button
          onClick={runResearch}
          disabled={triggering}
          className="bg-yellow-600 hover:bg-yellow-500 disabled:opacity-50 text-white text-sm px-4 py-2 rounded-lg transition-colors"
        >
          {triggering ? "Running..." : "▶ Run Research Agent"}
        </button>
      </div>

      {error && <div className="text-red-400 text-sm mb-4">{error}</div>}

      {/* Filter */}
      <div className="mb-5 flex gap-2 flex-wrap">
        <button
          onClick={() => setFilter("")}
          className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${!filter ? "bg-yellow-600 border-yellow-600 text-white" : "border-gray-700 text-gray-400 hover:text-white"}`}
        >
          All
        </button>
        {competitors.map(c => (
          <button
            key={c}
            onClick={() => setFilter(c === filter ? "" : c)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${filter === c ? "bg-yellow-600 border-yellow-600 text-white" : "border-gray-700 text-gray-400 hover:text-white"}`}
          >
            {c}
          </button>
        ))}
      </div>

      {items.length === 0 ? (
        <p className="text-gray-600 text-sm">No research items yet. Run the research agent to gather competitor intelligence.</p>
      ) : (
        <div className="space-y-3">
          {items.map(item => (
            <div key={item.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm font-semibold text-white">{item.competitor}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-mono uppercase ${SOURCE_BADGE[item.source] ?? "bg-gray-700 text-gray-300"}`}>
                  {item.source}
                </span>
                <span className="text-gray-600 text-xs ml-auto">
                  {item.created_at ? new Date(item.created_at).toLocaleDateString("en-AU", { day: "numeric", month: "short", year: "numeric" }) : ""}
                </span>
              </div>
              <p className={`text-gray-400 text-sm leading-relaxed ${!expanded[item.id] ? "line-clamp-3" : ""}`}>
                {item.content}
              </p>
              {item.content && item.content.length > 200 && (
                <button
                  onClick={() => toggle(item.id)}
                  className="text-xs text-yellow-400 hover:text-yellow-300 mt-2 transition-colors"
                >
                  {expanded[item.id] ? "Show less" : "Show more"}
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
