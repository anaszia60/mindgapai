import streamlit as st
import os
import json
from rag_engine import RAGEngine
from database import init_db, save_score, get_weak_topics, get_performance_history, save_achievement
from datetime import datetime

# --- SETTINGS & STYLING ---
st.set_page_config(
    page_title="MindGap AI | Adaptive Learning Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced Modern CSS with Animations, Hover Effects, Gradients
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: radial-gradient(circle at top right, #1e3a8a, #4c1d95);
        padding: 24px;
    }
    
    .stButton>button {
        width: 100%;
        max-width: 300px;
        height: 48px;
        border-radius: 12px;
        background: linear-gradient(90deg, #3b82f6, #a855f7);
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        transform: scale(1.05) translateY(-2px);
        box-shadow: 0 10px 15px rgba(59, 130, 246, 0.3);
        background: linear-gradient(90deg, #2563eb, #7e22ce);
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        animation: fadeIn 0.5s ease-in-out;
        width: 100%;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .gradient-text {
        background: linear-gradient(90deg, #60a5fa, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    .achievement-badge {
        background: linear-gradient(90deg, #fbbf24, #f59e0b);
        color: #1e293b;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
if 'rag' not in st.session_state:
    init_db()
    st.session_state.rag = RAGEngine()
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
if 'student_profile' not in st.session_state:
    st.session_state.student_profile = {"difficulty": "beginner", "language": "English", "weak_topics": []}

# --- SIDEBAR ---
with st.sidebar.container().add_class("glass-card"):
    st.markdown("<h1 class='gradient-text'>MindGap AI</h1>", unsafe_allow_html=True)
    st.write("Adaptive Learning Companion")
    st.divider()
    
    menu = st.radio("Navigation", ["🏠 Home", "📤 Upload Materials", "📊 Dashboard"])
    
    st.divider()
    st.selectbox("Difficulty Level", ["beginner", "intermediate", "advanced"], key="difficulty", on_change=lambda: st.session_state.student_profile.update({"difficulty": st.session_state.difficulty}))
    st.selectbox("Language", ["English", "Spanish", "French"], key="language", on_change=lambda: st.session_state.student_profile.update({"language": st.session_state.language}))
    st.info("💡 Upload notes/images for personalized learning.")

# --- PAGE: HOME ---
if menu == "🏠 Home":
    with st.container().add_class("glass-card"):
        st.markdown("<h1 class='gradient-text'>Bridge Your Knowledge Gaps</h1>", unsafe_allow_html=True)
        st.write("MindGap AI identifies gaps and teaches with personalized lessons.")
        
        topic = st.text_input("What do you want to learn?", placeholder="e.g. Neural Networks...")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            search_btn = st.button("Start Learning")

    if search_btn and topic:
        with st.spinner("Analyzing..."):
            # Get profile
            profile = st.session_state.student_profile
            weak_topics = get_weak_topics()
            profile["weak_topics"] = [w['topic'] for w in weak_topics]
            
            # Search context (now using Pinecone hybrid)
            context_chunks = st.session_state.rag.search(topic)
            context = "\n".join(context_chunks)
            
            # Generate Lesson with profile
            lesson = st.session_state.rag.generate_response(topic, context, profile)
            
            # Generate Quiz
            quiz_raw = st.session_state.rag.generate_quiz(topic, context, profile)
            try:
                quiz_data = json.loads(quiz_raw)
                st.session_state.current_quiz = quiz_data.get("questions", quiz_data)
            except:
                st.error("Quiz generation failed!")
                st.session_state.current_quiz = None
            
            # Gap Analysis
            if 'past_scores' in st.session_state:
                gap_analysis = st.session_state.rag.analyze_gaps(topic, st.session_state.past_scores, profile)
                st.info(gap_analysis)
            
            st.session_state.current_lesson = lesson
            st.session_state.current_topic = topic

    if 'current_lesson' in st.session_state:
        st.divider()
        st.subheader(f"📚 Lesson: {st.session_state.current_topic}")
        st.markdown(st.session_state.current_lesson)
        
        if st.session_state.get('current_quiz'):
            st.divider()
            st.subheader("📝 Quick Check")
            
            with st.form("quiz_form"):
                user_answers = []
                for idx, q in enumerate(st.session_state.current_quiz):
                    st.write(f"**Q{idx+1}: {q['question']}** (Confidence: {q.get('confidence', 'Medium')})")
                    ans = st.radio(f"Select for Q{idx+1}", q['options'], key=f"q_{idx}")
                    user_answers.append(ans)
                
                submitted = st.form_submit_button("Submit Quiz")
                
                if submitted:
                    score = 0
                    mistakes = []
                    for idx, q in enumerate(st.session_state.current_quiz):
                        if user_answers[idx] == q['correct_answer']:
                            score += 1
                        else:
                            mistakes.append(q['question'])
                            st.error(f"❌ Q{idx+1} Wrong. Correct: {q['correct_answer']}")
                            st.info(f"💡 Explanation: {q['explanation']}")
                    
                    st.success(f"Score: {score}/{len(st.session_state.current_quiz)}")
                    save_score(st.session_state.current_topic, score, len(st.session_state.current_quiz), st.session_state.student_profile["difficulty"])
                    if score / len(st.session_state.current_quiz) > 0.8:
                        save_achievement("Quiz Master")
                        st.balloons()
                    st.session_state.past_scores = {"topic": st.session_state.current_topic, "score": score, "mistakes": mistakes}

# --- PAGE: UPLOAD ---
elif menu == "📤 Upload Materials":
    with st.container().add_class("glass-card"):
        st.markdown("<h1 class='gradient-text'>Upload Study Materials</h1>", unsafe_allow_html=True)
        st.write("Supported: PDF, TXT, Images (for diagrams)")
        
        uploaded_file = st.file_uploader("Choose file", type=['pdf', 'txt', 'png', 'jpg'])
        
        if uploaded_file is not None:
            if st.button("Process File"):
                with st.spinner("Processing..."):
                    file_path = os.path.join("uploads", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Handle images with OCR
                    if uploaded_file.type.startswith('image'):
                        text = st.session_state.rag.ocr_image(file_path)
                    else:
                        text = ""
                    
                    num_chunks = st.session_state.rag.process_file(file_path, text)
                    st.success(f"✅ Processed into {num_chunks} chunks.")

# --- PAGE: DASHBOARD ---
elif menu == "📊 Dashboard":
    with st.container().add_class("glass-card"):
        st.markdown("<h1 class='gradient-text'>Learning Dashboard</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚠️ Knowledge Gaps")
            weak = get_weak_topics()
            if weak:
                for item in weak:
                    st.error(f"**{item['topic']}** (Failed {item['frequency']} times)")
            else:
                st.success("No gaps yet!")
                
        with col2:
            st.subheader("📜 History")
            history = get_performance_history()
            if history:
                for item in history:
                    st.info(f"**{item['topic']}**: {item['score']}/{item['total']} ({item['level']}) - {item['date']}")
            else:
                st.write("Start quizzing!")
        
        st.subheader("🏆 Achievements")
        achievements = get_performance_history()  # Reuse for simplicity; add real query if needed
        for ach in ["Quiz Master"] if achievements else []:
            st.markdown(f"<div class='achievement-badge'>{ach}</div>", unsafe_allow_html=True)
