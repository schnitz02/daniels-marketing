import { useEffect, useState } from "react"
import api from "../api"

function Badge({ type }) {
  const styles = { image: "bg-blue-900 text-blue-300", reel: "bg-purple-900 text-purple-300" }
  return <span className={`text-xs px-2 py-0.5 rounded-full uppercase font-mono ${styles[type] ?? "bg-gray-800 text-gray-400"}`}>{type}</span>
}

function IdeaCard({ idea, onApprove, onReject }) {
  const [notes, setNotes] = useState("")
  const [showReject, setShowReject] = useState(false)

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-3">
      <h3 className="font-semibold text-white mb-1">{idea.title}</h3>
      <p className="text-gray-400 text-sm mb-4 leading-relaxed">{idea.body}</p>
      {showReject ? (
        <div className="flex gap-2">
          <input
            value={notes}
            onChange={e => setNotes(e.target.value)}
            placeholder="Rejection reason (optional)"
            className="flex-1 bg-gray-800 text-white text-sm px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-red-500"
          />
          <button onClick={() => { onReject(idea.id, notes); setShowReject(false) }}
            className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-500 transition-colors">
            Confirm
          </button>
          <button onClick={() => setShowReject(false)} className="text-gray-500 text-sm px-3 hover:text-gray-300">Cancel</button>
        </div>
      ) : (
        <div className="flex gap-2">
          <button onClick={() => onApprove(idea.id)}
            className="bg-green-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-600 transition-colors">
            ✓ Approve
          </button>
          <button onClick={() => setShowReject(true)}
            className="bg-gray-800 text-red-400 border border-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-700 transition-colors">
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
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-3">
      <div className="flex gap-4 mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Badge type={item.type} />
          </div>
          <p className="text-gray-300 text-sm leading-relaxed">{item.caption}</p>
          <p className="text-gray-600 text-xs mt-1 font-mono">{item.file_path}</p>
        </div>
      </div>
      {showReject ? (
        <div className="flex gap-2">
          <input value={notes} onChange={e => setNotes(e.target.value)}
            placeholder="Rejection reason (optional)"
            className="flex-1 bg-gray-800 text-white text-sm px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-red-500" />
          <button onClick={() => { onReject(item.id, notes); setShowReject(false) }}
            className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-500">Confirm</button>
          <button onClick={() => setShowReject(false)} className="text-gray-500 text-sm px-3">Cancel</button>
        </div>
      ) : (
        <div className="flex gap-2">
          <button onClick={() => onApprove(item.id)}
            className="bg-green-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-600 transition-colors">
            ✓ Approve
          </button>
          <button onClick={() => setShowReject(true)}
            className="bg-gray-800 text-red-400 border border-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-700 transition-colors">
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

  useEffect(() => { load() }, [])

  const approveIdea = id => api.post(`/approvals/ideas/${id}/approve`).then(load)
  const rejectIdea = (id, notes) => api.post(`/approvals/ideas/${id}/reject`, { notes }).then(load)
  const approveContent = id => api.post(`/approvals/content/${id}/approve`).then(load)
  const rejectContent = (id, notes) => api.post(`/approvals/content/${id}/reject`, { notes }).then(load)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Approvals</h1>
      {error && <div className="text-red-400 bg-red-900/20 rounded-xl p-4 mb-6 text-sm">{error}</div>}
      <section className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <h2 className="text-base font-semibold">Stage 1 — Ideas</h2>
          <span className="bg-yellow-900 text-yellow-300 text-xs px-2 py-0.5 rounded-full">{ideas.length} pending</span>
        </div>
        {ideas.length === 0
          ? <p className="text-gray-600 text-sm">No pending ideas. The strategy agent will generate new ones on its next run.</p>
          : ideas.map(idea => <IdeaCard key={idea.id} idea={idea} onApprove={approveIdea} onReject={rejectIdea} />)
        }
      </section>
      <section>
        <div className="flex items-center gap-2 mb-4">
          <h2 className="text-base font-semibold">Stage 2 — Content</h2>
          <span className="bg-blue-900 text-blue-300 text-xs px-2 py-0.5 rounded-full">{content.length} pending</span>
        </div>
        {content.length === 0
          ? <p className="text-gray-600 text-sm">No pending content. Approve some ideas first to generate content.</p>
          : content.map(item => <ContentCard key={item.id} item={item} onApprove={approveContent} onReject={rejectContent} />)
        }
      </section>
    </div>
  )
}
