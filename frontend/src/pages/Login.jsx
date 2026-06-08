import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function Login() {
  const { login, register, org } = useAuth()
  const navigate = useNavigate()
  const [isRegister, setIsRegister] = useState(false)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ name: '', email: '', password: '' })

  if (org) { navigate('/', { replace: true }); return null }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (isRegister) {
        await register(form.name, form.email, form.password)
      } else {
        await login(form.email, form.password)
      }
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-wt-900 p-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2 mb-8">
          <Shield className="w-6 h-6 text-wt-accent" />
          <span className="text-xl font-semibold text-white">WatchTower</span>
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-1">{isRegister ? 'Create Account' : 'Sign In'}</h2>
          <p className="text-xs text-gray-500 mb-6">{isRegister ? 'Register your organization' : 'Enter your credentials'}</p>
          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <div>
                <label className="block text-xs text-gray-400 mb-1">Organization Name</label>
                <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
            )}
            <div>
              <label className="block text-xs text-gray-400 mb-1">Email</label>
              <input type="email" className="input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Password</label>
              <input type="password" className="input" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? 'Please wait...' : isRegister ? 'Register' : 'Sign In'}
            </button>
          </form>
          <p className="text-xs text-gray-500 mt-4 text-center">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button className="text-wt-accent hover:underline" onClick={() => setIsRegister(!isRegister)}>
              {isRegister ? 'Sign in' : 'Register'}
            </button>
          </p>
        </div>
        <p className="text-xs text-gray-600 text-center mt-4">
          Demo: demo@watchtower.dev / demo1234
        </p>
      </div>
    </div>
  )
}
