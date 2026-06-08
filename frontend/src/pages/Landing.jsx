import { Shield, Activity, AlertTriangle, Search, Server, Zap, ArrowRight, Github, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'

const features = [
  { icon: Activity, title: 'Real-time Monitoring', desc: 'Live log streaming and WebSocket-powered event feed with sub-second latency.' },
  { icon: AlertTriangle, title: 'Threat Detection', desc: '7 built-in detection rules — brute force SSH, SQL injection, port scans, off-hours logins, and path enumeration.' },
  { icon: Search, title: 'Log Intelligence', desc: 'Parse SSH auth, Nginx access, JSON, and generic syslog formats. Auto-detect structure without configuration.' },
  { icon: Server, title: 'Multi-tenant SaaS', desc: 'Organization-based isolation with per-org API keys, JWT authentication, and dedicated WebSocket channels.' },
  { icon: Zap, title: 'Fast & Async', desc: 'Python 3.14 + FastAPI async backend with SQLAlchemy 2.0 async ORM. PostgreSQL and SQLite support.' },
  { icon: Shield, title: 'Open Source', desc: 'Full source on GitHub. MIT license. Self-host or use the cloud instance. Built for security engineers.' },
]

const stats = [
  { label: 'Detection Rules', value: '7' },
  { label: 'Supported Formats', value: '4' },
  { label: 'Response Time', value: '<50ms' },
  { label: 'Lines of Code', value: '2,525' },
]

export default function Landing() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-wt-900 text-gray-300">
      <nav className="border-b border-gray-800 bg-wt-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-wt-accent" />
            <span className="font-semibold text-white">WatchTower</span>
          </Link>
          <div className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-sm text-gray-400 hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="text-sm text-gray-400 hover:text-white transition-colors">How it Works</a>
            <a href="https://github.com/dzdzdzdzdzdz213/watchtower" target="_blank" rel="noopener noreferrer" className="text-sm text-gray-400 hover:text-white transition-colors">GitHub</a>
            <Link to="/login" className="btn-primary text-sm">Sign In</Link>
            <Link to="/login?register=1" className="btn-ghost text-sm">Get Started</Link>
          </div>
          <button className="md:hidden text-gray-400" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
        {menuOpen && (
          <div className="md:hidden border-t border-gray-800 bg-wt-800 px-4 py-3 space-y-2">
            <a href="#features" onClick={() => setMenuOpen(false)} className="block text-sm text-gray-400 hover:text-white py-1">Features</a>
            <a href="#how-it-works" onClick={() => setMenuOpen(false)} className="block text-sm text-gray-400 hover:text-white py-1">How it Works</a>
            <a href="https://github.com/dzdzdzdzdzdz213/watchtower" target="_blank" rel="noopener noreferrer" onClick={() => setMenuOpen(false)} className="block text-sm text-gray-400 hover:text-white py-1">GitHub</a>
            <div className="flex gap-2 pt-2">
              <Link to="/login" className="btn-primary text-sm flex-1 text-center">Sign In</Link>
              <Link to="/login?register=1" className="btn-ghost text-sm flex-1 text-center">Get Started</Link>
            </div>
          </div>
        )}
      </nav>

      <section className="max-w-6xl mx-auto px-4 pt-20 pb-16 md:pt-32 md:pb-24 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-wt-accent/10 border border-wt-accent/20 text-wt-accent text-xs font-medium mb-6">
          <Shield className="w-3 h-3" /> Open Source SIEM Platform
        </div>
        <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight mb-6">
          Log Intelligence<br />
          <span className="text-wt-accent">at Your Fingertips</span>
        </h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-10">
          WatchTower is a modern SIEM platform that ingests, parses, and analyzes security logs in real time.
          Detect threats, monitor events, and respond to incidents — all from a single dashboard.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link to="/login?register=1" className="btn-primary text-base px-6 py-2.5 flex items-center gap-2">
            Get Started <ArrowRight className="w-4 h-4" />
          </Link>
          <a href="https://github.com/dzdzdzdzdzdz213/watchtower" target="_blank" rel="noopener noreferrer" className="btn-ghost text-base px-6 py-2.5 flex items-center gap-2">
            <Github className="w-4 h-4" /> View on GitHub
          </a>
        </div>
      </section>

      <section className="border-t border-gray-800 bg-wt-800/50">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((s) => (
              <div key={s.label} className="text-center">
                <div className="text-2xl md:text-3xl font-bold text-white">{s.value}</div>
                <div className="text-xs text-gray-500 mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="features" className="max-w-6xl mx-auto px-4 py-16 md:py-24">
        <h2 className="text-2xl md:text-3xl font-bold text-white text-center mb-12">Everything You Need</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f) => (
            <div key={f.title} className="card hover:border-wt-accent/30 transition-colors">
              <f.icon className="w-5 h-5 text-wt-accent mb-3" />
              <h3 className="text-sm font-semibold text-white mb-1">{f.title}</h3>
              <p className="text-xs text-gray-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="how-it-works" className="border-t border-gray-800 max-w-6xl mx-auto px-4 py-16 md:py-24">
        <h2 className="text-2xl md:text-3xl font-bold text-white text-center mb-12">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { step: '01', title: 'Ingest', desc: 'Send security logs from any source via REST API. Supports SSH auth logs, Nginx access logs, JSON payloads, and generic syslog.' },
            { step: '02', title: 'Analyze', desc: 'Built-in detection engine runs 7 rules against every event. Sliding window deques track brute force attempts, port scans, and more in real time.' },
            { step: '03', title: 'Respond', desc: 'Alerts appear on the dashboard and stream via WebSocket. Acknowledge or resolve incidents. Export logs for forensic analysis.' },
          ].map((s) => (
            <div key={s.step} className="text-center">
              <div className="w-10 h-10 rounded-full bg-wt-accent/10 border border-wt-accent/20 flex items-center justify-center text-wt-accent text-sm font-bold mx-auto mb-4">{s.step}</div>
              <h3 className="text-sm font-semibold text-white mb-2">{s.title}</h3>
              <p className="text-xs text-gray-500 leading-relaxed max-w-xs mx-auto">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-t border-gray-800 bg-wt-accent/5">
        <div className="max-w-6xl mx-auto px-4 py-16 text-center">
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-4">Ready to Get Started?</h2>
          <p className="text-gray-400 mb-8 max-w-lg mx-auto">Deploy your own instance or use the hosted version. Demo credentials: demo@watchtower.dev</p>
          <div className="flex items-center justify-center gap-3">
            <Link to="/login" className="btn-primary text-base px-6 py-2.5">Sign In to Dashboard</Link>
            <a href="https://github.com/dzdzdzdzdzdz213/watchtower" target="_blank" rel="noopener noreferrer" className="btn-ghost text-base px-6 py-2.5 flex items-center gap-2">
              <Github className="w-4 h-4" /> GitHub
            </a>
          </div>
        </div>
      </section>

      <footer className="border-t border-gray-800">
        <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <Shield className="w-3 h-3" /> WatchTower SIEM
          </div>
          <a href="https://github.com/dzdzdzdzdzdz213/watchtower" target="_blank" rel="noopener noreferrer" className="text-xs text-gray-600 hover:text-gray-400 transition-colors flex items-center gap-1">
            <Github className="w-3 h-3" /> dzdzdzdzdzdz213
          </a>
        </div>
      </footer>
    </div>
  )
}
