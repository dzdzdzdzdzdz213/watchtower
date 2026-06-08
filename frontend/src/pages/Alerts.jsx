import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api'
import toast from 'react-hot-toast'

const TABS = [
  { key: 'all', label: 'All' },
  { key: 'open', label: 'Open' },
  { key: 'acknowledged', label: 'Acknowledged' },
  { key: 'resolved', label: 'Resolved' },
]

export default function Alerts() {
  const [tab, setTab] = useState('all')
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['alerts', tab],
    queryFn: () => api.get('/alerts', { params: { status: tab === 'all' ? undefined : tab, per_page: 100 } }).then((r) => r.data),
  })

  const update = useMutation({
    mutationFn: ({ id, status }) => api.patch(`/alerts/${id}`, { status }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['alerts'] }); toast.success('Alert updated') },
    onError: () => toast.error('Failed to update alert'),
  })

  const SevBadge = ({ severity }) => {
    const cls = severity === 'critical' ? 'badge-critical' : severity === 'warning' ? 'badge-warning' : 'badge-info'
    return <span className={cls}>{severity}</span>
  }

  const StatusBadge = ({ status }) => {
    const colors = { open: 'bg-red-900/50 text-red-400', acknowledged: 'bg-yellow-900/50 text-yellow-400', resolved: 'bg-green-900/50 text-green-400' }
    return <span className={`badge ${colors[status] || ''}`}>{status}</span>
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-1 bg-wt-800 rounded-lg p-1 border border-gray-800 w-fit">
        {TABS.map(({ key, label }) => (
          <button key={key} onClick={() => setTab(key)} className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${tab === key ? 'bg-wt-accent text-white' : 'text-gray-400 hover:text-white'}`}>
            {label}
            {data && key !== 'all' && <span className="ml-1.5 opacity-60">({key === 'open' ? data.total : '-'})</span>}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-gray-500 text-sm text-center py-8">Loading...</p>}

      {data && data.alerts.length === 0 && <p className="text-gray-500 text-sm text-center py-8">No alerts</p>}

      <div className="space-y-2">
        {data?.alerts.map((alert) => (
          <div key={alert.id} className="card">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <SevBadge severity={alert.severity} />
                  <span className="text-sm font-medium text-white">{alert.rule_name.replace(/_/g, ' ')}</span>
                  <StatusBadge status={alert.status} />
                </div>
                <p className="text-xs text-gray-400 mb-2">{alert.description}</p>
                <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                  {alert.source_ip && <span>IP: {alert.source_ip}</span>}
                  {alert.affected_user && <span>User: {alert.affected_user}</span>}
                  <span>Count: {alert.log_count}</span>
                  <span>First: {new Date(alert.first_seen).toLocaleString()}</span>
                  <span>Last: {new Date(alert.last_seen).toLocaleString()}</span>
                </div>
              </div>
              <div className="flex gap-2 shrink-0">
                <button
                  disabled={alert.status !== 'open'}
                  onClick={() => update.mutate({ id: alert.id, status: 'acknowledged' })}
                  className="btn-ghost text-xs"
                >Acknowledge</button>
                <button
                  disabled={alert.status === 'resolved'}
                  onClick={() => update.mutate({ id: alert.id, status: 'resolved' })}
                  className="btn-primary text-xs"
                >Resolve</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
