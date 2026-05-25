"""
斗地主数据库操作模块
作用：管理斗地主游戏相关的数据，确保不同账号数据独立
"""

import sqlite3
import json
import hashlib

# ============================================
# 初始化斗地主相关数据表
# ============================================
def init_doudizhu_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # 用户斗地主数据表（每个用户独立）
    c.execute('''
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
    
    conn.commit()
    conn.close()
    print("✅ 斗地主数据库初始化成功！")

# ============================================
# 初始化管理员表
# ============================================
def init_admin_db():
    """初始化管理员表"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ 管理员数据库初始化成功！")

# ============================================
# 获取用户斗地主数据
# ============================================
def get_user_data(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM doudizhu_data WHERE username = ?', (username,))
    data = c.fetchone()
    conn.close()
    
    if data:
        return {
            'id': data[0],
            'username': data[1],
            'coins': data[2],
            'wins': data[3],
            'losses': data[4],
            'draws': data[5],
            'total_games': data[6],
            'current_game': data[7],
            'created_at': data[8],
            'updated_at': data[9]
        }
    return None

# ============================================
# 创建新用户斗地主数据
# ============================================
def create_user_doudizhu_data(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO doudizhu_data (username, coins, wins, losses, draws, total_games)
            VALUES (?, 1000, 0, 0, 0, 0)
        ''', (username,))
        conn.commit()
        success = True
    except:
        success = False
    conn.close()
    return success

# ============================================
# 更新用户金币
# ============================================
def update_coins(username, amount):
    """amount 可以是正数（增加）或负数（减少）"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        UPDATE doudizhu_data 
        SET coins = coins + ?, updated_at = CURRENT_TIMESTAMP
        WHERE username = ?
    ''', (amount, username))
    conn.commit()
    conn.close()
    return True

# ============================================
# 更新游戏结果
# ============================================
def update_game_result(username, result):
    """
    result: 'win' 或 'loss' 或 'draw'
    """
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if result == 'win':
        c.execute('''
            UPDATE doudizhu_data 
            SET wins = wins + 1, total_games = total_games + 1, 
                coins = coins + 100, updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
        ''', (username,))
    elif result == 'loss':
        c.execute('''
            UPDATE doudizhu_data 
            SET losses = losses + 1, total_games = total_games + 1, 
                coins = coins - 50, updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
        ''', (username,))
    elif result == 'draw':
        c.execute('''
            UPDATE doudizhu_data 
            SET draws = draws + 1, total_games = total_games + 1, 
                updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
        ''', (username,))
    
    conn.commit()
    conn.close()
    return True

# ============================================
# 保存当前游戏状态
# ============================================
def save_game_state(username, game_state):
    """game_state 是字典，会转为JSON存储"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        UPDATE doudizhu_data 
        SET current_game = ?, updated_at = CURRENT_TIMESTAMP
        WHERE username = ?
    ''', (json.dumps(game_state), username))
    conn.commit()
    conn.close()
    return True

# ============================================
# 获取当前游戏状态
# ============================================
def get_game_state(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT current_game FROM doudizhu_data WHERE username = ?', (username,))
    data = c.fetchone()
    conn.close()
    
    if data and data[0]:
        return json.loads(data[0])
    return None

# ============================================
# 清除游戏状态
# ============================================
def clear_game_state(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        UPDATE doudizhu_data 
        SET current_game = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE username = ?
    ''', (username,))
    conn.commit()
    conn.close()
    return True

# ============================================
# 获取排行榜
# ============================================
def get_leaderboard(limit=10):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        SELECT username, coins, wins, total_games 
        FROM doudizhu_data 
        ORDER BY coins DESC 
        LIMIT ?
    ''', (limit,))
    data = c.fetchall()
    conn.close()
    
    leaderboard = []
    for i, row in enumerate(data):
        leaderboard.append({
            'rank': i + 1,
            'username': row[0],
            'coins': row[1],
            'wins': row[2],
            'total_games': row[3]
        })
    return leaderboard

# ============================================
# 管理员相关函数
# ============================================

def check_admin(username, password):
    """验证管理员账号密码"""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM admins WHERE username = ? AND password = ?', 
              (username, hashed_password))
    admin = c.fetchone()
    conn.close()
    return admin is not None

def create_admin(username, password):
    """创建管理员账号"""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO admins (username, password) VALUES (?, ?)',
                  (username, hashed_password))
        conn.commit()
        success = True
    except:
        success = False
    conn.close()
    return success
