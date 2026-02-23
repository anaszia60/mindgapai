# Updated MindGap AI files with voice-to-voice conversation
# (using Whisper for STT + gTTS for TTS + streamlit-audiorec)

## 1. README.md

```markdown
---
title: MindGap AI
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: streamlit
pinned: false
---

# MindGap AI - Adaptive Learning Companion with Voice Chat

Detects knowledge gaps, generates personalized micro-lessons and supports **voice-to-voice conversation** using free models.

## Tech Stack
- Frontend/Backend: Streamlit
- Vector DB: FAISS (local) or Pinecone (optional)
- Embeddings: sentence-transformers/all-MiniLM-L6-v2
- LLM: Groq (llama-3.3-70b-versatile)
- STT: openai-whisper (base model)
- TTS: gTTS (Google Translate TTS)
- Voice recording: st-audiorec component
- Database: SQLite
- OCR: pytesseract (images)

## Quick Start (Local)

```bash
# Install system dependencies (important for whisper & audio)
sudo apt update && sudo apt install -y ffmpeg tesseract-ocr libtesseract-dev

pip install -r requirements.txt
