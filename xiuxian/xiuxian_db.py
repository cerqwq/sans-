"""
修仙游戏数据库模块
SQLite 存储角色数据
"""
import sqlite3
import json
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xiuxian_data.db')

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS xiuxian_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                character_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

def save_character(username: str, character_data: dict):
    with get_db() as conn:
        data_json = json.dumps(character_data, ensure_ascii=False)
        conn.execute("""
            INSERT INTO xiuxian_players (username, character_data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(username) DO UPDATE SET
                character_data = excluded.character_data,
                updated_at = CURRENT_TIMESTAMP
        """, (username, data_json))

def load_character(username: str) -> dict:
    with get_db() as conn:
        row = conn.execute(
            "SELECT character_data FROM xiuxian_players WHERE username = ?",
            (username,)
        ).fetchone()
        if row:
            return json.loads(row["character_data"])
        return None

def delete_character(username: str):
    with get_db() as conn:
        conn.execute("DELETE FROM xiuxian_players WHERE username = ?", (username,))

def get_all_players() -> list:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT username, character_data, created_at, updated_at FROM xiuxian_players ORDER BY updated_at DESC"
        ).fetchall()
        result = []
        for row in rows:
            data = json.loads(row["character_data"])
            result.append({
                "username": row["username"],
                "name": data.get("name", ""),
                "realm": data.get("realm", ""),
                "stage": data.get("stage", 0),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            })
        return result
