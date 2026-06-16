# Complex Computing Problem (CCP) — Project Report

## RAG-Based University Chatbot

**Project Title:** CCP RAG Chatbot — Retrieval-Augmented Generation Course Assistant  
**Module:** Complex Computing Problem (CCP)  
**Type:** Full-Stack Web Application with AI  

---

## 1. Introduction

This project is a **Retrieval-Augmented Generation (RAG)** chatbot designed to help university students with **Complex Computing Problem (CCP)** course content. Instead of relying only on a Large Language Model (LLM) — which can hallucinate or give outdated answers — the system first **searches a knowledge base** of course documents and then uses that retrieved context to generate accurate, grounded responses.

The application consists of a **React frontend** for the chat interface and a **Python FastAPI backend** that handles document ingestion, semantic search, and AI answer generation.

---

## 2. Problem Statement

University students often need quick answers about course modules, assessment criteria, deadlines, and technical concepts. Traditional chatbots without access to course materials may:

- Give incorrect or generic answers
- Invent information (hallucination)
- Not cite where answers come from

**Solution:** Build a RAG chatbot that answers questions **only from uploaded/ingested course documents**, shows **source citations**, and supports **natural language** interaction.

---

## 3. Project Objectives

| # | Objective | Status |
|---|-----------|--------|
| 1 | Build a modern React chat UI | ✅ Completed |
| 2 | Implement document upload (PDF, TXT, MD) | ✅ Completed |
| 3 | Create semantic search over course materials | ✅ Completed |
| 4 | Integrate LLM for natural language answers | ✅ Completed (Ollama) |
| 5 | Show source citations with relevance scores | ✅ Completed |
| 6 | Provide REST API with documentation | ✅ Completed |
| 7 | Pre-load sample CCP course documents | ✅ Completed |

---

## 4. Technologies Used & Why

### 4.1 Frontend

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **React 18** | UI components & state management | Industry-standard, component-based, required by project brief |
| **Vite** | Build tool & dev server | Fast HMR, modern replacement for Create React App |
| **CSS (Custom)** | Styling & dark theme UI | Lightweight, no extra UI library dependency |
| **Poppins (Google Font)** | Typography | Clean, modern, readable font for academic UI |

### 4.2 Backend

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **Python 3.12** | Server language | Best ecosystem for AI/ML and RAG pipelines |
| **FastAPI** | REST API framework | Fast, async, automatic OpenAPI/Swagger docs |
| **Uvicorn** | ASGI server | Production-ready server for FastAPI |
| **Pydantic / pydantic-settings** | Data validation & config | Type-safe request/response models and `.env` loading |
| **python-dotenv** | Environment variables | Keeps API keys and config out of source code |

### 4.3 RAG Pipeline

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **sentence-transformers** | Text embeddings | Converts text to vectors for semantic similarity search |
| **all-MiniLM-L6-v2** | Embedding model | Small, fast, runs locally, no API cost |
| **NumPy** | Vector math (cosine similarity) | Efficient similarity calculations between query and documents |
| **JSON file store** | Vector database | Lightweight persistence without C++ build tools (ChromaDB alternative for Windows compatibility) |
| **pypdf** | PDF text extraction | Allows students to upload PDF course notes |

### 4.4 Large Language Model (LLM)

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **Ollama** | Local LLM runtime | Free, runs offline, no API key needed, good for CCP demo |
| **llama3.2** | Language model | Balanced size vs quality for local machines |
| **OpenAI (optional)** | Cloud LLM fallback | Can be enabled via `.env` if user has API key |
| **context_only mode** | Retrieval without LLM | Useful for testing when no AI model is available |

### 4.5 Deployment / Local Server

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **XAMPP (Apache)** | Serve frontend build | Already available on developer machine (`htdocs`) |
| **`.htaccess` + `index.php`** | Redirect to production build | Fixes routing when accessing `/ChatBot/frontend/` via Apache |

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER (Browser)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              REACT FRONTEND (Vite / XAMPP)                  │
│  • ChatWindow  • Sidebar  • Document Upload  • API calls    │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API (port 8000)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 FASTAPI BACKEND (Python)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  /api/chat  │  │ /api/upload  │  │  /api/health     │  │
│  └──────┬──────┘  └──────┬───────┘  └──────────────────┘  │
│         │                │                                 │
│         ▼                ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              RAG PIPELINE                           │   │
│  │  1. Document Loader (chunk PDF/TXT/MD)              │   │
│  │  2. Embeddings (sentence-transformers)              │   │
│  │  3. Vector Store (NumPy + JSON)                     │   │
│  │  4. Retrieval (cosine similarity, top-K)            │   │
│  │  5. LLM Generation (Ollama / OpenAI)                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Ollama (localhost:11434)  +  vector_store.json           │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. How RAG Works (Step by Step)

### Step 1 — Document Ingestion
- User uploads PDF, TXT, or Markdown files (or sample docs load on startup)
- Text is extracted and split into **chunks** (500 characters, 50 overlap)
- **Why chunking?** LLMs have context limits; smaller chunks improve retrieval accuracy

### Step 2 — Embedding
- Each chunk is converted to a **384-dimensional vector** using `all-MiniLM-L6-v2`
- **Why embeddings?** Enables semantic search — finds meaning, not just keywords

### Step 3 — Storage
- Vectors + text + metadata saved to `backend/data/vector_store.json`
- **Why JSON store?** Simple, portable, no extra database server needed

### Step 4 — Retrieval (when user asks a question)
- User query is embedded into the same vector space
- **Cosine similarity** finds top 4 most relevant chunks
- Chunks below **35% relevance** are filtered out
- **Why threshold?** Prevents irrelevant document dumps for vague queries like "Hello"

### Step 5 — Generation
- Relevant chunks + user question sent to **Ollama (llama3.2)**
- LLM generates a natural language answer grounded in the context
- **Why RAG?** Reduces hallucination; answers are based on actual course material

### Step 6 — Response
- Answer displayed in chat UI with **source citations** and relevance scores

---

## 7. Features Implemented

### Chat Interface
- Real-time messaging with user/AI bubbles
- Typing indicator while waiting for response
- Suggested question chips for new users
- Source citations under each AI reply

### Knowledge Base Panel
- Document upload (PDF, TXT, MD)
- Live stats: chunk count & LLM provider
- Clear knowledge base button
- "How it works" guide in sidebar

### Smart Behaviour
- Greeting detection ("Hello", "Hi") → friendly welcome, no document dump
- Relevance filtering → only useful chunks shown
- Backend health indicator (connected/offline)
- CORS configured for localhost & XAMPP

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server status & KB stats |
| POST | `/api/chat` | Send message, get RAG answer |
| POST | `/api/upload` | Upload document to knowledge base |
| DELETE | `/api/knowledge-base` | Clear all documents |
| GET | `/docs` | Interactive Swagger API documentation |

---

## 8. Project Structure

```
ChatBot/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + CORS + startup
│   │   ├── config.py               # Settings from .env
│   │   ├── routes/chat.py          # API route handlers
│   │   └── rag/
│   │       ├── document_loader.py  # PDF/TXT parsing & chunking
│   │       ├── embeddings.py       # sentence-transformers wrapper
│   │       ├── vectorstore.py      # NumPy + JSON vector DB
│   │       ├── llm.py              # Ollama/OpenAI/context-only
│   │       └── pipeline.py         # RAG orchestration
│   ├── data/samples/               # Pre-loaded CCP documents
│   ├── .env.example                # Config template (safe to share)
│   ├── requirements.txt            # Python dependencies
│   └── start.bat                   # One-click backend start
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main layout
│   │   ├── api.js                  # Backend API client
│   │   └── components/
│   │       ├── ChatWindow.jsx      # Chat UI
│   │       ├── MessageBubble.jsx   # Message + sources display
│   │       └── Sidebar.jsx         # Upload & stats panel
│   ├── .htaccess                   # XAMPP Apache config
│   ├── index.php                   # Redirect to dist/
│   └── start.bat                   # One-click dev server
├── README.md                       # Setup instructions
├── CCP_REPORT.md                   # This report
└── .gitignore                      # Excludes secrets & build files
```

---

## 9. Configuration (.env)

All sensitive config is in `backend/.env` (NOT pushed to GitHub):

```env
LLM_PROVIDER=ollama          # ollama | openai | context_only
OLLAMA_MODEL=llama3.2
OPENAI_API_KEY=your-key      # only if using OpenAI
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=4
MIN_RELEVANCE_SCORE=0.35
```

---

## 10. How to Run

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (for AI answers)
- XAMPP (optional, for Apache hosting)

### Backend
```powershell
cd backend
copy .env.example .env
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
.\start.bat
```

### Frontend (Development)
```powershell
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Frontend (Production via XAMPP)
```powershell
cd frontend
npm run build
# Open http://localhost/ChatBot/frontend/dist/
```

### Ollama
```powershell
ollama pull llama3.2
```

---

## 11. Testing & Sample Questions

| Question | Expected Behaviour |
|----------|-------------------|
| "Hello" | Friendly greeting, no sources |
| "What is the CCP module about?" | AI answer from course overview doc |
| "What are the assessment components?" | Lists proposal, interim, final marks |
| "How does a RAG pipeline work?" | Explains ingest → embed → retrieve → generate |
| Upload a PDF | New chunks added to knowledge base |

---

## 12. Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| ChromaDB needed C++ build tools on Windows | Replaced with NumPy + JSON vector store |
| XAMPP served dev `index.html` (404 on main.jsx) | Added `.htaccess`, `index.php` redirect, Vite `base: './'` |
| "Hello" returned irrelevant document chunks | Added greeting detection + relevance threshold (35%) |
| Backend showed "offline" on frontend | CORS updated for `http://localhost`; backend must run on port 8000 |
| context_only mode dumped raw text | Switched to Ollama for natural AI answers |

---

## 13. Future Improvements

- Conversation history (multi-turn chat)
- Streaming responses (word-by-word typing)
- User authentication
- Docker deployment
- Hybrid search (keyword + semantic)
- Admin dashboard for document management
- Deploy to cloud (Vercel frontend + Railway/Render backend)

---

## 14. Conclusion

This project successfully demonstrates a **production-style RAG chatbot** for university CCP coursework. It combines **modern web development** (React, FastAPI) with **AI/ML concepts** (embeddings, vector search, LLM integration) to solve a real educational problem: giving students accurate, cited answers from course materials.

The system is modular, configurable, and runs entirely on a local machine without paid API dependencies (when using Ollama).

---

## 15. References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [sentence-transformers](https://www.sbert.net/)
- [Ollama](https://ollama.com/)
- [RAG — Retrieval Augmented Generation (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401)

---

*Report generated for CCP module submission.*
