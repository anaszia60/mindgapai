import streamlit as st
import os
import json
# import whisper  # Commented out - will load on demand
from gtts import gTTS
from io import BytesIO
import base64
from audio_recorder_streamlit import audio_recorder
from rag_engine import RAGEngine
from database import init_db, save_score, get_weak_topics, get_performance_history, save_achievement, get_achievements
import pytesseract
from PIL import Image

# ────────────────────────────────────────────────
#  Page config & styling
# ────────────────────────────────────────────────

st.set_page_config(
    page_title="MindGap AI • Voice + Text Learning",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Background with Animated Gradient - Darker for better contrast */
    .stApp {
        background: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #533483);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Gradient Text - Brighter for better visibility */
    .gradient-text {
        background: linear-gradient(135deg, #a8c0ff 0%, #c084fc 50%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 3rem;
        text-align: center;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.9; }
    }
    
    /* Glass Morphism Cards - Better contrast */
    .glass-card {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 2px solid rgba(255, 255, 255, 0.25);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(168, 192, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        background: rgba(255, 255, 255, 0.18);
    }
    
    /* Sidebar Styling - Darker with better contrast */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(26, 26, 46, 0.95) 0%, rgba(22, 33, 62, 0.95) 100%);
        backdrop-filter: blur(10px);
        border-right: 2px solid rgba(168, 192, 255, 0.2);
    }
    
    [data-testid="stSidebar"] .element-container {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Button Styles with Glow Effect - Brighter and more visible */
    .stButton > button {
        border-radius: 16px;
        background: linear-gradient(135deg, #667eea 0%, #a855f7 100%);
        color: #ffffff;
        font-weight: 700;
        border: 2px solid rgba(255, 255, 255, 0.2);
        padding: 0.75rem 2rem;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px 0 rgba(168, 85, 247, 0.5);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover:before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 30px 0 rgba(168, 85, 247, 0.8);
        background: linear-gradient(135deg, #7c3aed 0%, #c084fc 100%);
    }
    
    /* Input Fields - Better visibility */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid rgba(168, 192, 255, 0.4);
        background: rgba(255, 255, 255, 0.95);
        color: #1a1a2e;
        padding: 0.75rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #a855f7;
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.6);
        transform: scale(1.02);
        background: #ffffff;
    }
    
    .stTextInput label,
    .stTextArea label {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 1.05rem;
    }
    
    /* Chat Messages - Better contrast */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(168, 192, 255, 0.3);
        animation: slideIn 0.5s ease;
        color: #1a1a2e;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Progress Bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        border-radius: 10px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.1);
        border: 2px dashed rgba(255, 255, 255, 0.4);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.02);
    }
    
    /* Success/Error/Warning Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        padding: 1rem;
        animation: pulse 0.5s ease;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
        border-right-color: #764ba2 !important;
    }
    
    /* Headers - Brighter and more readable */
    h1, h2, h3 {
        color: #ffffff;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
        font-weight: 700;
    }
    
    h1 {
        font-size: 2.5rem;
    }
    
    h2 {
        font-size: 2rem;
    }
    
    h3 {
        font-size: 1.5rem;
    }
    
    p {
        color: rgba(255, 255, 255, 0.95);
        line-height: 1.6;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #f093fb);
    }
    
    /* Audio Player */
    audio {
        border-radius: 12px;
        filter: drop-shadow(0 4px 10px rgba(102, 126, 234, 0.3));
    }
    
    /* Floating Animation for Icons */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .floating {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Glow Effect */
    .glow {
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.6),
                    0 0 40px rgba(118, 75, 162, 0.4),
                    0 0 60px rgba(240, 147, 251, 0.2);
    }
    
    /* Particle Background Effect - More visible */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(168, 192, 255, 0.15) 2px, transparent 2px),
            radial-gradient(circle at 80% 80%, rgba(192, 132, 252, 0.15) 2px, transparent 2px),
            radial-gradient(circle at 40% 20%, rgba(251, 191, 36, 0.15) 2px, transparent 2px);
        background-size: 50px 50px, 80px 80px, 100px 100px;
        animation: particleFloat 20s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes particleFloat {
        0% { transform: translateY(0); }
        100% { transform: translateY(-100px); }
    }
    
    /* Loading Animation */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Neon Glow Text - Brighter and more visible */
    .neon-text {
        color: #ffffff;
        text-shadow: 
            0 0 10px rgba(168, 192, 255, 1),
            0 0 20px rgba(168, 192, 255, 0.8),
            0 0 30px rgba(192, 132, 252, 0.6),
            0 0 40px rgba(192, 132, 252, 0.4);
        animation: neonPulse 2s ease-in-out infinite;
        font-weight: 600;
    }
    
    @keyframes neonPulse {
        0%, 100% { 
            text-shadow: 0 0 10px rgba(168, 192, 255, 1), 
                        0 0 20px rgba(168, 192, 255, 0.8),
                        0 0 30px rgba(192, 132, 252, 0.6); 
        }
        50% { 
            text-shadow: 0 0 20px rgba(168, 192, 255, 1), 
                        0 0 30px rgba(192, 132, 252, 1),
                        0 0 40px rgba(192, 132, 252, 0.8); 
        }
    }
    
    /* Radio Button Styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stRadio label {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .stRadio > div > label > div {
        color: #ffffff !important;
    }
    
    /* Select Box Styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        border: 2px solid rgba(168, 192, 255, 0.4);
        transition: all 0.3s ease;
        color: #1a1a2e;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #a855f7;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.5);
        background: #ffffff;
    }
    
    .stSelectbox label {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 1.05rem;
    }
    
    /* Divider Styling */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
        margin: 2rem 0;
    }
    
    /* Caption Styling */
    .stCaption {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    /* Markdown Links */
    a {
        color: #a8c0ff;
        text-decoration: none;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    
    a:hover {
        color: #fbbf24;
        text-shadow: 0 0 15px rgba(251, 191, 36, 0.8);
    }
    
    /* Container Borders */
    .element-container {
        transition: all 0.3s ease;
    }
    
    /* Hover effect for interactive elements */
    .stButton, .stTextInput, .stTextArea, .stSelectbox, .stRadio {
        transition: all 0.3s ease;
    }
    
    /* Audio Player Custom Styling */
    audio::-webkit-media-controls-panel {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.8), rgba(118, 75, 162, 0.8));
    }
    
    /* Chat Input Styling */
    .stChatInputContainer {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1rem;
    }
    
    /* Success/Info/Warning/Error Box Enhancements */
    .stSuccess {
        background: linear-gradient(135deg, rgba(46, 213, 115, 0.2), rgba(46, 213, 115, 0.1));
        border-left: 4px solid #2ed573;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.2), rgba(79, 172, 254, 0.1));
        border-left: 4px solid #4facfe;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(251, 191, 36, 0.1));
        border-left: 4px solid #fbbf24;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
        border-left: 4px solid #ef4444;
    }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  Session state initialization
# ────────────────────────────────────────────────

if 'rag' not in st.session_state:
    init_db()
    st.session_state.rag = RAGEngine()
    os.makedirs("uploads", exist_ok=True)

if 'student_profile' not in st.session_state:
    st.session_state.student_profile = {
        "difficulty": "beginner",
        "language": "English",
        "weak_topics": []
    }

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Whisper model will be loaded on-demand when voice input is used
# if 'whisper_model' not in st.session_state:
#     with st.spinner("Loading Whisper model (first time only)..."):
#         st.session_state.whisper_model = whisper.load_model("base")

# ────────────────────────────────────────────────
#  Sidebar
# ────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <div class='floating' style='font-size: 4rem; margin-bottom: 0.5rem;'>🧠</div>
            <h1 class='gradient-text' style='font-size: 2rem; margin: 0;'>MindGap AI</h1>
            <p style='color: rgba(255,255,255,0.9); font-size: 0.9rem; margin-top: 0.5rem;'>✨ Voice + Text Adaptive Learning ✨</p>
        </div>
    """, unsafe_allow_html=True)

    menu = st.radio("🎯 Navigation", [
        "🏠 Home & Lessons",
        "📤 Upload Materials",
        "📊 Dashboard",
        "🗣️ Voice Conversation"
    ], label_visibility="visible")

    st.divider()
    
    st.markdown("### ⚙️ Settings")
    
    diff = st.selectbox("🎓 Learning level", ["beginner", "intermediate", "advanced"],
                        index=["beginner","intermediate","advanced"].index(st.session_state.student_profile["difficulty"]))
    lang = st.selectbox("🌍 Response language", ["English", "Spanish", "French"],
                        index=["English","Spanish","French"].index(st.session_state.student_profile["language"]))

    st.session_state.student_profile["difficulty"] = diff
    st.session_state.student_profile["language"] = lang

# ────────────────────────────────────────────────
#  Pages
# ────────────────────────────────────────────────

if menu == "🏠 Home & Lessons":
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <div class='floating' style='font-size: 5rem; margin-bottom: 1rem;'>🎓</div>
            <h1 class='gradient-text' style='font-size: 3.5rem;'>Bridge Your Knowledge Gaps</h1>
            <p class='neon-text' style='font-size: 1.2rem; margin-top: 1rem;'>Personalized AI-powered learning at your fingertips</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    topic = st.text_input("💡 What would you like to learn today?", 
                          placeholder="e.g. Python decorators, Photosynthesis, Blockchain...",
                          label_visibility="visible")

    if st.button("✨ Generate Lesson + Quiz", use_container_width=True) and topic.strip():
        with st.spinner("🔮 Creating personalized lesson..."):
            chunks = st.session_state.rag.search(topic)
            context = "\n".join(chunks)

            lesson_text = st.session_state.rag.generate_response(
                topic, context, st.session_state.student_profile, st.session_state.conversation_history
            )

            quiz_data = st.session_state.rag.generate_quiz(
                topic, context, st.session_state.student_profile
            )

            st.session_state.current_topic = topic
            st.session_state.current_lesson = lesson_text
            st.session_state.current_quiz = quiz_data

    if 'current_lesson' in st.session_state:
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown(f"""
                <div class='glass-card'>
                    <h2 style='color: white; margin-bottom: 1rem;'>📚 Lesson: <span class='neon-text'>{st.session_state.current_topic}</span></h2>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class='glass-card' style='background: white; color: #000000; padding: 2.5rem; line-height: 1.8; font-size: 1.05rem;'>
                    <style>
                        .glass-card h1, .glass-card h2, .glass-card h3 {{
                            color: #000000 !important;
                            font-weight: 700 !important;
                            margin-top: 1.5rem;
                            margin-bottom: 0.75rem;
                        }}
                        .glass-card h1 {{
                            font-size: 2rem !important;
                            border-bottom: 3px solid #8b5cf6;
                            padding-bottom: 0.5rem;
                        }}
                        .glass-card h2 {{
                            font-size: 1.5rem !important;
                        }}
                        .glass-card h3 {{
                            font-size: 1.25rem !important;
                        }}
                        .glass-card p {{
                            color: #000000 !important;
                            margin-bottom: 1rem;
                            font-weight: 400;
                        }}
                        .glass-card strong, .glass-card b {{
                            color: #000000 !important;
                            font-weight: 700 !important;
                        }}
                        .glass-card ul {{
                            list-style: none;
                            padding-left: 0;
                            margin: 1rem 0;
                        }}
                        .glass-card ul li {{
                            position: relative;
                            padding-left: 2rem;
                            margin-bottom: 0.75rem;
                            color: #000000 !important;
                            font-weight: 500;
                        }}
                        .glass-card ul li::before {{
                            content: '●';
                            position: absolute;
                            left: 0.5rem;
                            color: #8b5cf6;
                            font-size: 1.2rem;
                            font-weight: bold;
                        }}
                        .glass-card ol {{
                            padding-left: 2rem;
                            margin: 1rem 0;
                        }}
                        .glass-card ol li {{
                            margin-bottom: 0.75rem;
                            color: #000000 !important;
                            font-weight: 500;
                        }}
                        .glass-card code {{
                            background: #f3f4f6;
                            padding: 0.2rem 0.5rem;
                            border-radius: 4px;
                            color: #6366f1;
                            font-family: 'Courier New', monospace;
                            font-weight: 600;
                        }}
                    </style>
                    {st.session_state.current_lesson}
                </div>
            """, unsafe_allow_html=True)

        if st.session_state.current_quiz:
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            st.markdown("""
                <div class='glass-card'>
                    <h3 style='color: white;'>🎯 Quick Knowledge Check</h3>
                </div>
            """, unsafe_allow_html=True)
            
            user_answers = []

            for i, q in enumerate(st.session_state.current_quiz):
                st.markdown(f"""
                    <div class='glass-card' style='background: rgba(255, 255, 255, 0.2);'>
                        <p style='color: white; font-weight: 600; font-size: 1.1rem;'>❓ Q{i+1}. {q['question']}</p>
                    </div>
                """, unsafe_allow_html=True)
                choice = st.radio(" ", q['options'], key=f"q_{i}_{st.session_state.current_topic}", horizontal=True, label_visibility="collapsed")
                user_answers.append(choice)

            if st.button("🚀 Submit Answers", type="primary", use_container_width=True):
                score = sum(1 for a, q in zip(user_answers, st.session_state.current_quiz) if a == q['correct_answer'])
                total = len(st.session_state.current_quiz)

                percentage = score/total * 100
                
                if percentage == 100:
                    st.markdown(f"""
                        <div class='glass-card glow' style='text-align: center; background: rgba(46, 213, 115, 0.3);'>
                            <h2 class='neon-text' style='font-size: 2.5rem;'>🎉 Perfect Score! 🎉</h2>
                            <p style='color: white; font-size: 1.5rem;'>{score}/{total} ({percentage:.0f}%)</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                elif percentage >= 70:
                    st.markdown(f"""
                        <div class='glass-card' style='text-align: center; background: rgba(52, 211, 153, 0.3);'>
                            <h2 style='color: white; font-size: 2rem;'>✅ Great Job!</h2>
                            <p style='color: white; font-size: 1.3rem;'>{score}/{total} ({percentage:.0f}%)</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class='glass-card' style='text-align: center; background: rgba(251, 191, 36, 0.3);'>
                            <h2 style='color: white; font-size: 2rem;'>📖 Keep Learning!</h2>
                            <p style='color: white; font-size: 1.3rem;'>{score}/{total} ({percentage:.0f}%)</p>
                        </div>
                    """, unsafe_allow_html=True)

                save_score(st.session_state.current_topic, score, total, st.session_state.student_profile["difficulty"])

                if score == total:
                    save_achievement("Perfect Score Master")

                for i, (q, ans) in enumerate(zip(st.session_state.current_quiz, user_answers)):
                    if ans != q['correct_answer']:
                        st.error(f"❌ Q{i+1}: Wrong → Correct answer: **{q['correct_answer']}**")
                        st.info(f"💡 {q['explanation']}")

# ────────────────────────────────────────────────
#  Upload Materials
# ────────────────────────────────────────────────

elif menu == "📤 Upload Materials":
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <div class='floating' style='font-size: 5rem; margin-bottom: 1rem;'>📚</div>
            <h1 class='gradient-text' style='font-size: 3rem;'>Upload Study Materials</h1>
            <p class='neon-text' style='font-size: 1.1rem; margin-top: 1rem;'>PDF • TXT • PNG • JPG • JPEG</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    file = st.file_uploader("📎 Select file to upload", type=["pdf","txt","png","jpg","jpeg"])

    if file and st.button("🚀 Process File", use_container_width=True):
        path = os.path.join("uploads", file.name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())

        ocr_text = ""
        if file.type.startswith("image/"):
            try:
                img = Image.open(path)
                ocr_text = pytesseract.image_to_string(img)
            except:
                st.warning("⚠️ Could not perform OCR on image.")

        with st.spinner("🔄 Indexing content..."):
            count = st.session_state.rag.process_file(path, ocr_text)
            st.markdown(f"""
                <div class='glass-card glow' style='text-align: center; background: rgba(46, 213, 115, 0.3);'>
                    <h2 class='neon-text'>✅ Success!</h2>
                    <p style='color: white; font-size: 1.2rem;'>Added <strong>{count}</strong> chunks to knowledge base</p>
                </div>
            """, unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  Dashboard
# ────────────────────────────────────────────────

elif menu == "📊 Dashboard":
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <div class='floating' style='font-size: 5rem; margin-bottom: 1rem;'>📈</div>
            <h1 class='gradient-text' style='font-size: 3rem;'>Your Learning Dashboard</h1>
            <p class='neon-text' style='font-size: 1.1rem; margin-top: 1rem;'>Track your progress and achievements</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div class='glass-card'>
                <h3 style='color: white;'>⚠️ Knowledge Gaps</h3>
            </div>
        """, unsafe_allow_html=True)
        
        weak = get_weak_topics()
        if weak:
            for w in weak:
                st.markdown(f"""
                    <div class='glass-card' style='background: rgba(239, 68, 68, 0.3); border-color: rgba(239, 68, 68, 0.5);'>
                        <p style='color: white; margin: 0;'>🔴 <strong>{w['topic']}</strong> (failed {w['frequency']}×)</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class='glass-card glow' style='background: rgba(46, 213, 115, 0.3);'>
                    <p style='color: white; text-align: center; margin: 0;'>✅ No weak topics detected — great job!</p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class='glass-card'>
                <h3 style='color: white;'>📊 Recent Performance</h3>
            </div>
        """, unsafe_allow_html=True)
        
        hist = get_performance_history()
        if hist:
            for r in hist[:8]:
                percentage = (r['score'] / r['total']) * 100
                color = "rgba(46, 213, 115, 0.3)" if percentage >= 70 else "rgba(251, 191, 36, 0.3)"
                st.markdown(f"""
                    <div class='glass-card' style='background: {color};'>
                        <p style='color: white; margin: 0;'><strong>{r['topic']}</strong> • {r['score']}/{r['total']} ({percentage:.0f}%) • {r['date'][:10]}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class='glass-card' style='background: rgba(255, 255, 255, 0.1);'>
                    <p style='color: white; text-align: center; margin: 0;'>No quiz data yet. Start learning!</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='glass-card'>
            <h3 style='color: white;'>🏆 Achievements</h3>
        </div>
    """, unsafe_allow_html=True)
    
    ach = get_achievements()
    if ach:
        cols = st.columns(3)
        for idx, a in enumerate(ach):
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class='glass-card glow' style='text-align: center; background: rgba(251, 191, 36, 0.3);'>
                        <div style='font-size: 3rem;'>🏆</div>
                        <p style='color: white; font-weight: 600; margin: 0.5rem 0;'>{a['name']}</p>
                        <p style='color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;'>{a['date'][:10]}</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class='glass-card' style='background: rgba(255, 255, 255, 0.1); text-align: center;'>
                <p style='color: white; margin: 0;'>Keep learning to unlock achievements! 🌟</p>
            </div>
        """, unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  Voice Conversation
# ────────────────────────────────────────────────

elif menu == "🗣️ Voice Conversation":
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <div class='floating' style='font-size: 5rem; margin-bottom: 1rem;'>🎤</div>
            <h1 class='gradient-text' style='font-size: 3rem;'>Voice Chat with MindGap AI</h1>
            <p class='neon-text' style='font-size: 1.1rem; margin-top: 1rem;'>Speak → AI listens → AI speaks back</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Show history
    for msg in st.session_state.conversation_history:
        with st.chat_message("user"):
            st.write(msg["user"])
        with st.chat_message("assistant"):
            st.write(msg["ai"])
            if "audio_data" in msg:
                st.audio(msg["audio_data"], format="audio/mp3")

    # Live microphone recording
    st.markdown("""
        <div class='glass-card' style='text-align: center;'>
            <h3 style='color: white; margin-bottom: 1rem;'>🎤 Voice Input</h3>
            <p style='color: rgba(255,255,255,0.9);'>Click the microphone button below to start recording</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check if FFmpeg is available
    import shutil
    import os
    
    # Try to add FFmpeg to PATH if not already there
    ffmpeg_dir = r"C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin"
    if os.path.exists(ffmpeg_dir) and ffmpeg_dir not in os.environ.get('PATH', ''):
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
    
    ffmpeg_path = shutil.which('ffmpeg')
    
    if ffmpeg_path:
        ffmpeg_available = True
        st.success("✅ Voice recording enabled")
    else:
        ffmpeg_available = False
        st.warning("⚠️ FFmpeg not found. Voice recording requires FFmpeg. Please install FFmpeg and restart the app.")
    
    if ffmpeg_available:
        audio_bytes = audio_recorder(
            text="Click to record",
            recording_color="#e74c3c",
            neutral_color="#3498db",
            icon_name="microphone",
            icon_size="2x"
        )

        if audio_bytes:
            with st.spinner("Transcribing your voice..."):
                try:
                    # Save temp file
                    tmp_audio = "temp_voice_input.wav"
                    with open(tmp_audio, "wb") as f:
                        f.write(audio_bytes)

                    # Load whisper model if not loaded
                    if 'whisper_model' not in st.session_state:
                        import whisper
                        with st.spinner("Loading speech recognition model (first time only)..."):
                            st.session_state.whisper_model = whisper.load_model("base")

                    # Whisper → text
                    result = st.session_state.whisper_model.transcribe(tmp_audio, language="en")
                    user_speech = result["text"].strip()

                    if not user_speech:
                        st.warning("Could not understand speech. Try speaking more clearly.")
                    else:
                        st.chat_message("user").write(user_speech)

                        # Get context + generate answer
                        with st.spinner("Thinking..."):
                            ctx_chunks = st.session_state.rag.search(user_speech)
                            context_str = "\n".join(ctx_chunks)

                            ai_text = st.session_state.rag.generate_response(
                                user_speech,
                                context_str,
                                st.session_state.student_profile,
                                st.session_state.conversation_history
                            )

                            st.chat_message("assistant").write(ai_text)

                            # Text → Speech
                            try:
                                lang_code = {"English":"en", "Spanish":"es", "French":"fr"}.get(
                                    st.session_state.student_profile["language"], "en"
                                )
                                tts = gTTS(ai_text, lang=lang_code, slow=False)
                                audio_io = BytesIO()
                                tts.write_to_fp(audio_io)
                                audio_io.seek(0)

                                st.audio(audio_io, format="audio/mp3")

                                # Save to history
                                st.session_state.conversation_history.append({
                                    "user": user_speech,
                                    "ai": ai_text,
                                    "audio_data": audio_io.getvalue()
                                })

                            except Exception as e:
                                st.error(f"TTS failed: {e}")
                                # Save to history without audio
                                st.session_state.conversation_history.append({
                                    "user": user_speech,
                                    "ai": ai_text
                                })

                except Exception as e:
                    st.error(f"Voice transcription failed: {e}")
                finally:
                    # Cleanup
                    if os.path.exists(tmp_audio):
                        os.remove(tmp_audio)
