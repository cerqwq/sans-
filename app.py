import os
import uuid
import random
import string
import hashlib
import sqlite3

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room

from doudizhu_db import (
    init_doudizhu_db, init_admin_db, get_user_data, create_user_doudizhu_data,
    update_game_result, save_game_state, get_game_state, get_leaderboard,
    check_admin, create_admin, update_coins
)

# ============================================
# 配置
# ============================================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ============================================
# 常量
# ============================================
RANK_VALUES = {
    '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15, '小王': 16, '大王': 17
}

# ============================================
# 游戏房间（内存存储）
# ============================================
game_rooms = {}


def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# ============================================
# 数据库初始化
# ============================================
def init_db():
    import sqlite3
    conn = sqlite3.connect('database.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# ============================================
# 页面路由
# ============================================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register_page')
def register_page():
    return render_template('register.html')


@app.route('/nav')
def nav():
    if 'username' not in session:
        return render_template('index.html')
    return render_template('nav.html')


@app.route('/doudizhu')
def doudizhu():
    if 'username' not in session:
        return render_template('index.html')
    return render_template('doudizhu.html')


@app.route('/lobby')
def lobby():
    if 'username' not in session:
        return render_template('index.html')
    return render_template('lobby.html')


@app.route('/doudizhu_online')
def doudizhu_online():
    if 'username' not in session:
        return render_template('index.html')
    return render_template('doudizhu_online.html')


@app.route('/profile')
def profile():
    if 'username' not in session:
        return render_template('index.html')
    return render_template('profile.html')


@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')


@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return render_template('admin_login.html')
    return render_template('admin.html')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')


@app.route('/switch_account')
def switch_account():
    session.clear()
    return render_template('index.html')


# ============================================
# 用户认证 API
# ============================================
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})

    hashed = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect('database.db')
    user = conn.execute(
        'SELECT 1 FROM users WHERE username = ? AND password = ?',
        (username, hashed)
    ).fetchone()
    conn.close()

    if user:
        session['session_id'] = str(uuid.uuid4())
        session['username'] = username

        if not get_user_data(username):
            create_user_doudizhu_data(username)

        return jsonify({'success': True, 'message': '登录成功！', 'session_id': session['session_id']})

    return jsonify({'success': False, 'message': '用户名或密码错误！'})


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空！'})

    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度至少6位！'})

    if len(username) > 20:
        return jsonify({'success': False, 'message': '用户名不能超过20个字符！'})

    hashed = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn = sqlite3.connect('database.db')
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
        conn.commit()
        conn.close()

        create_user_doudizhu_data(username)
        return jsonify({'success': True, 'message': '注册成功！'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': '用户名已存在！'})
    except Exception as e:
        return jsonify({'success': False, 'message': '注册失败，请稍后重试'})


# ============================================
# 游戏数据 API
# ============================================
@app.route('/api/get_user_data', methods=['GET'])
def api_get_user_data():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})

    data = get_user_data(session['username'])
    if data:
        return jsonify({'success': True, 'data': data})
    return jsonify({'success': False, 'message': '数据不存在'})


@app.route('/api/update_result', methods=['POST'])
def api_update_result():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})

    result = request.json.get('result')
    if result not in ('win', 'loss', 'draw'):
        return jsonify({'success': False, 'message': '无效的结果'})

    update_game_result(session['username'], result)
    return jsonify({'success': True, 'data': get_user_data(session['username'])})


@app.route('/api/save_game', methods=['POST'])
def api_save_game():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})

    save_game_state(session['username'], request.json.get('game_state'))
    return jsonify({'success': True, 'message': '游戏已保存'})


@app.route('/api/load_game', methods=['GET'])
def api_load_game():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'})

    state = get_game_state(session['username'])
    if state:
        return jsonify({'success': True, 'game_state': state})
    return jsonify({'success': False, 'message': '没有保存的游戏'})


@app.route('/api/leaderboard', methods=['GET'])
def api_leaderboard():
    return jsonify({'success': True, 'leaderboard': get_leaderboard(10)})


# ============================================
# 管理员 API
# ============================================
@app.route('/api/admin_login', methods=['POST'])
def api_admin_login():
    data = request.json
    if check_admin(data.get('username', ''), data.get('password', '')):
        session['is_admin'] = True
        session['admin_username'] = data['username']
        return jsonify({'success': True, 'message': '管理员登录成功！'})
    return jsonify({'success': False, 'message': '管理员账号或密码错误！'})


@app.route('/api/admin/users', methods=['GET'])
def api_admin_users():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '请先以管理员身份登录'})

    conn = sqlite3.connect('database.db')
    rows = conn.execute('''
        SELECT u.id, u.username, u.created_at,
               d.coins, d.wins, d.losses, d.draws, d.total_games
        FROM users u
        LEFT JOIN doudizhu_data d ON u.username = d.username
        ORDER BY d.coins DESC
    ''').fetchall()
    conn.close()

    return jsonify({
        'success': True,
        'users': [{
            'id': r[0], 'username': r[1], 'created_at': r[2],
            'coins': r[3] or 0, 'wins': r[4] or 0,
            'losses': r[5] or 0, 'draws': r[6] or 0, 'total_games': r[7] or 0
        } for r in rows]
    })


@app.route('/api/admin/update_coins', methods=['POST'])
def api_admin_update_coins():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '请先以管理员身份登录'})

    data = request.json
    try:
        update_coins(data['username'], data.get('amount', 0))
        return jsonify({'success': True, 'message': '金币已更新'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/admin/set_coins', methods=['POST'])
def api_admin_set_coins():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '请先以管理员身份登录'})

    data = request.json
    try:
        conn = sqlite3.connect('database.db')
        conn.execute('''
            UPDATE doudizhu_data SET coins = ?, updated_at = CURRENT_TIMESTAMP WHERE username = ?
        ''', (data.get('coins', 1000), data['username']))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f"金币已设置为 {data.get('coins', 1000)}"})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/admin/delete_user', methods=['POST'])
def api_admin_delete_user():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '请先以管理员身份登录'})

    username = request.json.get('username')
    try:
        conn = sqlite3.connect('database.db')
        conn.execute('DELETE FROM doudizhu_data WHERE username = ?', (username,))
        conn.execute('DELETE FROM users WHERE username = ?', (username,))
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
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})

    hashed = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn = sqlite3.connect('database.db')
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
        conn.execute('''
            INSERT INTO doudizhu_data (username, coins, wins, losses, draws, total_games)
            VALUES (?, ?, 0, 0, 0, 0)
        ''', (username, data.get('coins', 1000)))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'用户 {username} 添加成功！'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': '用户名已存在！'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# ============================================
# WebSocket 事件
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

    # 清理该用户在其他等待房间的残留
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
        'players': [{'sid': request.sid, 'username': username, 'ready': False, 'position': 0}],
        'game_state': 'waiting',
        'current_turn': 0, 'last_play': None, 'last_player': -1,
        'pass_count': 0, 'landlord': -1, 'multiplier': 1,
        'bomb_count': 0, 'bottom_cards': [], 'call_count': 0, 'call_history': []
    }

    join_room(room_code)
    emit('room_created', {'room_code': room_code, 'players': game_rooms[room_code]['players']})


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

    # 检查重复
    for player in room['players']:
        if player['username'] == username or player['sid'] == request.sid:
            emit('error', {'message': '你已经在该房间中了！'})
            return

    # 从其他等待房间移除
    for code, other_room in list(game_rooms.items()):
        if code != room_code and other_room['game_state'] == 'waiting':
            for player in other_room['players']:
                if player['username'] == username:
                    other_room['players'].remove(player)
                    emit('player_left', {'username': username}, room=code)
                    if len(other_room['players']) == 0:
                        del game_rooms[code]
                    break

    room['players'].append({
        'sid': request.sid, 'username': username,
        'ready': False, 'position': len(room['players'])
    })
    join_room(room_code)
    emit('player_joined', {'players': room['players']}, room=room_code)


@socketio.on('join_game')
def handle_join_game(data):
    room_code = data.get('room_code')
    username = data.get('username', '玩家')

    if room_code not in game_rooms:
        emit('error', {'message': '房间不存在'})
        return

    room = game_rooms[room_code]

    for player in room['players']:
        if player['username'] == username:
            player['sid'] = request.sid
            join_room(room_code)
            emit('room_state', {
                'players': [{'username': p['username'], 'position': p['position'], 'ready': p['ready']}
                            for p in room['players']],
                'game_state': room['game_state']
            })
            return

    emit('error', {'message': '你不在该房间中'})


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
        'players': [{'username': p['username'], 'position': p['position'], 'ready': p['ready']}
                    for p in room['players']],
        'all_ready': all_ready
    }, room=room_code)

    if all_ready and len(room['players']) >= 2:
        room['game_state'] = 'calling'
        start_calling_phase(room_code)


# ============================================
# 叫地主阶段
# ============================================
def start_calling_phase(room_code):
    room = game_rooms[room_code]

    deck = create_full_deck()
    random.shuffle(deck)

    hands = [deck[i * 17:(i + 1) * 17] for i in range(len(room['players']))]
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
            'players': [{'username': p['username'], 'position': p['position'],
                         'card_count': len(p['cards']), 'is_landlord': False}
                        for p in room['players']],
            'current_turn': room['current_turn'],
            'your_position': i,
            'bottom_cards': bottom_cards,
            'phase': 'calling',
            'multiplier': room['multiplier']
        }, room=player['sid'])

    current_player = room['players'][room['current_turn']]
    emit('your_turn_to_call', {'multiplier': room['multiplier']}, room=current_player['sid'])


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
            'username': current_player['username'], 'action': 'call',
            'multiplier': room['multiplier']
        })

        emit('call_result', {
            'username': current_player['username'], 'action': 'call',
            'multiplier': room['multiplier'], 'call_count': room['call_count']
        }, room=room_code)

        if all(p['has_called'] for p in room['players']):
            finalize_landlord(room_code, room['current_turn'])
        else:
            _advance_call_turn(room, room_code)
    else:
        room['call_history'].append({
            'username': current_player['username'], 'action': 'no_call',
            'multiplier': room['multiplier']
        })

        emit('call_result', {
            'username': current_player['username'], 'action': 'no_call',
            'multiplier': room['multiplier'], 'call_count': room['call_count']
        }, room=room_code)

        # 检查是否所有人都没叫
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

        if all(p['has_called'] for p in room['players']):
            # 找到最后一个叫地主的人
            for h in reversed(room['call_history']):
                if h['action'] == 'call':
                    for i, p in enumerate(room['players']):
                        if p['username'] == h['username']:
                            finalize_landlord(room_code, i)
                            return
            # 没人叫，重新发牌
            emit('all_no_call', {}, room=room_code)
            start_calling_phase(room_code)
        else:
            _advance_call_turn(room, room_code)


def _advance_call_turn(room, room_code):
    next_turn = (room['current_turn'] + 1) % len(room['players'])
    while room['players'][next_turn]['has_called']:
        next_turn = (next_turn + 1) % len(room['players'])

    room['current_turn'] = next_turn
    emit('your_turn_to_call', {'multiplier': room['multiplier']},
         room=room['players'][next_turn]['sid'])


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
            'players': [{'username': p['username'], 'position': p['position'],
                         'card_count': len(p['cards']), 'is_landlord': p['is_landlord']}
                        for p in room['players']],
            'current_turn': room['current_turn'],
            'your_position': i,
            'bottom_cards': room['bottom_cards'],
            'multiplier': room['multiplier']
        }, room=player['sid'])

    emit('your_turn_to_play', {}, room=room['players'][landlord_idx]['sid'])


# ============================================
# 出牌阶段
# ============================================
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
        if not can_beat_play(cards, room['last_play']):
            emit('error', {'message': '管不上，请选择更大的牌'})
            return

    if play_type['type'] in ('bomb', 'rocket'):
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
        emit('your_turn_to_play', {}, room=room['players'][next_turn]['sid'])


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

    emit('your_turn_to_play', {}, room=room['players'][next_turn]['sid'])


# ============================================
# 斗地主核心逻辑
# ============================================
def create_full_deck():
    suits = ['♠', '♥', '♣', '♦']
    ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
    deck = [f'{s}{r}' for s in suits for r in ranks]
    deck.extend(['🃏小王', '🃏大王'])
    return deck


def sort_cards(cards):
    suit_order = {'♠': 0, '♥': 1, '♣': 2, '♦': 3, '🃏': 4}

    def key(card):
        suit = card[0]
        rank = card[1:]
        return (RANK_VALUES.get(rank, 0), suit_order.get(suit, 0))

    return sorted(cards, key=key)


def validate_play_type(cards):
    if not cards:
        return {'valid': False, 'message': '请选择牌'}

    n = len(cards)
    ranks = [c[1:] for c in cards]
    rank_count = {}
    for r in ranks:
        rank_count[r] = rank_count.get(r, 0) + 1

    counts = sorted(rank_count.values(), reverse=True)
    unique_ranks = sorted(rank_count.keys(), key=lambda r: RANK_VALUES.get(r, 0))

    # 单张
    if n == 1:
        return {'valid': True, 'type': 'single', 'rank': ranks[0]}

    # 对子
    if n == 2 and ranks[0] == ranks[1]:
        return {'valid': True, 'type': 'pair', 'rank': ranks[0]}

    # 王炸
    if n == 2 and '小王' in ranks and '大王' in ranks:
        return {'valid': True, 'type': 'rocket', 'rank': 'rocket'}

    # 三条
    if n == 3 and counts[0] == 3:
        r = [k for k, v in rank_count.items() if v == 3][0]
        return {'valid': True, 'type': 'triple', 'rank': r}

    # 三带一
    if n == 4 and counts[0] == 3 and counts[1] == 1:
        r = [k for k, v in rank_count.items() if v == 3][0]
        return {'valid': True, 'type': 'triple_one', 'rank': r}

    # 三带二
    if n == 5 and counts[0] == 3 and counts[1] == 2:
        r = [k for k, v in rank_count.items() if v == 3][0]
        return {'valid': True, 'type': 'triple_two', 'rank': r}

    # 炸弹
    if n == 4 and counts[0] == 4:
        r = [k for k, v in rank_count.items() if v == 4][0]
        return {'valid': True, 'type': 'bomb', 'rank': r}

    # 顺子
    if n >= 5 and all(v == 1 for v in rank_count.values()):
        is_straight = all(
            RANK_VALUES.get(unique_ranks[i], 0) - RANK_VALUES.get(unique_ranks[i - 1], 0) == 1
            for i in range(1, len(unique_ranks))
        )
        if is_straight and all(RANK_VALUES.get(r, 0) <= 14 for r in unique_ranks):
            return {'valid': True, 'type': 'straight', 'rank': unique_ranks[-1], 'length': n}

    # 连对
    if n >= 6 and n % 2 == 0 and all(v == 2 for v in rank_count.values()):
        pair_count = n // 2
        if pair_count >= 3:
            is_consecutive = all(
                RANK_VALUES.get(unique_ranks[i], 0) - RANK_VALUES.get(unique_ranks[i - 1], 0) == 1
                for i in range(1, len(unique_ranks))
            )
            if is_consecutive and all(RANK_VALUES.get(r, 0) <= 14 for r in unique_ranks):
                return {'valid': True, 'type': 'consecutive_pairs', 'rank': unique_ranks[-1], 'length': pair_count}

    # 飞机系列
    if counts[0] == 3:
        triple_ranks = sorted(
            [k for k, v in rank_count.items() if v == 3],
            key=lambda r: RANK_VALUES.get(r, 0)
        )
        triple_count = len(triple_ranks)
        if triple_count >= 2:
            is_consecutive = all(
                RANK_VALUES.get(triple_ranks[i], 0) - RANK_VALUES.get(triple_ranks[i - 1], 0) == 1
                for i in range(1, len(triple_ranks))
            )
            if is_consecutive and all(RANK_VALUES.get(r, 0) <= 14 for r in triple_ranks):
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

    return RANK_VALUES.get(new_type['rank'], 0) > RANK_VALUES.get(last_type['rank'], 0)


# ============================================
# 启动
# ============================================
init_db()
init_doudizhu_db()
init_admin_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n{'='*40}")
    print(f"  斗地主服务器启动")
    print(f"  本机访问: http://127.0.0.1:{port}")
    print(f"{'='*40}\n")
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
