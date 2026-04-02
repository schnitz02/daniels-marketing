import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom"
import Overview from "./pages/Overview"
import Approvals from "./pages/Approvals"
import Calendar from "./pages/Calendar"
import Analytics from "./pages/Analytics"
import Strategy from "./pages/Strategy"
import Website from "./pages/Website"
import Agents from "./pages/Agents"
import SocialStats from "./pages/SocialStats"
import Research from "./pages/Research"

const NAV = [
  ["Overview", "/"],
  ["Approvals", "/approvals"],
  ["Calendar", "/calendar"],
  ["Analytics", "/analytics"],
  ["Strategy", "/strategy"],
  ["Website", "/website"],
  ["Agents", "/agents"],
  ["Social Stats", "/social-stats"],
  ["Research", "/research"],
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-[#F5F4EC] text-[#00395D] overflow-hidden">
        <nav className="w-56 bg-[#00395D] border-r border-[#1a5276] flex flex-col p-4 gap-1 shrink-0">
          <div className="flex justify-center mb-8 pt-2">
            <img src="/logo.png" alt="Daniel's Donuts" className="w-36" />
          </div>
          {NAV.map(([label, path]) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              className={({ isActive }) =>
                `px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? "bg-[#04D3C5] text-white font-medium"
                    : "text-white/70 hover:text-white hover:bg-white/10"
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <main className="flex-1 overflow-auto p-8 bg-[#F5F4EC]">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/approvals" element={<Approvals />} />
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/strategy" element={<Strategy />} />
            <Route path="/website" element={<Website />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/social-stats" element={<SocialStats />} />
            <Route path="/research" element={<Research />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
