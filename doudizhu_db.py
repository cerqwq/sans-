"""
斗地主数据库操作模块
管理斗地主游戏相关的数据，确保不同账号数据独立
"""

import sqlite3
import json
import hashlib
from contextlib import contextmanager

DB_PATH = 'database.db'


@contextmanager
def get_db():
    """数据库连接上下文管理器，自动提交/回滚/关闭"""
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


def init_doudizhu_db():
    with get_db() as conn:
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
    print("斗地主数据库初始化成功")


def init_admin_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    print("管理员数据库初始化成功")


def get_user_data(username):
    with get_db() as conn:
        row = conn.execute(
            'SELECT * FROM doudizhu_data WHERE username = ?', (username,)
        ).fetchone()

    if row:
        return {
            'id': row['id'],
            'username': row['username'],
            'coins': row['coins'],
            'wins': row['wins'],
            'losses': row['losses'],
            'draws': row['draws'],
            'total_games': row['total_games'],
            'current_game': row['current_game'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
    return None


def create_user_doudizhu_data(username):
    try:
        with get_db() as conn:
            conn.execute('''
                INSERT INTO doudizhu_data (username, coins, wins, losses, draws, total_games)
                VALUES (?, 1000, 0, 0, 0, 0)
            ''', (username,))
        return True
    except sqlite3.IntegrityError:
        return False


def update_coins(username, amount):
    with get_db() as conn:
        conn.execute('''
            UPDATE doudizhu_data
            SET coins = coins + ?, updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
        ''', (amount, username))
    return True


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
    return True


def save_game_state(username, game_state):
    with get_db() as conn:
        conn.execute('''
            UPDATE doudizhu_data
            SET current_game = ?, updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
        ''', (json.dumps(game_state), username))
    return True


def get_game_state(username):
    with get_db() as conn:
        row = conn.execute(
            'SELECT current_game FROM doudizhu_data WHERE username = ?', (username,)
        ).fetchone()

    if row and row['current_game']:
        return json.loads(row['current_game'])
    return None


def clear_game_state(username):
    with get_db() as conn:
        conn.execute('''
            UPDATE doudizhu_data
            SET current_game = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
        ''', (username,))
    return True


def get_leaderboard(limit=10):
    with get_db() as conn:
        rows = conn.execute('''
            SELECT username, coins, wins, total_games
            FROM doudizhu_data
            ORDER BY coins DESC
            LIMIT ?
        ''', (limit,)).fetchall()

    return [
        {
            'rank': i + 1,
            'username': row['username'],
            'coins': row['coins'],
            'wins': row['wins'],
            'total_games': row['total_games']
        }
        for i, row in enumerate(rows)
    ]


def check_admin(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    with get_db() as conn:
        row = conn.execute(
            'SELECT 1 FROM admins WHERE username = ? AND password = ?',
            (username, hashed)
        ).fetchone()
    return row is not None


def create_admin(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    try:
        with get_db() as conn:
            conn.execute(
                'INSERT INTO admins (username, password) VALUES (?, ?)',
                (username, hashed)
            )
        return True
    except sqlite3.IntegrityError:
        return False
