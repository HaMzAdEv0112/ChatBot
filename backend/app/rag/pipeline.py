from pathlib import Path

from app.rag.document_loader import ingest_file
from app.rag.llm import filter_relevant_chunks, generate_answer, greeting_response, is_greeting
from app.rag.vectorstore import vector_store


class RAGPipeline:
    def ingest_path(self, file_path: Path) -> dict:
        documents = ingest_file(file_path)
        added = vector_store.add_documents(documents)
        return {
            "filename": file_path.name,
            "chunks_added": added,
        }

    def chat(self, query: str) -> dict:
        query = query.strip()
        if is_greeting(query):
            return {"answer": greeting_response(), "sources": []}

        context_chunks = vector_store.search(query)
        relevant_chunks = filter_relevant_chunks(context_chunks)
        answer = generate_answer(query, relevant_chunks)
        sources = [
            {
                "source": chunk["metadata"].get("source", "unknown"),
                "score": round(chunk["score"], 3),
                "excerpt": chunk["text"][:200] + ("..." if len(chunk["text"]) > 200 else ""),
            }
            for chunk in relevant_chunks
        ]
        return {
            "answer": answer,
            "sources": sources,
        }

    def get_stats(self) -> dict:
        return vector_store.get_stats()

    def clear_knowledge_base(self) -> None:
        vector_store.clear()


rag_pipeline = RAGPipeline()
