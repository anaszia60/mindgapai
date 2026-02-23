import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
import json

# Optional Pinecone
try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

load_dotenv()

embed_model = SentenceTransformer('all-MiniLM-L6-v2')
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# Decide vector store
use_pinecone = PINECONE_AVAILABLE and bool(os.getenv("PINECONE_API_KEY"))

if use_pinecone:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "mindgap-index"
    existing_indexes = [index.name for index in pc.list_indexes()]
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=384,
            metric='cosine',
            spec={'serverless': {'cloud': 'aws', 'region': 'us-east-1'}}
        )
    vector_index = pc.Index(index_name)
else:
    # FAISS fallback
    faiss_index = faiss.IndexFlatL2(384)
    stored_chunks = []

class RAGEngine:
    def __init__(self):
        self.dimension = 384

    def process_file(self, file_path, ocr_text=""):
        text = ocr_text

        if file_path.endswith('.pdf'):
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text += f.read() + "\n"

        chunks = self._simple_chunk(text)

        embeddings = embed_model.encode(chunks)

        if use_pinecone:
            vectors = [
                {"id": str(i), "values": emb.tolist(), "metadata": {"text": chunk}}
                for i, (emb, chunk) in enumerate(zip(embeddings, chunks))
            ]
            vector_index.upsert(vectors=vectors)
        else:
            global faiss_index, stored_chunks
            faiss_index.add(np.array(embeddings).astype('float32'))
            stored_chunks.extend(chunks)

        return len(chunks)

    def _simple_chunk(self, text, size=450, overlap=80):
        words = text.split()
        chunks = []
        for i in range(0, len(words), size - overlap):
            chunk = " ".join(words[i:i + size])
            chunks.append(chunk)
        return chunks

    def search(self, query, top_k=3):
        query_emb = embed_model.encode([query])[0]

        if use_pinecone:
            res = vector_index.query(
                vector=query_emb.tolist(),
                top_k=top_k,
                include_metadata=True
            )
            return [m['metadata']['text'] for m in res['matches'] if 'text' in m['metadata']]
        else:
            global faiss_index, stored_chunks
            if len(stored_chunks) == 0:
                return []
            distances, indices = faiss_index.search(np.array([query_emb]).astype('float32'), top_k)
            return [stored_chunks[i] for i in indices[0] if i < len(stored_chunks)]

    def generate_response(self, prompt, context="", profile={}, history=[]):
        history_text = "\n".join([f"User: {h.get('user','')}\nAI: {h.get('ai','')}" for h in history[-5:]])
        
        full_prompt = f"""Context from materials:\n{context}

Student profile:
Difficulty: {profile.get('difficulty', 'beginner')}
Language preference: {profile.get('language', 'English')}
Weak topics: {', '.join(profile.get('weak_topics', []))}

Recent conversation:
{history_text}

User message: {prompt}

Respond naturally, helpfully and educationally. Keep explanations clear and adapt to the student's level.
"""

        try:
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are MindGap AI – friendly, adaptive learning assistant."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"I apologize, but I'm having trouble connecting to the AI service. Error: {str(e)}\n\nPlease check your GROQ_API_KEY in the .env file and ensure it's valid."

    def generate_quiz(self, topic, context="", profile={}):
        prompt = f"""Based on topic '{topic}' and context:\n{context}

Create 3 multiple-choice questions (JSON array).
Each question must have:
- "question": str
- "options": list of 4 strings
- "correct_answer": one of the options (exact string)
- "explanation": short explanation

Output **only** valid JSON array, nothing else.
"""
        try:
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            print(f"Quiz generation error: {e}")
            return []
