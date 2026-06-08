import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import LogExplorer from './pages/LogExplorer'
import Alerts from './pages/Alerts'
import Settings from './pages/Settings'
import Layout from './components/Layout'

function ProtectedRoute({ children }) {
  const { org } = useAuth()
  return org ? children : <Navigate to="/login" replace />
}

function GuestRoute({ children }) {
  const { org } = useAuth()
  return org ? <Navigate to="/dashboard" replace /> : children
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<GuestRoute><Landing /></GuestRoute>} />
      <Route path="/login" element={<GuestRoute><Login /></GuestRoute>} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="logs" element={<LogExplorer />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
