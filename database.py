import sqlite3
import os

DB_PATH = 'mindgap.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # User performance and weak topics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            score INTEGER,
            total_questions INTEGER,
            level TEXT, -- beginner, intermediate, advanced
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weak_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT UNIQUE NOT NULL,
            frequency INTEGER DEFAULT 1,
            last_failed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_score(topic, score, total, level):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO student_performance (topic, score, total_questions, level) VALUES (?, ?, ?, ?)',
                   (topic, score, total, level))
    
    # If score is low (e.g., < 70%), add to weak topics
    if (score / total) < 0.7:
        cursor.execute('''
            INSERT INTO weak_topics (topic) VALUES (?)
            ON CONFLICT(topic) DO UPDATE SET frequency = frequency + 1, last_failed_at = CURRENT_TIMESTAMP
        ''', (topic,))
        
    conn.commit()
    conn.close()

def get_weak_topics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT topic, frequency FROM weak_topics ORDER BY frequency DESC LIMIT 10')
    topics = cursor.fetchall()
    conn.close()
    return [{"topic": t[0], "frequency": t[1]} for t in topics]

def get_performance_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT topic, score, total_questions, level, timestamp FROM student_performance ORDER BY timestamp DESC')
    history = cursor.fetchall()
    conn.close()
    return [{"topic": h[0], "score": h[1], "total": h[2], "level": h[3], "date": h[4]} for h in history]
