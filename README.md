---
title: MindGap AI
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: streamlit
pinned: false
---

# MindGap AI - Adaptive Learning Companion

MindGap AI is a hackathon-ready application designed to detect student knowledge gaps and generate personalized micro-lessons using RAG and Streamlit.

## Tech Stack
- **Frontend/Backend**: Streamlit
- **Vector Search**: FAISS
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
- **LLM**: Groq API (`llama-3.3-70b-versatile`)
- **Database**: SQLite (Performance tracking)

## 📂 Project Structure
- `app.py`: Main Streamlit application.
- `rag_engine.py`: Core RAG logic.
- `database.py`: SQLite storage.
- `requirements.txt`: Project dependencies.

## 🚀 Quick Start (Local)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file or set the environment variable:
   ```env
   GROQ_API_KEY=your_key_here
   ```

3. **Run**:
   ```bash
   streamlit run app.py
   ```

## 🌍 Deployment (Hugging Face Spaces)
The app is optimized for Hugging Face Spaces. 
1. Create a Space with the **Streamlit SDK**.
2. Connect your GitHub repository.
3. Add `GROQ_API_KEY` to the Space **Secrets**.
4. The app will automatically build and run.

## 💡 Hackathon Demo Tips
- **Unified Flow**: Streamlit provides a seamless experience for uploading notes, learning, and testing in one place.
- **RAG & FAISS**: Your documents are indexed locally for fast, contextual retrieval.
- **Adaptive Learning**: The LLM adjusts the lesson depth based on your queries and performance history.

