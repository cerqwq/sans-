"""
斗地主 WebSocket 事件处理模块
供 server.py 和 app.py 共用
"""

import random
import string
import copy
from flask_socketio import emit, join_room
from flask import request

from doudizhu_db import (
    update_game_result, update_coins, save_room, delete_room
)
from game_engine import (
    create_deck, shuffle_deck, sort_cards, validate_play, can_beat
)

# 游戏房间 (内存存储)
game_rooms = {}


def gen_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def serialize_room(room):
    data = copy.deepcopy(room)
    for p in data['players']:
        p.pop('sid', None)
        p.pop('cards', None)
    return data


def register_ws_handlers(socketio):
    """注册所有 WebSocket 事件处理器"""

    @socketio.on('connect')
    def handle_connect():
        print(f'[WS] 连接: {request.sid}')

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f'[WS] 断开: {request.sid}')
        for code, room in list(game_rooms.items()):
            for p in room['players']:
                if p['sid'] == request.sid:
                    room['players'].remove(p)
                    if not room['players']:
                        del game_rooms[code]
                    else:
                        emit('player_left', {'username': p['username']}, room=code)
                    break

    @socketio.on('create_room')
    def handle_create_room(data):
        username = data.get('username', '玩家')

        for code, room in list(game_rooms.items()):
            if room['state'] == 'waiting':
                for p in room['players']:
                    if p['username'] == username or p['sid'] == request.sid:
                        room['players'].remove(p)
                        emit('player_left', {'username': username}, room=code)
                        if not room['players']:
                            del game_rooms[code]
                        break

        room_code = gen_room_code()
        while room_code in game_rooms:
            room_code = gen_room_code()

        game_rooms[room_code] = {
            'players': [{'sid': request.sid, 'username': username, 'ready': False, 'pos': 0}],
            'state': 'waiting',
            'turn': 0, 'last_play': None, 'last_player': -1,
            'pass_count': 0, 'landlord': -1, 'multiplier': 1,
            'bomb_count': 0, 'bottom_cards': [], 'call_count': 0, 'call_history': []
        }

        save_room(room_code, 'waiting', serialize_room(game_rooms[room_code]))
        join_room(room_code)
        emit('room_created', {'room_code': room_code, 'players': game_rooms[room_code]['players']})

    @socketio.on('join_room')
    def handle_join_room(data):
        room_code = (data.get('room_code') or '').upper()
        username = data.get('username', '玩家')

        if room_code not in game_rooms:
            emit('error', {'message': '房间不存在'})
            return

        room = game_rooms[room_code]

        if len(room['players']) >= 3:
            emit('error', {'message': '房间已满'})
            return
        if room['state'] != 'waiting':
            emit('error', {'message': '游戏已开始'})
            return

        for p in room['players']:
            if p['username'] == username or p['sid'] == request.sid:
                emit('error', {'message': '你已经在该房间中了！'})
                return

        for code, other in list(game_rooms.items()):
            if code != room_code and other['state'] == 'waiting':
                for p in other['players']:
                    if p['username'] == username:
                        other['players'].remove(p)
                        emit('player_left', {'username': username}, room=code)
                        if not other['players']:
                            del game_rooms[code]
                        break

        room['players'].append({
            'sid': request.sid, 'username': username,
            'ready': False, 'pos': len(room['players'])
        })

        save_room(room_code, room['state'], serialize_room(room))
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
        for p in room['players']:
            if p['username'] == username:
                p['sid'] = request.sid
                join_room(room_code)
                emit('room_state', {
                    'players': [{'username': x['username'], 'position': x['pos'], 'ready': x['ready']}
                                for x in room['players']],
                    'game_state': room['state']
                })
                return

        emit('error', {'message': '你不在该房间中'})

    @socketio.on('player_ready')
    def handle_player_ready(data):
        room_code = data.get('room_code')
        if room_code not in game_rooms:
            return

        room = game_rooms[room_code]
        for p in room['players']:
            if p['sid'] == request.sid:
                p['ready'] = not p['ready']
                break

        all_ready = all(p['ready'] for p in room['players'])
        emit('player_ready_update', {
            'players': [{'username': p['username'], 'position': p['pos'], 'ready': p['ready']}
                        for p in room['players']],
            'all_ready': all_ready
        }, room=room_code)

        if all_ready and len(room['players']) >= 3:
            room['state'] = 'calling'
            start_calling_phase(room_code)
        elif all_ready and len(room['players']) < 3:
            emit('error', {'message': '需要3名玩家才能开始游戏'}, room=room_code)

    @socketio.on('call_landlord')
    def handle_call_landlord(data):
        room_code = data.get('room_code')
        call = data.get('call', False)

        if room_code not in game_rooms:
            return

        room = game_rooms[room_code]
        cur = room['players'][room['turn']]

        if cur['sid'] != request.sid:
            emit('error', {'message': '还没轮到你'})
            return

        cur['has_called'] = True
        room['call_count'] += 1

        if call:
            room['multiplier'] *= 2
            room['call_history'].append({'username': cur['username'], 'action': 'call'})
            emit('call_result', {
                'username': cur['username'], 'action': 'call',
                'multiplier': room['multiplier'], 'call_count': room['call_count']
            }, room=room_code)

            if all(p['has_called'] for p in room['players']):
                finalize_landlord(room_code, room['turn'])
            else:
                advance_call_turn(room, room_code)
        else:
            room['call_history'].append({'username': cur['username'], 'action': 'no_call'})
            emit('call_result', {
                'username': cur['username'], 'action': 'no_call',
                'multiplier': room['multiplier'], 'call_count': room['call_count']
            }, room=room_code)

            all_no_call = all(
                p['has_called'] and not any(h['username'] == p['username'] and h['action'] == 'call'
                                            for h in room['call_history'])
                for p in room['players']
            )

            if all_no_call:
                emit('all_no_call', {}, room=room_code)
                start_calling_phase(room_code)
                return

            if all(p['has_called'] for p in room['players']):
                for h in reversed(room['call_history']):
                    if h['action'] == 'call':
                        for i, p in enumerate(room['players']):
                            if p['username'] == h['username']:
                                finalize_landlord(room_code, i)
                                return
                emit('all_no_call', {}, room=room_code)
                start_calling_phase(room_code)
            else:
                advance_call_turn(room, room_code)

    @socketio.on('play_cards')
    def handle_play_cards(data):
        room_code = data.get('room_code')
        cards = data.get('cards', [])

        if room_code not in game_rooms:
            return

        room = game_rooms[room_code]
        cur = room['players'][room['turn']]

        if cur['sid'] != request.sid:
            emit('error', {'message': '还没轮到你'})
            return

        play_type = validate_play(cards)
        if not play_type['valid']:
            emit('error', {'message': play_type['message']})
            return

        # 服务端验证：出的牌必须在手牌中
        hand_copy = list(cur['cards'])
        for card in cards:
            if card in hand_copy:
                hand_copy.remove(card)
            else:
                emit('error', {'message': '你没有这些牌！'})
                return

        if room['last_play'] and room['last_player'] != room['turn']:
            if not can_beat(cards, room['last_play']):
                emit('error', {'message': '管不上，请选择更大的牌'})
                return

        if play_type['type'] in ('bomb', 'rocket'):
            room['multiplier'] *= 2
            room['bomb_count'] += 1

        for card in cards:
            if card in cur['cards']:
                cur['cards'].remove(card)

        room['last_play'] = cards
        room['last_player'] = room['turn']
        room['pass_count'] = 0

        nxt = (room['turn'] + 1) % len(room['players'])
        room['turn'] = nxt

        emit('cards_played', {
            'username': cur['username'],
            'cards': cards,
            'card_count': len(cur['cards']),
            'next_turn': nxt,
            'position': cur['pos'],
            'play_type': play_type['type'],
            'multiplier': room['multiplier'],
            'bomb_count': room['bomb_count']
        }, room=room_code)

        if len(cur['cards']) == 0:
            coin_change = 100 * room['multiplier'] if cur['is_landlord'] else 50 * room['multiplier']

            for p in room['players']:
                if p['username'] == cur['username']:
                    update_coins(p['username'], coin_change)
                    update_game_result(p['username'], 'win')
                else:
                    update_coins(p['username'], -coin_change // 2)
                    update_game_result(p['username'], 'loss')

            emit('game_over', {
                'winner': cur['username'],
                'winner_position': cur['pos'],
                'multiplier': room['multiplier'],
                'bomb_count': room['bomb_count'],
                'coin_change': coin_change
            }, room=room_code)
            room['state'] = 'ended'
            save_room(room_code, 'ended', serialize_room(room))
            delete_room(room_code)
        else:
            save_room(room_code, 'playing', serialize_room(room))
            emit('your_turn_to_play', {}, room=room['players'][nxt]['sid'])

    @socketio.on('pass_turn')
    def handle_pass_turn(data):
        room_code = data.get('room_code')
        if room_code not in game_rooms:
            return

        room = game_rooms[room_code]
        cur = room['players'][room['turn']]

        if cur['sid'] != request.sid:
            emit('error', {'message': '还没轮到你'})
            return

        if room['last_player'] == room['turn'] or room['last_player'] == -1:
            emit('error', {'message': '你是第一个出牌的，必须出牌'})
            return

        room['pass_count'] += 1
        nxt = (room['turn'] + 1) % len(room['players'])

        emit('turn_passed', {'username': cur['username'], 'next_turn': nxt}, room=room_code)

        if room['pass_count'] >= 2:
            room['pass_count'] = 0
            room['last_play'] = None
            room['last_player'] = -1
            emit('new_round', {}, room=room_code)

        room['turn'] = nxt
        emit('your_turn_to_play', {}, room=room['players'][nxt]['sid'])


def start_calling_phase(room_code):
    room = game_rooms[room_code]

    deck = shuffle_deck(create_deck())
    hands = [deck[i * 17:(i + 1) * 17] for i in range(len(room['players']))]
    bottom_cards = deck[51:54]
    room['bottom_cards'] = bottom_cards

    for i, p in enumerate(room['players']):
        p['cards'] = hands[i]
        p['is_landlord'] = False
        p['has_called'] = False

    room['turn'] = random.randint(0, len(room['players']) - 1)
    room['call_count'] = 0
    room['call_history'] = []
    room['multiplier'] = 1

    for i, p in enumerate(room['players']):
        emit('game_started', {
            'your_cards': sort_cards(p['cards']),
            'players': [{'username': x['username'], 'position': x['pos'],
                         'card_count': len(x['cards']), 'is_landlord': False}
                        for x in room['players']],
            'current_turn': room['turn'],
            'your_position': i,
            'bottom_cards': bottom_cards,
            'phase': 'calling',
            'multiplier': room['multiplier']
        }, room=p['sid'])

    save_room(room_code, 'calling', serialize_room(room))
    emit('your_turn_to_call', {'multiplier': room['multiplier']},
         room=room['players'][room['turn']]['sid'])


def advance_call_turn(room, room_code):
    nxt = (room['turn'] + 1) % len(room['players'])
    while room['players'][nxt]['has_called']:
        nxt = (nxt + 1) % len(room['players'])
    room['turn'] = nxt
    emit('your_turn_to_call', {'multiplier': room['multiplier']},
         room=room['players'][nxt]['sid'])


def finalize_landlord(room_code, landlord_idx):
    room = game_rooms[room_code]
    room['landlord'] = landlord_idx
    room['players'][landlord_idx]['is_landlord'] = True
    room['players'][landlord_idx]['cards'].extend(room['bottom_cards'])
    room['turn'] = landlord_idx
    room['state'] = 'playing'

    for i, p in enumerate(room['players']):
        emit('landlord_confirmed', {
            'landlord': landlord_idx,
            'landlord_username': room['players'][landlord_idx]['username'],
            'your_cards': sort_cards(p['cards']) if i == landlord_idx else None,
            'players': [{'username': x['username'], 'position': x['pos'],
                         'card_count': len(x['cards']), 'is_landlord': x['is_landlord']}
                        for x in room['players']],
            'current_turn': room['turn'],
            'your_position': i,
            'bottom_cards': room['bottom_cards'],
            'multiplier': room['multiplier']
        }, room=p['sid'])

    emit('your_turn_to_play', {}, room=room['players'][landlord_idx]['sid'])
