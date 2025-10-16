import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import config


def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            course TEXT NOT NULL,
            program TEXT NOT NULL,
            age INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            photo_id TEXT,
            events TEXT,  -- JSON array of selected events
            verification_status TEXT DEFAULT 'not_verified',  -- not_verified, pending, verified, denied
            student_id_photo TEXT,
            is_banned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Likes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(from_user_id, to_user_id),
            FOREIGN KEY (from_user_id) REFERENCES users(user_id),
            FOREIGN KEY (to_user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Dislikes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dislikes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(from_user_id, to_user_id),
            FOREIGN KEY (from_user_id) REFERENCES users(user_id),
            FOREIGN KEY (to_user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user1_id, user2_id),
            FOREIGN KEY (user1_id) REFERENCES users(user_id),
            FOREIGN KEY (user2_id) REFERENCES users(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()


def user_exists(user_id: int) -> bool:
    """Check if user exists in database"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def create_user(user_id: int, username: Optional[str], course: str, program: str, 
                age: int, name: str, description: str, photo_id: Optional[str] = None):
    """Create a new user"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (user_id, username, course, program, age, name, description, photo_id, events)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, course, program, age, name, description, photo_id, '[]'))
    conn.commit()
    conn.close()


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user data"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        user = dict(row)
        user['events'] = json.loads(user['events'])
        return user
    return None


def update_user_field(user_id: int, field: str, value: Any):
    """Update a specific field for user"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f'UPDATE users SET {field} = ? WHERE user_id = ?', (value, user_id))
    conn.commit()
    conn.close()


def update_user_events(user_id: int, events: List[str]):
    """Update user's selected events"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET events = ? WHERE user_id = ?', (json.dumps(events), user_id))
    conn.commit()
    conn.close()


def set_verification_status(user_id: int, status: str):
    """Set user verification status"""
    update_user_field(user_id, 'verification_status', status)


def save_student_id_photo(user_id: int, photo_id: str):
    """Save student ID photo"""
    update_user_field(user_id, 'student_id_photo', photo_id)


def remove_student_id_photo(user_id: int):
    """Remove student ID photo reference"""
    update_user_field(user_id, 'student_id_photo', None)


def ban_user(user_id: int):
    """Ban a user"""
    update_user_field(user_id, 'is_banned', 1)


def is_user_banned(user_id: int) -> bool:
    """Check if user is banned"""
    user = get_user(user_id)
    return user and user['is_banned'] == 1


def add_like(from_user_id: int, to_user_id: int) -> bool:
    """Add a like. Returns True if it's a match"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO likes (from_user_id, to_user_id)
            VALUES (?, ?)
        ''', (from_user_id, to_user_id))
        conn.commit()
        
        # Check if it's a mutual like (match)
        cursor.execute('''
            SELECT 1 FROM likes 
            WHERE from_user_id = ? AND to_user_id = ?
        ''', (to_user_id, from_user_id))
        
        is_match = cursor.fetchone() is not None
        
        if is_match:
            # Create match record
            user1, user2 = sorted([from_user_id, to_user_id])
            cursor.execute('''
                INSERT OR IGNORE INTO matches (user1_id, user2_id)
                VALUES (?, ?)
            ''', (user1, user2))
            conn.commit()
        
        conn.close()
        return is_match
    except sqlite3.IntegrityError:
        conn.close()
        return False


def add_dislike(from_user_id: int, to_user_id: int):
    """Add a dislike"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO dislikes (from_user_id, to_user_id)
            VALUES (?, ?)
        ''', (from_user_id, to_user_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    
    conn.close()


def get_potential_matches(user_id: int) -> List[Dict[str, Any]]:
    """Get list of potential matches for a user, sorted by compatibility"""
    user = get_user(user_id)
    if not user:
        return []
    
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get users that haven't been liked or disliked yet, excluding self
    # Now includes all users regardless of verification status
    cursor.execute('''
        SELECT * FROM users
        WHERE user_id != ?
        AND is_banned = 0
        AND user_id NOT IN (
            SELECT to_user_id FROM likes WHERE from_user_id = ?
        )
        AND user_id NOT IN (
            SELECT to_user_id FROM dislikes WHERE from_user_id = ?
        )
    ''', (user_id, user_id, user_id))
    
    rows = cursor.fetchall()
    conn.close()
    
    users = []
    for row in rows:
        u = dict(row)
        u['events'] = json.loads(u['events'])
        users.append(u)
    
    # Sort by compatibility
    user_events = set(user['events'])
    
    def compatibility_score(other_user):
        # Verification bonus (highest priority - verified users shown first)
        verification_bonus = 100 if other_user['verification_status'] == 'verified' else 0
        
        # Events similarity (primary)
        other_events = set(other_user['events'])
        events_score = len(user_events & other_events) * 10
        
        # Program similarity (secondary)
        program_score = 0
        if user['program'].lower() == other_user['program'].lower():
            program_score = 5
        elif any(word in other_user['program'].lower() for word in user['program'].lower().split()):
            program_score = 2
        
        # Age similarity (tertiary)
        age_diff = abs(user['age'] - other_user['age'])
        age_score = max(0, 5 - age_diff)
        
        return verification_bonus + events_score + program_score + age_score
    
    users.sort(key=compatibility_score, reverse=True)
    return users[:config.MAX_PROFILES_PER_SEARCH]


def delete_user(user_id: int):
    """Delete user and all related data"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM likes WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
    cursor.execute('DELETE FROM dislikes WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
    cursor.execute('DELETE FROM matches WHERE user1_id = ? OR user2_id = ?', (user_id, user_id))
    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()


def get_users_who_liked(user_id: int) -> List[Dict[str, Any]]:
    """Get list of users who liked the current user"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get users who liked this user, excluding those already liked back or disliked
    cursor.execute('''
        SELECT u.* FROM users u
        INNER JOIN likes l ON u.user_id = l.from_user_id
        WHERE l.to_user_id = ?
        AND u.is_banned = 0
        AND u.user_id NOT IN (
            SELECT to_user_id FROM likes WHERE from_user_id = ?
        )
        AND u.user_id NOT IN (
            SELECT to_user_id FROM dislikes WHERE from_user_id = ?
        )
        ORDER BY l.created_at DESC
    ''', (user_id, user_id, user_id))
    
    rows = cursor.fetchall()
    conn.close()
    
    users = []
    for row in rows:
        u = dict(row)
        u['events'] = json.loads(u['events'])
        users.append(u)
    
    return users