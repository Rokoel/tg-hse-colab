# db.py
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
import time
from config import BASE_DIR

DB_PATH = BASE_DIR / "bot.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # users: basic profile & verification status
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,            -- Telegram user id
        username TEXT,
        course INTEGER,
        direction TEXT,
        age INTEGER,
        name TEXT,
        description TEXT,
        profile_photo TEXT,                -- local path or NULL
        verified INTEGER DEFAULT 0,        -- 0 not, 1 pending, 2 approved, 3 denied
        created_at INTEGER
    )
    """)
    # ids: store student ID photo paths (only until decision)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS id_uploads (
        user_id INTEGER PRIMARY KEY,
        file_path TEXT,
        uploaded_at INTEGER
    )
    """)
    # likes: store likes to compute mutual
    cur.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        from_user INTEGER,
        to_user INTEGER,
        liked_at INTEGER,
        PRIMARY KEY (from_user, to_user)
    )
    """)
    # events set and user selections
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        name TEXT PRIMARY KEY
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_events (
        user_id INTEGER,
        event_name TEXT,
        PRIMARY KEY (user_id, event_name)
    )
    """)
    # bans
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bans (
        user_id INTEGER PRIMARY KEY,
        banned_at INTEGER
    )
    """)
    conn.commit()
    conn.close()

# user helpers
def create_or_update_user(user_id:int, username:Optional[str], course:Optional[int]=None,
                          direction:Optional[str]=None, age:Optional[int]=None,
                          name:Optional[str]=None, description:Optional[str]=None,
                          profile_photo:Optional[str]=None):
    conn = get_conn()
    cur = conn.cursor()
    now = int(time.time())
    # upsert
    cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if cur.fetchone():
        cur.execute("""
            UPDATE users SET username=?, course=?, direction=?, age=?, name=?, description=?, profile_photo=?
            WHERE id = ?
        """, (username, course, direction, age, name, description, profile_photo, user_id))
    else:
        cur.execute("""
            INSERT INTO users (id, username, course, direction, age, name, description, profile_photo, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, course, direction, age, name, description, profile_photo, now))
    conn.commit()
    conn.close()

def get_user(user_id:int) -> Optional[Dict[str,Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def set_verification_status(user_id:int, status:int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET verified = ? WHERE id = ?", (status, user_id))
    conn.commit()
    conn.close()

def save_id_upload(user_id:int, file_path:str):
    conn = get_conn()
    cur = conn.cursor()
    now = int(time.time())
    cur.execute("REPLACE INTO id_uploads (user_id, file_path, uploaded_at) VALUES (?, ?, ?)",
                (user_id, file_path, now))
    conn.commit()
    conn.close()

def pop_id_upload(user_id:int) -> Optional[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT file_path FROM id_uploads WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    path = row["file_path"]
    cur.execute("DELETE FROM id_uploads WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return path

# events
def ensure_events(initial_events: List[str]):
    conn = get_conn()
    cur = conn.cursor()
    for ev in initial_events:
        cur.execute("INSERT OR IGNORE INTO events (name) VALUES (?)", (ev,))
    conn.commit()
    conn.close()

def add_event(name: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO events (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def remove_event(name: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE name = ?", (name,))
    # also remove user_events entries
    cur.execute("DELETE FROM user_events WHERE event_name = ?", (name,))
    conn.commit()
    conn.close()

def list_events() -> List[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM events ORDER BY name")
    res = [r["name"] for r in cur.fetchall()]
    conn.close()
    return res

def set_user_event(user_id:int, event_name:str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO user_events (user_id, event_name) VALUES (?, ?)", (user_id, event_name))
    conn.commit()
    conn.close()

def clear_user_events(user_id:int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_events WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_events(user_id:int) -> List[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT event_name FROM user_events WHERE user_id = ?", (user_id,))
    res = [r["event_name"] for r in cur.fetchall()]
    conn.close()
    return res

# likes
def like_user(from_user:int, to_user:int):
    conn = get_conn()
    cur = conn.cursor()
    now = int(time.time())
    cur.execute("INSERT OR REPLACE INTO likes (from_user, to_user, liked_at) VALUES (?, ?, ?)", (from_user, to_user, now))
    conn.commit()
    conn.close()

def unlike_user(from_user:int, to_user:int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM likes WHERE from_user = ? AND to_user = ?", (from_user, to_user))
    conn.commit()
    conn.close()

def is_mutual(a:int, b:int) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM likes WHERE from_user=? AND to_user=? LIMIT 1", (a, b))
    r1 = cur.fetchone()
    cur.execute("SELECT 1 FROM likes WHERE from_user=? AND to_user=? LIMIT 1", (b, a))
    r2 = cur.fetchone()
    conn.close()
    return bool(r1 and r2)

def get_verified_pool(exclude_user:int) -> List[Dict[str,Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE verified = 2 AND id != ? ", (exclude_user,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# bans
def ban_user(user_id:int):
    conn = get_conn()
    cur = conn.cursor()
    now = int(time.time())
    cur.execute("INSERT OR REPLACE INTO bans (user_id, banned_at) VALUES (?, ?)", (user_id, now))
    conn.commit()
    conn.close()

def is_banned(user_id:int) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM bans WHERE user_id = ?", (user_id,))
    res = cur.fetchone() is not None
    conn.close()
    return res
