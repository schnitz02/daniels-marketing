import { useEffect, useState } from "react"
import api from "../api"

function Badge({ type }) {
  const styles = { image: "bg-blue-100 text-blue-700", reel: "bg-purple-100 text-purple-700" }
  return <span className={`text-xs px-2 py-0.5 rounded-full uppercase font-mono ${styles[type] ?? "bg-gray-100 text-gray-500"}`}>{type}</span>
}

function IdeaCard({ idea, onApprove, onReject }) {
  const [notes, setNotes] = useState("")
  const [showReject, setShowReject] = useState(false)
  const [showEvidence, setShowEvidence] = useState(false)

  return (
    <div className="bg-white border border-[#E8E4D9] rounded-xl p-5 mb-3 shadow-sm">
      <h3 className="font-semibold text-[#00395D] mb-1">{idea.title}</h3>
      <p className="text-[#4A5568] text-sm mb-4 leading-relaxed">{idea.body}</p>
      {idea.evidence && (
        <div className="mb-4">
          <button
            onClick={() => setShowEvidence(v => !v)}
            className="text-xs text-[#04D3C5] hover:text-[#03bdb0] transition-colors"
          >
            {showEvidence ? "▾ Hide reasoning" : "▸ Why this idea?"}
          </button>
          {showEvidence && (
            <p className="mt-2 text-xs text-[#4A5568] bg-[#F5F4EC] rounded-lg p-3 leading-relaxed border border-[#E8E4D9]">
              {idea.evidence}
            </p>
          )}
        </div>
      )}
      {showReject ? (
        <div className="flex gap-2">
          <input
            value={notes}
            onChange={e => setNotes(e.target.value)}
            placeholder="Rejection reason (optional)"
            className="flex-1 bg-white text-[#00395D] text-sm px-3 py-2 rounded-lg border border-[#E8E4D9] focus:outline-none focus:border-[#04D3C5]"
          />
          <button onClick={() => { onReject(idea.id, notes); setShowReject(false) }}
            className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-400 transition-colors">
            Confirm
          </button>
          <button onClick={() => setShowReject(false)} className="text-[#6B8A9A] text-sm px-3 hover:text-[#00395D]">Cancel</button>
        </div>
      ) : (
        <div className="flex gap-2">
          <button onClick={() => onApprove(idea.id)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-500 transition-colors">
            ✓ Approve
          </button>
          <button onClick={() => setShowReject(true)}
            className="bg-white text-red-500 border border-red-200 px-4 py-2 rounded-lg text-sm hover:bg-red-50 transition-colors">
            ✗ Reject
          </button>
        </div>
      )}
    </div>
  )
}

function ContentCard({ item, onApprove, onReject }) {
  const [notes, setNotes] = useState("")
  const [showReject, setShowReject] = useState(false)

  return (
    <div className="bg-white border border-[#E8E4D9] rounded-xl p-5 mb-3 shadow-sm">
      <div className="flex gap-4 mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Badge type={item.type} />
          </div>
          <p className="text-[#4A5568] text-sm leading-relaxed">{item.caption}</p>
          <p className="text-[#6B8A9A] text-xs mt-1 font-mono">{item.file_path}</p>
        </div>
      </div>
      {showReject ? (
        <div className="flex gap-2">
          <input value={notes} onChange={e => setNotes(e.target.value)}
            placeholder="Rejection reason (optional)"
            className="flex-1 bg-white text-[#00395D] text-sm px-3 py-2 rounded-lg border border-[#E8E4D9] focus:outline-none focus:border-[#04D3C5]" />
          <button onClick={() => { onReject(item.id, notes); setShowReject(false) }}
            className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-400">Confirm</button>
          <button onClick={() => setShowReject(false)} className="text-[#6B8A9A] text-sm px-3">Cancel</button>
        </div>
      ) : (
        <div className="flex gap-2">
          <button onClick={() => onApprove(item.id)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-500 transition-colors">
            ✓ Approve
          </button>
          <button onClick={() => onReject(item.id, "")}
            className="bg-white text-red-500 border border-red-200 px-4 py-2 rounded-lg text-sm hover:bg-red-50 transition-colors">
            ✗ Reject
          </button>
        </div>
      )}
    </div>
  )
}

export default function Approvals() {
  const [ideas, setIdeas] = useState([])
  const [content, setContent] = useState([])
  const [error, setError] = useState(null)

  const load = () => {
    setError(null)
    return Promise.all([
      api.get("/approvals/ideas").then(r => setIdeas(r.data)),
      api.get("/approvals/content").then(r => setContent(r.data)),
    ]).catch(() => setError("Could not load approvals. Make sure the backend is running on port 8000."))
  }

  useEffect(() => { load(); const t = setInterval(load, 8000); return () => clearInterval(t) }, [])

  const approveIdea = id => api.post(`/approvals/ideas/${id}/approve`).then(load)
  const rejectIdea = (id, notes) => api.post(`/approvals/ideas/${id}/reject`, { notes }).then(load)
  const approveContent = id => api.post(`/approvals/content/${id}/approve`).then(load)
  const rejectContent = (id, notes) => api.post(`/approvals/content/${id}/reject`, { notes }).then(load)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 text-[#00395D]">Approvals</h1>
      {error && <div className="text-red-600 bg-red-50 border border-red-200 rounded-xl p-4 mb-6 text-sm">{error}</div>}
      <section className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <h2 className="text-base font-semibold text-[#00395D]">Stage 1 — Ideas</h2>
          <span className="bg-[#F7CA5E]/30 text-[#00395D] text-xs px-2 py-0.5 rounded-full font-medium">{ideas.length} pending</span>
        </div>
        {ideas.length === 0
          ? <p className="text-[#6B8A9A] text-sm">No pending ideas. The strategy agent will generate new ones on its next run.</p>
          : ideas.map(idea => <IdeaCard key={idea.id} idea={idea} onApprove={approveIdea} onReject={rejectIdea} />)
        }
      </section>
      <section>
        <div className="flex items-center gap-2 mb-4">
          <h2 className="text-base font-semibold text-[#00395D]">Stage 2 — Content</h2>
          <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full font-medium">{content.length} pending</span>
        </div>
        {content.length === 0
          ? <p className="text-[#6B8A9A] text-sm">No pending content. Approve some ideas first to generate content.</p>
          : content.map(item => <ContentCard key={item.id} item={item} onApprove={approveContent} onReject={rejectContent} />)
        }
      </section>
    </div>
  )
}
