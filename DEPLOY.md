# Live Deploy Guide — Streamlit Cloud

Professor example: https://pdc-rag-chatbot-saad.streamlit.app/

Your app will get a URL like: **https://chatbot-hamza.streamlit.app/**

Same stack as Saad's project:
- **Streamlit** — live web UI
- **Groq AI** — free LLM (`llama-3.1-8b-instant`)
- **TF-IDF** — local retrieval mode (no API key needed)

---

## Step 1: Get FREE Groq API Key

1. Open https://console.groq.com/
2. Sign up (free)
3. Go to **API Keys** → Create key
4. Copy key (starts with `gsk_...`)

---

## Step 2: Push code to GitHub

```powershell
cd c:\xampp\htdocs\ChatBot
git add .
git commit -m "Add Streamlit live deployment"
git push
```

Make sure these files are on GitHub:
- `streamlit_app.py`
- `requirements.txt` (root folder)
- `.streamlit/config.toml`
- `backend/data/samples/` (course documents)

---

## Step 3: Deploy on Streamlit Cloud

1. Open https://share.streamlit.io/
2. Sign in with **GitHub**
3. Click **New app**
4. Fill in:
   - **Repository:** `HaMzAdEv0112/ChatBot`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
5. Click **Advanced settings**
   - Python version: **3.12**
6. Click **Deploy**

Wait 2–5 minutes for first build.

---

## Step 4: Add Groq API Key (Secrets)

1. On your app page → **Manage app** (bottom right)
2. Click **Settings** → **Secrets**
3. Paste this:

```toml
GROQ_API_KEY = "gsk_paste_your_real_key_here"
```

4. Click **Save** — app will restart automatically

---

## Step 5: Share live link

Your live URL will be:

```
https://YOUR-APP-NAME.streamlit.app/
```

Add this to:
- GitHub repo **About** section (Website field)
- CCP Report
- Presentation slides

---

## Test locally before deploy

```powershell
cd c:\xampp\htdocs\ChatBot
pip install -r requirements.txt
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# Edit secrets.toml and add your GROQ_API_KEY
streamlit run streamlit_app.py
```

Opens at http://localhost:8501

---

## Two modes in the app

| Mode | API Key needed? | Description |
|------|-----------------|-------------|
| **Groq AI (Fast)** | Yes (free) | RAG + natural AI answers |
| **Local Engine (TF-IDF)** | No | Shows retrieved document excerpts |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| App won't start | Check `requirements.txt` is in repo **root** |
| Groq error | Add `GROQ_API_KEY` in Streamlit Secrets |
| No documents | Ensure `backend/data/samples/` is pushed to GitHub |
| Build fails | Streamlit Cloud → Logs → check error message |

---

## For CCP submission

| Item | Value |
|------|-------|
| GitHub | https://github.com/HaMzAdEv0112/ChatBot |
| Live Demo | https://YOUR-APP-NAME.streamlit.app/ |
| Local Demo | React + FastAPI (see README.md) |

You now have **both**: live Streamlit link for sir + full React/FastAPI project for code marks.
