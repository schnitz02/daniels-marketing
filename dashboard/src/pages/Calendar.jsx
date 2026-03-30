import { useEffect, useState } from "react"
import api from "../api"

const PLATFORM_COLORS = {
  instagram: "bg-pink-900 text-pink-300",
  facebook: "bg-blue-900 text-blue-300",
  tiktok: "bg-gray-800 text-white",
}
const STATUS_COLORS = {
  published: "bg-green-900 text-green-300",
  scheduled: "bg-yellow-900 text-yellow-300",
  failed: "bg-red-900 text-red-300",
}

export default function Calendar() {
  const [posts, setPosts] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    api.get("/dashboard/calendar").then(r => setPosts(r.data)).catch(() => setError(true))
  }, [])

  if (error) return <div className="text-red-400 text-sm">Could not load calendar. Is the backend running?</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Content Calendar</h1>
      {posts.length === 0 ? (
        <p className="text-gray-600 text-sm">No posts yet. Approve content to start scheduling.</p>
      ) : (
        <div className="space-y-2">
          {posts.map(post => (
            <div key={post.id} className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-center gap-4">
              <span className={`text-xs px-2 py-0.5 rounded-full ${PLATFORM_COLORS[post.platform] ?? "bg-gray-800 text-gray-400"}`}>
                {post.platform}
              </span>
              <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[post.status] ?? "bg-gray-800 text-gray-400"}`}>
                {post.status}
              </span>
              <span className="text-gray-400 text-sm">
                {post.published_at !== "None" ? `Published ${post.published_at}` : post.scheduled_at !== "None" ? `Scheduled ${post.scheduled_at}` : "Pending schedule"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
