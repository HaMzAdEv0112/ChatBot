# RAG Architecture & Implementation Guide

## System Architecture

```
┌─────────────┐     HTTP/REST     ┌─────────────┐
│   React     │ ◄──────────────► │   FastAPI   │
│  Frontend   │                   │   Backend   │
└─────────────┘                   └──────┬──────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
             ┌───────────┐       ┌─────────────┐      ┌───────────┐
             │  ChromaDB │       │  Embeddings │      │    LLM    │
             │  Vector   │       │  (MiniLM)   │      │ (Ollama/  │
             │   Store   │       │             │      │  OpenAI)  │
             └───────────┘       └─────────────┘      └───────────┘
```

## Backend Stack

- **FastAPI:** High-performance Python web framework with automatic OpenAPI docs
- **ChromaDB:** Embedded vector database for similarity search
- **sentence-transformers:** Local embedding model (all-MiniLM-L6-v2)
- **pypdf:** PDF text extraction for document ingestion

## Frontend Stack

- **React 18:** Component-based UI library
- **Vite:** Fast development server and build tool
- **CSS:** Custom styling for a modern chat interface

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Health check and KB stats |
| POST | /api/chat | Send a message, receive RAG answer |
| POST | /api/upload | Upload PDF/TXT/MD to knowledge base |
| DELETE | /api/knowledge-base | Clear all ingested documents |

## Configuration

Copy `backend/.env.example` to `backend/.env` and configure:

### Option 1: Ollama (Free, Local)
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```
Run: `ollama pull llama3.2`

### Option 2: OpenAI (Cloud)
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Option 3: Context Only (No LLM)
```
LLM_PROVIDER=context_only
```
Returns retrieved document excerpts without AI generation.

## Running the Project

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Evaluation Criteria for CCP

When evaluating your RAG chatbot, consider:

1. **Retrieval Accuracy:** Does it find relevant documents?
2. **Answer Quality:** Are responses accurate and grounded in context?
3. **Latency:** Response time under 5 seconds for typical queries
4. **Usability:** Clean UI, clear error messages, upload workflow
5. **Robustness:** Handles empty KB, missing LLM, invalid files gracefully

## Possible Extensions

- Conversation history / multi-turn chat
- User authentication and per-user document stores
- Streaming responses for real-time typing effect
- Hybrid search (keyword + semantic)
- Admin dashboard for document management
- Deployment with Docker Compose
