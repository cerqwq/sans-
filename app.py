from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import hashlib
import json
import os
import uuid
import random
import string
from doudizhu_db import *

# ============================================
# Flask 应用配置
# ============================================
app = Flask(__name__)

# ============================================
# Session 配置
# ============================================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-123456')

# ============================================
# SocketIO 配置
# ============================================
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ============================================
# 游戏房间管理
# ============================================
game_rooms = {}

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ============================================
# 初始化数据库
# ============================================
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ 用户数据库初始化成功！")

# ============================================
# 首页路由
# ============================================
@app.route('/')
def index():
    return render_template('index.html')

# ============================================
# 注册页面路由
# ============================================
@app.route('/register_page')
def register_page():
    return render_template('register.html')

# ============================================
# 登录接口
# ============================================
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
              (username, hashed_password))
    user = c.fetchone()
    conn.close()
    
    if user:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        session['username'] = username
        
        user_data = get_user_data(username)
        if not user_data:
            create_user_doudizhu_data(username)
        
        return jsonify({
            'success': True, 
            'message': '登录成功！',
            'session_id': session_id
        })
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误！'})

# ============================================
# 注册接口
# ============================================
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空！'})
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度至少6位！'})
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                  (username, hashed_password))
        conn.commit()
        conn.close()
        
        create_user_doudizhu_data(username)
        
        return jsonify({'success': True, 'message': '注册成功！'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': '用户名已存在！'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败：{str(e)}'})

# ============================================
# 导航页面
# ============================================
@app.route('/nav')
def nav():
    if 'username' not in session:
        return render_template('index.html')
    return render_template('nav.html')

# ============================================
# 斗地主游戏页面
# ============================================
@app.route('/doudizhu')
def doudizhu():
    if 'username' not in session:
        return render_template('index.html')
    return render_template('doudizhu.html')

# ============================================
# 联机大厅页面
# ============================================
@app.route('/lobby')
def lobby():
    if 'username' not in session:
        return render_template('index.html')
    return render_template('lobby.html')

# ============================================
# 联机游戏页面
# ============================================
@app.route('/doudizhu_online')
def doudizhu_online():
    if 'username' not in session:
        return render_template('index.html')
    return render_template('doudizhu_online.html')

# ============================================
# 个人中心页面
# ============================================
@app.route('/profile')
def profile():
    if 'username' not in session:
        return render_template('index.html')
    return render_template('profile.html')

# ============================================
# 管理员登录页面
# ============================================
@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

# ============================================
# 管理员登录接口
# ============================================
@app.route('/api/admin_login', methods=['POST'])
def api_admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if check_admin(username, password):
        session['is_admin'] = True
        session['admin_username'] = username
        return jsonify({'success': True, 'message': '管理员登录成功！'})
    else:
        return jsonify({'success': False, 'message': '管理员账号或密码错误！'})

# ============================================
# 管理后台页面
# ============================================
@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return render_template('admin_login.html')
    return render_template('admin.html')

# ============================================
# 获取用户斗地主数据
# ============================================
@app.route('/api/get_user_data', methods=['GET'])
def api_get_user_data():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    username = session['username']
    data = get_user_data(username)
    
    if data:
        return jsonify({'success': True, 'data': data})
    else:
        return jsonify({'success': False, 'message': '数据不存在'})

# ============================================
# 更新游戏结果
# ============================================
@app.route('/api/update_result', methods=['POST'])
def api_update_result():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    username = session['username']
    data = request.json
    result = data.get('result')
    
    update_game_result(username, result)
    
    user_data = get_user_data(username)
    return jsonify({'success': True, 'data': user_data})

# ============================================
# 保存游戏状态
# ============================================
@app.route('/api/save_game', methods=['POST'])
def api_save_game():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    username = session['username']
    data = request.json
    game_state = data.get('game_state')
    
    save_game_state(username, game_state)
    return jsonify({'success': True, 'message': '游戏已保存'})

# ============================================
# 加载游戏状态
# ============================================
@app.route('/api/load_game', methods=['GET'])
def api_load_game():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    username = session['username']
    game_state = get_game_state(username)
    
    if game_state:
        return jsonify({'success': True, 'game_state': game_state})
    else:
        return jsonify({'success': False, 'message': '没有保存的游戏'})

# ============================================
# 获取排行榜
# ============================================
@app.route('/api/leaderboard', methods=['GET'])
def api_leaderboard():
    leaderboard = get_leaderboard(10)
    return jsonify({'success': True, 'leaderboard': leaderboard})

# ============================================
# 添加测试账号
# ============================================
@app.route('/add_test_user', methods=['GET'])
def add_test_user():
    username = 'admin'
    password = hashlib.sha256('123456'.encode()).hexdigest()
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                  (username, password))
        conn.commit()
        conn.close()
        
        create_user_doudizhu_data(username)
        
        return jsonify({'success': True, 'message': '测试账号添加成功！账号：admin，密码：123456'})
    except:
        return jsonify({'success': True, 'message': '测试账号已存在，无需重复添加！'})

# ============================================
# 创建默认管理员账号
# ============================================
@app.route('/create_admin')
def create_default_admin():
    username = 'relink'
    password = '196405'
    
    if create_admin(username, password):
        return f'✅ 管理员账号创建成功！<br>账号：{username}<br>密码：{password}'
    else:
        return '⚠️ 管理员账号已存在，无需重复创建'

# ============================================
# 退出登录
# ============================================
@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')

# ============================================
# 切换账号
# ============================================
@app.route('/switch_account')
def switch_account():
    session.clear()
    return render_template('index.html')

# ============================================
# 管理后台API
# ============================================
@app.route('/api/admin/users', methods=['GET'])
def api_admin_users():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '请先以管理员身份登录'})
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT u.id, u.username, u.created_at,
               d.coins, d.wins, d.losses, d.draws, d.total_games
        FROM users u
        LEFT JOIN doudizhu_data d ON u.username = d.username
        ORDER BY d.coins DESC
    ''')
    
    users_data = c.fetchall()
    conn.close()
    
    users = []
    for row in users_data:
        users.append({
            'id': row[0],
            'username': row[1],
            'created_at': row[2],
            'coins': row[3] if row[3] is not None else 0,
            'wins': row[4] if row[4] is not None else 0,
            'losses': row[5] if row[5] is not None else 0,
            'draws': row[6] if row[6] is not None else 0,
            'total_games': row[7] if row[7] is not None else 0
        })
    
    return jsonify({'success': True, 'users': users})

@app.route('/api/admin/update_coins', methods=['POST'])
def api_admin_update_coins():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '请先以管理员身份登录'})
    
    data = request.json
    username = data.get('username')
    amount = data.get('amount', 0)
    
    try:
        update_coins(username, amount)
        return jsonify({'success': True, 'message': '金币已更新'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/admin/set_coins', methods=['POST'])
def api_admin_set_coins():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '请先以管理员身份登录'})
    
    data = request.json
    username = data.get('username')
    coins = data.get('coins', 1000)
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            UPDATE doudizhu_data 
            SET coins = ?, updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
        ''', (coins, username))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'金币已设置为 {coins}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/admin/delete_user', methods=['POST'])
def api_admin_delete_user():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '请先以管理员身份登录'})
    
    data = request.json
    username = data.get('username')
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('DELETE FROM doudizhu_data WHERE username = ?', (username,))
        c.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'用户 {username} 已删除'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/admin/add_user', methods=['POST'])
def api_admin_add_user():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '请先以管理员身份登录'})
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    coins = data.get('coins', 1000)
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                  (username, hashed_password))
        c.execute('''
            INSERT INTO doudizhu_data (username, coins, wins, losses, draws, total_games)
            VALUES (?, ?, 0, 0, 0, 0)
        ''', (username, coins))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'用户 {username} 添加成功！'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': '用户名已存在！'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ============================================
# WebSocket 事件处理
# ============================================

@socketio.on('connect')
def handle_connect():
    print(f'客户端连接: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'客户端断开: {request.sid}')
    for room_code, room in list(game_rooms.items()):
        for player in room['players']:
            if player['sid'] == request.sid:
                room['players'].remove(player)
                if len(room['players']) == 0:
                    del game_rooms[room_code]
                else:
                    emit('player_left', {'username': player['username']}, room=room_code)
                break

@socketio.on('create_room')
def handle_create_room(data):
    username = data.get('username', '玩家')
    
    for code, room in list(game_rooms.items()):
        if room['game_state'] == 'waiting':
            for player in room['players']:
                if player['username'] == username or player['sid'] == request.sid:
                    room['players'].remove(player)
                    emit('player_left', {'username': username}, room=code)
                    if len(room['players']) == 0:
                        del game_rooms[code]
                    break
    
    room_code = generate_room_code()
    while room_code in game_rooms:
        room_code = generate_room_code()
    
    game_rooms[room_code] = {
        'players': [{
            'sid': request.sid,
            'username': username,
            'ready': False,
            'position': 0
        }],
        'game_state': 'waiting',
        'current_turn': 0,
        'last_play': None,
        'last_player': -1,
        'pass_count': 0,
        'landlord': -1,
        'multiplier': 1,
        'bomb_count': 0,
        'bottom_cards': [],
        'call_count': 0,
        'call_history': []
    }
    
    join_room(room_code)
    emit('room_created', {
        'room_code': room_code,
        'players': game_rooms[room_code]['players']
    })
    print(f'房间 {room_code} 创建成功，房主: {username}')

@socketio.on('join_room')
def handle_join_room(data):
    room_code = data.get('room_code', '').upper()
    username = data.get('username', '玩家')
    
    if room_code not in game_rooms:
        emit('error', {'message': '房间不存在'})
        return
    
    room = game_rooms[room_code]
    
    if len(room['players']) >= 3:
        emit('error', {'message': '房间已满'})
        return
    
    if room['game_state'] != 'waiting':
        emit('error', {'message': '游戏已开始'})
        return
    
    for player in room['players']:
        if player['username'] == username:
            emit('error', {'message': '你已经在该房间中了！'})
            return
        if player['sid'] == request.sid:
            emit('error', {'message': '你已经在该房间中了！'})
            return
    
    for code, other_room in list(game_rooms.items()):
        if code != room_code and other_room['game_state'] == 'waiting':
            for player in other_room['players']:
                if player['username'] == username:
                    other_room['players'].remove(player)
                    emit('player_left', {'username': username}, room=code)
                    if len(other_room['players']) == 0:
                        del game_rooms[code]
                    break
    
    player = {
        'sid': request.sid,
        'username': username,
        'ready': False,
        'position': len(room['players'])
    }
    
    room['players'].append(player)
    join_room(room_code)
    
    emit('player_joined', {
        'players': room['players']
    }, room=room_code)
    
    print(f'{username} 加入房间 {room_code}')

@socketio.on('join_game')
def handle_join_game(data):
    room_code = data.get('room_code')
    username = data.get('username', '玩家')
    
    if room_code not in game_rooms:
        emit('error', {'message': '房间不存在'})
        return
    
    room = game_rooms[room_code]
    
    player_found = False
    for player in room['players']:
        if player['username'] == username:
            player['sid'] = request.sid
            player_found = True
            break
    
    if not player_found:
        emit('error', {'message': '你不在该房间中'})
        return
    
    join_room(room_code)
    
    emit('room_state', {
        'players': [{
            'username': p['username'],
            'position': p['position'],
            'ready': p['ready']
        } for p in room['players']],
        'game_state': room['game_state']
    })
    
    print(f'{username} 加入游戏房间 {room_code}')

@socketio.on('player_ready')
def handle_player_ready(data):
    room_code = data.get('room_code')
    
    if room_code not in game_rooms:
        return
    
    room = game_rooms[room_code]
    
    for player in room['players']:
        if player['sid'] == request.sid:
            player['ready'] = not player['ready']
            break
    
    all_ready = all(p['ready'] for p in room['players'])
    
    emit('player_ready_update', {
        'players': [{
            'username': p['username'],
            'position': p['position'],
            'ready': p['ready']
        } for p in room['players']],
        'all_ready': all_ready
    }, room=room_code)
    
    if all_ready and len(room['players']) >= 2:
        room['game_state'] = 'calling'
        start_calling_phase(room_code)

def start_calling_phase(room_code):
    room = game_rooms[room_code]
    
    deck = create_full_deck()
    random.shuffle(deck)
    
    hands = []
    for i in range(len(room['players'])):
        hands.append(deck[i * 17:(i + 1) * 17])
    
    bottom_cards = deck[51:54]
    room['bottom_cards'] = bottom_cards
    
    for i, player in enumerate(room['players']):
        player['cards'] = hands[i]
        player['is_landlord'] = False
        player['has_called'] = False
    
    first_caller = random.randint(0, len(room['players']) - 1)
    room['current_turn'] = first_caller
    room['call_count'] = 0
    room['call_history'] = []
    room['multiplier'] = 1
    
    for i, player in enumerate(room['players']):
        emit('game_started', {
            'your_cards': sort_cards(player['cards']),
            'players': [{
                'username': p['username'],
                'position': p['position'],
                'card_count': len(p['cards']),
                'is_landlord': False
            } for p in room['players']],
            'current_turn': room['current_turn'],
            'your_position': i,
            'bottom_cards': bottom_cards,
            'phase': 'calling',
            'multiplier': room['multiplier']
        }, room=player['sid'])
    
    current_player = room['players'][room['current_turn']]
    emit('your_turn_to_call', {
        'multiplier': room['multiplier']
    }, room=current_player['sid'])

@socketio.on('call_landlord')
def handle_call_landlord(data):
    room_code = data.get('room_code')
    call = data.get('call', False)
    
    if room_code not in game_rooms:
        return
    
    room = game_rooms[room_code]
    current_player = room['players'][room['current_turn']]
    
    if current_player['sid'] != request.sid:
        emit('error', {'message': '还没轮到你'})
        return
    
    current_player['has_called'] = True
    room['call_count'] += 1
    
    if call:
        room['multiplier'] *= 2
        room['call_history'].append({
            'username': current_player['username'],
            'action': 'call',
            'multiplier': room['multiplier']
        })
        
        emit('call_result', {
            'username': current_player['username'],
            'action': 'call',
            'multiplier': room['multiplier'],
            'call_count': room['call_count']
        }, room=room_code)
        
        all_called = all(p['has_called'] for p in room['players'])
        
        if all_called:
            finalize_landlord(room_code, room['current_turn'])
        else:
            next_turn = (room['current_turn'] + 1) % len(room['players'])
            while room['players'][next_turn]['has_called']:
                next_turn = (next_turn + 1) % len(room['players'])
            
            room['current_turn'] = next_turn
            current_player = room['players'][room['current_turn']]
            emit('your_turn_to_call', {
                'multiplier': room['multiplier']
            }, room=current_player['sid'])
    else:
        room['call_history'].append({
            'username': current_player['username'],
            'action': 'no_call',
            'multiplier': room['multiplier']
        })
        
        emit('call_result', {
            'username': current_player['username'],
            'action': 'no_call',
            'multiplier': room['multiplier'],
            'call_count': room['call_count']
        }, room=room_code)
        
        all_no_call = all(
            p['has_called'] and not any(
                h['username'] == p['username'] and h['action'] == 'call'
                for h in room['call_history']
            )
            for p in room['players']
        )
        
        if all_no_call:
            emit('all_no_call', {}, room=room_code)
            start_calling_phase(room_code)
            return
        
        all_called = all(p['has_called'] for p in room['players'])
        
        if all_called:
            last_caller = None
            for h in reversed(room['call_history']):
                if h['action'] == 'call':
                    last_caller = h['username']
                    break
            
            if last_caller:
                for i, p in enumerate(room['players']):
                    if p['username'] == last_caller:
                        finalize_landlord(room_code, i)
                        return
            else:
                emit('all_no_call', {}, room=room_code)
                start_calling_phase(room_code)
                return
        else:
            next_turn = (room['current_turn'] + 1) % len(room['players'])
            while room['players'][next_turn]['has_called']:
                next_turn = (next_turn + 1) % len(room['players'])
            
            room['current_turn'] = next_turn
            current_player = room['players'][room['current_turn']]
            emit('your_turn_to_call', {
                'multiplier': room['multiplier']
            }, room=current_player['sid'])

def finalize_landlord(room_code, landlord_idx):
    room = game_rooms[room_code]
    room['landlord'] = landlord_idx
    room['players'][landlord_idx]['is_landlord'] = True
    room['players'][landlord_idx]['cards'].extend(room['bottom_cards'])
    room['current_turn'] = landlord_idx
    room['game_state'] = 'playing'
    
    for i, player in enumerate(room['players']):
        emit('landlord_confirmed', {
            'landlord': landlord_idx,
            'landlord_username': room['players'][landlord_idx]['username'],
            'your_cards': sort_cards(player['cards']) if i == landlord_idx else None,
            'players': [{
                'username': p['username'],
                'position': p['position'],
                'card_count': len(p['cards']),
                'is_landlord': p['is_landlord']
            } for p in room['players']],
            'current_turn': room['current_turn'],
            'your_position': i,
            'bottom_cards': room['bottom_cards'],
            'multiplier': room['multiplier']
        }, room=player['sid'])
    
    landlord_player = room['players'][landlord_idx]
    emit('your_turn_to_play', {}, room=landlord_player['sid'])

@socketio.on('play_cards')
def handle_play_cards(data):
    room_code = data.get('room_code')
    cards = data.get('cards', [])
    
    if room_code not in game_rooms:
        return
    
    room = game_rooms[room_code]
    current_player = room['players'][room['current_turn']]
    
    if current_player['sid'] != request.sid:
        emit('error', {'message': '还没轮到你'})
        return
    
    play_type = validate_play_type(cards)
    if not play_type['valid']:
        emit('error', {'message': play_type['message']})
        return
    
    if room['last_play'] and room['last_player'] != room['current_turn']:
        can_beat = can_beat_play(cards, room['last_play'])
        if not can_beat:
            emit('error', {'message': '管不上，请选择更大的牌'})
            return
    
    if play_type['type'] == 'bomb' or play_type['type'] == 'rocket':
        room['multiplier'] *= 2
        room['bomb_count'] += 1
    
    for card in cards:
        if card in current_player['cards']:
            current_player['cards'].remove(card)
    
    room['last_play'] = cards
    room['last_player'] = room['current_turn']
    room['pass_count'] = 0
    
    next_turn = (room['current_turn'] + 1) % len(room['players'])
    room['current_turn'] = next_turn
    
    emit('cards_played', {
        'username': current_player['username'],
        'cards': cards,
        'card_count': len(current_player['cards']),
        'next_turn': next_turn,
        'position': current_player['position'],
        'play_type': play_type['type'],
        'multiplier': room['multiplier'],
        'bomb_count': room['bomb_count']
    }, room=room_code)
    
    if len(current_player['cards']) == 0:
        coin_change = 100 * room['multiplier'] if current_player['is_landlord'] else 50 * room['multiplier']
        
        emit('game_over', {
            'winner': current_player['username'],
            'winner_position': current_player['position'],
            'multiplier': room['multiplier'],
            'bomb_count': room['bomb_count'],
            'coin_change': coin_change
        }, room=room_code)
        room['game_state'] = 'ended'
    else:
        next_player = room['players'][next_turn]
        emit('your_turn_to_play', {}, room=next_player['sid'])

@socketio.on('pass_turn')
def handle_pass_turn(data):
    room_code = data.get('room_code')
    
    if room_code not in game_rooms:
        return
    
    room = game_rooms[room_code]
    current_player = room['players'][room['current_turn']]
    
    if current_player['sid'] != request.sid:
        emit('error', {'message': '还没轮到你'})
        return
    
    if room['last_player'] == room['current_turn'] or room['last_player'] == -1:
        emit('error', {'message': '你是第一个出牌的，必须出牌'})
        return
    
    room['pass_count'] += 1
    
    next_turn = (room['current_turn'] + 1) % len(room['players'])
    
    if room['pass_count'] >= 2:
        room['pass_count'] = 0
        room['last_play'] = None
        room['last_player'] = -1
        emit('new_round', {}, room=room_code)
    
    room['current_turn'] = next_turn
    
    emit('turn_passed', {
        'username': current_player['username'],
        'next_turn': next_turn
    }, room=room_code)
    
    next_player = room['players'][next_turn]
    emit('your_turn_to_play', {}, room=next_player['sid'])

# ============================================
# 斗地主核心逻辑函数
# ============================================

def create_full_deck():
    suits = ['♠', '♥', '♣', '♦']
    ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
    deck = []
    for suit in suits:
        for rank in ranks:
            deck.append(f'{suit}{rank}')
    deck.append('🃏小王')
    deck.append('🃏大王')
    return deck

def sort_cards(cards):
    rank_order = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                  'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15, '小王': 16, '大王': 17}
    suit_order = {'♠': 0, '♥': 1, '♣': 2, '♦': 3, '🃏': 4}
    
    def card_sort_key(card):
        suit = card[0]
        rank = card[1:]
        return (rank_order.get(rank, 0), suit_order.get(suit, 0))
    
    return sorted(cards, key=card_sort_key)

def validate_play_type(cards):
    if len(cards) == 0:
        return {'valid': False, 'message': '请选择牌'}
    
    n = len(cards)
    ranks = []
    for card in cards:
        rank = card[1:]
        ranks.append(rank)
    
    rank_count = {}
    for r in ranks:
        rank_count[r] = rank_count.get(r, 0) + 1
    counts = sorted(rank_count.values(), reverse=True)
    unique_ranks = sorted(rank_count.keys(), key=lambda r: {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15, '小王': 16, '大王': 17}.get(r, 0))
    
    rank_values = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                   'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15, '小王': 16, '大王': 17}
    
    if n == 1:
        return {'valid': True, 'type': 'single', 'rank': ranks[0]}
    
    if n == 2 and ranks[0] == ranks[1]:
        return {'valid': True, 'type': 'pair', 'rank': ranks[0]}
    
    if n == 2 and '小王' in ranks and '大王' in ranks:
        return {'valid': True, 'type': 'rocket', 'rank': 'rocket'}
    
    if n == 3 and counts[0] == 3:
        r = [k for k, v in rank_count.items() if v == 3][0]
        return {'valid': True, 'type': 'triple', 'rank': r}
    
    if n == 4 and counts[0] == 3 and counts[1] == 1:
        r = [k for k, v in rank_count.items() if v == 3][0]
        return {'valid': True, 'type': 'triple_one', 'rank': r}
    
    if n == 5 and counts[0] == 3 and counts[1] == 2:
        r = [k for k, v in rank_count.items() if v == 3][0]
        return {'valid': True, 'type': 'triple_two', 'rank': r}
    
    if n == 4 and counts[0] == 4:
        r = [k for k, v in rank_count.items() if v == 4][0]
        return {'valid': True, 'type': 'bomb', 'rank': r}
    
    if n >= 5 and all(v == 1 for v in rank_count.values()):
        is_straight = True
        for i in range(1, len(unique_ranks)):
            if rank_values.get(unique_ranks[i], 0) - rank_values.get(unique_ranks[i-1], 0) != 1:
                is_straight = False
                break
        has_invalid = any(rank_values.get(r, 0) > 14 for r in unique_ranks)
        if is_straight and not has_invalid:
            return {'valid': True, 'type': 'straight', 'rank': unique_ranks[-1], 'length': n}
    
    if n >= 6 and n % 2 == 0 and all(v == 2 for v in rank_count.values()):
        pair_count = n // 2
        if pair_count >= 3:
            is_consecutive = True
            for i in range(1, len(unique_ranks)):
                if rank_values.get(unique_ranks[i], 0) - rank_values.get(unique_ranks[i-1], 0) != 1:
                    is_consecutive = False
                    break
            has_invalid = any(rank_values.get(r, 0) > 14 for r in unique_ranks)
            if is_consecutive and not has_invalid:
                return {'valid': True, 'type': 'consecutive_pairs', 'rank': unique_ranks[-1], 'length': pair_count}
    
    if counts[0] == 3:
        triple_ranks = sorted([k for k, v in rank_count.items() if v == 3], key=lambda r: rank_values.get(r, 0))
        triple_count = len(triple_ranks)
        if triple_count >= 2:
            is_consecutive = True
            for i in range(1, len(triple_ranks)):
                if rank_values.get(triple_ranks[i], 0) - rank_values.get(triple_ranks[i-1], 0) != 1:
                    is_consecutive = False
                    break
            has_invalid = any(rank_values.get(r, 0) > 14 for r in triple_ranks)
            if is_consecutive and not has_invalid:
                remaining = n - triple_count * 3
                if remaining == 0:
                    return {'valid': True, 'type': 'plane', 'rank': triple_ranks[-1], 'length': triple_count}
                if remaining == triple_count:
                    return {'valid': True, 'type': 'plane_single', 'rank': triple_ranks[-1], 'length': triple_count}
                if remaining == triple_count * 2:
                    return {'valid': True, 'type': 'plane_pair', 'rank': triple_ranks[-1], 'length': triple_count}
    
    return {'valid': False, 'message': '无效的牌型'}

def can_beat_play(new_cards, last_cards):
    new_type = validate_play_type(new_cards)
    last_type = validate_play_type(last_cards)
    
    if not new_type['valid'] or not last_type['valid']:
        return False
    
    rank_values = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                   'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15, '小王': 16, '大王': 17}
    
    if new_type['type'] == 'rocket':
        return True
    if last_type['type'] == 'rocket':
        return False
    
    if new_type['type'] == 'bomb' and last_type['type'] != 'bomb':
        return True
    if last_type['type'] == 'bomb' and new_type['type'] != 'bomb':
        return False
    
    if new_type['type'] != last_type['type']:
        return False
    
    if new_type.get('length') and last_type.get('length'):
        if new_type['length'] != last_type['length']:
            return False
    
    if len(new_cards) != len(last_cards):
        return False
    
    return rank_values.get(new_type['rank'], 0) > rank_values.get(last_type['rank'], 0)

# ============================================
# 初始化数据库（gunicorn 导入时也会执行）
# ============================================
init_db()
init_doudizhu_db()
init_admin_db()

# ============================================
# 程序入口（本地运行用）
# ============================================
if __name__ == '__main__':
    print()
    print("=" * 55)
    print("  🎮 欢乐斗地主 - 服务器启动中...")
    print("=" * 55)
    print()

    port = int(os.environ.get('PORT', 5000))
    print(f"  💻 本机访问: http://127.0.0.1:{port}")
    print()
    print(f"  ℹ️  按 Ctrl+C 停止服务器")
    print()
    print("=" * 55)
    print()

    socketio.run(app, debug=False, host='0.0.0.0', port=port)
