# MindGap AI - Hackathon Guide

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Add your Groq API Key to .env
echo "GROQ_API_KEY=your_key_here" > .env
python app.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📊 Sample API Requests

### Upload Document
**POST** `/api/upload`
- Body: `multipart/form-data` with `file=@path/to/notes.pdf`

### Generate Lesson
**POST** `/api/lesson`
```json
{
  "topic": "Neural Networks"
}
```

### Generate Quiz
**POST** `/api/quiz`
```json
{
  "topic": "Neural Networks"
}
```

## 📂 Project Structure
- `backend/app.py`: Main Flask API.
- `backend/rag_engine.py`: FAISS + SentenceTransformers + Groq.
- `backend/database.py`: SQLite performance tracking.
- `frontend/src/App.jsx`: Main interface logic.
- `frontend/src/components/`: Modular UI components.

## 💡 Hackathon Tips
- **Groq Prompting**: We use `llama-3.3-70b-versatile` for low latency and high-quality responses.
- **RAG**: Chunks are stored in a local FAISS index for lightning-fast retrieval.
- **Micro-learning**: The system detects user level (beginner/adv) and adjusts the lesson depth.
