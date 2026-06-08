import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { Copy, Check, Eye, EyeOff, LogOut, Shield } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function Settings() {
  const { org, logout } = useAuth()
  const navigate = useNavigate()
  const [revealKey, setRevealKey] = useState(false)
  const [copied, setCopied] = useState(false)

  const copyKey = async () => {
    await navigator.clipboard.writeText(org.api_key)
    setCopied(true)
    toast.success('API key copied')
    setTimeout(() => setCopied(false), 2000)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const curlExample = `curl -X POST ${import.meta.env.VITE_API_URL || '/api'}/ingest/${org?.api_key} \\
  -H "Content-Type: application/json" \\
  -d '{"logs": ["Jun 8 10:00:00 server sshd[1234]: Failed password for root from 10.0.0.1 port 22 ssh2"]}'`

  return (
    <div className="max-w-2xl space-y-4">
      <div className="card">
        <h3 className="text-sm font-semibold text-white mb-4">Organization</h3>
        <div className="space-y-3 text-sm">
          <div><span className="text-gray-500 text-xs">Name</span><p className="text-gray-300">{org?.name}</p></div>
          <div><span className="text-gray-500 text-xs">Email</span><p className="text-gray-300">{org?.email}</p></div>
          <div><span className="text-gray-500 text-xs">Plan</span><p className="text-gray-300 capitalize">{org?.plan}</p></div>
        </div>
      </div>

      <div className="card">
        <h3 className="text-sm font-semibold text-white mb-4">API Key</h3>
        <div className="flex items-center gap-2 mb-4">
          <code className="flex-1 bg-wt-900 rounded px-3 py-2 text-xs font-mono text-gray-300 truncate">
            {revealKey ? org?.api_key : '••••••••-' + org?.api_key?.slice(-4)}
          </code>
          <button onClick={() => setRevealKey(!revealKey)} className="btn-ghost !p-2">
            {revealKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
          <button onClick={copyKey} className="btn-ghost !p-2">
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>

        <h4 className="text-xs font-medium text-gray-400 mb-2">Send logs via curl</h4>
        <pre className="text-xs text-gray-400 font-mono bg-wt-900 rounded p-3 overflow-x-auto">{curlExample}</pre>
      </div>

      <div className="card">
        <button onClick={handleLogout} className="flex items-center gap-2 text-sm text-red-400 hover:text-red-300 transition-colors">
          <LogOut className="w-4 h-4" /> Logout
        </button>
      </div>
    </div>
  )
}
