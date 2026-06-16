import re

import httpx
from openai import OpenAI

from app.config import settings

SYSTEM_PROMPT = """You are a helpful university assistant for the Complex Computing Problem (CCP) course.
Answer questions using ONLY the provided context from the knowledge base.
If the context does not contain enough information, say so clearly and suggest what the student could look up.
Be concise, accurate, and educational. Cite the source document when relevant."""

GREETING_PATTERN = re.compile(
    r"^(hi|hello|hey|hola|salam|assalam|good\s+(morning|afternoon|evening)|"
    r"how\s+are\s+you|what'?s\s+up|yo|sup)[\s!.?]*$",
    re.IGNORECASE,
)


def is_greeting(query: str) -> bool:
    return bool(GREETING_PATTERN.match(query.strip()))


def greeting_response() -> str:
    return (
        "Hello! I'm your CCP course assistant. "
        "Ask me about the Complex Computing Problem module — topics like assessment, "
        "RAG architecture, recommended technologies, or deadlines. "
        "You can also upload your own PDF or notes using the sidebar."
    )


def filter_relevant_chunks(context_chunks: list[dict]) -> list[dict]:
    threshold = settings.min_relevance_score
    return [chunk for chunk in context_chunks if chunk["score"] >= threshold]


def build_prompt(query: str, context_chunks: list[dict]) -> str:
    if not context_chunks:
        return f"""No relevant documents were found in the knowledge base.

Student question: {query}

Please respond that no matching course material was found and suggest uploading relevant documents."""

    context_block = "\n\n".join(
        f"[Source: {chunk['metadata'].get('source', 'unknown')}]\n{chunk['text']}"
        for chunk in context_chunks
    )
    return f"""Context from knowledge base:
{context_block}

Student question: {query}

Answer based on the context above:"""


def generate_with_openai(prompt: str) -> str:
    if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key":
        raise ValueError("OpenAI API key is not configured. Set OPENAI_API_KEY in backend/.env")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def generate_with_ollama(prompt: str) -> str:
    url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.3},
    }
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
    except httpx.ConnectError:
        raise ValueError(
            "Cannot connect to Ollama. Start Ollama and run: ollama pull "
            f"{settings.ollama_model}"
        )


def generate_context_only(_prompt: str, context_chunks: list[dict]) -> str:
    if not context_chunks:
        return (
            "I couldn't find relevant course material for that question. "
            "Try asking about CCP assessment, RAG pipeline, or recommended technologies — "
            "or upload your own documents using the sidebar."
        )

    intro = "Here's what I found in the course materials:\n\n"
    excerpts = "\n\n---\n\n".join(
        f"**{chunk['metadata'].get('source', 'Document')}** (relevance: {chunk['score']:.0%})\n"
        f"{chunk['text']}"
        for chunk in context_chunks
    )
    footer = (
        "\n\n---\n\n*Tip: Install Ollama or add an OpenAI key in backend/.env "
        "for natural AI answers instead of raw document excerpts.*"
    )
    return intro + excerpts + footer


def generate_answer(query: str, context_chunks: list[dict]) -> str:
    if is_greeting(query):
        return greeting_response()

    relevant_chunks = filter_relevant_chunks(context_chunks)
    prompt = build_prompt(query, relevant_chunks)
    provider = settings.llm_provider.lower()

    if provider == "openai":
        return generate_with_openai(prompt)
    if provider == "ollama":
        return generate_with_ollama(prompt)
    return generate_context_only(prompt, relevant_chunks)
