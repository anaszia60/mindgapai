# MindGap AI - Adaptive Learning Companion

MindGap AI is a hackathon-ready full-stack application designed to detect student knowledge gaps and generate personalized micro-lessons.

## Tech Stack
- **Frontend**: React (Vite) + Tailwind CSS
- **Backend**: Flask + SQLite
- **Vector Search**: FAISS
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
- **LLM**: Groq API (`llama-3.3-70b-versatile`)

## 📂 Project Structure
- `backend/app.py`: Main Flask API.
- `backend/rag_engine.py`: FAISS + SentenceTransformers + Groq.
- `backend/database.py`: SQLite performance tracking.
- `frontend/src/App.jsx`: Main interface logic.
- `frontend/src/components/`: Modular UI components.

## 💡 Hackathon Demo Tips
- **Groq Prompting**: We use `llama-3.3-70b-versatile` for low latency and high-quality responses.
- **Micro-learning**: The system detects user level (beginner/adv) and adjusts the lesson depth.
- **RAG**: Chunks are stored in a local FAISS index for lightning-fast retrieval.

## Features
- 🏠 **Home**: Topic-based learning initiation.
- 📁 **Notes Upload**: Upload PDF/Text files to build your knowledge base.
- 📊 **Dashboard**: Track progress and weak topics.
- 📖 **Micro-lessons**: AI-generated lessons based on your level.
- 📝 **Quizzes**: Interactive MCQs with instant feedback.
- 🧠 **Memory**: Tracks weak topics to reinforce learning.

## Setup Instructions

### Backend
1. Navigate to `backend` directory.
2. Create a virtual environment: `python -m venv venv`.
3. Activate it: `source venv/bin/activate`.
4. Install dependencies: `pip install -r requirements.txt`.
5. Create a `.env` file with your `GROQ_API_KEY`.
6. Run the app: `python app.py`.

### Frontend
1. Navigate to `frontend` directory.
2. Install dependencies: `npm install`.
3. Run the dev server: `npm run dev`.

## Example Dataset
- Sample lecture notes on "Photosynthesis" or "Quantum Mechanics" (provided in `data/sample_notes.txt`).
