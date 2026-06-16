import json
import uuid
from pathlib import Path

import numpy as np

from app.config import settings
from app.rag.embeddings import embed_query, embed_texts

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
STORE_FILE = DATA_DIR / "vector_store.json"


class VectorStore:
    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.documents: list[str] = []
        self.embeddings: np.ndarray | None = None
        self.metadatas: list[dict] = []
        self._load()

    def _load(self) -> None:
        if not STORE_FILE.exists():
            return
        try:
            data = json.loads(STORE_FILE.read_text(encoding="utf-8"))
            self.documents = data.get("documents", [])
            self.metadatas = data.get("metadatas", [])
            embeddings = data.get("embeddings", [])
            self.embeddings = np.array(embeddings, dtype=np.float32) if embeddings else None
        except (json.JSONDecodeError, OSError):
            self.documents = []
            self.metadatas = []
            self.embeddings = None

    def _save(self) -> None:
        payload = {
            "documents": self.documents,
            "metadatas": self.metadatas,
            "embeddings": self.embeddings.tolist() if self.embeddings is not None else [],
        }
        STORE_FILE.write_text(json.dumps(payload), encoding="utf-8")

    def add_documents(self, documents: list[dict]) -> int:
        if not documents:
            return 0

        texts = [doc["text"] for doc in documents]
        new_embeddings = np.array(embed_texts(texts), dtype=np.float32)
        new_metadatas = [doc["metadata"] for doc in documents]

        if self.embeddings is None or len(self.documents) == 0:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

        self.documents.extend(texts)
        self.metadatas.extend(new_metadatas)
        self._save()
        return len(documents)

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        top_k = top_k or settings.top_k_results
        if not self.documents or self.embeddings is None:
            return []

        query_vec = np.array(embed_query(query), dtype=np.float32)
        norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_vec)
        norms = np.where(norms == 0, 1e-10, norms)
        scores = np.dot(self.embeddings, query_vec) / norms

        k = min(top_k, len(self.documents))
        top_indices = np.argsort(scores)[::-1][:k]

        return [
            {
                "text": self.documents[i],
                "metadata": self.metadatas[i],
                "score": float(scores[i]),
            }
            for i in top_indices
        ]

    def get_stats(self) -> dict:
        return {"document_chunks": len(self.documents)}

    def clear(self) -> None:
        self.documents = []
        self.metadatas = []
        self.embeddings = None
        if STORE_FILE.exists():
            STORE_FILE.unlink()


vector_store = VectorStore()
