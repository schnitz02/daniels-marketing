import { useEffect, useState } from "react"
import api from "../api"

const PLATFORM_COLORS = {
  instagram: "bg-pink-100 text-pink-700",
  facebook: "bg-blue-100 text-blue-700",
  tiktok: "bg-gray-100 text-gray-700",
}
const STATUS_COLORS = {
  published: "bg-green-100 text-green-700",
  scheduled: "bg-[#F7CA5E]/30 text-[#00395D]",
  failed: "bg-red-100 text-red-600",
}

export default function Calendar() {
  const [posts, setPosts] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    api.get("/dashboard/calendar").then(r => setPosts(r.data)).catch(() => setError(true))
  }, [])

  if (error) return <div className="text-red-600 text-sm">Could not load calendar. Is the backend running?</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 text-[#00395D]">Content Calendar</h1>
      {posts.length === 0 ? (
        <p className="text-[#6B8A9A] text-sm">No posts yet. Approve content to start scheduling.</p>
      ) : (
        <div className="space-y-2">
          {posts.map(post => (
            <div key={post.id} className="bg-white border border-[#E8E4D9] rounded-xl p-4 flex items-center gap-4 shadow-sm">
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${PLATFORM_COLORS[post.platform] ?? "bg-gray-100 text-gray-600"}`}>
                {post.platform}
              </span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[post.status] ?? "bg-gray-100 text-gray-600"}`}>
                {post.status}
              </span>
              <span className="text-[#4A5568] text-sm">
                {post.published_at !== "None" ? `Published ${post.published_at}` : post.scheduled_at !== "None" ? `Scheduled ${post.scheduled_at}` : "Pending schedule"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
