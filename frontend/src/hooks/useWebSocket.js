import { useEffect, useRef, useState } from 'react'

const API = import.meta.env.VITE_API_URL || '/api'

export default function useWebSocket(apiKey) {
  const [lastAlert, setLastAlert] = useState(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    if (!apiKey) return
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const baseUrl = API.replace(/^https?:\/\//, '').replace('/api', '')
    const url = `${proto}://${baseUrl}/ws/${apiKey}`

    function connect() {
      const ws = new WebSocket(url)
      ws.onopen = () => setConnected(true)
      ws.onmessage = (e) => {
        const data = JSON.parse(e.data)
        if (data.type === 'new_alert') setLastAlert(data.alert)
      }
      ws.onclose = () => {
        setConnected(false)
        setTimeout(connect, 3000)
      }
      wsRef.current = ws
    }

    connect()
    return () => wsRef.current?.close()
  }, [apiKey])

  return { lastAlert, connected }
}
