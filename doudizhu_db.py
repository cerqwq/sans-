"""
斗地主数据库模块
上下文管理器模式，统一连接管理
"""

import sqlite3
import json
import hashlib
from contextlib import contextmanager

DB_PATH = 'database.db'


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """初始化所有表"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS doudizhu_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                coins INTEGER DEFAULT 1000,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                total_games INTEGER DEFAULT 0,
                current_game TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    print("[DB] 数据库初始化完成")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================
# 用户操作
# ============================================

def create_user(username, password):
    """创建用户账号"""
    hashed = hash_password(password)
    try:
        with get_db() as conn:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
            conn.execute('''
                INSERT INTO doudizhu_data (username, coins, wins, losses, draws, total_games)
                VALUES (?, 1000, 0, 0, 0, 0)
            ''', (username,))
        return True, '注册成功！'
    except sqlite3.IntegrityError:
        return False, '用户名已存在！'


def verify_user(username, password):
    """验证用户登录"""
    hashed = hash_password(password)
    with get_db() as conn:
        row = conn.execute(
            'SELECT 1 FROM users WHERE username = ? AND password = ?',
            (username, hashed)
        ).fetchone()
    return row is not None


def ensure_user_data(username):
    """确保用户有游戏数据"""
    with get_db() as conn:
        exists = conn.execute(
            'SELECT 1 FROM doudizhu_data WHERE username = ?', (username,)
        ).fetchone()
        if not exists:
            conn.execute('''
                INSERT INTO doudizhu_data (username, coins, wins, losses, draws, total_games)
                VALUES (?, 1000, 0, 0, 0, 0)
            ''', (username,))


# ============================================
# 游戏数据操作
# ============================================

def get_user_data(username):
    with get_db() as conn:
        row = conn.execute(
            'SELECT * FROM doudizhu_data WHERE username = ?', (username,)
        ).fetchone()
    if row:
        return dict(row)
    return None


def update_game_result(username, result):
    with get_db() as conn:
        if result == 'win':
            conn.execute('''
                UPDATE doudizhu_data
                SET wins = wins + 1, total_games = total_games + 1,
                    coins = coins + 100, updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
            ''', (username,))
        elif result == 'loss':
            conn.execute('''
                UPDATE doudizhu_data
                SET losses = losses + 1, total_games = total_games + 1,
                    coins = coins - 50, updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
            ''', (username,))
        elif result == 'draw':
            conn.execute('''
                UPDATE doudizhu_data
                SET draws = draws + 1, total_games = total_games + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
            ''', (username,))


def update_coins(username, amount):
    with get_db() as conn:
        conn.execute('''
            UPDATE doudizhu_data
            SET coins = coins + ?, updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
        ''', (amount, username))


def set_coins(username, coins):
    with get_db() as conn:
        conn.execute('''
            UPDATE doudizhu_data
            SET coins = ?, updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
        ''', (coins, username))


def get_leaderboard(limit=10):
    with get_db() as conn:
        rows = conn.execute('''
            SELECT username, coins, wins, total_games
            FROM doudizhu_data ORDER BY coins DESC LIMIT ?
        ''', (limit,)).fetchall()
    return [dict(r) for r in rows]


# ============================================
# 管理员操作
# ============================================

def check_admin(username, password):
    hashed = hash_password(password)
    with get_db() as conn:
        row = conn.execute(
            'SELECT 1 FROM admins WHERE username = ? AND password = ?',
            (username, hashed)
        ).fetchone()
    return row is not None


def create_admin(username, password):
    hashed = hash_password(password)
    try:
        with get_db() as conn:
            conn.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, hashed))
        return True
    except sqlite3.IntegrityError:
        return False


def get_all_users():
    with get_db() as conn:
        rows = conn.execute('''
            SELECT u.id, u.username, u.created_at,
                   d.coins, d.wins, d.losses, d.draws, d.total_games
            FROM users u
            LEFT JOIN doudizhu_data d ON u.username = d.username
            ORDER BY d.coins DESC
        ''').fetchall()
    return [dict(r) for r in rows]


def delete_user(username):
    with get_db() as conn:
        conn.execute('DELETE FROM doudizhu_data WHERE username = ?', (username,))
        conn.execute('DELETE FROM users WHERE username = ?', (username,))


def add_user_by_admin(username, password, coins=1000):
    hashed = hash_password(password)
    try:
        with get_db() as conn:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
            conn.execute('''
                INSERT INTO doudizhu_data (username, coins, wins, losses, draws, total_games)
                VALUES (?, ?, 0, 0, 0, 0)
            ''', (username, coins))
        return True, f'用户 {username} 添加成功！'
    except sqlite3.IntegrityError:
        return False, '用户名已存在！'
