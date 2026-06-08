import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, ChevronDown, ChevronRight, Copy, Check } from 'lucide-react'
import api from '../api'
import toast from 'react-hot-toast'

export default function LogExplorer() {
  const [filters, setFilters] = useState({ severity: '', event_type: '', source_ip: '', search: '', from: '', to: '' })
  const [applied, setApplied] = useState('')
  const [page, setPage] = useState(1)
  const [expanded, setExpanded] = useState(null)
  const [copied, setCopied] = useState(null)

  const { data, isLoading } = useQuery({
    queryKey: ['logs', applied, page],
    queryFn: () => api.get('/logs', { params: { ...Object.fromEntries(Object.entries(JSON.parse(applied)).filter(([, v]) => v)), page, per_page: 50 } }).then((r) => r.data),
    enabled: !!applied,
  })

  const apply = () => { setApplied(JSON.stringify(filters)); setPage(1) }

  const copyLog = async (text) => {
    await navigator.clipboard.writeText(text)
    setCopied(text.slice(0, 20))
    setTimeout(() => setCopied(null), 1500)
  }

  const SevBadge = ({ severity }) => {
    const cls = severity === 'critical' ? 'badge-critical' : severity === 'warning' ? 'badge-warning' : 'badge-info'
    return <span className={cls}>{severity}</span>
  }

  return (
    <div className="space-y-4">
      <div className="card">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <select className="select" value={filters.severity} onChange={(e) => setFilters({ ...filters, severity: e.target.value })}>
            <option value="">All Severities</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
          </select>
          <input className="input" placeholder="Event type" value={filters.event_type} onChange={(e) => setFilters({ ...filters, event_type: e.target.value })} />
          <input className="input" placeholder="Source IP" value={filters.source_ip} onChange={(e) => setFilters({ ...filters, source_ip: e.target.value })} />
          <input type="date" className="input" value={filters.from} onChange={(e) => setFilters({ ...filters, from: e.target.value })} />
          <input type="date" className="input" value={filters.to} onChange={(e) => setFilters({ ...filters, to: e.target.value })} />
          <div className="flex gap-2">
            <input className="input flex-1" placeholder="Search..." value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} />
            <button onClick={apply} className="btn-primary"><Search className="w-4 h-4" /></button>
          </div>
        </div>
      </div>

      {!applied && <p className="text-gray-500 text-sm text-center py-8">Set filters and click search</p>}

      {isLoading && <p className="text-gray-500 text-sm text-center py-8">Loading...</p>}

      {data && (
        <>
          <p className="text-xs text-gray-500">{data.total} results (page {data.page})</p>
          <div className="space-y-1">
            {data.logs.length === 0 && <p className="text-gray-500 text-sm text-center py-8">No logs found</p>}
            {data.logs.map((log) => (
              <div key={log.id} className="card !p-0">
                <button onClick={() => setExpanded(expanded === log.id ? null : log.id)} className="w-full flex items-center gap-3 px-4 py-2.5 text-xs hover:bg-wt-700 transition-colors text-left">
                  {expanded === log.id ? <ChevronDown className="w-3 h-3 text-gray-500 shrink-0" /> : <ChevronRight className="w-3 h-3 text-gray-500 shrink-0" />}
                  <span className="text-gray-400 font-mono w-36 shrink-0">{new Date(log.timestamp).toLocaleString()}</span>
                  <SevBadge severity={log.severity} />
                  <span className="text-gray-300 w-28 shrink-0">{log.event_type}</span>
                  <span className="text-gray-400 font-mono w-28 shrink-0">{log.source_ip || '-'}</span>
                  <span className="text-gray-500 truncate">{log.raw_message?.slice(0, 100)}</span>
                </button>
                {expanded === log.id && (
                  <div className="px-4 pb-3 pt-1 border-t border-gray-800">
                    <pre className="text-xs text-gray-400 font-mono bg-wt-900 rounded p-3 overflow-x-auto mb-2">{log.raw_message}</pre>
                    <button onClick={() => copyLog(log.raw_message)} className="text-xs text-wt-accent hover:underline flex items-center gap-1">
                      {copied === log.raw_message.slice(0, 20) ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                      {copied === log.raw_message.slice(0, 20) ? 'Copied' : 'Copy raw log'}
                    </button>
                    {Object.keys(log.parsed_fields).length > 0 && (
                      <div className="mt-2 grid grid-cols-2 gap-1 text-xs">
                        {Object.entries(log.parsed_fields).map(([k, v]) => (
                          <div key={k} className="flex gap-2">
                            <span className="text-gray-500">{k}:</span>
                            <span className="text-gray-300 font-mono">{String(v)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
          {data.total > 50 && (
            <div className="flex justify-center gap-2 mt-4">
              <button disabled={page <= 1} onClick={() => setPage(page - 1)} className="btn-ghost text-xs">Previous</button>
              <button disabled={page * 50 >= data.total} onClick={() => setPage(page + 1)} className="btn-ghost text-xs">Next</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
