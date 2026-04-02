import { useEffect, useState } from "react"
import api from "../api"
import { formatDate } from "../utils/date"

const SOURCE_BADGE = {
  instagram: "bg-pink-900 text-pink-300",
  facebook: "bg-blue-900 text-blue-300",
  tiktok: "bg-purple-900 text-purple-300",
  web: "bg-gray-700 text-gray-300",
  claude_research: "bg-yellow-900 text-yellow-300",
}

/** Strip markdown code fences and parse JSON, returning null on failure */
function parseInsights(raw) {
  if (!raw) return null
  try {
    // Strip markdown code fences if present
    const stripped = raw.replace(/^```json\s*/i, "").replace(/^```\s*/i, "").replace(/```\s*$/, "").trim()
    // Try standard JSON first
    try {
      const parsed = JSON.parse(stripped)
      if (Array.isArray(parsed.insights)) return parsed.insights
    } catch {}
    // Try converting Python-style single-quote dict to JSON
    const jsonified = stripped
      .replace(/'/g, '"')
      .replace(/None/g, "null")
      .replace(/True/g, "true")
      .replace(/False/g, "false")
    const parsed = JSON.parse(jsonified)
    if (Array.isArray(parsed.insights)) return parsed.insights
  } catch {}
  return null
}

function InsightCard({ insights }) {
  return (
    <div className="space-y-3 mt-3">
      {insights.map((ins, i) => (
        <div key={i} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs text-gray-500 uppercase tracking-wide font-semibold">Insight {i + 1}</span>
            {ins.platform && (
              <span className="text-xs text-blue-300 bg-blue-900 px-2 py-0.5 rounded-full">{ins.platform}</span>
            )}
          </div>
          <p className="text-gray-300 text-sm leading-relaxed mb-3">{ins.insight}</p>
          {ins.actionable && (
            <div className="border-l-2 border-yellow-600 pl-3">
              <p className="text-xs text-gray-500 uppercase tracking-wide font-semibold mb-1">Recommended Action</p>
              <p className="text-gray-400 text-sm leading-relaxed">{ins.actionable}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  )
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
                  {formatDate(item.created_at)}
                </span>
              </div>
              {(() => {
                const insights = parseInsights(item.content)
                if (insights) {
                  return (
                    <>
                      {!expanded[item.id]
                        ? <InsightCard insights={insights.slice(0, 1)} />
                        : <InsightCard insights={insights} />
                      }
                      {insights.length > 1 && (
                        <button
                          onClick={() => toggle(item.id)}
                          className="text-xs text-yellow-400 hover:text-yellow-300 mt-3 transition-colors"
                        >
                          {expanded[item.id] ? `▾ Show less` : `▸ Show all ${insights.length} insights`}
                        </button>
                      )}
                    </>
                  )
                }
                return (
                  <>
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
                  </>
                )
              })()}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
