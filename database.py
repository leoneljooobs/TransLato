"""
Módulo de base de datos SQLite para almacenar palabras y gestionar el historial semanal.
"""
import sqlite3
from datetime import datetime, timedelta
import os

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.db"))
# Asegurar que el directorio contenedor exista
os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                username TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                original_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        conn.commit()

def register_user(user_id: int, chat_id: int, username: str = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, chat_id, username)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                chat_id = excluded.chat_id,
                username = excluded.username
        """, (user_id, chat_id, username))
        conn.commit()

def add_word(user_id: int, chat_id: int, original_text: str, translated_text: str, username: str = None):
    register_user(user_id, chat_id, username)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO words (user_id, original_text, translated_text, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, original_text.strip(), translated_text.strip(), datetime.now().isoformat()))
        conn.commit()

def get_weekly_words(user_id: int, days: int = 7):
    """Obtiene las palabras registradas en los últimos 'days' días."""
    since_date = (datetime.now() - timedelta(days=days)).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT original_text, translated_text, created_at
            FROM words
            WHERE user_id = ? AND created_at >= ?
            ORDER BY created_at ASC
        """, (user_id, since_date))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_all_users():
    """Obtiene todos los usuarios registrados para el envío del resumen semanal."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, chat_id, username FROM users")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_total_words_count(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM words WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return row["count"] if row else 0

if __name__ == "__main__":
    init_db()
    print(f"Base de datos inicializada en: {DB_PATH}")

