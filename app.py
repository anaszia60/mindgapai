import streamlit as st
import os
import json
from rag_engine import RAGEngine
from database import init_db, save_score, get_weak_topics, get_performance_history
from datetime import datetime

# --- SETTINGS & STYLING ---
st.set_page_config(
    page_title="MindGap AI | Adaptive Learning Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphism CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #3b82f6;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.5);
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    .gradient-text {
        background: linear-gradient(90deg, #60a5fa, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
if 'rag' not in st.session_state:
    init_db()
    st.session_state.rag = RAGEngine()
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 class='gradient-text'>MindGap AI</h1>", unsafe_allow_html=True)
    st.write("Adaptive Learning Companion")
    st.divider()
    
    menu = st.radio("Navigation", ["🏠 Home", "📤 Upload Materials", "📊 Dashboard"])
    
    st.divider()
    st.info("💡 Tip: Upload your notes first so the AI can learn from your specific course content.")

# --- PAGE: HOME ---
if menu == "🏠 Home":
    st.markdown("<h1 class='gradient-text'>Bridge Your Knowledge Gaps.</h1>", unsafe_allow_html=True)
    st.write("MindGap AI identifies what you don't know and teaches you with personalized micro-lessons.")
    
    topic = st.text_input("What do you want to learn today?", placeholder="e.g. Neural Networks, Mitosis, Supply Chain...")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_btn = st.button("Start Learning")

    if search_btn and topic:
        with st.spinner("Analyzing your topic..."):
            # Search context
            context_chunks = st.session_state.rag.search(topic)
            context = "\n".join(context_chunks)
            
            # Generate Lesson
            lesson = st.session_state.rag.generate_response(topic, context)
            
            # Generate Quiz
            quiz_raw = st.session_state.rag.generate_quiz(topic, context)
            try:
                # Sometimes models return extra text, try to find JSON
                quiz_data = json.loads(quiz_raw)
                # Handle potential Groq response format
                if "questions" in quiz_data:
                    st.session_state.current_quiz = quiz_data["questions"]
                else:
                    st.session_state.current_quiz = quiz_data if isinstance(quiz_data, list) else [quiz_data]
            except:
                st.error("Could not generate quiz. You can still read the lesson below!")
                st.session_state.current_quiz = None
            
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
                    st.write(f"**Q{idx+1}: {q['question']}**")
                    ans = st.radio(f"Select option for Q{idx+1}", q['options'], key=f"q_{idx}")
                    user_answers.append(ans)
                
                submitted = st.form_submit_button("Submit Quiz")
                
                if submitted:
                    score = 0
                    for idx, q in enumerate(st.session_state.current_quiz):
                        if user_answers[idx] == q['correct_answer']:
                            score += 1
                        else:
                            st.error(f"❌ Q{idx+1} Wrong. Correct: {q['correct_answer']}")
                            st.info(f"💡 Explanation: {q['explanation']}")
                    
                    st.success(f"Score: {score}/{len(st.session_state.current_quiz)}")
                    save_score(st.session_state.current_topic, score, len(st.session_state.current_quiz), "beginner")
                    st.balloons()

# --- PAGE: UPLOAD ---
elif menu == "📤 Upload Materials":
    st.markdown("<h1 class='gradient-text'>Upload Study Materials</h1>", unsafe_allow_html=True)
    st.write("Supported formats: PDF, TXT")
    
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'txt'])
    
    if uploaded_file is not None:
        if st.button("Process File"):
            with st.spinner("Processing your knowledge base..."):
                file_path = os.path.join("uploads", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                num_chunks = st.session_state.rag.process_file(file_path)
                st.success(f"✅ Success! File processed into {num_chunks} memory chunks.")
                st.info("You can now go to 'Home' and ask questions about this content!")

# --- PAGE: DASHBOARD ---
elif menu == "📊 Dashboard":
    st.markdown("<h1 class='gradient-text'>Learning Dashboard</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Knowledge Gaps")
        weak = get_weak_topics()
        if weak:
            for item in weak:
                st.error(f"**{item['topic']}** (Failed {item['frequency']} times)")
        else:
            st.success("No gaps detected yet! Keep learning.")
            
    with col2:
        st.subheader("📜 Recent History")
        history = get_performance_history()
        if history:
            for item in history:
                st.info(f"**{item['topic']}**: {item['score']}/{item['total']} ({item['level']}) - {item['date']}")
        else:
            st.write("Start a quiz to see your history.")
