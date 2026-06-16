import { useEffect, useRef, useState } from 'react'
import { sendMessage } from '../api'
import MessageBubble from './MessageBubble'

const SUGGESTIONS = [
  'What is the CCP module about?',
  'What are the assessment components?',
  'How does a RAG pipeline work?',
  'What technologies are recommended?',
]

export default function ChatWindow({ onStatsChange }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        'Hello! I am your CCP course assistant. Ask me anything about Complex Computing Problem, or upload your own course materials.',
      sources: [],
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = async (text) => {
    const message = (text || input).trim()
    if (!message || loading) return

    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: message }])
    setLoading(true)

    try {
      const data = await sendMessage(message)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, sources: data.sources || [] },
      ])
      onStatsChange?.()
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${err.message}. Make sure the backend is running on port 8000.`,
          sources: [],
          isError: true,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-window">
      <div className="messages">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {loading && (
          <div className="message assistant loading">
            <div className="avatar">AI</div>
            <div className="bubble">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length <= 1 && (
        <div className="suggestions">
          {SUGGESTIONS.map((s) => (
            <button key={s} className="suggestion-chip" onClick={() => handleSend(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about CCP course content..."
          rows={1}
          disabled={loading}
        />
        <button
          className="send-btn"
          onClick={() => handleSend()}
          disabled={!input.trim() || loading}
          aria-label="Send message"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
          </svg>
        </button>
      </div>
    </div>
  )
}
