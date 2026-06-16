import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.config import settings
from app.rag.pipeline import rag_pipeline

router = APIRouter(prefix="/api", tags=["chat"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]


@router.get("/health")
def health_check():
    stats = rag_pipeline.get_stats()
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "knowledge_base_chunks": stats["document_chunks"],
    }


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = rag_pipeline.chat(request.message.strip())
        return result
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}") from exc


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        result = rag_pipeline.ingest_path(tmp_path)
        return {"message": "Document ingested successfully", **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc
    finally:
        tmp_path.unlink(missing_ok=True)


@router.delete("/knowledge-base")
def clear_knowledge_base():
    rag_pipeline.clear_knowledge_base()
    return {"message": "Knowledge base cleared"}
