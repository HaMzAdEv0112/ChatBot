@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
echo Starting CCP RAG Backend on http://localhost:8000
uvicorn app.main:app --reload --port 8000
