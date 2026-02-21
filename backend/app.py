import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from database import init_db, save_score, get_weak_topics, get_performance_history
from rag_engine import RAGEngine
import json

app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize DB and RAG
init_db()
rag = RAGEngine()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    
    num_chunks = rag.process_file(path)
    return jsonify({"message": f"File uploaded and processed into {num_chunks} chunks.", "filename": filename})

@app.route('/api/lesson', methods=['POST'])
def get_lesson():
    data = request.json
    topic = data.get('topic')
    context_chunks = rag.search(topic)
    context = "\n".join(context_chunks)
    
    lesson = rag.generate_response(topic, context)
    return jsonify({"lesson": lesson})

@app.route('/api/quiz', methods=['POST'])
def get_quiz():
    data = request.json
    topic = data.get('topic')
    context_chunks = rag.search(topic)
    context = "\n".join(context_chunks)
    
    quiz_json = rag.generate_quiz(topic, context)
    try:
        # Grok might return it wrapped in markdown or just raw JSON
        quiz_data = json.loads(quiz_json)
        return jsonify(quiz_data)
    except:
        return jsonify({"error": "Failed to generate quiz JSON", "raw": quiz_json}), 500

@app.route('/api/save-performance', methods=['POST'])
def save_performance():
    data = request.json
    topic = data.get('topic')
    score = data.get('score')
    total = data.get('total')
    level = data.get('level', 'beginner')
    
    save_score(topic, score, total, level)
    return jsonify({"status": "success"})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    weak = get_weak_topics()
    history = get_performance_history()
    return jsonify({"weak_topics": weak, "history": history})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
