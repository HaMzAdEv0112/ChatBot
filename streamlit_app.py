import io
import json
import math
import re
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

import streamlit as st
from pypdf import PdfReader

SAMPLES_DIR = Path(__file__).parent / "backend" / "data" / "samples"
SYSTEM_PROMPT = """You are a helpful university assistant for the Complex Computing Problem (CCP) course.
Answer using ONLY the provided context from the knowledge base.
If the context is insufficient, say so clearly. Be concise and educational."""

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
    "and", "or", "but", "if", "then", "than", "that", "this", "these",
    "those", "it", "its", "what", "which", "who", "how", "when", "where", "why",
}

GREETING = re.compile(
    r"^(hi|hello|hey|salam|assalam|good\s+(morning|afternoon|evening))[\s!.?]*$",
    re.IGNORECASE,
)

SUGGESTIONS = [
    "What is the CCP module about?",
    "What are the assessment components?",
    "How does a RAG pipeline work?",
    "What technologies are recommended?",
]


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        piece = text[start : start + size].strip()
        if piece:
            chunks.append(piece)
        start += size - overlap
    return chunks


def tokenize(text: str) -> list[str]:
    return [
        w for w in re.findall(r"[a-z0-9]+", text.lower())
        if len(w) > 2 and w not in STOP_WORDS
    ]


def load_samples() -> list[dict]:
    docs = []
    if not SAMPLES_DIR.exists():
        return docs
    for path in sorted(SAMPLES_DIR.glob("*")):
        if path.suffix.lower() in {".md", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for i, chunk in enumerate(chunk_text(text, 500, 50)):
                docs.append({"text": chunk, "source": path.name, "chunk_index": i})
    return docs


def ingest_upload(name: str, raw: bytes, suffix: str, size: int, overlap: int) -> list[dict]:
    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(raw))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = raw.decode("utf-8", errors="ignore")

    return [
        {"text": c, "source": name, "chunk_index": i}
        for i, c in enumerate(chunk_text(text, size, overlap))
    ]


def set_documents(docs: list[dict]) -> None:
    st.session_state.documents = docs


def search(query: str, top_k: int, min_score: float) -> list[dict]:
    docs = st.session_state.get("documents", [])
    if not docs:
        return []

    q_tokens = tokenize(query)
    if not q_tokens:
        return []

    q_counts = Counter(q_tokens)
    q_norm = math.sqrt(sum(v * v for v in q_counts.values())) or 1.0
    results = []

    for doc in docs:
        d_tokens = tokenize(doc["text"])
        if not d_tokens:
            continue
        d_counts = Counter(d_tokens)
        dot = sum(q_counts[t] * d_counts.get(t, 0) for t in q_counts)
        d_norm = math.sqrt(sum(v * v for v in d_counts.values())) or 1.0
        score = dot / (q_norm * d_norm)
        if score >= min_score:
            results.append({
                "text": doc["text"],
                "source": doc["source"],
                "score": float(score),
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def build_context(chunks: list[dict]) -> str:
    return "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in chunks)


def answer_local(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant course material found. Try another question or upload documents in the sidebar."
    lines = ["**Retrieved from knowledge base:**\n"]
    for c in chunks:
        lines.append(f"**{c['source']}** ({c['score']:.0%} match)\n{c['text']}\n")
    return "\n".join(lines)


def answer_groq(query: str, chunks: list[dict], model: str) -> str:
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key or "your" in api_key.lower():
        return "Add your free **GROQ_API_KEY** in Streamlit Cloud → Settings → Secrets."

    context = build_context(chunks) if chunks else "No matching documents found."
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer from context only:",
            },
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }).encode()

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        return data["choices"][0]["message"]["content"] or ""
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="ignore")
        return f"Groq API error ({exc.code}). Check your GROQ_API_KEY in Secrets."
    except Exception:
        return "Could not reach Groq API. Try again in a moment."


def init_state() -> None:
    if "ready" not in st.session_state:
        st.session_state.ready = True
        st.session_state.messages = []
        set_documents(load_samples())


st.set_page_config(page_title="CCP RAG Chatbot", page_icon="🧠", layout="wide")
init_state()

with st.sidebar:
    st.title("⚙️ Configuration")
    mode = st.radio("Engine", ["Groq AI (Fast)", "Local Engine (Keyword)"])
    st.divider()
    st.subheader("🔧 Retrieval Settings")
    top_k = st.slider("Top K results", 1, 8, 4)
    min_score = st.slider("Min relevance", 0.0, 0.8, 0.05, 0.01)
    chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
    chunk_overlap = st.slider("Chunk overlap", 0, 200, 50, 10)
    st.divider()
    groq_model = "llama-3.1-8b-instant"
    if mode.startswith("Groq"):
        groq_model = st.selectbox(
            "🤖 Model",
            ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
        )
    st.divider()
    st.metric("Document chunks", len(st.session_state.documents))
    uploaded = st.file_uploader("Upload PDF / TXT / MD", type=["pdf", "txt", "md"])
    if uploaded:
        suffix = Path(uploaded.name).suffix.lower()
        new_docs = ingest_upload(uploaded.name, uploaded.read(), suffix, chunk_size, chunk_overlap)
        if new_docs:
            set_documents(st.session_state.documents + new_docs)
            st.success(f"Added {len(new_docs)} chunks from {uploaded.name}")
    if st.button("Clear knowledge base"):
        set_documents(load_samples())
        st.session_state.messages = []
        st.rerun()

st.markdown(
    """
    <div style='text-align:center;padding:1rem 0'>
        <h1>🧠 CCP RAG Knowledge Chatbot</h1>
        <p>Complex Computing Problem · RAG + Groq AI · By HaMzA</p>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
c1.caption("⚡ RAG-Powered")
c2.caption("● Online" if mode.startswith("Groq") else "● Local")
c3.caption("🎓 CCP Project")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for s in msg["sources"]:
                    st.caption(f"{s['source']} — {s['score']:.0%} match")

if not st.session_state.messages:
    st.caption("Suggested questions:")
    cols = st.columns(2)
    for i, q in enumerate(SUGGESTIONS):
        if cols[i % 2].button(q, key=f"suggest_{i}", use_container_width=True):
            st.session_state.pending = q
            st.rerun()

prompt = st.chat_input("Ask about CCP course content...")
if st.session_state.get("pending"):
    prompt = st.session_state.pop("pending")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if GREETING.match(prompt.strip()):
            reply = (
                "Hello! I'm your CCP assistant. Ask about assessment, RAG architecture, "
                "technologies, or upload course files in the sidebar."
            )
            sources = []
        else:
            sources = search(prompt, top_k, min_score)
            reply = answer_groq(prompt, sources, groq_model) if mode.startswith("Groq") else answer_local(prompt, sources)
        st.markdown(reply)
        if sources:
            with st.expander("Sources"):
                for s in sources:
                    st.caption(f"**{s['source']}** — {s['score']:.0%}")

    st.session_state.messages.append({"role": "assistant", "content": reply, "sources": sources})

st.caption("Groq mode = RAG + LLaMA (free) · Local mode = keyword retrieval")
