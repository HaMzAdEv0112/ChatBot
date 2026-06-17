import io
import re
from pathlib import Path

import streamlit as st
from groq import Groq
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SAMPLES_DIR = Path(__file__).parent / "backend" / "data" / "samples"
SYSTEM_PROMPT = """You are a helpful university assistant for the Complex Computing Problem (CCP) course.
Answer using ONLY the provided context from the knowledge base.
If the context is insufficient, say so clearly. Be concise and educational."""

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


def rebuild_index(docs: list[dict]) -> None:
    st.session_state.documents = docs
    if not docs:
        st.session_state.vectorizer = None
        st.session_state.matrix = None
        return
    texts = [d["text"] for d in docs]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    matrix = vectorizer.fit_transform(texts)
    st.session_state.vectorizer = vectorizer
    st.session_state.matrix = matrix


def search(query: str, top_k: int, min_score: float) -> list[dict]:
    docs = st.session_state.documents
    vectorizer = st.session_state.vectorizer
    matrix = st.session_state.matrix
    if not docs or vectorizer is None or matrix is None:
        return []

    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, matrix).flatten()
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
    results = []
    for idx, score in ranked:
        if score < min_score:
            continue
        d = docs[idx]
        results.append({"text": d["text"], "source": d["source"], "score": float(score)})
    return results


def build_context(chunks: list[dict]) -> str:
    return "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in chunks)


def answer_local(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return (
            "No relevant course material found. Try another question or upload documents in the sidebar."
        )
    lines = ["**Retrieved from knowledge base (TF-IDF):**\n"]
    for c in chunks:
        lines.append(f"**{c['source']}** ({c['score']:.0%} match)\n{c['text']}\n")
    return "\n".join(lines)


def answer_groq(query: str, chunks: list[dict], model: str) -> str:
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key or api_key.startswith("gsk_your"):
        return "⚠️ Add your free **GROQ_API_KEY** in Streamlit Secrets to use Groq AI mode."

    context = build_context(chunks) if chunks else "No matching documents found."
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer from context only:",
            },
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content or ""


def init_state() -> None:
    if "ready" not in st.session_state:
        st.session_state.ready = True
        st.session_state.messages = []
        rebuild_index(load_samples())


def main() -> None:
    st.set_page_config(
        page_title="CCP RAG Chatbot",
        page_icon="🧠",
        layout="wide",
    )
    init_state()

    with st.sidebar:
        st.title("⚙️ Configuration")
        mode = st.radio(
            "Engine",
            ["Groq AI (Fast)", "Local Engine (TF-IDF)"],
            help="Groq = free cloud AI + RAG. Local = TF-IDF retrieval only.",
        )
        st.divider()
        st.subheader("🔧 Retrieval Settings")
        top_k = st.slider("Top K results", 1, 8, 4)
        min_score = st.slider("Min relevance", 0.0, 0.8, 0.08, 0.01)
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
            new_docs = ingest_upload(
                uploaded.name, uploaded.read(), suffix, chunk_size, chunk_overlap
            )
            if new_docs:
                rebuild_index(st.session_state.documents + new_docs)
                st.success(f"Added {len(new_docs)} chunks from {uploaded.name}")
        if st.button("Clear knowledge base"):
            rebuild_index(load_samples())
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

    col1, col2, col3 = st.columns(3)
    col1.caption("⚡ RAG-Powered")
    col2.caption("● Online" if mode.startswith("Groq") else "● Local TF-IDF")
    col3.caption("🎓 CCP Project")

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
                    "technologies, or upload your own course files in the sidebar."
                )
                sources = []
            else:
                sources = search(prompt, top_k, min_score)
                if mode.startswith("Groq"):
                    reply = answer_groq(prompt, sources, groq_model)
                else:
                    reply = answer_local(prompt, sources)
            st.markdown(reply)
            if sources:
                with st.expander("Sources"):
                    for s in sources:
                        st.caption(f"**{s['source']}** — {s['score']:.0%}")

        st.session_state.messages.append(
            {"role": "assistant", "content": reply, "sources": sources}
        )

    st.caption(
        "Local mode uses TF-IDF retrieval · Groq mode uses RAG + LLaMA (free tier) · "
        "Add `GROQ_API_KEY` in Streamlit Cloud Secrets"
    )


if __name__ == "__main__":
    main()
