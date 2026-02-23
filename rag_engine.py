import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize models
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

class RAGEngine:
    def __init__(self):
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []
        
    def process_file(self, file_path):
        text = ""
        if file_path.endswith('.pdf'):
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        else:
            with open(file_path, 'r') as f:
                text = f.read()
        
        # Simple chunking
        new_chunks = self._chunk_text(text)
        self.chunks.extend(new_chunks)
        
        # Embed and add to FAISS
        embeddings = embed_model.encode(new_chunks)
        self.index.add(np.array(embeddings).astype('float32'))
        return len(new_chunks)

    def _chunk_text(self, text, size=500, overlap=50):
        words = text.split()
        chunks = []
        for i in range(0, len(words), size - overlap):
            chunk = " ".join(words[i:i + size])
            chunks.append(chunk)
        return chunks

    def search(self, query, top_k=3):
        if not self.chunks:
            return []
        query_vector = embed_model.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), top_k)
        results = [self.chunks[i] for i in indices[0] if i != -1]
        return results

    def generate_response(self, prompt, context=""):
        full_prompt = f"Context: {context}\n\nUser Question: {prompt}\n\nTask: Provide a concise micro-lesson. Detect if the user is a beginner, intermediate, or advanced learner based on the query and tailor the explanation."
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are MindGap AI, an adaptive learning companion. You identify knowledge gaps and provide perfectly tailored lessons."},
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.choices[0].message.content

    def generate_quiz(self, topic, context=""):
        prompt = f"Based on this topic: {topic} and context: {context}, generate 3 multiple-choice questions. Format the response as a JSON array of objects with keys: 'question', 'options' (array), 'correct_answer' (string matching one option), and 'explanation'."
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a quiz generator. Output ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content
