# CCP RAG Chatbot

A **Retrieval-Augmented Generation (RAG)** chatbot for the university **Complex Computing Problem (CCP)** module. Built with a **React** frontend and **Python FastAPI** backend.

## Architecture

```
React UI  →  FastAPI API  →  Vector Store + Embeddings + LLM (Ollama)
```

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite |
| Backend | FastAPI, Python 3.10+ |
| Vector DB | NumPy + JSON (lightweight, no C++ build tools) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Ollama (local) or OpenAI (cloud) |

## Features

- Chat interface with source citations
- Document upload (PDF, TXT, Markdown)
- Semantic search over course materials
- Pre-loaded sample CCP documents
- Configurable LLM provider (Ollama / OpenAI / context-only)
- REST API with auto-generated docs at `/docs`

## Live Demo (Streamlit Cloud) — for CCP presentation

Deploy a **live link** like the professor's example (`*.streamlit.app`):

1. Get free Groq key: https://console.groq.com/keys
2. Deploy at https://share.streamlit.io/ → connect GitHub repo
3. Main file: `streamlit_app.py`
4. Add `GROQ_API_KEY` in Streamlit Secrets

**Full step-by-step:** see [DEPLOY.md](DEPLOY.md)

```powershell
# Test Streamlit locally
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## Quick Start (Local React + FastAPI)

### 1. Backend (double-click or terminal)

```powershell
cd backend
.\start.bat
```

Or manually:

```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

### 3. LLM Setup (choose one)

**Option A — Ollama (recommended, free & local)**

```powershell
# Install Ollama from https://ollama.com, then:
ollama pull llama3.2
```

Set in `backend/.env`:
```
LLM_PROVIDER=ollama
```

**Option B — OpenAI**

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
```

**Option C — No LLM (retrieval only)**

```
LLM_PROVIDER=context_only
```

Returns matched document excerpts without AI generation.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Status and knowledge base stats |
| `POST` | `/api/chat` | `{"message": "your question"}` |
| `POST` | `/api/upload` | Upload PDF/TXT/MD file |
| `DELETE` | `/api/knowledge-base` | Clear all documents |

Interactive docs: **http://localhost:8000/docs**

## Project Structure

```
ChatBot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment settings
│   │   ├── routes/chat.py       # API routes
│   │   └── rag/
│   │       ├── document_loader.py
│   │       ├── embeddings.py
│   │       ├── vectorstore.py
│   │       ├── llm.py
│   │       └── pipeline.py
│   ├── data/samples/            # Pre-loaded CCP documents
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.jsx
        ├── api.js
        └── components/
            ├── ChatWindow.jsx
            ├── MessageBubble.jsx
            └── Sidebar.jsx
```

## How RAG Works

1. **Ingest** — Documents are split into chunks and converted to vectors
2. **Store** — Embeddings are saved in a JSON vector store (NumPy cosine search)
3. **Retrieve** — User query is embedded; top-K similar chunks are found
4. **Generate** — Retrieved context + query is sent to the LLM for an answer

## Sample Questions

- "What is the CCP module about?"
- "What are the assessment components?"
- "How does a RAG pipeline work?"
- "What technologies are recommended for CCP?"

## Push to GitHub

```powershell
cd c:\xampp\htdocs\ChatBot
git add .
git commit -m "Initial commit: CCP RAG chatbot with React frontend and FastAPI backend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

> `.env`, `venv/`, `node_modules/`, and `dist/` are in `.gitignore` — secrets and build artifacts won't be pushed.

## License

University CCP project — for educational use.
