import { useCallback, useEffect, useState } from 'react'
import { getHealth } from './api'
import ChatWindow from './components/ChatWindow'
import Sidebar from './components/Sidebar'

export default function App() {
  const [stats, setStats] = useState(null)
  const [backendOnline, setBackendOnline] = useState(true)

  const refreshStats = useCallback(async () => {
    try {
      const data = await getHealth()
      setStats(data)
      setBackendOnline(true)
    } catch {
      setBackendOnline(false)
    }
  }, [])

  useEffect(() => {
    refreshStats()
    const interval = setInterval(refreshStats, 30000)
    return () => clearInterval(interval)
  }, [refreshStats])

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">CCP</div>
            <div>
              <h1>RAG Chatbot</h1>
              <p>Complex Computing Problem Assistant</p>
            </div>
          </div>
          <div className={`status-badge ${backendOnline ? 'online' : 'offline'}`}>
            <span className="status-dot"></span>
            {backendOnline ? 'Backend connected' : 'Backend offline'}
          </div>
        </div>
      </header>

      <main className="main">
        <Sidebar stats={stats} onStatsChange={refreshStats} />
        <ChatWindow onStatsChange={refreshStats} />
      </main>
    </div>
  )
}
