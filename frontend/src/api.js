// Dev: Vite proxy → localhost:8000. Production (XAMPP/dist): direct to backend.
const API_BASE = import.meta.env.DEV ? '/api' : 'http://localhost:8000/api'

export async function sendMessage(message) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })

  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to get response')
  }
  return data
}

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  })

  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.detail || 'Upload failed')
  }
  return data
}

export async function getHealth() {
  const response = await fetch(`${API_BASE}/health`)
  if (!response.ok) {
    throw new Error('Backend unavailable')
  }
  return response.json()
}

export async function clearKnowledgeBase() {
  const response = await fetch(`${API_BASE}/knowledge-base`, {
    method: 'DELETE',
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to clear knowledge base')
  }
  return data
}
