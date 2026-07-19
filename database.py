import sqlite3
from datetime import date

DB_PATH = "data/tracker.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            deadline DATE NOT NULL,
            created_at DATE DEFAULT CURRENT_DATE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            profession TEXT,
            target_exam TEXT,
            hours_per_day REAL,
            onboarded INTEGER DEFAULT 0
        )
    """)
    conn.execute("INSERT OR IGNORE INTO user_profile (id, onboarded) VALUES (1, 0)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER,
            title TEXT NOT NULL,
            deadline DATE NOT NULL,
            status TEXT DEFAULT 'pending',
            completed_at DATE,
            FOREIGN KEY (goal_id) REFERENCES goals (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS streak (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_completed_date DATE
        )
    """)
    conn.execute("INSERT OR IGNORE INTO streak (id, current_streak, longest_streak) VALUES (1, 0, 0)")
    conn.commit()
    conn.close()