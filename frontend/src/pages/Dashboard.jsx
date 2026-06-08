import { useQuery } from '@tanstack/react-query'
import { Activity, AlertTriangle, ScrollText, ShieldAlert } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, CartesianGrid } from 'recharts'
import api from '../api'
import { useAuth } from '../context/AuthContext'
import useWebSocket from '../hooks/useWebSocket'
import { useEffect, useState } from 'react'

const SEV_COLORS = { critical: '#ef4444', warning: '#eab308', info: '#3b82f6' }
const SEV_ORDER = ['critical', 'warning', 'info']

function StatCard({ icon: Icon, label, value, critical }) {
  return (
    <div className={`card flex items-center gap-3 ${critical && parseInt(value) > 0 ? 'bg-red-950/30 border-red-900/50' : ''}`}>
      <div className={`p-2 rounded ${critical ? 'bg-red-900/30' : 'bg-wt-600'}`}>
        <Icon className={`w-4 h-4 ${critical ? 'text-red-400' : 'text-wt-accent'}`} />
      </div>
      <div>
        <div className="text-xs text-gray-500">{label}</div>
        <div className={`text-xl font-semibold ${critical && parseInt(value) > 0 ? 'text-red-400' : 'text-white'}`}>{value}</div>
      </div>
    </div>
  )
}

function LiveAlertFeed() {
  const [alerts, setAlerts] = useState([])
  const { org } = useAuth()
  const { lastAlert, connected } = useWebSocket(org?.api_key)

  useEffect(() => {
    if (lastAlert) setAlerts((prev) => [lastAlert, ...prev].slice(0, 20))
  }, [lastAlert])

  const { data: alertData } = useQuery({
    queryKey: ['recent-alerts', org?.id],
    queryFn: () => api.get('/alerts?per_page=20').then((r) => r.data),
    enabled: !!org,
    refetchInterval: 30000,
  })

  useEffect(() => {
    if (alertData?.alerts) setAlerts(alertData.alerts)
  }, [alertData])

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-white">Live Alerts</h3>
        <span className={`text-xs px-2 py-0.5 rounded ${connected ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'}`}>
          {connected ? 'Live' : 'Disconnected'}
        </span>
      </div>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {alerts.length === 0 && <p className="text-xs text-gray-500 text-center py-4">No alerts yet</p>}
        {alerts.map((a) => (
          <div key={a.id} className="text-xs bg-wt-700 rounded p-2 animate-[slideIn_0.3s_ease]">
            <div className="flex items-center gap-2 mb-1">
              <span className={`badge-${a.severity}`}>{a.severity}</span>
              <span className="text-gray-300 font-medium">{a.rule_name}</span>
            </div>
            <p className="text-gray-500 truncate">{a.description}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { org } = useAuth()
  const { data, isLoading } = useQuery({
    queryKey: ['stats', org?.id],
    queryFn: () => api.get('/stats').then((r) => r.data),
    enabled: !!org,
    refetchInterval: 30000,
  })

  if (isLoading) return <div className="text-gray-500 text-sm">Loading dashboard...</div>

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard icon={ScrollText} label="Total Logs (24h)" value={data?.log_count ?? 0} />
        <StatCard icon={AlertTriangle} label="Open Alerts" value={data?.open_alerts ?? 0} />
        <StatCard icon={ShieldAlert} label="Critical Alerts" value={data?.critical_alerts ?? 0} critical />
        <StatCard icon={Activity} label="Total Alerts (24h)" value={data?.alert_count ?? 0} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 card">
          <h3 className="text-sm font-semibold text-white mb-3">Events per Hour</h3>
          {data?.timeline?.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={data.timeline}>
                <defs>
                  {SEV_ORDER.map((s) => (<filter key={s} id={`grad-${s}`}><stop offset="5%" stopColor={SEV_COLORS[s]} stopOpacity={0.3} /><stop offset="95%" stopColor={SEV_COLORS[s]} stopOpacity={0} /></filter>))}
                </defs>
                <XAxis dataKey="hour" tick={{ fontSize: 10, fill: '#666' }} tickFormatter={(v) => v.slice(11, 16)} />
                <YAxis tick={{ fontSize: 10, fill: '#666' }} />
                <Tooltip contentStyle={{ background: '#1a1a25', border: '1px solid #333', borderRadius: 8, fontSize: 12 }} />
                {SEV_ORDER.map((s) => (
                  <Area key={s} type="monotone" dataKey={s} stackId="1" stroke={SEV_COLORS[s]} fill={SEV_COLORS[s]} fillOpacity={0.2} />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[250px] text-xs text-gray-600">No event data in the last 24 hours</div>
          )}
        </div>
        <div className="card">
          <h3 className="text-sm font-semibold text-white mb-3">Severity</h3>
          {Object.values(data?.severity_breakdown || {}).some((v) => v > 0) ? (
            <>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={SEV_ORDER.map((s) => ({ name: s, value: data?.severity_breakdown?.[s] || 0 })).filter((d) => d.value > 0)} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="value">
                    {SEV_ORDER.map((s) => (<Cell key={s} fill={SEV_COLORS[s]} />))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#1a1a25', border: '1px solid #333', borderRadius: 8, fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 text-xs text-gray-400 mt-2">
                {SEV_ORDER.map((s) => (
                  <span key={s} className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full" style={{ background: SEV_COLORS[s] }} /> {s}
                  </span>
                ))}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-[250px] text-xs text-gray-600">No severity data yet</div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="text-sm font-semibold text-white mb-3">Top Source IPs</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data?.top_source_ips || []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#222" />
              <XAxis type="number" tick={{ fontSize: 10, fill: '#666' }} />
              <YAxis dataKey="ip" type="category" width={120} tick={{ fontSize: 10, fill: '#666' }} />
              <Tooltip contentStyle={{ background: '#1a1a25', border: '1px solid #333', borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <LiveAlertFeed />
      </div>
    </div>
  )
}
