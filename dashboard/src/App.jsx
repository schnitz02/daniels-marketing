import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom"
import Overview from "./pages/Overview"
import Approvals from "./pages/Approvals"
import Calendar from "./pages/Calendar"
import Analytics from "./pages/Analytics"
import Strategy from "./pages/Strategy"
import Website from "./pages/Website"
import Agents from "./pages/Agents"

const NAV = [
  ["Overview", "/"],
  ["Approvals", "/approvals"],
  ["Calendar", "/calendar"],
  ["Analytics", "/analytics"],
  ["Strategy", "/strategy"],
  ["Website", "/website"],
  ["Agents", "/agents"],
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
        <nav className="w-52 bg-gray-900 border-r border-gray-800 flex flex-col p-4 gap-1 shrink-0">
          <div className="flex items-center gap-2 mb-6 px-2">
            <span className="text-2xl">🍩</span>
            <span className="font-bold text-brand text-sm leading-tight">Daniel's<br/>Donuts</span>
          </div>
          {NAV.map(([label, path]) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              className={({ isActive }) =>
                `px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? "bg-brand text-white font-medium"
                    : "text-gray-400 hover:text-white hover:bg-gray-800"
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <main className="flex-1 overflow-auto p-8">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/approvals" element={<Approvals />} />
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/strategy" element={<Strategy />} />
            <Route path="/website" element={<Website />} />
            <Route path="/agents" element={<Agents />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
