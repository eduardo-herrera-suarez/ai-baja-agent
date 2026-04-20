import sqlite3
import json

DB_NAME = "memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS summaries (
        session_id TEXT PRIMARY KEY,
        summary TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS preferences (
        session_id TEXT PRIMARY KEY,
        data TEXT
    )
    """)

    # 🔥 ADD THIS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_state (
        session_id TEXT PRIMARY KEY,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_message(session_id, role, content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO messages (session_id, role, content)
    VALUES (?, ?, ?)
    """, (session_id, role, content))

    conn.commit()
    conn.close()

def get_conversation(session_id, limit=6):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, content FROM messages
    WHERE session_id = ?
    ORDER BY id ASC
    """, (session_id,))

    rows = cursor.fetchall()
    conn.close()

    return [{"role": r[0], "content": r[1]} for r in rows][-limit:]

def get_summary(session_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT summary FROM summaries
    WHERE session_id = ?
    """, (session_id,))

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else ""

def save_summary(session_id, summary):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO summaries (session_id, summary)
    VALUES (?, ?)
    ON CONFLICT(session_id)
    DO UPDATE SET summary = excluded.summary
    """, (session_id, summary))

    conn.commit()
    conn.close()

def get_preferences(session_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT data FROM preferences WHERE session_id = ?
    """, (session_id,))

    row = cursor.fetchone()
    conn.close()

    return json.loads(row[0]) if row else {}

def save_preferences(session_id, data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO preferences (session_id, data)
    VALUES (?, ?)
    ON CONFLICT(session_id)
    DO UPDATE SET data = excluded.data
    """, (session_id, json.dumps(data)))

    conn.commit()
    conn.close()

def get_agent_state(session_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT data from backend.agent_state WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()

    return json.loads(row[0]) if row else {}


def save_agent_state(session_id, data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO agent_state (session_id, data)
    VALUES (?, ?)
    ON CONFLICT(session_id)
    DO UPDATE SET data = excluded.data
    """, (session_id, json.dumps(data)))

    conn.commit()
    conn.close()    