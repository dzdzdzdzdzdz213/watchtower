import { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, ScrollText, AlertTriangle, Settings, LogOut, Menu, X, Shield } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const nav = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/logs', label: 'Log Explorer', icon: ScrollText },
  { to: '/alerts', label: 'Alerts', icon: AlertTriangle },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function Layout() {
  const [open, setOpen] = useState(false)
  const { org, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className={`fixed inset-y-0 left-0 z-50 w-60 bg-wt-800 border-r border-gray-800 transform transition-transform duration-200 lg:relative lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center gap-2 px-5 h-14 border-b border-gray-800">
          <Shield className="w-5 h-5 text-wt-accent" />
          <span className="font-semibold text-white text-sm">WatchTower</span>
        </div>
        <nav className="p-3 space-y-1">
          {nav.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${isActive ? 'bg-wt-accent/10 text-wt-accent' : 'text-gray-400 hover:text-white hover:bg-wt-600'}`
              }
            >
              <Icon className="w-4 h-4" /> {label}
            </NavLink>
          ))}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 p-3 border-t border-gray-800">
          <div className="flex items-center gap-2 px-3 py-2 text-xs text-gray-500 mb-2 truncate">{org?.name}</div>
          <button onClick={handleLogout} className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:text-white hover:bg-wt-600 w-full transition-colors">
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </aside>

      {open && <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setOpen(false)} />}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center gap-3 px-4 h-14 border-b border-gray-800 bg-wt-900 lg:hidden">
          <button onClick={() => setOpen(true)} className="text-gray-400 hover:text-white"><Menu className="w-5 h-5" /></button>
          <Shield className="w-5 h-5 text-wt-accent" />
          <span className="font-semibold text-white text-sm">WatchTower</span>
        </header>
        <main className="flex-1 overflow-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
