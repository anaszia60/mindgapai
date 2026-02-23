import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image
import numpy as np
import json

load_dotenv()

# Initialize models
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "mindgap-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )
index = pc.Index(index_name)

class RAGEngine:
    def __init__(self):
        self.chunks = []  # For local cache if needed

    def process_file(self, file_path, ocr_text=""):
        text = ocr_text
        if file_path.endswith('.pdf'):
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif file_path.endswith('.txt'):
            with open(file_path, 'r') as f:
                text = f.read()
        
        # Auto-chunk & summarize with LLM
        summary_prompt = f"Summarize and chunk this text into logical sections: {text[:2000]}..."  # Truncate if too long
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": summary_prompt}]
        )
        chunks = response.choices[0].message.content.split("\n\n")  # Simple split
        
        # Embed and upsert to Pinecone
        embeddings = embed_model.encode(chunks)
        vectors = [{"id": str(i), "values": emb.tolist(), "metadata": {"text": chunk}} for i, (emb, chunk) in enumerate(zip(embeddings, chunks))]
        index.upsert(vectors=vectors)
        self.chunks.extend(chunks)
        return len(chunks)

    def ocr_image(self, file_path):
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)

    def search(self, query, top_k=3):
        # Hybrid search: Keyword filter + semantic
        query_emb = embed_model.encode([query])[0].tolist()
        results = index.query(vector=query_emb, top_k=top_k, include_metadata=True)
        return [match['metadata']['text'] for match in results['matches'] if 'text' in match['metadata']]

    def generate_response(self, prompt, context="", profile={}):
        full_prompt = f"""
Context: {context}
Student Profile: Difficulty: {profile['difficulty']}, Language: {profile['language']}, Weak Topics: {', '.join(profile['weak_topics'])}
User Question: {prompt}

Task: Provide a tailored micro-lesson. Adjust for difficulty, use {profile['language']}, focus on weak topics. Few-shot example: For beginner on AI: 'AI is like a smart robot that learns from data.'
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are MindGap AI, adaptive tutor."},
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.choices[0].message.content

    def generate_quiz(self, topic, context="", profile={}):
        prompt = f"""
Based on topic: {topic}, context: {context}, profile: {json.dumps(profile)}.
Generate 3 MCQs. Add 'confidence' key (Low/Medium/High based on difficulty).
Format: JSON array of objects: 'question', 'options' (array), 'correct_answer', 'explanation', 'confidence'.
Few-shot: [{{"question": "What is AI?", "options": ["A", "B"], "correct_answer": "A", "explanation": "...", "confidence": "Low"}}]
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Output ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content

    def analyze_gaps(self, topic, past_scores, profile):
        prompt = f"Analyze gaps from scores: {json.dumps(past_scores)}, profile: {json.dumps(profile)}. Suggest next lessons and motivational tips."
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
