import streamlit as st
import os
import json
import whisper
from gtts import gTTS
from io import BytesIO
import base64
from st_audiorec import audiorec
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
    .gradient-text {
        background: linear-gradient(90deg, #60a5fa, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .glass-card {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .stButton > button {
        border-radius: 10px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.25s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 12px rgba(59,130,246,0.4);
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

if 'whisper_model' not in st.session_state:
    with st.spinner("Loading Whisper model (first time only)..."):
        st.session_state.whisper_model = whisper.load_model("base")

# ────────────────────────────────────────────────
#  Sidebar
# ────────────────────────────────────────────────

with st.sidebar:
    st.markdown("<h1 class='gradient-text'>MindGap AI</h1>", unsafe_allow_html=True)
    st.caption("Voice + Text Adaptive Learning")

    menu = st.radio("Go to", [
        "🏠 Home & Lessons",
        "📤 Upload Materials",
        "📊 Dashboard",
        "🗣️ Voice Conversation"
    ])

    st.divider()

    diff = st.selectbox("Learning level", ["beginner", "intermediate", "advanced"],
                        index=["beginner","intermediate","advanced"].index(st.session_state.student_profile["difficulty"]))
    lang = st.selectbox("Response language", ["English", "Spanish", "French"],
                        index=["English","Spanish","French"].index(st.session_state.student_profile["language"]))

    st.session_state.student_profile["difficulty"] = diff
    st.session_state.student_profile["language"] = lang

# ────────────────────────────────────────────────
#  Pages
# ────────────────────────────────────────────────

if menu == "🏠 Home & Lessons":
    st.markdown("<h2 class='gradient-text'>Bridge Your Knowledge Gaps</h2>", unsafe_allow_html=True)

    topic = st.text_input("What would you like to learn today?", 
                          placeholder="e.g. Python decorators, Photosynthesis, Blockchain...")

    if st.button("Generate Lesson + Quiz", use_container_width=True) and topic.strip():
        with st.spinner("Creating personalized lesson..."):
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
        with st.container():
            st.subheader(f"Lesson: **{st.session_state.current_topic}**")
            st.markdown(st.session_state.current_lesson)

        if st.session_state.current_quiz:
            st.subheader("Quick Knowledge Check")
            user_answers = []

            for i, q in enumerate(st.session_state.current_quiz):
                st.markdown(f"**Q{i+1}.** {q['question']}")
                choice = st.radio(" ", q['options'], key=f"q_{i}_{st.session_state.current_topic}", horizontal=True)
                user_answers.append(choice)

            if st.button("Submit Answers", type="primary"):
                score = sum(1 for a, q in zip(user_answers, st.session_state.current_quiz) if a == q['correct_answer'])
                total = len(st.session_state.current_quiz)

                st.success(f"**Score: {score}/{total}**  ({score/total:.0%})")

                save_score(st.session_state.current_topic, score, total, st.session_state.student_profile["difficulty"])

                if score == total:
                    save_achievement("Perfect Score Master")
                    st.balloons()

                for i, (q, ans) in enumerate(zip(st.session_state.current_quiz, user_answers)):
                    if ans != q['correct_answer']:
                        st.error(f"Q{i+1}: Wrong → **{q['correct_answer']}**")
                        st.info(q['explanation'])

# ────────────────────────────────────────────────
#  Upload Materials
# ────────────────────────────────────────────────

elif menu == "📤 Upload Materials":
    st.markdown("<h2 class='gradient-text'>Upload Study Materials</h2>", unsafe_allow_html=True)
    st.write("PDF, TXT, PNG, JPG, JPEG")

    file = st.file_uploader("Select file", type=["pdf","txt","png","jpg","jpeg"])

    if file and st.button("Process File", use_container_width=True):
        path = os.path.join("uploads", file.name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())

        ocr_text = ""
        if file.type.startswith("image/"):
            try:
                img = Image.open(path)
                ocr_text = pytesseract.image_to_string(img)
            except:
                st.warning("Could not perform OCR on image.")

        with st.spinner("Indexing content..."):
            count = st.session_state.rag.process_file(path, ocr_text)
            st.success(f"Added **{count}** chunks to knowledge base.")

# ────────────────────────────────────────────────
#  Dashboard
# ────────────────────────────────────────────────

elif menu == "📊 Dashboard":
    st.markdown("<h2 class='gradient-text'>Your Learning Dashboard</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Knowledge Gaps")
        weak = get_weak_topics()
        if weak:
            for w in weak:
                st.error(f"• {w['topic']}  (failed {w['frequency']}×)")
        else:
            st.success("No weak topics detected yet — great job!")

    with col2:
        st.subheader("Recent Performance")
        hist = get_performance_history()
        if hist:
            for r in hist[:8]:
                st.info(f"{r['topic']} • {r['score']}/{r['total']} • {r['date'][:10]}")
        else:
            st.write("No quiz data yet.")

    st.subheader("Achievements")
    ach = get_achievements()
    if ach:
        for a in ach:
            st.success(f"🏆 {a['name']} – {a['date'][:10]}")
    else:
        st.write("Keep learning to unlock achievements!")

# ────────────────────────────────────────────────
#  Voice Conversation
# ────────────────────────────────────────────────

elif menu == "🗣️ Voice Conversation":
    st.markdown("<h2 class='gradient-text'>Voice Chat with MindGap AI</h2>", unsafe_allow_html=True)
    st.caption("Speak → AI listens → AI speaks back")

    # Show history
    for msg in st.session_state.conversation_history:
        with st.chat_message("user"):
            st.write(msg["user"])
        with st.chat_message("assistant"):
            st.write(msg["ai"])
            if "audio_data" in msg:
                st.audio(msg["audio_data"], format="audio/mp3")

    # Record voice
    audio_bytes = audiorec(
        key="voice_input",
        label="Click to speak (mic access required)"
    )

    if audio_bytes is not None:
        with st.spinner("Transcribing your voice..."):
            # Save temp file
            tmp_wav = "temp_voice_input.wav"
            with open(tmp_wav, "wb") as f:
                f.write(audio_bytes)

            # Whisper → text
            result = st.session_state.whisper_model.transcribe(tmp_wav, language="en")
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

            # Cleanup
            if os.path.exists(tmp_wav):
                os.remove(tmp_wav)
