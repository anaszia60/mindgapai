import React, { useState } from 'react';
import { HelpCircle, CheckCircle, XCircle, ChevronRight, Trophy } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const Quiz = ({ questions, topic, onComplete }) => {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedOption, setSelectedOption] = useState(null);
    const [showResult, setShowResult] = useState(false);
    const [score, setScore] = useState(0);
    const [quizFinished, setQuizFinished] = useState(false);

    const currentQuestion = questions[currentIndex];

    const handleOptionClick = (option) => {
        if (showResult) return;
        setSelectedOption(option);
        setShowResult(true);
        if (option === currentQuestion.correct_answer) {
            setScore(score + 1);
        }
    };

    const handleNext = () => {
        if (currentIndex < questions.length - 1) {
            setCurrentIndex(currentIndex + 1);
            setSelectedOption(null);
            setShowResult(false);
        } else {
            setQuizFinished(true);
            onComplete(score + (selectedOption === currentQuestion.correct_answer ? 1 : 0), questions.length);
        }
    };

    if (quizFinished) {
        return (
            <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="glass-card text-center py-12"
            >
                <Trophy className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
                <h2 className="text-3xl font-bold mb-2">Quiz Completed!</h2>
                <p className="text-slate-400 text-lg mb-6">
                    You scored <span className="text-blue-400 font-bold">{score}/{questions.length}</span> in {topic}
                </p>
                <div className="flex justify-center">
                    <button
                        onClick={() => window.location.reload()}
                        className="btn-primary"
                    >
                        Review Performance
                    </button>
                </div>
            </motion.div>
        );
    }

    return (
        <div className="glass-card mt-8">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold flex items-center gap-2">
                    <HelpCircle className="w-6 h-6 text-blue-500" />
                    Quick Quiz
                </h3>
                <span className="text-sm font-medium text-slate-400">Question {currentIndex + 1} of {questions.length}</span>
            </div>

            <div className="mb-8">
                <p className="text-xl font-medium mb-6">{currentQuestion.question}</p>
                <div className="space-y-3">
                    {currentQuestion.options.map((option, idx) => (
                        <button
                            key={idx}
                            onClick={() => handleOptionClick(option)}
                            className={`w-full text-left p-4 rounded-xl border transition-all flex items-center justify-between ${showResult
                                    ? option === currentQuestion.correct_answer
                                        ? 'bg-green-500/10 border-green-500/50 text-green-400'
                                        : option === selectedOption
                                            ? 'bg-red-500/10 border-red-500/50 text-red-400'
                                            : 'bg-slate-900 border-slate-700 opacity-50'
                                    : 'bg-slate-900 border-slate-700 hover:border-blue-500/50 hover:bg-slate-800'
                                }`}
                        >
                            <span>{option}</span>
                            {showResult && option === currentQuestion.correct_answer && <CheckCircle className="w-5 h-5" />}
                            {showResult && option === selectedOption && option !== currentQuestion.correct_answer && <XCircle className="w-5 h-5" />}
                        </button>
                    ))}
                </div>
            </div>

            {showResult && (
                <AnimatePresence>
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="mb-6 p-4 rounded-xl bg-blue-500/5 border border-blue-500/20"
                    >
                        <p className="text-sm text-blue-300"><span className="font-bold">Explanation:</span> {currentQuestion.explanation}</p>
                    </motion.div>
                </AnimatePresence>
            )}

            {showResult && (
                <button
                    onClick={handleNext}
                    className="w-full btn-primary flex items-center justify-center gap-2"
                >
                    {currentIndex < questions.length - 1 ? 'Next Question' : 'Finish Quiz'}
                    <ChevronRight className="w-4 h-4" />
                </button>
            )}
        </div>
    );
};

export default Quiz;
