"""
斗地主游戏引擎
纯逻辑模块：牌组、验证、AI
"""

import random

RANK_VALUES = {
    '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15, '小王': 16, '大王': 17
}

SUITS = ['♠', '♥', '♣', '♦']
RANKS = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']


def create_deck():
    """创建一副54张牌"""
    deck = [f'{s}{r}' for s in SUITS for r in RANKS]
    deck.extend(['🃏小王', '🃏大王'])
    return deck


def shuffle_deck(deck):
    random.shuffle(deck)
    return deck


def sort_cards(cards):
    """按点数和花色排序"""
    suit_order = {'♠': 0, '♥': 1, '♣': 2, '♦': 3, '🃏': 4}

    def key(card):
        suit = card[0]
        rank = card[1:]
        return (RANK_VALUES.get(rank, 0), suit_order.get(suit, 0))

    return sorted(cards, key=key)


def get_rank(card):
    """获取牌的点数"""
    return card[1:]


def get_suit(card):
    """获取牌的花色"""
    return card[0]


def is_red(card):
    """判断是否红色牌"""
    s = get_suit(card)
    return s in ('♥', '♦') or get_rank(card) == '大王'


def validate_play(cards):
    """
    验证出牌是否合法
    返回: {'valid': bool, 'type': str, 'rank': str, ...} 或 {'valid': False, 'message': str}
    """
    if not cards:
        return {'valid': False, 'message': '请选择牌'}

    n = len(cards)
    ranks = [get_rank(c) for c in cards]
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

    # 四带二
    if n == 6 and counts[0] == 4:
        r = [k for k, v in rank_count.items() if v == 4][0]
        return {'valid': True, 'type': 'four_two', 'rank': r}

    # 顺子 (>=5张, 不含2和王)
    if n >= 5 and all(v == 1 for v in rank_count.values()):
        is_straight = all(
            RANK_VALUES.get(unique_ranks[i], 0) - RANK_VALUES.get(unique_ranks[i - 1], 0) == 1
            for i in range(1, len(unique_ranks))
        )
        if is_straight and all(RANK_VALUES.get(r, 0) <= 14 for r in unique_ranks):
            return {'valid': True, 'type': 'straight', 'rank': unique_ranks[-1], 'length': n}

    # 连对 (>=3对, 不含2和王)
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


def can_beat(new_cards, last_cards):
    """判断new_cards能否压过last_cards"""
    new_type = validate_play(new_cards)
    last_type = validate_play(last_cards)

    if not new_type['valid'] or not last_type['valid']:
        return False

    # 王炸最大
    if new_type['type'] == 'rocket':
        return True
    if last_type['type'] == 'rocket':
        return False

    # 炸弹 > 非炸弹
    if new_type['type'] == 'bomb' and last_type['type'] != 'bomb':
        return True
    if last_type['type'] == 'bomb' and new_type['type'] != 'bomb':
        return False

    # 同类型比较
    if new_type['type'] != last_type['type']:
        return False

    # 顺子/连对/飞机需要长度相同
    if new_type.get('length') and last_type.get('length'):
        if new_type['length'] != last_type['length']:
            return False

    if len(new_cards) != len(last_cards):
        return False

    return RANK_VALUES.get(new_type['rank'], 0) > RANK_VALUES.get(last_type['rank'], 0)


# ============================================
# AI 逻辑
# ============================================

def ai_find_beat(hand, last_play):
    """
    AI: 找到能压过last_play的最小牌组合
    返回: 出的牌列表, 或None(不出)
    """
    if not last_play:
        return [hand[0]] if hand else None

    last_type = validate_play(last_play)
    if not last_type['valid']:
        return None

    last_value = RANK_VALUES.get(last_type['rank'], 0)
    rank_count = {}
    for c in hand:
        r = get_rank(c)
        rank_count[r] = rank_count.get(r, 0) + 1

    # 单张
    if last_type['type'] == 'single':
        for c in hand:
            if RANK_VALUES.get(get_rank(c), 0) > last_value:
                return [c]

    # 对子
    if last_type['type'] == 'pair':
        for r in sorted(rank_count, key=lambda x: RANK_VALUES.get(x, 0)):
            if rank_count[r] >= 2 and RANK_VALUES.get(r, 0) > last_value:
                return [c for c in hand if get_rank(c) == r][:2]

    # 三条
    if last_type['type'] == 'triple':
        for r in sorted(rank_count, key=lambda x: RANK_VALUES.get(x, 0)):
            if rank_count[r] >= 3 and RANK_VALUES.get(r, 0) > last_value:
                return [c for c in hand if get_rank(c) == r][:3]

    # 三带一
    if last_type['type'] == 'triple_one':
        for r in sorted(rank_count, key=lambda x: RANK_VALUES.get(x, 0)):
            if rank_count[r] >= 3 and RANK_VALUES.get(r, 0) > last_value:
                triple = [c for c in hand if get_rank(c) == r][:3]
                remaining = [c for c in hand if get_rank(c) != r]
                if remaining:
                    return triple + [remaining[0]]

    # 三带二
    if last_type['type'] == 'triple_two':
        for r in sorted(rank_count, key=lambda x: RANK_VALUES.get(x, 0)):
            if rank_count[r] >= 3 and RANK_VALUES.get(r, 0) > last_value:
                triple = [c for c in hand if get_rank(c) == r][:3]
                for r2 in rank_count:
                    if r2 != r and rank_count[r2] >= 2:
                        pair = [c for c in hand if get_rank(c) == r2][:2]
                        return triple + pair

    # 顺子
    if last_type['type'] == 'straight':
        length = last_type['length']
        singles = sorted(set(get_rank(c) for c in hand if RANK_VALUES.get(get_rank(c), 0) <= 14),
                        key=lambda r: RANK_VALUES.get(r, 0))
        for start_idx in range(len(singles)):
            if RANK_VALUES.get(singles[start_idx], 0) > last_value - length + 1:
                seq = singles[start_idx:start_idx + length]
                if len(seq) == length:
                    vals = [RANK_VALUES.get(r, 0) for r in seq]
                    if all(vals[i] - vals[i-1] == 1 for i in range(1, len(vals))):
                        result = []
                        used = set()
                        for r in seq:
                            for c in hand:
                                if get_rank(c) == r and c not in used:
                                    result.append(c)
                                    used.add(c)
                                    break
                        if len(result) == length:
                            return result

    # 连对
    if last_type['type'] == 'consecutive_pairs':
        pair_count = last_type['length']
        pairs = sorted([r for r, v in rank_count.items() if v >= 2 and RANK_VALUES.get(r, 0) <= 14],
                      key=lambda r: RANK_VALUES.get(r, 0))
        for start_idx in range(len(pairs)):
            if RANK_VALUES.get(pairs[start_idx], 0) > last_value - pair_count + 1:
                seq = pairs[start_idx:start_idx + pair_count]
                if len(seq) == pair_count:
                    vals = [RANK_VALUES.get(r, 0) for r in seq]
                    if all(vals[i] - vals[i-1] == 1 for i in range(1, len(vals))):
                        result = []
                        for r in seq:
                            cards_of_rank = [c for c in hand if get_rank(c) == r]
                            result.extend(cards_of_rank[:2])
                        if len(result) == pair_count * 2:
                            return result

    # 飞机（不带翅膀）
    if last_type['type'] == 'plane':
        triple_count = last_type['length']
        triples = sorted([r for r, v in rank_count.items() if v >= 3 and RANK_VALUES.get(r, 0) <= 14],
                        key=lambda r: RANK_VALUES.get(r, 0))
        for start_idx in range(len(triples)):
            if RANK_VALUES.get(triples[start_idx], 0) > last_value - triple_count + 1:
                seq = triples[start_idx:start_idx + triple_count]
                if len(seq) == triple_count:
                    vals = [RANK_VALUES.get(r, 0) for r in seq]
                    if all(vals[i] - vals[i-1] == 1 for i in range(1, len(vals))):
                        result = []
                        for r in seq:
                            cards_of_rank = [c for c in hand if get_rank(c) == r]
                            result.extend(cards_of_rank[:3])
                        if len(result) == triple_count * 3:
                            return result

    # 飞机带单翅膀
    if last_type['type'] == 'plane_single':
        triple_count = last_type['length']
        triples = sorted([r for r, v in rank_count.items() if v >= 3 and RANK_VALUES.get(r, 0) <= 14],
                        key=lambda r: RANK_VALUES.get(r, 0))
        for start_idx in range(len(triples)):
            if RANK_VALUES.get(triples[start_idx], 0) > last_value - triple_count + 1:
                seq = triples[start_idx:start_idx + triple_count]
                if len(seq) == triple_count:
                    vals = [RANK_VALUES.get(r, 0) for r in seq]
                    if all(vals[i] - vals[i-1] == 1 for i in range(1, len(vals))):
                        result = []
                        for r in seq:
                            cards_of_rank = [c for c in hand if get_rank(c) == r]
                            result.extend(cards_of_rank[:3])
                        # 添加单张翅膀
                        remaining = [c for c in hand if c not in result]
                        if len(remaining) >= triple_count:
                            result.extend(remaining[:triple_count])
                            if len(result) == triple_count * 4:
                                return result

    # 飞机带对子翅膀
    if last_type['type'] == 'plane_pair':
        triple_count = last_type['length']
        triples = sorted([r for r, v in rank_count.items() if v >= 3 and RANK_VALUES.get(r, 0) <= 14],
                        key=lambda r: RANK_VALUES.get(r, 0))
        for start_idx in range(len(triples)):
            if RANK_VALUES.get(triples[start_idx], 0) > last_value - triple_count + 1:
                seq = triples[start_idx:start_idx + triple_count]
                if len(seq) == triple_count:
                    vals = [RANK_VALUES.get(r, 0) for r in seq]
                    if all(vals[i] - vals[i-1] == 1 for i in range(1, len(vals))):
                        result = []
                        for r in seq:
                            cards_of_rank = [c for c in hand if get_rank(c) == r]
                            result.extend(cards_of_rank[:3])
                        # 添加对子翅膀
                        remaining_ranks = {}
                        for c in hand:
                            if c not in result:
                                r = get_rank(c)
                                remaining_ranks[r] = remaining_ranks.get(r, 0) + 1
                        pairs_available = [r for r, v in remaining_ranks.items() if v >= 2]
                        if len(pairs_available) >= triple_count:
                            for r in pairs_available[:triple_count]:
                                cards_of_rank = [c for c in hand if get_rank(c) == r and c not in result]
                                result.extend(cards_of_rank[:2])
                            if len(result) == triple_count * 5:
                                return result

    # 四带二（单张）
    if last_type['type'] == 'four_two':
        four_rank = [r for r, v in rank_count.items() if v == 4]
        if four_rank:
            for r in sorted(four_rank, key=lambda x: RANK_VALUES.get(x, 0)):
                if RANK_VALUES.get(r, 0) > last_value:
                    four_cards = [c for c in hand if get_rank(c) == r]
                    remaining = [c for c in hand if c not in four_cards]
                    if len(remaining) >= 2:
                        return four_cards + remaining[:2]

    # 炸弹
    for r in sorted(rank_count, key=lambda x: RANK_VALUES.get(x, 0)):
        if rank_count[r] == 4:
            if last_type['type'] != 'bomb' or RANK_VALUES.get(r, 0) > last_value:
                return [c for c in hand if get_rank(c) == r]

    # 王炸
    has_small = any(get_rank(c) == '小王' for c in hand)
    has_big = any(get_rank(c) == '大王' for c in hand)
    if has_small and has_big and last_type['type'] != 'rocket':
        return [c for c in hand if get_rank(c) in ('小王', '大王')]

    return None


def ai_decide_call(hand):
    """AI决定是否叫地主"""
    score = 0
    for c in hand:
        r = get_rank(c)
        v = RANK_VALUES.get(r, 0)
        if v >= 15:  # 2
            score += 3
        elif v >= 14:  # A
            score += 2
        elif v >= 13:  # K
            score += 1
    # 王加分
    ranks = [get_rank(c) for c in hand]
    if '大王' in ranks:
        score += 4
    if '小王' in ranks:
        score += 3
    # 炸弹加分
    rc = {}
    for r in ranks:
        rc[r] = rc.get(r, 0) + 1
    for v in rc.values():
        if v == 4:
            score += 5
    return score >= 8
