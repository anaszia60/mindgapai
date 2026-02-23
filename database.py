import sqlite3
import os

DB_PATH = 'mindgap.db'

def init_db():
    """
    Initialize the SQLite database with required tables:
    - student_performance: stores quiz results
    - weak_topics: tracks topics the student struggles with
    - achievements: stores unlocked badges/achievements
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Performance history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            score INTEGER,
            total_questions INTEGER,
            level TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Weak topics tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weak_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT UNIQUE NOT NULL,
            frequency INTEGER DEFAULT 1,
            last_failed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Achievements / gamification badges
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_score(topic, score, total, level):
    """
    Save quiz result and update weak topics if performance is low (<70%)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO student_performance 
        (topic, score, total_questions, level) 
        VALUES (?, ?, ?, ?)
    ''', (topic, score, total, level))
    
    # Mark as weak topic if score is below 70%
    if total > 0 and (score / total) < 0.7:
        cursor.execute('''
            INSERT INTO weak_topics (topic) 
            VALUES (?) 
            ON CONFLICT(topic) 
            DO UPDATE SET 
                frequency = frequency + 1,
                last_failed_at = CURRENT_TIMESTAMP
        ''', (topic,))
        
    conn.commit()
    conn.close()

def save_achievement(name):
    """
    Award an achievement/badge to the student
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO achievements (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def get_weak_topics():
    """
    Return list of topics the student has repeatedly struggled with
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT topic, frequency 
        FROM weak_topics 
        ORDER BY frequency DESC 
        LIMIT 10
    ''')
    topics = cursor.fetchall()
    conn.close()
    
    return [{"topic": t[0], "frequency": t[1]} for t in topics]

def get_performance_history():
    """
    Return recent quiz performance history (newest first)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT topic, score, total_questions, level, timestamp 
        FROM student_performance 
        ORDER BY timestamp DESC
    ''')
    history = cursor.fetchall()
    conn.close()
    
    return [
        {
            "topic": h[0],
            "score": h[1],
            "total": h[2],
            "level": h[3],
            "date": h[4]
        }
        for h in history
    ]

def get_achievements():
    """
    Return list of earned achievements (newest first)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT name, timestamp FROM achievements ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return [{"name": row[0], "date": row[1]} for row in rows]
