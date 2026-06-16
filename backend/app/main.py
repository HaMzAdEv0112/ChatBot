from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.rag.document_loader import ingest_file
from app.rag.pipeline import rag_pipeline
from app.routes.chat import router as chat_router

app = FastAPI(
    title="CCP RAG Chatbot API",
    description="Retrieval-Augmented Generation chatbot for Complex Computing Problem",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.on_event("startup")
def load_sample_documents():
    samples_dir = Path(__file__).resolve().parents[1] / "data" / "samples"
    if not samples_dir.exists():
        return

    stats = rag_pipeline.get_stats()
    if stats["document_chunks"] > 0:
        return

    for file_path in sorted(samples_dir.glob("*")):
        if file_path.suffix.lower() in {".pdf", ".txt", ".md"}:
            try:
                documents = ingest_file(file_path)
                from app.rag.vectorstore import vector_store

                vector_store.add_documents(documents)
            except Exception:
                pass


@app.get("/")
def root():
    return {
        "message": "CCP RAG Chatbot API",
        "docs": "/docs",
        "health": "/api/health",
        "llm_provider": settings.llm_provider,
    }
