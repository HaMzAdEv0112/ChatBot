import { useRef, useState } from 'react'
import { clearKnowledgeBase, uploadDocument } from '../api'

export default function Sidebar({ stats, onStatsChange }) {
  const fileInputRef = useRef(null)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [clearing, setClearing] = useState(false)

  const handleUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setUploadStatus(null)

    try {
      const result = await uploadDocument(file)
      setUploadStatus({
        type: 'success',
        text: `"${result.filename}" added (${result.chunks_added} chunks)`,
      })
      onStatsChange?.()
    } catch (err) {
      setUploadStatus({ type: 'error', text: err.message })
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleClear = async () => {
    if (!confirm('Clear all documents from the knowledge base?')) return

    setClearing(true)
    try {
      await clearKnowledgeBase()
      setUploadStatus({ type: 'success', text: 'Knowledge base cleared' })
      onStatsChange?.()
    } catch (err) {
      setUploadStatus({ type: 'error', text: err.message })
    } finally {
      setClearing(false)
    }
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Knowledge Base</h2>
        <p className="sidebar-subtitle">Upload course materials for RAG retrieval</p>
      </div>

      <div className="stats-card">
        <div className="stat">
          <span className="stat-value">{stats?.knowledge_base_chunks ?? '—'}</span>
          <span className="stat-label">Document chunks</span>
        </div>
        <div className="stat">
          <span className="stat-value stat-provider">{stats?.llm_provider ?? '—'}</span>
          <span className="stat-label">LLM provider</span>
        </div>
      </div>

      <div className="upload-section">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.md"
          onChange={handleUpload}
          hidden
          id="file-upload"
        />
        <label htmlFor="file-upload" className={`upload-btn ${uploading ? 'disabled' : ''}`}>
          {uploading ? 'Uploading...' : 'Upload Document'}
        </label>
        <p className="upload-hint">PDF, TXT, or Markdown</p>
      </div>

      {uploadStatus && (
        <div className={`status-banner ${uploadStatus.type}`}>{uploadStatus.text}</div>
      )}

      <button className="clear-btn" onClick={handleClear} disabled={clearing}>
        {clearing ? 'Clearing...' : 'Clear Knowledge Base'}
      </button>

      <div className="sidebar-info">
        <h3>How it works</h3>
        <ol>
          <li>Documents are chunked and embedded</li>
          <li>Your question retrieves relevant passages</li>
          <li>An LLM generates an answer from context</li>
        </ol>
      </div>
    </aside>
  )
}
