import React, { useState } from 'react';
import Navbar from './components/Navbar';
import FileUploader from './components/FileUploader';
import LessonCard from './components/LessonCard';
import Quiz from './components/Quiz';
import Dashboard from './components/Dashboard';
import { Search, Loader2, BookOpen, Brain, Sparkles } from 'lucide-react';
import axios from 'axios';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [lesson, setLesson] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!topic) return;
    setLoading(true);
    setError('');
    setLesson(null);
    setQuiz(null);

    try {
      const lessonRes = await axios.post('http://localhost:5000/api/lesson', { topic });
      setLesson(lessonRes.data.lesson);

      const quizRes = await axios.post('http://localhost:5000/api/quiz', { topic });
      // Assuming quiz returns { questions: [...] }
      setQuiz(quizRes.data.questions || quizRes.data);
    } catch (err) {
      setError('Failed to fetch content. Make sure the backend is running and you have uploaded some documents.');
    } finally {
      setLoading(false);
    }
  };

  const onQuizComplete = async (score, total) => {
    try {
      await axios.post('http://localhost:5000/api/save-performance', {
        topic,
        score,
        total,
        level: 'beginner' // Could be dynamic
      });
    } catch (err) {
      console.error('Error saving performance:', err);
    }
  };

  return (
    <div className="min-h-screen pt-24">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="max-w-4xl mx-auto px-6">
        {activeTab === 'home' && (
          <div className="space-y-12 pb-20">
            <div className="text-center space-y-4">
              <h1 className="text-5xl md:text-6xl font-black gradient-text tracking-tight">
                Bridge Your Knowledge Gaps.
              </h1>
              <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                MindGap AI uses RAG and Grok to identify what you don't know and teaches you with personalized micro-lessons.
              </p>
            </div>

            <form onSubmit={handleSearch} className="relative max-w-2xl mx-auto">
              <input
                type="text"
                placeholder="What do you want to learn today?"
                className="w-full input-field pl-12 pr-32 py-4 text-lg shadow-2xl"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-6 h-6" />
              <button
                type="submit"
                disabled={loading}
                className="absolute right-2 top-1/2 -translate-y-1/2 btn-primary py-2 px-6 flex items-center gap-2"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Start Learning'}
              </button>
            </form>

            {error && (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-center">
                {error}
              </div>
            )}

            {!lesson && !loading && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-10">
                <div className="glass-card text-center">
                  <Brain className="w-8 h-8 text-blue-500 mx-auto mb-3" />
                  <h4 className="font-bold mb-1">Adaptive</h4>
                  <p className="text-xs text-slate-400">Tailors content to your level</p>
                </div>
                <div className="glass-card text-center">
                  <BookOpen className="w-8 h-8 text-indigo-500 mx-auto mb-3" />
                  <h4 className="font-bold mb-1">Contextual</h4>
                  <p className="text-xs text-slate-400">Uses your own notes for context</p>
                </div>
                <div className="glass-card text-center">
                  <Sparkles className="w-8 h-8 text-amber-500 mx-auto mb-3" />
                  <h4 className="font-bold mb-1">Smart Quiz</h4>
                  <p className="text-xs text-slate-400">Instant feedback & tracking</p>
                </div>
              </div>
            )}

            {lesson && <LessonCard lesson={lesson} topic={topic} />}
            {quiz && quiz.length > 0 && <Quiz questions={quiz} topic={topic} onComplete={onQuizComplete} />}
          </div>
        )}

        {activeTab === 'upload' && <FileUploader />}
      </main>

      {activeTab === 'dashboard' && <Dashboard />}
    </div>
  );
}

export default App;
