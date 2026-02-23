---
title: MindGap AI
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: streamlit
pinned: false
---

# MindGap AI - Adaptive Learning Companion

MindGap AI detects knowledge gaps and generates personalized micro-lessons using RAG, APIs, and Streamlit. Now with Pinecone for vector search, OCR for images, adaptive prompts, and gamification.

## Tech Stack
- **Frontend/Backend**: Streamlit
- **Vector Search**: Pinecone API (hybrid search)
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
- **LLM**: Groq API (`llama-3.3-70b-versatile`)
- **Database**: SQLite
- **OCR**: Pytesseract (for images)
- **Other**: Adaptive learning via API prompts

## 📂 Project Structure
- `app.py`: Main app.
- `rag_engine.py`: RAG with Pinecone.
- `database.py`: SQLite for tracking.
- `requirements.txt`: Dependencies.

## 🚀 Quick Start (Local)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
