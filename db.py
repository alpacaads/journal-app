import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DB_PATH = Path("data/journal.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    entry_date TEXT NOT NULL,
    mood TEXT NOT NULL,
    answers_json TEXT NOT NULL,
    status TEXT NOT NULL, -- draft | complete | generated
    generated_json TEXT,  -- title/story/highlights/theme/template/layout
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, entry_date)
);

CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    media_type TEXT NOT NULL, -- photo | video
    file_path TEXT NOT NULL,
    original_name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
);
"""

def _conn() -> sqlite3.Connection:
    # Ensure folder exists (Streamlit Cloud can start from scratch)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    # IMPORTANT: ensure schema exists no matter which page loads first
    conn.executescript(_SCHEMA)

    return conn

def init_db() -> None:
    # Kept for compatibility; schema is already ensured in _conn()
    with _conn() as conn:
        conn.executescript(_SCHEMA)

def upsert_entry(
    user_id: str,
    entry_date: str,
    mood: str,
    answers_json: str,
    status: str,
    generated_json: Optional[str] = None,
) -> int:
    with _conn() as conn:
        cur = conn.execute(
            "SELECT id FROM entries WHERE user_id = ? AND entry_date = ?",
            (user_id, entry_date),
        )
        row = cur.fetchone()

        if row:
            entry_id = int(row[0])
            conn.execute(
                """
                UPDATE entries
                SET mood = ?, answers_json = ?, status = ?, generated_json = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (mood, answers_json, status, generated_json, entry_id),
            )
            return entry_id

        cur = conn.execute(
            """
            INSERT INTO entries (user_id, entry_date, mood, answers_json, status, generated_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, entry_date, mood, answers_json, status, generated_json),
        )
        return int(cur.lastrowid)

def add_media(entry_id: int, media_type: str, file_path: str, original_name: str) -> int:
    with _conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO media (entry_id, media_type, file_path, original_name)
            VALUES (?, ?, ?, ?)
            """,
            (entry_id, media_type, file_path, original_name),
        )
        return int(cur.lastrowid)

def list_entries(user_id: str) -> List[Tuple[Any, ...]]:
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT id, entry_date, mood, status, updated_at
            FROM entries
            WHERE user_id = ?
            ORDER BY entry_date DESC
            """,
            (user_id,),
        )
        return cur.fetchall()

def get_entry(entry_id: int) -> Optional[Dict[str, Any]]:
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT id, user_id, entry_date, mood, answers_json, status, generated_json, created_at, updated_at
            FROM entries
            WHERE id = ?
            """,
            (entry_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        keys = ["id", "user_id", "entry_date", "mood", "answers_json", "status", "generated_json", "created_at", "updated_at"]
        return dict(zip(keys, row))

def list_media(entry_id: int) -> List[Dict[str, Any]]:
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT id, media_type, file_path, original_name, created_at
            FROM media
            WHERE entry_id = ?
            ORDER BY id ASC
            """,
            (entry_id,),
        )
        rows = cur.fetchall()
        out = []
        for r in rows:
            out.append({
                "id": r[0],
                "media_type": r[1],
                "file_path": r[2],
                "original_name": r[3],
                "created_at": r[4],
            })
        return out
