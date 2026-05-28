"""
鬼谷八荒风格 · 文字修仙游戏引擎
纯游戏逻辑，无服务器依赖
"""
import random
import math
import time
from enum import Enum

# ============================================================
# 境界系统
# ============================================================
class Realm(Enum):
    LIANQI = "练气"
    ZHUJI = "筑基"
    JIEDAN = "结丹"
    YUANYING = "元婴"
    HUASHEN = "化神"
    LIANXU = "炼虚"
    HETI = "合体"
    DACHENG = "大乘"
    DUJIE = "渡劫"
    FEISHENG = "飞升"

REALM_ORDER = [Realm.LIANQI, Realm.ZHUJI, Realm.JIEDAN, Realm.YUANYING, Realm.HUASHEN, Realm.LIANXU, Realm.HETI, Realm.DACHENG, Realm.DUJIE, Realm.FEISHENG]

REALM_DATA = {
    Realm.LIANQI: {
        "name": "练气",
        "stages": ["初期", "中期", "后期", "圆满"],
        "max_lifespan": 180,
        "base_cultivation_speed": 1.0,
        "breakthrough_base_rate": 0.85,
        "breakthrough_materials": {"灵石": 50, "聚气丹": 1},
        "description": "感应天地灵气，引气入体",
    },
    Realm.ZHUJI: {
        "name": "筑基",
        "stages": ["初期", "中期", "后期", "圆满"],
        "max_lifespan": 350,
        "base_cultivation_speed": 0.8,
        "breakthrough_base_rate": 0.65,
        "breakthrough_materials": {"灵石": 200, "筑基丹": 2, "灵芝": 1},
        "description": "凝聚真元，筑就道基",
    },
    Realm.JIEDAN: {
        "name": "结丹",
        "stages": ["初期", "中期", "后期", "圆满"],
        "max_lifespan": 600,
        "base_cultivation_speed": 0.6,
        "breakthrough_base_rate": 0.50,
        "breakthrough_materials": {"灵石": 500, "金丹丹": 3, "千年灵芝": 1, "天雷珠": 1},
        "description": "真元凝聚成丹，金丹大道",
    },
    Realm.YUANYING: {
        "name": "元婴",
        "stages": ["初期", "中期", "后期", "圆满"],
        "max_lifespan": 1000,
        "base_cultivation_speed": 0.45,
        "breakthrough_base_rate": 0.35,
        "breakthrough_materials": {"灵石": 2000, "元婴丹": 5, "天材地宝": 3},
        "description": "金丹化婴，元神出窍",
    },
    Realm.HUASHEN: {
        "name": "化神",
        "stages": ["初期", "中期", "后期", "圆满"],
        "max_lifespan": 2500,
        "base_cultivation_speed": 0.35,
        "breakthrough_base_rate": 0.25,
        "breakthrough_materials": {"灵石": 10000, "化神丹": 10, "仙器碎片": 5},
        "description": "元婴化神，掌控天地",
    },
    Realm.LIANXU: {
        "name": "炼虚",
        "stages": ["初期", "中期", "后期", "圆满"],
        "max_lifespan": 5000,
        "base_cultivation_speed": 0.28,
        "breakthrough_base_rate": 0.20,
        "breakthrough_materials": {"灵石": 50000, "炼虚丹": 15, "天道碎片": 3, "仙器碎片": 10},
        "description": "炼化虚空，合道天地",
    },
    Realm.HETI: {
        "name": "合体",
        "stages": ["初期", "中期", "后期", "圆满"],
        "max_lifespan": 10000,
        "base_cultivation_speed": 0.22,
        "breakthrough_base_rate": 0.15,
        "breakthrough_materials": {"灵石": 200000, "合体丹": 20, "天道碎片": 8, "混沌精华": 2},
        "description": "肉身与元神合一，天人合一",
    },
    Realm.DACHENG: {
        "name": "大乘",
        "stages": ["初期", "中期", "后期", "圆满"],
        "max_lifespan": 20000,
        "base_cultivation_speed": 0.18,
        "breakthrough_base_rate": 0.12,
        "breakthrough_materials": {"灵石": 500000, "大乘丹": 30, "天道碎片": 15, "混沌精华": 5, "造化玉碟": 1},
        "description": "大道圆满，功德无量",
    },
    Realm.DUJIE: {
        "name": "渡劫",
        "stages": ["一重天劫", "二重天劫", "三重天劫", "九重天劫"],
        "max_lifespan": 50000,
        "base_cultivation_speed": 0.15,
        "breakthrough_base_rate": 0.10,
        "breakthrough_materials": {"灵石": 1000000, "渡劫丹": 50, "天道碎片": 30, "混沌精华": 10, "造化玉碟": 3},
        "description": "承受天劫洗礼，超脱凡尘",
    },
    Realm.FEISHENG: {
        "name": "飞升",
        "stages": ["仙人", "真仙", "金仙", "大罗金仙"],
        "max_lifespan": -1,
        "base_cultivation_speed": 0.12,
        "breakthrough_base_rate": 0.08,
        "breakthrough_materials": {},
        "description": "飞升仙界，长生不老",
    },
}

def get_realm_full_name(realm: Realm, stage_index: int) -> str:
    data = REALM_DATA[realm]
    return f"{data['name']}{data['stages'][stage_index]}"

# ============================================================
# 五行系统
# ============================================================
class Element(Enum):
    METAL = "金"
    WOOD = "木"
    WATER = "水"
    FIRE = "火"
    EARTH = "土"

ELEMENT_ADVANTAGE = {
    Element.METAL: Element.WOOD,
    Element.WOOD: Element.EARTH,
    Element.EARTH: Element.WATER,
    Element.WATER: Element.FIRE,
    Element.FIRE: Element.METAL,
}

def get_element_multiplier(attacker: Element, defender: Element) -> float:
    if ELEMENT_ADVANTAGE.get(attacker) == defender:
        return 1.5
    if ELEMENT_ADVANTAGE.get(defender) == attacker:
        return 0.7
    return 1.0

# 相生关系 (Generating cycle): 金生水, 水生木, 木生火, 火生土, 土生金
ELEMENT_GENERATING = {
    Element.METAL: Element.WATER,
    Element.WATER: Element.WOOD,
    Element.WOOD: Element.FIRE,
    Element.FIRE: Element.EARTH,
    Element.EARTH: Element.METAL,
}

# 相克关系 (Overcoming cycle): 金克木, 木克土, 土克水, 水克火, 火克金
ELEMENT_OVERCOMING = {
    Element.METAL: Element.WOOD,
    Element.WOOD: Element.EARTH,
    Element.EARTH: Element.WATER,
    Element.WATER: Element.FIRE,
    Element.FIRE: Element.METAL,
}

# 灵根被动加成 (%)
ELEMENT_PASSIVE = {
    Element.METAL: {"atk_pct": 5},
    Element.WOOD:  {"hp_pct": 5},
    Element.WATER: {"mp_pct": 5},
    Element.FIRE:  {"hp_pct": 2.5, "atk_pct": 2.5},
    Element.EARTH: {"def_pct": 5},
}

def compute_element_bonuses(elements: list) -> dict:
    """计算灵根被动加成，相生翻倍，相克减半；五灵根全属性+15%"""
    total = {"hp_pct": 0, "mp_pct": 0, "atk_pct": 0, "def_pct": 0}
    # 五灵根：五行齐聚，跳过相克惩罚，全属性+15%
    if len(elements) >= 5:
        return {"hp_pct": 15, "mp_pct": 15, "atk_pct": 15, "def_pct": 15}
    elem_enums = [Element(e) for e in elements]
    for elem in elem_enums:
        base = {"hp_pct": 0, "mp_pct": 0, "atk_pct": 0, "def_pct": 0}
        base.update(ELEMENT_PASSIVE[elem])
        for other in elem_enums:
            if other == elem:
                continue
            if ELEMENT_GENERATING.get(elem) == other:
                for k in base:
                    base[k] *= 2
                break
            if ELEMENT_OVERCOMING.get(elem) == other:
                for k in base:
                    base[k] *= 0.5
                break
        for k in total:
            total[k] += base[k]
    return total

def character_elements(character: dict) -> list:
    """安全获取灵根列表"""
    elems = character.get("element", [])
    if isinstance(elems, str):
        return [elems]
    return elems

def has_element(character: dict, element_str: str) -> bool:
    """检查角色是否拥有某灵根"""
    return element_str in character_elements(character)

def _best_element_multiplier(attacker_elements, defender_element: str) -> float:
    """多灵根攻击者取最优五行克制倍率"""
    if isinstance(attacker_elements, str):
        attacker_elements = [attacker_elements]
    best = 1.0
    for elem_str in attacker_elements:
        mult = get_element_multiplier(Element(elem_str), Element(defender_element))
        best = max(best, mult)
    return best

# ============================================================
# 迁移旧存档
# ============================================================
def migrate_character(character: dict) -> dict:
    """将旧版单灵根角色迁移为多灵根格式"""
    elems = character.get("element", "金")
    if isinstance(elems, str):
        character["element"] = [elems]
    if "sword_uses" not in character:
        character["sword_uses"] = 0
    if "sword_tier" not in character:
        character["sword_tier"] = 1
    # 迁移旧技能列表：落石术替换为对应灵根技能
    if "skills" in character:
        new_skills = []
        for s in character["skills"]:
            if s == "落石术":
                elem = character["element"][0] if character["element"] else "土"
                elem_skill_map = {"金": "金刃术", "木": "木刺术", "水": "水弹术", "火": "火球术", "土": "落石术"}
                new_skills.append(elem_skill_map.get(elem, "落石术"))
            else:
                new_skills.append(s)
        character["skills"] = new_skills
    return character

# ============================================================
# 骰子系统
# ============================================================
def _roll_stats() -> dict:
    """随机生成4项基础属性，总和≤35，每项≥1"""
    for _ in range(1000):  # 防止无限循环
        stats = {
            "根骨": random.randint(1, 12),
            "悟性": random.randint(1, 12),
            "气运": random.randint(1, 12),
            "魅力": random.randint(1, 12),
        }
        if sum(stats.values()) <= 35:
            return stats
    # fallback: 强制限制
    return {"根骨": 8, "悟性": 8, "气运": 8, "魅力": 8}

def _roll_elements() -> list:
    """随机生成灵根：1根40%/2根30%/3根20%/4根8%/5根2%"""
    roll = random.random()
    if roll < 0.40:
        count = 1
    elif roll < 0.70:
        count = 2
    elif roll < 0.90:
        count = 3
    elif roll < 0.98:
        count = 4
    else:
        count = 5
    all_elements = ["金", "木", "水", "火", "土"]
    return random.sample(all_elements, count)

def roll_dice() -> dict:
    """掷骰子：返回随机属性和灵根"""
    stats = _roll_stats()
    elements = _roll_elements()
    return {"stats": stats, "elements": elements}

# ============================================================
# 物品系统
# ============================================================
ITEM_DB = {
    # 丹药
    "聚气丹": {"type": "consumable", "effect": "cultivation", "value": 50, "desc": "增加50修为", "rarity": "凡品", "price": 30},
    "回春丹": {"type": "consumable", "effect": "heal", "value": 100, "desc": "恢复100生命", "rarity": "凡品", "price": 20},
    "筑基丹": {"type": "consumable", "effect": "breakthrough", "value": 10, "desc": "突破成功率+10%", "rarity": "灵品", "price": 200},
    "金丹丹": {"type": "consumable", "effect": "breakthrough", "value": 15, "desc": "突破成功率+15%", "rarity": "灵品", "price": 500},
    "元婴丹": {"type": "consumable", "effect": "breakthrough", "value": 20, "desc": "突破成功率+20%", "rarity": "仙品", "price": 1500},
    "化神丹": {"type": "consumable", "effect": "breakthrough", "value": 25, "desc": "突破成功率+25%", "rarity": "仙品", "price": 5000},
    # 材料
    "灵石": {"type": "material", "effect": "currency", "value": 1, "desc": "通用货币", "rarity": "凡品", "price": 1},
    "灵芝": {"type": "material", "effect": "material", "value": 0, "desc": "炼丹材料", "rarity": "凡品", "price": 15},
    "千年灵芝": {"type": "material", "effect": "material", "value": 0, "desc": "珍稀炼丹材料", "rarity": "灵品", "price": 80},
    "天雷珠": {"type": "material", "effect": "material", "value": 0, "desc": "蕴含天雷之力", "rarity": "灵品", "price": 120},
    "天材地宝": {"type": "material", "effect": "material", "value": 0, "desc": "天地灵气凝聚", "rarity": "仙品", "price": 500},
    "仙器碎片": {"type": "material", "effect": "material", "value": 0, "desc": "上古仙器残片", "rarity": "仙品", "price": 800},
    "铁矿石": {"type": "material", "effect": "material", "value": 0, "desc": "普通矿石，可锻造法器", "rarity": "凡品", "price": 10},
    "玄铁矿": {"type": "material", "effect": "material", "value": 0, "desc": "蕴含灵气的矿石", "rarity": "灵品", "price": 60},
    "冰晶": {"type": "material", "effect": "material", "value": 0, "desc": "极寒之地凝结的冰之精华", "rarity": "灵品", "price": 90},
    "魂晶": {"type": "material", "effect": "material", "value": 0, "desc": "亡灵消散后留下的灵魂结晶", "rarity": "灵品", "price": 100},
    "天机碎片": {"type": "material", "effect": "material", "value": 0, "desc": "天机阁流出的神秘碎片", "rarity": "仙品", "price": 200},
    "解毒丹": {"type": "consumable", "effect": "heal", "value": 60, "desc": "解毒并恢复60生命", "rarity": "凡品", "price": 25},
    # 法器
    "铁剑": {"type": "weapon", "effect": "attack", "value": 10, "desc": "攻击+10", "rarity": "凡品", "price": 50},
    "青锋剑": {"type": "weapon", "effect": "attack", "value": 25, "desc": "攻击+25", "rarity": "灵品", "price": 300},
    "玄铁剑": {"type": "weapon", "effect": "attack", "value": 50, "desc": "攻击+50", "rarity": "仙品", "price": 1200},
    "布甲": {"type": "armor", "effect": "defense", "value": 8, "desc": "防御+8", "rarity": "凡品", "price": 40},
    "灵纹甲": {"type": "armor", "effect": "defense", "value": 20, "desc": "防御+20", "rarity": "灵品", "price": 250},
    "玄武甲": {"type": "armor", "effect": "defense", "value": 45, "desc": "防御+45", "rarity": "仙品", "price": 1000},
    # 新增法器
    "寒冰弓": {"type": "weapon", "effect": "attack", "value": 35, "desc": "攻击+35，寒气逼人", "rarity": "灵品", "price": 500},
    "烈焰刀": {"type": "weapon", "effect": "attack", "value": 40, "desc": "攻击+40，烈焰缠绕", "rarity": "灵品", "price": 650},
    "雷神锤": {"type": "weapon", "effect": "attack", "value": 60, "desc": "攻击+60，雷霆万钧", "rarity": "仙品", "price": 1500},
    "碧玉甲": {"type": "armor", "effect": "defense", "value": 15, "desc": "防御+15，温润如玉", "rarity": "灵品", "price": 180},
    "金丝软甲": {"type": "armor", "effect": "defense", "value": 30, "desc": "防御+30，轻盈坚韧", "rarity": "灵品", "price": 450},
    "天蚕宝衣": {"type": "armor", "effect": "defense", "value": 55, "desc": "防御+55，刀枪不入", "rarity": "仙品", "price": 1800},
    # 新增丹药
    "培元丹": {"type": "consumable", "effect": "cultivation", "value": 120, "desc": "增加120修为", "rarity": "灵品", "price": 80},
    "续命丹": {"type": "consumable", "effect": "lifespan", "value": 30, "desc": "增加30年寿元", "rarity": "灵品", "price": 300},
    "破境丹": {"type": "consumable", "effect": "breakthrough", "value": 30, "desc": "突破成功率+30%", "rarity": "仙品", "price": 3000},
    # ── 高阶丹药 ──
    "炼虚丹": {"type": "consumable", "effect": "breakthrough", "value": 35, "desc": "突破成功率+35%", "rarity": "仙品", "price": 15000},
    "合体丹": {"type": "consumable", "effect": "breakthrough", "value": 40, "desc": "突破成功率+40%", "rarity": "仙品", "price": 50000},
    "大乘丹": {"type": "consumable", "effect": "breakthrough", "value": 45, "desc": "突破成功率+45%", "rarity": "神品", "price": 150000},
    "渡劫丹": {"type": "consumable", "effect": "breakthrough", "value": 50, "desc": "突破成功率+50%", "rarity": "神品", "price": 500000},
    "回元丹": {"type": "consumable", "effect": "heal", "value": 500, "desc": "恢复500生命", "rarity": "仙品", "price": 2000},
    "九转还魂丹": {"type": "consumable", "effect": "heal", "value": 1500, "desc": "恢复1500生命", "rarity": "神品", "price": 20000},
    "天元丹": {"type": "consumable", "effect": "cultivation", "value": 500, "desc": "增加500修为", "rarity": "仙品", "price": 1500},
    "造化丹": {"type": "consumable", "effect": "cultivation", "value": 2000, "desc": "增加2000修为", "rarity": "神品", "price": 30000},
    "续命仙丹": {"type": "consumable", "effect": "lifespan", "value": 200, "desc": "增加200年寿元", "rarity": "仙品", "price": 10000},
    "万寿丹": {"type": "consumable", "effect": "lifespan", "value": 1000, "desc": "增加1000年寿元", "rarity": "神品", "price": 100000},
    # ── 高阶材料 ──
    "天道碎片": {"type": "material", "effect": "material", "value": 0, "desc": "天道之力凝聚的碎片", "rarity": "神品", "price": 5000},
    "混沌精华": {"type": "material", "effect": "material", "value": 0, "desc": "混沌初开时的精华", "rarity": "神品", "price": 20000},
    "造化玉碟": {"type": "material", "effect": "material", "value": 0, "desc": "蕴含造化之力的玉碟", "rarity": "神品", "price": 100000},
    "龙珠": {"type": "material", "effect": "material", "value": 0, "desc": "真龙体内凝结的龙珠", "rarity": "仙品", "price": 3000},
    "妖丹": {"type": "material", "effect": "material", "value": 0, "desc": "妖兽修炼凝聚的内丹", "rarity": "灵品", "price": 500},
    "鲛人泪": {"type": "material", "effect": "material", "value": 0, "desc": "鲛人泣泪成珠", "rarity": "仙品", "price": 2000},
    "蟠桃": {"type": "consumable", "effect": "cultivation", "value": 5000, "desc": "增加5000修为", "rarity": "神品", "price": 50000},
    "凤凰羽": {"type": "material", "effect": "material", "value": 0, "desc": "凤凰涅槃时落下的羽毛", "rarity": "仙品", "price": 8000},
    "玄冰精髓": {"type": "material", "effect": "material", "value": 0, "desc": "万年玄冰凝结的精华", "rarity": "仙品", "price": 3000},
    # ── 探索事件补充物品 ──
    "人参果": {"type": "consumable", "effect": "cultivation", "value": 300, "desc": "增加300修为，草还丹之效", "rarity": "仙品", "price": 2000},
    "火枣": {"type": "consumable", "effect": "cultivation", "value": 200, "desc": "增加200修为，火属性灵果", "rarity": "灵品", "price": 800},
    "仙杏": {"type": "consumable", "effect": "cultivation", "value": 250, "desc": "增加250修为，仙家果实", "rarity": "灵品", "price": 1200},
    "何首乌": {"type": "consumable", "effect": "lifespan", "value": 20, "desc": "增加20年寿元", "rarity": "灵品", "price": 300},
    "雪莲": {"type": "consumable", "effect": "heal", "value": 200, "desc": "恢复200生命，圣洁之花", "rarity": "灵品", "price": 250},
    "龙涎草": {"type": "material", "effect": "material", "value": 0, "desc": "龙族栖息地生长的灵草", "rarity": "仙品", "price": 600},
    "聚灵珠": {"type": "consumable", "effect": "cultivation", "value": 500, "desc": "增加500修为，汇聚天地灵气", "rarity": "仙品", "price": 3000},
    "仙鹤羽毛": {"type": "material", "effect": "material", "value": 0, "desc": "仙鹤脱落的灵羽，可用于炼器", "rarity": "仙品", "price": 1500},
    "凤凰涅槃丹": {"type": "consumable", "effect": "cultivation", "value": 2000, "desc": "增加2000修为，凤凰涅槃精华", "rarity": "神品", "price": 50000},
    "烈焰之心": {"type": "material", "effect": "material", "value": 0, "desc": "地火核心凝聚的火之精华", "rarity": "仙品", "price": 3000},
    # ── 高阶法器 ──
    "天罡剑": {"type": "weapon", "effect": "attack", "value": 100, "desc": "攻击+100，天罡正气", "rarity": "仙品", "price": 5000},
    "诛仙剑": {"type": "weapon", "effect": "attack", "value": 180, "desc": "攻击+180，诛仙灭神", "rarity": "神品", "price": 50000},
    "混沌钟": {"type": "weapon", "effect": "attack", "value": 250, "desc": "攻击+250，混沌至宝", "rarity": "神品", "price": 200000},
    "玄天甲": {"type": "armor", "effect": "defense", "value": 100, "desc": "防御+100，玄天护体", "rarity": "仙品", "price": 5000},
    "混沌铠": {"type": "armor", "effect": "defense", "value": 180, "desc": "防御+180，混沌护体", "rarity": "神品", "price": 50000},
    "天道甲": {"type": "armor", "effect": "defense", "value": 300, "desc": "防御+300，天道护体", "rarity": "神品", "price": 200000},
    "龙吟枪": {"type": "weapon", "effect": "attack", "value": 150, "desc": "攻击+150，龙吟九天", "rarity": "仙品", "price": 30000},
    "凤舞鞭": {"type": "weapon", "effect": "attack", "value": 130, "desc": "攻击+130，凤舞九天", "rarity": "仙品", "price": 25000},
    "天机扇": {"type": "weapon", "effect": "attack", "value": 120, "desc": "攻击+120，天机妙算", "rarity": "仙品", "price": 20000},
    "碧落甲": {"type": "armor", "effect": "defense", "value": 80, "desc": "防御+80，碧落黄泉", "rarity": "仙品", "price": 4000},
    "天蚕仙衣": {"type": "armor", "effect": "defense", "value": 120, "desc": "防御+120，天蚕仙丝", "rarity": "仙品", "price": 15000},
    # ── 饰品 ──
    "灵犀玉佩": {"type": "accessory", "effect": "mp_pct", "value": 10, "desc": "灵力+10%", "rarity": "灵品", "price": 800},
    "龙纹手镯": {"type": "accessory", "effect": "atk_pct", "value": 8, "desc": "攻击+8%", "rarity": "灵品", "price": 1000},
    "凤羽项链": {"type": "accessory", "effect": "hp_pct", "value": 10, "desc": "生命+10%", "rarity": "灵品", "price": 1000},
    "玄武戒指": {"type": "accessory", "effect": "def_pct", "value": 10, "desc": "防御+10%", "rarity": "灵品", "price": 1000},
    "天道之眼": {"type": "accessory", "effect": "crit_pct", "value": 15, "desc": "暴击率+15%", "rarity": "仙品", "price": 10000},
    "混沌之心": {"type": "accessory", "effect": "all_pct", "value": 10, "desc": "全属性+10%", "rarity": "神品", "price": 100000},
    "造化之链": {"type": "accessory", "effect": "exp_pct", "value": 20, "desc": "经验+20%", "rarity": "仙品", "price": 15000},
    "轮回之戒": {"type": "accessory", "effect": "lifespan_pct", "value": 25, "desc": "寿元+25%", "rarity": "神品", "price": 50000},
    # ── 套装 ──
    "天罡战靴": {"type": "armor", "effect": "defense", "value": 60, "desc": "防御+60，天罡套装之一", "rarity": "仙品", "price": 3000, "set": "天罡"},
    "天罡护腕": {"type": "accessory", "effect": "atk_pct", "value": 12, "desc": "攻击+12%，天罡套装之一", "rarity": "仙品", "price": 3000, "set": "天罡"},
    "天罡头盔": {"type": "armor", "effect": "defense", "value": 50, "desc": "防御+50，天罡套装之一", "rarity": "仙品", "price": 3000, "set": "天罡"},
    "混沌战靴": {"type": "armor", "effect": "defense", "value": 120, "desc": "防御+120，混沌套装之一", "rarity": "神品", "price": 30000, "set": "混沌"},
    "混沌护腕": {"type": "accessory", "effect": "atk_pct", "value": 20, "desc": "攻击+20%，混沌套装之一", "rarity": "神品", "price": 30000, "set": "混沌"},
    "混沌头盔": {"type": "armor", "effect": "defense", "value": 100, "desc": "防御+100，混沌套装之一", "rarity": "神品", "price": 30000, "set": "混沌"},
}

# ============================================================
# 炼丹/合成系统
# ============================================================
CRAFTING_DB = {
    # 丹药合成
    "聚气丹": {"materials": {"灵石": 30, "灵芝": 2}, "result": "聚气丹", "result_count": 1, "desc": "灵芝×2 + 灵石×30"},
    "回春丹": {"materials": {"灵石": 20, "灵芝": 1}, "result": "回春丹", "result_count": 1, "desc": "灵芝×1 + 灵石×20"},
    "筑基丹": {"materials": {"灵石": 150, "千年灵芝": 1, "聚气丹": 2}, "result": "筑基丹", "result_count": 1, "desc": "千年灵芝×1 + 聚气丹×2 + 灵石×150"},
    "金丹丹": {"materials": {"灵石": 400, "千年灵芝": 2, "天雷珠": 1}, "result": "金丹丹", "result_count": 1, "desc": "千年灵芝×2 + 天雷珠×1 + 灵石×400"},
    "元婴丹": {"materials": {"灵石": 1200, "天材地宝": 2, "魂晶": 1}, "result": "元婴丹", "result_count": 1, "desc": "天材地宝×2 + 魂晶×1 + 灵石×1200"},
    "化神丹": {"materials": {"灵石": 4000, "天材地宝": 3, "仙器碎片": 2, "天机碎片": 1}, "result": "化神丹", "result_count": 1, "desc": "天材地宝×3 + 仙器碎片×2 + 天机碎片×1 + 灵石×4000"},
    "解毒丹": {"materials": {"灵石": 25, "灵芝": 1}, "result": "解毒丹", "result_count": 1, "desc": "灵芝×1 + 灵石×25"},
    # 法器锻造
    "青锋剑": {"materials": {"灵石": 200, "玄铁矿": 2, "铁矿石": 3}, "result": "青锋剑", "result_count": 1, "desc": "玄铁矿×2 + 铁矿石×3 + 灵石×200", "type": "weapon"},
    "玄铁剑": {"materials": {"灵石": 800, "玄铁矿": 4, "天雷珠": 2}, "result": "玄铁剑", "result_count": 1, "desc": "玄铁矿×4 + 天雷珠×2 + 灵石×800", "type": "weapon"},
    "灵纹甲": {"materials": {"灵石": 180, "玄铁矿": 1, "冰晶": 1}, "result": "灵纹甲", "result_count": 1, "desc": "玄铁矿×1 + 冰晶×1 + 灵石×180", "type": "armor"},
    "玄武甲": {"materials": {"灵石": 700, "玄铁矿": 3, "天材地宝": 1}, "result": "玄武甲", "result_count": 1, "desc": "玄铁矿×3 + 天材地宝×1 + 灵石×700", "type": "armor"},
    # 新增配方
    "寒冰弓": {"materials": {"灵石": 350, "冰晶": 3, "玄铁矿": 2}, "result": "寒冰弓", "result_count": 1, "desc": "冰晶×3 + 玄铁矿×2 + 灵石×350", "type": "weapon"},
    "烈焰刀": {"materials": {"灵石": 450, "天雷珠": 2, "玄铁矿": 3}, "result": "烈焰刀", "result_count": 1, "desc": "天雷珠×2 + 玄铁矿×3 + 灵石×450", "type": "weapon"},
    "雷神锤": {"materials": {"灵石": 1000, "天雷珠": 4, "仙器碎片": 1}, "result": "雷神锤", "result_count": 1, "desc": "天雷珠×4 + 仙器碎片×1 + 灵石×1000", "type": "weapon"},
    "碧玉甲": {"materials": {"灵石": 120, "冰晶": 1, "铁矿石": 2}, "result": "碧玉甲", "result_count": 1, "desc": "冰晶×1 + 铁矿石×2 + 灵石×120", "type": "armor"},
    "金丝软甲": {"materials": {"灵石": 300, "玄铁矿": 2, "魂晶": 1}, "result": "金丝软甲", "result_count": 1, "desc": "玄铁矿×2 + 魂晶×1 + 灵石×300", "type": "armor"},
    "天蚕宝衣": {"materials": {"灵石": 1200, "天材地宝": 2, "仙器碎片": 1, "冰晶": 3}, "result": "天蚕宝衣", "result_count": 1, "desc": "天材地宝×2 + 仙器碎片×1 + 冰晶×3 + 灵石×1200", "type": "armor"},
    "培元丹": {"materials": {"灵石": 60, "千年灵芝": 1}, "result": "培元丹", "result_count": 1, "desc": "千年灵芝×1 + 灵石×60"},
    "续命丹": {"materials": {"灵石": 200, "千年灵芝": 2, "魂晶": 1}, "result": "续命丹", "result_count": 1, "desc": "千年灵芝×2 + 魂晶×1 + 灵石×200"},
    "破境丹": {"materials": {"灵石": 2000, "天材地宝": 2, "天机碎片": 2, "千年灵芝": 3}, "result": "破境丹", "result_count": 1, "desc": "天材地宝×2 + 天机碎片×2 + 千年灵芝×3 + 灵石×2000"},
    # ── 高阶丹药配方 ──
    "炼虚丹": {"materials": {"灵石": 12000, "天材地宝": 5, "天道碎片": 1}, "result": "炼虚丹", "result_count": 1, "desc": "天材地宝×5 + 天道碎片×1 + 灵石×12000"},
    "合体丹": {"materials": {"灵石": 40000, "天材地宝": 8, "天道碎片": 3, "混沌精华": 1}, "result": "合体丹", "result_count": 1, "desc": "天材地宝×8 + 天道碎片×3 + 混沌精华×1 + 灵石×40000"},
    "大乘丹": {"materials": {"灵石": 120000, "天材地宝": 12, "天道碎片": 5, "混沌精华": 2}, "result": "大乘丹", "result_count": 1, "desc": "天材地宝×12 + 天道碎片×5 + 混沌精华×2 + 灵石×120000"},
    "渡劫丹": {"materials": {"灵石": 400000, "天材地宝": 20, "天道碎片": 10, "混沌精华": 5, "造化玉碟": 1}, "result": "渡劫丹", "result_count": 1, "desc": "天材地宝×20 + 天道碎片×10 + 混沌精华×5 + 造化玉碟×1 + 灵石×400000"},
    "回元丹": {"materials": {"灵石": 1500, "千年灵芝": 3, "天材地宝": 1}, "result": "回元丹", "result_count": 1, "desc": "千年灵芝×3 + 天材地宝×1 + 灵石×1500"},
    "九转还魂丹": {"materials": {"灵石": 15000, "千年灵芝": 5, "天材地宝": 3, "魂晶": 5}, "result": "九转还魂丹", "result_count": 1, "desc": "千年灵芝×5 + 天材地宝×3 + 魂晶×5 + 灵石×15000"},
    "天元丹": {"materials": {"灵石": 1000, "千年灵芝": 2, "天材地宝": 1}, "result": "天元丹", "result_count": 1, "desc": "千年灵芝×2 + 天材地宝×1 + 灵石×1000"},
    "造化丹": {"materials": {"灵石": 25000, "千年灵芝": 5, "天材地宝": 3, "天道碎片": 1}, "result": "造化丹", "result_count": 1, "desc": "千年灵芝×5 + 天材地宝×3 + 天道碎片×1 + 灵石×25000"},
    "续命仙丹": {"materials": {"灵石": 8000, "千年灵芝": 3, "魂晶": 3, "天材地宝": 1}, "result": "续命仙丹", "result_count": 1, "desc": "千年灵芝×3 + 魂晶×3 + 天材地宝×1 + 灵石×8000"},
    "万寿丹": {"materials": {"灵石": 80000, "千年灵芝": 5, "天道碎片": 3, "混沌精华": 1}, "result": "万寿丹", "result_count": 1, "desc": "千年灵芝×5 + 天道碎片×3 + 混沌精华×1 + 灵石×80000"},
    # ── 高阶法器锻造 ──
    "天罡剑": {"materials": {"灵石": 4000, "玄铁矿": 5, "天雷珠": 3, "仙器碎片": 2}, "result": "天罡剑", "result_count": 1, "desc": "玄铁矿×5 + 天雷珠×3 + 仙器碎片×2 + 灵石×4000", "type": "weapon"},
    "诛仙剑": {"materials": {"灵石": 40000, "仙器碎片": 5, "天道碎片": 3, "凤凰羽": 1}, "result": "诛仙剑", "result_count": 1, "desc": "仙器碎片×5 + 天道碎片×3 + 凤凰羽×1 + 灵石×40000", "type": "weapon"},
    "混沌钟": {"materials": {"灵石": 150000, "天道碎片": 10, "混沌精华": 5, "造化玉碟": 2}, "result": "混沌钟", "result_count": 1, "desc": "天道碎片×10 + 混沌精华×5 + 造化玉碟×2 + 灵石×150000", "type": "weapon"},
    "玄天甲": {"materials": {"灵石": 4000, "玄铁矿": 5, "天材地宝": 2, "仙器碎片": 1}, "result": "玄天甲", "result_count": 1, "desc": "玄铁矿×5 + 天材地宝×2 + 仙器碎片×1 + 灵石×4000", "type": "armor"},
    "混沌铠": {"materials": {"灵石": 40000, "仙器碎片": 5, "天道碎片": 3, "混沌精华": 2}, "result": "混沌铠", "result_count": 1, "desc": "仙器碎片×5 + 天道碎片×3 + 混沌精华×2 + 灵石×40000", "type": "armor"},
    "天道甲": {"materials": {"灵石": 150000, "天道碎片": 10, "混沌精华": 5, "造化玉碟": 3}, "result": "天道甲", "result_count": 1, "desc": "天道碎片×10 + 混沌精华×5 + 造化玉碟×3 + 灵石×150000", "type": "armor"},
    "龙吟枪": {"materials": {"灵石": 25000, "龙珠": 1, "玄铁矿": 5, "仙器碎片": 2}, "result": "龙吟枪", "result_count": 1, "desc": "龙珠×1 + 玄铁矿×5 + 仙器碎片×2 + 灵石×25000", "type": "weapon"},
    "凤舞鞭": {"materials": {"灵石": 20000, "凤凰羽": 1, "玄铁矿": 4, "仙器碎片": 2}, "result": "凤舞鞭", "result_count": 1, "desc": "凤凰羽×1 + 玄铁矿×4 + 仙器碎片×2 + 灵石×20000", "type": "weapon"},
    "天机扇": {"materials": {"灵石": 15000, "天机碎片": 5, "玄铁矿": 3, "仙器碎片": 1}, "result": "天机扇", "result_count": 1, "desc": "天机碎片×5 + 玄铁矿×3 + 仙器碎片×1 + 灵石×15000", "type": "weapon"},
    # ── 饰品锻造 ──
    "灵犀玉佩": {"materials": {"灵石": 600, "冰晶": 2, "千年灵芝": 1}, "result": "灵犀玉佩", "result_count": 1, "desc": "冰晶×2 + 千年灵芝×1 + 灵石×600", "type": "accessory"},
    "龙纹手镯": {"materials": {"灵石": 800, "玄铁矿": 2, "龙珠": 1}, "result": "龙纹手镯", "result_count": 1, "desc": "玄铁矿×2 + 龙珠×1 + 灵石×800", "type": "accessory"},
    "凤羽项链": {"materials": {"灵石": 800, "凤凰羽": 1, "千年灵芝": 1}, "result": "凤羽项链", "result_count": 1, "desc": "凤凰羽×1 + 千年灵芝×1 + 灵石×800", "type": "accessory"},
    "玄武戒指": {"materials": {"灵石": 800, "玄铁矿": 2, "冰晶": 2}, "result": "玄武戒指", "result_count": 1, "desc": "玄铁矿×2 + 冰晶×2 + 灵石×800", "type": "accessory"},
    "天道之眼": {"materials": {"灵石": 8000, "天道碎片": 2, "仙器碎片": 2}, "result": "天道之眼", "result_count": 1, "desc": "天道碎片×2 + 仙器碎片×2 + 灵石×8000", "type": "accessory"},
    "混沌之心": {"materials": {"灵石": 80000, "混沌精华": 3, "天道碎片": 5, "造化玉碟": 1}, "result": "混沌之心", "result_count": 1, "desc": "混沌精华×3 + 天道碎片×5 + 造化玉碟×1 + 灵石×80000", "type": "accessory"},
    "造化之链": {"materials": {"灵石": 12000, "天材地宝": 3, "天道碎片": 2}, "result": "造化之链", "result_count": 1, "desc": "天材地宝×3 + 天道碎片×2 + 灵石×12000", "type": "accessory"},
    "轮回之戒": {"materials": {"灵石": 40000, "天道碎片": 5, "混沌精华": 2, "魂晶": 5}, "result": "轮回之戒", "result_count": 1, "desc": "天道碎片×5 + 混沌精华×2 + 魂晶×5 + 灵石×40000", "type": "accessory"},
    # ── 套装锻造 ──
    "天罡战靴": {"materials": {"灵石": 2500, "玄铁矿": 3, "天雷珠": 2}, "result": "天罡战靴", "result_count": 1, "desc": "玄铁矿×3 + 天雷珠×2 + 灵石×2500", "type": "armor"},
    "天罡护腕": {"materials": {"灵石": 2500, "玄铁矿": 3, "天雷珠": 2}, "result": "天罡护腕", "result_count": 1, "desc": "玄铁矿×3 + 天雷珠×2 + 灵石×2500", "type": "accessory"},
    "天罡头盔": {"materials": {"灵石": 2500, "玄铁矿": 3, "天雷珠": 2}, "result": "天罡头盔", "result_count": 1, "desc": "玄铁矿×3 + 天雷珠×2 + 灵石×2500", "type": "armor"},
    "混沌战靴": {"materials": {"灵石": 25000, "仙器碎片": 3, "天道碎片": 2, "混沌精华": 1}, "result": "混沌战靴", "result_count": 1, "desc": "仙器碎片×3 + 天道碎片×2 + 混沌精华×1 + 灵石×25000", "type": "armor"},
    "混沌护腕": {"materials": {"灵石": 25000, "仙器碎片": 3, "天道碎片": 2, "混沌精华": 1}, "result": "混沌护腕", "result_count": 1, "desc": "仙器碎片×3 + 天道碎片×2 + 混沌精华×1 + 灵石×25000", "type": "accessory"},
    "混沌头盔": {"materials": {"灵石": 25000, "仙器碎片": 3, "天道碎片": 2, "混沌精华": 1}, "result": "混沌头盔", "result_count": 1, "desc": "仙器碎片×3 + 天道碎片×2 + 混沌精华×1 + 灵石×25000", "type": "armor"},
}


def craft_item(character: dict, recipe_name: str) -> dict:
    """合成物品"""
    if recipe_name not in CRAFTING_DB:
        return {"success": False, "message": "未知配方"}

    recipe = CRAFTING_DB[recipe_name]

    # 检查材料
    for mat, count in recipe["materials"].items():
        if mat == "灵石":
            if character["inventory"].get("灵石", 0) < count:
                return {"success": False, "message": f"灵石不足，需要{count}个"}
        else:
            if character["inventory"].get(mat, 0) < count:
                return {"success": False, "message": f"{mat}不足，需要{count}个"}

    # 消耗材料
    for mat, count in recipe["materials"].items():
        if mat == "灵石":
            character["inventory"]["灵石"] -= count
        else:
            character["inventory"][mat] -= count
            if character["inventory"][mat] <= 0:
                del character["inventory"][mat]

    # 获得产物
    result_item = recipe["result"]
    result_count = recipe.get("result_count", 1)
    character["inventory"][result_item] = character["inventory"].get(result_item, 0) + result_count

    # 统计合成次数
    character.setdefault("stats", {})["craft_count"] = character.get("stats", {}).get("craft_count", 0) + 1
    # 统计法器合成次数
    if recipe.get("type") in ("weapon", "armor"):
        character["stats"]["craft_weapon_count"] = character["stats"].get("craft_weapon_count", 0) + 1

    return {"success": True, "message": f"成功炼制 {result_item}×{result_count}！", "item": result_item, "count": result_count}


def get_crafting_recipes(character: dict) -> list:
    """获取所有配方及其可用性"""
    recipes = []
    for name, recipe in CRAFTING_DB.items():
        can_craft = True
        for mat, count in recipe["materials"].items():
            if mat == "灵石":
                if character["inventory"].get("灵石", 0) < count:
                    can_craft = False
                    break
            else:
                if character["inventory"].get(mat, 0) < count:
                    can_craft = False
                    break
        recipes.append({
            "name": name,
            "desc": recipe["desc"],
            "materials": recipe["materials"],
            "result": recipe["result"],
            "result_count": recipe.get("result_count", 1),
            "can_craft": can_craft,
            "type": recipe.get("type", "consumable"),
        })
    return recipes

# ============================================================
# 技能系统
# ============================================================
SWORD_PROGRESSION = [
    ("基础剑法", 0),
    ("入门剑法", 50),
    ("熟练剑法", 150),
    ("登堂入室-剑法", 400),
    ("出神入化-剑法", 1000),
]

SKILL_DB = {
    # ── 剑法进阶（免费，随使用升级）──
    "基础剑法":     {"element": Element.METAL, "damage": 15, "cost": 0, "atk_mult": 0.3, "is_sword": True, "sword_tier": 1, "desc": "基础剑法，随使用提升", "price": 0},
    "入门剑法":     {"element": Element.METAL, "damage": 25, "cost": 0, "atk_mult": 0.4, "is_sword": True, "sword_tier": 2, "desc": "入门级剑法", "price": 0},
    "熟练剑法":     {"element": Element.METAL, "damage": 40, "cost": 0, "atk_mult": 0.5, "is_sword": True, "sword_tier": 3, "desc": "熟练的剑法", "price": 0},
    "登堂入室-剑法": {"element": Element.METAL, "damage": 60, "cost": 0, "atk_mult": 0.6, "is_sword": True, "sword_tier": 4, "desc": "登堂入室之境", "price": 0},
    "出神入化-剑法": {"element": Element.METAL, "damage": 85, "cost": 0, "atk_mult": 0.8, "is_sword": True, "sword_tier": 5, "desc": "出神入化之境", "price": 0},
    # ── 金属性技能 ──
    "金刃术":   {"element": Element.METAL, "damage": 18, "cost": 12, "atk_mult": 0.3, "desc": "金属性基础法术", "price": 100},
    "天罡剑诀": {"element": Element.METAL, "damage": 45, "cost": 30, "atk_mult": 0.5, "desc": "金属性高级剑法", "price": 500},
    "金虹贯日": {"element": Element.METAL, "damage": 70, "cost": 50, "atk_mult": 0.7, "desc": "金属性进阶法术", "price": 1200},
    # ── 木属性技能 ──
    "木刺术":     {"element": Element.WOOD, "damage": 16, "cost": 10, "atk_mult": 0.3, "desc": "木属性基础法术", "price": 100},
    "回春术":     {"element": Element.WOOD, "damage": -40, "cost": 20, "atk_mult": 0, "desc": "木属性恢复技能", "price": 150},
    "万叶飞花":   {"element": Element.WOOD, "damage": 50, "cost": 35, "atk_mult": 0.5, "desc": "木属性进阶法术", "price": 500},
    "青木长生诀": {"element": Element.WOOD, "damage": -80, "cost": 45, "atk_mult": 0, "desc": "木属性高级恢复", "price": 1000},
    # ── 水属性技能 ──
    "水弹术":   {"element": Element.WATER, "damage": 18, "cost": 12, "atk_mult": 0.3, "desc": "水属性基础法术", "price": 100},
    "玄冰诀":   {"element": Element.WATER, "damage": 48, "cost": 32, "atk_mult": 0.5, "desc": "水属性冰系法术", "price": 500},
    "寒潮涌动": {"element": Element.WATER, "damage": 72, "cost": 52, "atk_mult": 0.7, "desc": "水属性进阶法术", "price": 1200},
    # ── 火属性技能 ──
    "火球术":   {"element": Element.FIRE, "damage": 22, "cost": 15, "atk_mult": 0.3, "desc": "火属性基础法术", "price": 100},
    "五雷正法": {"element": Element.FIRE, "damage": 55, "cost": 38, "atk_mult": 0.5, "desc": "火属性雷法", "price": 500},
    "赤焰焚天": {"element": Element.FIRE, "damage": 78, "cost": 55, "atk_mult": 0.7, "desc": "火属性进阶法术", "price": 1200},
    # ── 土属性技能 ──
    "落石术":   {"element": Element.EARTH, "damage": 20, "cost": 14, "atk_mult": 0.3, "desc": "土属性基础法术", "price": 100},
    "厚土盾":   {"element": Element.EARTH, "damage": 0, "cost": 18, "atk_mult": 0, "desc": "土属性防御技能，本回合防御翻倍", "price": 150},
    "碎岩掌":   {"element": Element.EARTH, "damage": 52, "cost": 35, "atk_mult": 0.5, "desc": "土属性进阶掌法", "price": 500},
    "山崩地裂": {"element": Element.EARTH, "damage": 80, "cost": 58, "atk_mult": 0.7, "desc": "土属性高级法术", "price": 1200},
    # ── 高阶金属性 ──
    "万剑归宗": {"element": Element.METAL, "damage": 120, "cost": 80, "atk_mult": 0.9, "desc": "金属性顶级剑法", "price": 5000},
    "诛仙剑阵": {"element": Element.METAL, "damage": 180, "cost": 120, "atk_mult": 1.2, "desc": "金属性仙级剑阵", "price": 0},
    # ── 高阶木属性 ──
    "万木归春": {"element": Element.WOOD, "damage": -200, "cost": 80, "atk_mult": 0, "desc": "木属性顶级恢复", "price": 5000},
    "生命之树": {"element": Element.WOOD, "damage": 100, "cost": 70, "atk_mult": 0.8, "desc": "木属性仙级法术", "price": 0},
    # ── 高阶水属性 ──
    "北冥神功": {"element": Element.WATER, "damage": 150, "cost": 100, "atk_mult": 1.0, "desc": "水属性顶级法术", "price": 5000},
    "沧海桑田": {"element": Element.WATER, "damage": 200, "cost": 130, "atk_mult": 1.2, "desc": "水属性仙级法术", "price": 0},
    # ── 高阶火属性 ──
    "天火焚世": {"element": Element.FIRE, "damage": 160, "cost": 110, "atk_mult": 1.0, "desc": "火属性顶级法术", "price": 5000},
    "焚天大道": {"element": Element.FIRE, "damage": 220, "cost": 140, "atk_mult": 1.3, "desc": "火属性仙级法术", "price": 0},
    # ── 高阶土属性 ──
    "乾坤一掷": {"element": Element.EARTH, "damage": 140, "cost": 90, "atk_mult": 0.9, "desc": "土属性顶级法术", "price": 5000},
    "混沌破灭": {"element": Element.EARTH, "damage": 190, "cost": 125, "atk_mult": 1.1, "desc": "土属性仙级法术", "price": 0},
    # ── 混合属性 ──
    "五行轮转": {"element": Element.FIRE, "damage": 170, "cost": 100, "atk_mult": 1.0, "desc": "五行合一，威力倍增", "price": 0},
    "天地同寿": {"element": Element.EARTH, "damage": 250, "cost": 150, "atk_mult": 1.5, "desc": "以命换命的终极法术", "price": 0},
    "造化之力": {"element": Element.WOOD, "damage": -300, "cost": 120, "atk_mult": 0, "desc": "造化之力，起死回生", "price": 0},
}

# ============================================================
# 功法系统（被动增益）
# ============================================================
TECHNIQUE_DB = {
    # ── 黄级功法 ──
    "乾元功":   {"tier": "黄级", "element": Element.METAL, "hp_pct": 5,  "mp_pct": 8,  "atk_pct": 3,  "def_pct": 2,  "desc": "金属性入门心法", "price": 100},
    "枯木逢春": {"tier": "黄级", "element": Element.WOOD,  "hp_pct": 6,  "mp_pct": 6,  "atk_pct": 2,  "def_pct": 4,  "desc": "木属性入门心法", "price": 100},
    "流水诀":   {"tier": "黄级", "element": Element.WATER, "hp_pct": 4,  "mp_pct": 10, "atk_pct": 3,  "def_pct": 3,  "desc": "水属性入门心法", "price": 100},
    "烈火心法": {"tier": "黄级", "element": Element.FIRE,  "hp_pct": 5,  "mp_pct": 5,  "atk_pct": 5,  "def_pct": 2,  "desc": "火属性入门心法", "price": 100},
    "磐石功":   {"tier": "黄级", "element": Element.EARTH, "hp_pct": 8,  "mp_pct": 4,  "atk_pct": 2,  "def_pct": 5,  "desc": "土属性入门心法", "price": 100},
    # ── 玄级功法 ──
    "金虹剑典": {"tier": "玄级", "element": Element.METAL, "hp_pct": 10, "mp_pct": 12, "atk_pct": 6,  "def_pct": 5,  "desc": "金属性进阶功法", "price": 400},
    "青木诀":   {"tier": "玄级", "element": Element.WOOD,  "hp_pct": 12, "mp_pct": 10, "atk_pct": 5,  "def_pct": 7,  "desc": "木属性进阶功法", "price": 400},
    "寒冰真诀": {"tier": "玄级", "element": Element.WATER, "hp_pct": 8,  "mp_pct": 15, "atk_pct": 6,  "def_pct": 6,  "desc": "水属性进阶功法", "price": 400},
    "赤焰心经": {"tier": "玄级", "element": Element.FIRE,  "hp_pct": 10, "mp_pct": 10, "atk_pct": 8,  "def_pct": 4,  "desc": "火属性进阶功法", "price": 400},
    "厚土玄功": {"tier": "玄级", "element": Element.EARTH, "hp_pct": 14, "mp_pct": 8,  "atk_pct": 4,  "def_pct": 8,  "desc": "土属性进阶功法", "price": 400},
    # ── 地级功法 ──
    "庚金剑典":   {"tier": "地级", "element": Element.METAL, "hp_pct": 15, "mp_pct": 18, "atk_pct": 10, "def_pct": 8,  "desc": "金属性高阶功法", "price": 1500},
    "青木长生诀": {"tier": "地级", "element": Element.WOOD,  "hp_pct": 18, "mp_pct": 15, "atk_pct": 8,  "def_pct": 10, "desc": "木属性高阶功法", "price": 1500},
    "碧海潮生":   {"tier": "地级", "element": Element.WATER, "hp_pct": 12, "mp_pct": 22, "atk_pct": 10, "def_pct": 8,  "desc": "水属性高阶功法", "price": 1500},
    "赤焰焚天诀": {"tier": "地级", "element": Element.FIRE,  "hp_pct": 15, "mp_pct": 15, "atk_pct": 12, "def_pct": 8,  "desc": "火属性高阶功法", "price": 1500},
    "山岳真经":   {"tier": "地级", "element": Element.EARTH, "hp_pct": 20, "mp_pct": 12, "atk_pct": 8,  "def_pct": 12, "desc": "土属性高阶功法", "price": 1500},
    # ── 天级功法 ──
    "天罡剑典": {"tier": "天级", "element": Element.METAL, "hp_pct": 22, "mp_pct": 25, "atk_pct": 15, "def_pct": 12, "desc": "金属性顶级功法", "price": 5000},
    "造化神功": {"tier": "天级", "element": Element.WOOD,  "hp_pct": 25, "mp_pct": 22, "atk_pct": 12, "def_pct": 15, "desc": "木属性顶级功法", "price": 5000},
    "太虚神功": {"tier": "天级", "element": Element.WATER, "hp_pct": 20, "mp_pct": 28, "atk_pct": 15, "def_pct": 12, "desc": "水属性顶级功法", "price": 5000},
    "焚天灭世": {"tier": "天级", "element": Element.FIRE,  "hp_pct": 22, "mp_pct": 22, "atk_pct": 18, "def_pct": 10, "desc": "火属性顶级功法", "price": 5000},
    "天地同寿": {"tier": "天级", "element": Element.EARTH, "hp_pct": 28, "mp_pct": 18, "atk_pct": 12, "def_pct": 18, "desc": "土属性顶级功法", "price": 5000},
    # ── 仙级功法（不可购买，探索获得）──
    "诛仙剑典": {"tier": "仙级", "element": Element.METAL, "hp_pct": 30, "mp_pct": 35, "atk_pct": 22, "def_pct": 18, "desc": "金属性仙级功法", "price": 0},
    "万木归春": {"tier": "仙级", "element": Element.WOOD,  "hp_pct": 35, "mp_pct": 30, "atk_pct": 18, "def_pct": 22, "desc": "木属性仙级功法", "price": 0},
    "混沌大道": {"tier": "仙级", "element": Element.WATER, "hp_pct": 30, "mp_pct": 40, "atk_pct": 22, "def_pct": 18, "desc": "水属性仙级功法", "price": 0},
    "焚天大道": {"tier": "仙级", "element": Element.FIRE,  "hp_pct": 32, "mp_pct": 32, "atk_pct": 28, "def_pct": 15, "desc": "火属性仙级功法", "price": 0},
    "混元大道": {"tier": "仙级", "element": Element.EARTH, "hp_pct": 38, "mp_pct": 28, "atk_pct": 18, "def_pct": 25, "desc": "土属性仙级功法", "price": 0},
    # ── 神级功法 ──
    "天道无极": {"tier": "神级", "element": Element.METAL, "hp_pct": 40, "mp_pct": 40, "atk_pct": 30, "def_pct": 25, "desc": "金属性神级功法", "price": 0},
    "万木长春": {"tier": "神级", "element": Element.WOOD, "hp_pct": 45, "mp_pct": 35, "atk_pct": 25, "def_pct": 30, "desc": "木属性神级功法", "price": 0},
    "太虚无量": {"tier": "神级", "element": Element.WATER, "hp_pct": 35, "mp_pct": 50, "atk_pct": 30, "def_pct": 25, "desc": "水属性神级功法", "price": 0},
    "焚天大道经": {"tier": "神级", "element": Element.FIRE, "hp_pct": 38, "mp_pct": 38, "atk_pct": 35, "def_pct": 20, "desc": "火属性神级功法", "price": 0},
    "混元无极": {"tier": "神级", "element": Element.EARTH, "hp_pct": 48, "mp_pct": 35, "atk_pct": 25, "def_pct": 32, "desc": "土属性神级功法", "price": 0},
    # ── 混沌级功法 ──
    "混沌大道": {"tier": "混沌级", "element": Element.FIRE, "hp_pct": 55, "mp_pct": 55, "atk_pct": 40, "def_pct": 35, "desc": "混沌级无上功法", "price": 0},
    "造化功": {"tier": "混沌级", "element": Element.WOOD, "hp_pct": 60, "mp_pct": 50, "atk_pct": 35, "def_pct": 40, "desc": "混沌级造化功法", "price": 0},
    "天道经": {"tier": "混沌级", "element": Element.METAL, "hp_pct": 50, "mp_pct": 60, "atk_pct": 45, "def_pct": 30, "desc": "混沌级天道功法", "price": 0},
    "轮回诀": {"tier": "混沌级", "element": Element.WATER, "hp_pct": 45, "mp_pct": 65, "atk_pct": 40, "def_pct": 35, "desc": "混沌级轮回功法", "price": 0},
    "无极功": {"tier": "混沌级", "element": Element.EARTH, "hp_pct": 65, "mp_pct": 45, "atk_pct": 30, "def_pct": 45, "desc": "混沌级无极功法", "price": 0},
}

# ============================================================
# 神通系统（主动攻击技能）
# ============================================================
ABILITY_DB = {
    # ── 黄级神通 ──
    "撼山掌": {"tier": "黄级", "element": Element.EARTH, "base_damage": 25,  "atk_mult": 0.5, "cost": 15, "desc": "土属性基础掌法", "obtain": "explore"},
    "金刚拳": {"tier": "黄级", "element": Element.METAL, "base_damage": 22,  "atk_mult": 0.5, "cost": 12, "desc": "金属性基础拳法", "obtain": "explore"},
    "春风化雨": {"tier": "黄级", "element": Element.WOOD,  "base_damage": -30, "atk_mult": 0,   "cost": 20, "desc": "木属性恢复神通", "obtain": "explore"},
    "流光弹": {"tier": "黄级", "element": Element.WATER, "base_damage": 20,  "atk_mult": 0.5, "cost": 14, "desc": "水属性基础法术", "obtain": "explore"},
    "烈焰弹": {"tier": "黄级", "element": Element.FIRE,  "base_damage": 28,  "atk_mult": 0.5, "cost": 16, "desc": "火属性基础法术", "obtain": "explore"},
    # ── 玄级神通 ──
    "碎岩掌": {"tier": "玄级", "element": Element.EARTH, "base_damage": 40,  "atk_mult": 0.6, "cost": 25, "desc": "土属性进阶掌法", "obtain": "both"},
    "剑气纵横": {"tier": "玄级", "element": Element.METAL, "base_damage": 38,  "atk_mult": 0.6, "cost": 22, "desc": "金属性进阶剑法", "obtain": "both"},
    "万叶飞花": {"tier": "玄级", "element": Element.WOOD,  "base_damage": -60, "atk_mult": 0,   "cost": 35, "desc": "木属性进阶恢复", "obtain": "both"},
    "寒潮涌动": {"tier": "玄级", "element": Element.WATER, "base_damage": 35,  "atk_mult": 0.6, "cost": 24, "desc": "水属性进阶法术", "obtain": "both"},
    "烈焰斩": {"tier": "玄级", "element": Element.FIRE,  "base_damage": 45,  "atk_mult": 0.6, "cost": 28, "desc": "火属性进阶斩击", "obtain": "both"},
    # ── 地级神通 ──
    "山崩地裂": {"tier": "地级", "element": Element.EARTH, "base_damage": 60,  "atk_mult": 0.7, "cost": 40, "desc": "土属性高阶神通", "obtain": "breakthrough"},
    "万剑归宗": {"tier": "地级", "element": Element.METAL, "base_damage": 55,  "atk_mult": 0.7, "cost": 38, "desc": "金属性高阶剑法", "obtain": "breakthrough"},
    "回春术": {"tier": "地级", "element": Element.WOOD,  "base_damage": -100,"atk_mult": 0,   "cost": 50, "desc": "木属性高阶恢复", "obtain": "breakthrough"},
    "玄冰刺": {"tier": "地级", "element": Element.WATER, "base_damage": 50,  "atk_mult": 0.7, "cost": 35, "desc": "水属性高阶法术", "obtain": "breakthrough"},
    "赤焰焚天": {"tier": "地级", "element": Element.FIRE,  "base_damage": 65,  "atk_mult": 0.7, "cost": 42, "desc": "火属性高阶神通", "obtain": "breakthrough"},
    # ── 天级神通 ──
    "乾坤一掷": {"tier": "天级", "element": Element.EARTH, "base_damage": 85,  "atk_mult": 0.8, "cost": 55, "desc": "土属性顶级神通", "obtain": "breakthrough"},
    "雷霆万钧": {"tier": "天级", "element": Element.METAL, "base_damage": 80,  "atk_mult": 0.8, "cost": 50, "desc": "金属性顶级神通", "obtain": "breakthrough"},
    "枯木逢春": {"tier": "天级", "element": Element.WOOD,  "base_damage": -150,"atk_mult": 0,   "cost": 65, "desc": "木属性顶级恢复", "obtain": "breakthrough"},
    "太虚水龙": {"tier": "天级", "element": Element.WATER, "base_damage": 75,  "atk_mult": 0.8, "cost": 48, "desc": "水属性顶级神通", "obtain": "breakthrough"},
    "天火焚世": {"tier": "天级", "element": Element.FIRE,  "base_damage": 90,  "atk_mult": 0.8, "cost": 58, "desc": "火属性顶级神通", "obtain": "breakthrough"},
    # ── 仙级神通（不可购买，探索/突破领悟）──
    "混沌破灭": {"tier": "仙级", "element": Element.EARTH, "base_damage": 120, "atk_mult": 1.0, "cost": 80, "desc": "土属性仙级神通", "obtain": "breakthrough"},
    "诛仙剑阵": {"tier": "仙级", "element": Element.METAL, "base_damage": 110, "atk_mult": 1.0, "cost": 75, "desc": "金属性仙级神通", "obtain": "breakthrough"},
    "万木归春": {"tier": "仙级", "element": Element.WOOD,  "base_damage": -250,"atk_mult": 0,   "cost": 90, "desc": "木属性仙级恢复", "obtain": "breakthrough"},
    "北冥神功": {"tier": "仙级", "element": Element.WATER, "base_damage": 100, "atk_mult": 1.0, "cost": 70, "desc": "水属性仙级神通", "obtain": "breakthrough"},
    "焚天大道": {"tier": "仙级", "element": Element.FIRE,  "base_damage": 130, "atk_mult": 1.0, "cost": 85, "desc": "火属性仙级神通", "obtain": "breakthrough"},
    # ── 神级神通 ──
    "天道之剑": {"tier": "神级", "element": Element.METAL, "base_damage": 200, "atk_mult": 1.2, "cost": 100, "desc": "金属性神级神通", "obtain": "breakthrough"},
    "万木朝宗": {"tier": "神级", "element": Element.WOOD, "base_damage": -400, "atk_mult": 0, "cost": 120, "desc": "木属性神级恢复", "obtain": "breakthrough"},
    "太虚水龙": {"tier": "神级", "element": Element.WATER, "base_damage": 180, "atk_mult": 1.2, "cost": 95, "desc": "水属性神级神通", "obtain": "breakthrough"},
    "天火灭世": {"tier": "神级", "element": Element.FIRE, "base_damage": 220, "atk_mult": 1.3, "cost": 110, "desc": "火属性神级神通", "obtain": "breakthrough"},
    "山河社稷": {"tier": "神级", "element": Element.EARTH, "base_damage": 190, "atk_mult": 1.2, "cost": 105, "desc": "土属性神级神通", "obtain": "breakthrough"},
    # ── 混沌级神通 ──
    "混沌破灭斩": {"tier": "混沌级", "element": Element.METAL, "base_damage": 300, "atk_mult": 1.5, "cost": 150, "desc": "金属性混沌级神通", "obtain": "breakthrough"},
    "造化之力": {"tier": "混沌级", "element": Element.WOOD, "base_damage": -600, "atk_mult": 0, "cost": 180, "desc": "木属性混沌级恢复", "obtain": "breakthrough"},
    "太虚无量": {"tier": "混沌级", "element": Element.WATER, "base_damage": 280, "atk_mult": 1.5, "cost": 140, "desc": "水属性混沌级神通", "obtain": "breakthrough"},
    "焚天大道": {"tier": "混沌级", "element": Element.FIRE, "base_damage": 350, "atk_mult": 1.6, "cost": 160, "desc": "火属性混沌级神通", "obtain": "breakthrough"},
    "混沌之盾": {"tier": "混沌级", "element": Element.EARTH, "base_damage": 250, "atk_mult": 1.4, "cost": 130, "desc": "土属性混沌级神通", "obtain": "breakthrough"},
}

# ============================================================
# NPC 系统
# ============================================================
NPC_DB = {
    "李老头": {
        "title": "杂货商人",
        "realm": Realm.LIANQI,
        "stage": 0,
        "element": Element.EARTH,
        "hp": 80, "attack": 8, "defense": 5,
        "dialogue": {
            0: "小友，老夫这里有些丹药，要不要看看？",
            30: "小友人品不错，老夫给你打个折。",
            60: "咱们是老交情了，这些好东西给你留着呢。",
            100: "小友，老夫珍藏的宝贝只给你看！",
        },
        "shop": ["聚气丹", "回春丹", "灵芝", "铁剑", "布甲", "培元丹"],
        "technique_shop": ["乾元功", "枯木逢春", "流水诀", "烈火心法", "磐石功"],
        "skill_shop": ["金刃术", "木刺术", "水弹术", "火球术", "落石术"],
        "personality": "和善",
        "quests": [
            {"name": "收集灵芝", "desc": "收集5株灵芝交给李老头", "target": "灵芝", "count": 5,
             "reward": {"灵石": 100, "聚气丹": 3}, "relation_boost": 15},
            {"name": "驱赶野兽", "desc": "击败3只野狼", "target_kill": "野狼", "count": 3,
             "reward": {"灵石": 80, "回春丹": 2}, "relation_boost": 10},
            {"name": "剿灭山贼", "desc": "击败5只山贼", "target_kill": "山贼", "count": 5,
             "reward": {"灵石": 150, "碧玉甲": 1}, "relation_boost": 20},
        ],
        "relation_rewards": {
            50: {"item": "千年灵芝", "message": "李老头送你一株千年灵芝作为谢礼。"},
            100: {"item": "金丹丹", "message": "李老头：这是老夫珍藏的金丹丹，只给你！"},
        },
    },
    "赵灵儿": {
        "title": "云霄派弟子",
        "realm": Realm.ZHUJI,
        "stage": 1,
        "element": Element.WATER,
        "hp": 200, "attack": 30, "defense": 15,
        "dialogue": {
            0: "你是哪来的散修？这里不是你该来的地方。",
            30: "嗯...你修炼得还不错，有空可以切磋一下。",
            60: "道友，我这有些秘境的线索，你要听吗？",
            100: "道友，我愿与你结为道侣，共同修行。",
        },
        "shop": ["筑基丹", "青锋剑", "灵纹甲", "寒冰弓", "碧玉甲"],
        "technique_shop": ["寒冰真诀", "青木诀"],
        "skill_shop": ["玄冰诀", "万叶飞花", "回春术"],
        "personality": "高冷",
        "quests": [
            {"name": "翠竹林探险", "desc": "在翠竹林探索5次", "target_explore": "翠竹林", "count": 5,
             "reward": {"灵石": 200, "筑基丹": 1}, "relation_boost": 20},
            {"name": "击败树妖", "desc": "在翠竹林击败2只树妖", "target_kill": "树妖", "count": 2,
             "reward": {"灵石": 300, "青锋剑": 1}, "relation_boost": 25},
            {"name": "诛杀蜂群", "desc": "击败3群蜂群", "target_kill": "蜂群", "count": 3,
             "reward": {"灵石": 250, "续命丹": 1}, "relation_boost": 18},
        ],
        "relation_rewards": {
            80: {"item": "元婴丹", "message": "赵灵儿：这枚元婴丹是我师父赐我的，送给你。"},
            120: {"technique": "寒冰真诀", "message": "赵灵儿传授你寒冰真诀！"},
        },
    },
    "张铁柱": {
        "title": "散修",
        "realm": Realm.LIANQI,
        "stage": 2,
        "element": Element.FIRE,
        "hp": 120, "attack": 18, "defense": 8,
        "dialogue": {
            0: "嘿！兄弟，一起闯荡江湖不？",
            30: "上次那妖兽差点要了我命，多亏你帮忙。",
            60: "老铁，我发现了个好地方，一起去探探？",
            100: "兄弟，以后你的事就是我的事！",
        },
        "shop": [],
        "technique_shop": [],
        "skill_shop": ["五雷正法", "碎岩掌", "厚土盾"],
        "personality": "豪爽",
        "quests": [
            {"name": "切磋武艺", "desc": "在战斗中使用技能5次", "target_skill_use": 5,
             "reward": {"灵石": 150, "天雷珠": 2}, "relation_boost": 15},
            {"name": "收集矿石", "desc": "收集3块铁矿石", "target": "铁矿石", "count": 3,
             "reward": {"灵石": 120, "玄铁矿": 1}, "relation_boost": 12},
        ],
        "relation_rewards": {
            60: {"skill": "五雷正法", "message": "张铁柱：兄弟，这招五雷正法教给你！"},
            100: {"item": "玄铁剑", "message": "张铁柱：这是我珍藏的玄铁剑，送给你防身！"},
        },
    },
    "白骨夫人": {
        "title": "魔道修士",
        "realm": Realm.JIEDAN,
        "stage": 0,
        "element": Element.WATER,
        "hp": 400, "attack": 60, "defense": 30,
        "dialogue": {
            0: "咯咯咯...又有猎物送上门了。",
            -30: "你身上有我想要的东西，识相的就交出来。",
            60: "有趣...你比想象中强，我欣赏你。",
            100: "小家伙，姐姐我罩着你。",
        },
        "shop": ["金丹丹", "玄铁剑", "烈焰刀", "金丝软甲"],
        "technique_shop": ["碧海潮生", "庚金剑典"],
        "skill_shop": ["金虹贯日", "赤焰焚天", "寒潮涌动", "山崩地裂"],
        "personality": "阴险",
        "quests": [
            {"name": "幽冥试炼", "desc": "在幽冥涧探索8次", "target_explore": "幽冥涧", "count": 8,
             "reward": {"灵石": 500, "元婴丹": 1}, "relation_boost": 30},
            {"name": "猎杀怨灵", "desc": "击败4只怨灵", "target_kill": "怨灵", "count": 4,
             "reward": {"灵石": 400, "魂晶": 3}, "relation_boost": 25},
        ],
    },
    "天机老人": {
        "title": "天机阁主",
        "realm": Realm.HUASHEN,
        "stage": 3,
        "element": Element.METAL,
        "hp": 800, "attack": 80, "defense": 50,
        "dialogue": {
            0: "天机不可泄露...但你我有缘，可以聊聊。",
            50: "你的修为不错，老夫可以指点你一二。",
            100: "好！老夫收你为关门弟子！",
        },
        "shop": ["元婴丹", "化神丹", "雷神锤", "天蚕宝衣", "破境丹"],
        "technique_shop": ["雷霆万钧", "太虚水龙", "天火焚世"],
        "skill_shop": ["雷霆万钧", "太虚水龙", "天火焚世"],
        "personality": "神秘",
        "quests": [
            {"name": "天机试炼", "desc": "击败3只天机傀儡", "target_kill": "天机傀儡", "count": 3,
             "reward": {"灵石": 800, "天机碎片": 3}, "relation_boost": 35},
            {"name": "收集碎片", "desc": "收集5块天机碎片", "target": "天机碎片", "count": 5,
             "reward": {"灵石": 1000, "仙器碎片": 2}, "relation_boost": 40},
        ],
        "relation_rewards": {
            80: {"item": "化神丹", "message": "天机老人：这枚化神丹，助你一臂之力。"},
            150: {"technique": "雷霆万钧", "message": "天机老人传授你天级功法雷霆万钧！"},
        },
    },
    "海商龙三": {
        "title": "星落海商人", "realm": Realm.JIEDAN, "stage": 2, "element": Element.WATER,
        "hp": 300, "attack": 40, "defense": 25,
        "dialogue": {0: "客官，要买点海货吗？", 50: "看在老交情的份上，给你便宜点。", 100: "这些宝贝只给你看！"},
        "shop": ["回元丹", "冰晶", "玄冰精髓", "天蚕仙衣"],
        "technique_shop": ["碧海潮生", "寒冰真诀"], "skill_shop": ["寒潮涌动", "玄冰刺"],
        "personality": "圆滑",
        "quests": [
            {"name": "海商的烦恼", "desc": "击败3只海妖", "target_kill": "海妖", "count": 3, "reward": {"灵石": 500, "冰晶": 3}, "relation_boost": 20},
            {"name": "深海宝藏", "desc": "在星落海探索6次", "target_explore": "星落海", "count": 6, "reward": {"灵石": 800, "玄冰精髓": 1}, "relation_boost": 25},
        ],
        "relation_rewards": {80: {"item": "玄冰精髓", "message": "龙三：这玄冰精髓可是好东西，送你了！"}, 150: {"technique": "碧海潮生", "message": "龙三传授你地级功法碧海潮生！"}},
    },
    "天玄宗主": {
        "title": "天玄宗宗主", "realm": Realm.HUASHEN, "stage": 3, "element": Element.METAL,
        "hp": 1000, "attack": 100, "defense": 60,
        "dialogue": {0: "你来了？天玄宗欢迎你。", 50: "你的资质不错，可以加入天玄宗。", 100: "好！老夫收你为亲传弟子！"},
        "shop": ["天罡剑", "玄天甲", "天罡战靴", "天罡护腕", "天罡头盔"],
        "technique_shop": ["天罡剑典", "造化神功"], "skill_shop": ["万剑归宗", "雷霆万钧"],
        "personality": "威严",
        "quests": [
            {"name": "天玄试炼", "desc": "击败5只天玄弟子", "target_kill": "天玄弟子", "count": 5, "reward": {"灵石": 1000, "天机碎片": 3}, "relation_boost": 30},
            {"name": "护山之战", "desc": "击败2只护山神兽", "target_kill": "护山神兽", "count": 2, "reward": {"灵石": 1500, "仙器碎片": 2}, "relation_boost": 35},
        ],
        "relation_rewards": {100: {"item": "天罡剑", "message": "天玄宗主：这柄天罡剑赐予你！"}, 180: {"technique": "天罡剑典", "message": "天玄宗主传授你天级功法天罡剑典！"}},
    },
    "孟婆": {
        "title": "忘川摆渡人", "realm": Realm.YUANYING, "stage": 2, "element": Element.WATER,
        "hp": 500, "attack": 60, "defense": 40,
        "dialogue": {0: "来，喝碗汤，忘却前尘。", 50: "你不想喝？那也无妨。", 100: "你与我有缘，这碗汤免费。"},
        "shop": ["九转还魂丹", "续命仙丹", "万寿丹"],
        "technique_shop": ["碧海潮生", "太虚神功"], "skill_shop": ["北冥神功", "沧海桑田"],
        "personality": "神秘",
        "quests": [
            {"name": "忘川之旅", "desc": "在九幽地府探索5次", "target_explore": "九幽地府", "count": 5, "reward": {"灵石": 800, "魂晶": 5}, "relation_boost": 25},
            {"name": "判官之怒", "desc": "击败2只判官", "target_kill": "判官", "count": 2, "reward": {"灵石": 1200, "天道碎片": 1}, "relation_boost": 30},
        ],
        "relation_rewards": {80: {"item": "九转还魂丹", "message": "孟婆：这碗汤能起死回生，送你了。"}, 150: {"technique": "太虚神功", "message": "孟婆传授你天级功法太虚神功！"}},
    },
    "仙灵岛主": {
        "title": "仙灵岛岛主", "realm": Realm.FEISHENG, "stage": 0, "element": Element.WOOD,
        "hp": 2000, "attack": 150, "defense": 100,
        "dialogue": {0: "你来了？仙灵岛欢迎你。", 50: "你的修为不错，可以在这里修炼。", 100: "好！老夫收你为仙灵岛弟子！"},
        "shop": ["造化丹", "万寿丹", "混沌之心", "造化之链"],
        "technique_shop": ["造化功", "天道经"], "skill_shop": ["造化之力", "五行轮转"],
        "personality": "仙风道骨",
        "quests": [
            {"name": "仙岛试炼", "desc": "击败3只守岛神兽", "target_kill": "守岛神兽", "count": 3, "reward": {"灵石": 2000, "造化玉碟": 1}, "relation_boost": 40},
            {"name": "蟠桃盛会", "desc": "收集3颗蟠桃", "target": "蟠桃", "count": 3, "reward": {"灵石": 3000, "混沌精华": 2}, "relation_boost": 50},
        ],
        "relation_rewards": {100: {"item": "蟠桃", "message": "仙灵岛主：这颗蟠桃送你，祝你修为精进。"}, 200: {"technique": "造化功", "message": "仙灵岛主传授你混沌级功法造化功！"}},
    },
    "飞升仙人": {
        "title": "飞升台守卫", "realm": Realm.FEISHENG, "stage": 3, "element": Element.METAL,
        "hp": 3000, "attack": 200, "defense": 150,
        "dialogue": {0: "你准备好了吗？飞升之路充满艰险。", 50: "你的实力不错，但还需更多历练。", 100: "好！老夫助你一臂之力！"},
        "shop": ["天道甲", "混沌铠", "混沌战靴", "混沌护腕", "混沌头盔"],
        "technique_shop": ["混沌大道", "天道经", "无极功"], "skill_shop": ["混沌破灭斩", "天火灭世"],
        "personality": "超然",
        "quests": [
            {"name": "飞升试炼", "desc": "击败3只天道使者", "target_kill": "天道使者", "count": 3, "reward": {"灵石": 5000, "天道碎片": 5}, "relation_boost": 50},
            {"name": "混沌之战", "desc": "击败2只混沌魔神", "target_kill": "混沌魔神", "count": 2, "reward": {"灵石": 8000, "混沌精华": 3}, "relation_boost": 60},
        ],
        "relation_rewards": {120: {"item": "天道碎片", "message": "飞升仙人：这些天道碎片助你飞升。"}, 200: {"technique": "混沌大道", "message": "飞升仙人传授你混沌级功法混沌大道！"}},
    },
    "药王": {
        "title": "炼丹宗师", "realm": Realm.YUANYING, "stage": 2, "element": Element.WOOD,
        "hp": 400, "attack": 30, "defense": 20,
        "dialogue": {0: "老夫药王，炼丹之道的行者。", 50: "你的炼丹天赋不错，老夫可以指点你。", 100: "好！老夫收你为关门弟子！"},
        "shop": ["聚气丹", "培元丹", "天元丹", "造化丹", "回春丹", "回元丹"],
        "technique_shop": ["枯木逢春", "青木长生诀"], "skill_shop": ["回春术", "万木归春"],
        "personality": "和善",
        "quests": [
            {"name": "炼丹之道", "desc": "炼制5炉丹药", "target_craft": 5, "reward": {"灵石": 500, "千年灵芝": 3}, "relation_boost": 20},
            {"name": "灵草采集", "desc": "收集10株灵芝", "target": "灵芝", "count": 10, "reward": {"灵石": 300, "培元丹": 2}, "relation_boost": 15},
        ],
        "relation_rewards": {60: {"item": "天元丹", "message": "药王：这枚天元丹送你，好好修炼。"}, 120: {"technique": "青木长生诀", "message": "药王传授你地级功法青木长生诀！"}},
    },
    "剑痴": {
        "title": "剑道狂人", "realm": Realm.HUASHEN, "stage": 1, "element": Element.METAL,
        "hp": 600, "attack": 90, "defense": 40,
        "dialogue": {0: "剑！我的最爱！你也是剑修吗？", 50: "你的剑法不错，来切磋一下！", 100: "好！我把毕生剑道传授给你！"},
        "shop": ["天罡剑", "诛仙剑"],
        "technique_shop": ["天罡剑典", "庚金剑典"], "skill_shop": ["万剑归宗", "诛仙剑阵"],
        "personality": "狂放",
        "quests": [
            {"name": "剑道之路", "desc": "在战斗中使用剑法20次", "target_skill_use": 20, "reward": {"灵石": 1000, "仙器碎片": 2}, "relation_boost": 25},
            {"name": "剑灵之战", "desc": "击败3只剑灵", "target_kill": "剑灵", "count": 3, "reward": {"灵石": 1500, "凤凰羽": 1}, "relation_boost": 30},
        ],
        "relation_rewards": {80: {"skill": "万剑归宗", "message": "剑痴：这招万剑归宗教给你！"}, 150: {"technique": "天罡剑典", "message": "剑痴传授你天级功法天罡剑典！"}},
    },
    "阵法大师": {
        "title": "天机阁阵法师", "realm": Realm.JIEDAN, "stage": 3, "element": Element.EARTH,
        "hp": 350, "attack": 45, "defense": 35,
        "dialogue": {0: "阵法之道，博大精深。", 50: "你对阵法有兴趣？老夫可以教你。", 100: "好！老夫收你为阵法弟子！"},
        "shop": ["天机碎片", "天机扇"],
        "technique_shop": ["厚土玄功", "山岳真经"], "skill_shop": ["山崩地裂", "乾坤一掷"],
        "personality": "严谨",
        "quests": [
            {"name": "阵法入门", "desc": "收集5块天机碎片", "target": "天机碎片", "count": 5, "reward": {"灵石": 600, "天机碎片": 2}, "relation_boost": 20},
            {"name": "傀儡之战", "desc": "击败3只阵法傀儡", "target_kill": "阵法傀儡", "count": 3, "reward": {"灵石": 800, "天机碎片": 3}, "relation_boost": 25},
        ],
        "relation_rewards": {60: {"item": "天机扇", "message": "阵法大师：这柄天机扇送你。"}, 120: {"technique": "山岳真经", "message": "阵法大师传授你地级功法山岳真经！"}},
    },
    "鬼医": {
        "title": "九幽鬼医", "realm": Realm.YUANYING, "stage": 1, "element": Element.WOOD,
        "hp": 450, "attack": 50, "defense": 30,
        "dialogue": {0: "嘿嘿...你受伤了？老夫可以帮你。", 50: "你的体质特殊，老夫对你很感兴趣。", 100: "好！老夫收你为鬼医弟子！"},
        "shop": ["九转还魂丹", "续命丹", "万寿丹"],
        "technique_shop": ["造化神功", "万木归春"], "skill_shop": ["枯木逢春", "万木朝宗"],
        "personality": "阴险",
        "quests": [
            {"name": "鬼医之道", "desc": "在九幽地府探索8次", "target_explore": "九幽地府", "count": 8, "reward": {"灵石": 1000, "魂晶": 5}, "relation_boost": 25},
            {"name": "幽冥龙之战", "desc": "击败2只幽冥龙", "target_kill": "幽冥龙", "count": 2, "reward": {"灵石": 1500, "龙珠": 1}, "relation_boost": 30},
        ],
        "relation_rewards": {80: {"item": "万寿丹", "message": "鬼医：这枚万寿丹送你。"}, 150: {"technique": "造化神功", "message": "鬼医传授你天级功法造化神功！"}},
    },
    "妖皇": {
        "title": "万妖山妖皇", "realm": Realm.HUASHEN, "stage": 2, "element": Element.FIRE,
        "hp": 800, "attack": 95, "defense": 50,
        "dialogue": {0: "你来了？万妖山欢迎你。", 50: "你的实力不错，可以加入万妖山。", 100: "好！老夫收你为万妖山弟子！"},
        "shop": ["妖丹", "凤凰羽", "烈焰之心"],
        "technique_shop": ["焚天灭世", "赤焰焚天诀"], "skill_shop": ["天火焚世", "焚天大道"],
        "personality": "霸道",
        "quests": [
            {"name": "妖族之路", "desc": "击败5只妖王", "target_kill": "妖王", "count": 5, "reward": {"灵石": 1000, "妖丹": 3}, "relation_boost": 30},
            {"name": "万妖朝拜", "desc": "在万妖山探索6次", "target_explore": "万妖山", "count": 6, "reward": {"灵石": 1500, "凤凰羽": 1}, "relation_boost": 35},
        ],
        "relation_rewards": {80: {"item": "妖丹", "message": "妖皇：这些妖丹送你。"}, 150: {"technique": "焚天灭世", "message": "妖皇传授你天级功法焚天灭世！"}},
    },
    "混沌老祖": {
        "title": "混沌深渊守护者", "realm": Realm.FEISHENG, "stage": 1, "element": Element.EARTH,
        "hp": 2500, "attack": 180, "defense": 120,
        "dialogue": {0: "你来了？混沌深渊欢迎你。", 50: "你的实力不错，可以在这里修炼。", 100: "好！老夫收你为混沌弟子！"},
        "shop": ["混沌精华", "混沌之心", "混沌铠", "混沌战靴", "混沌护腕", "混沌头盔"],
        "technique_shop": ["混沌大道", "造化功", "无极功"], "skill_shop": ["混沌破灭斩", "混沌之盾"],
        "personality": "深邃",
        "quests": [
            {"name": "混沌之路", "desc": "击败3只混沌魔神", "target_kill": "混沌魔神", "count": 3, "reward": {"灵石": 3000, "混沌精华": 2}, "relation_boost": 40},
            {"name": "灭世之战", "desc": "击败2只灭世天魔", "target_kill": "灭世天魔", "count": 2, "reward": {"灵石": 5000, "造化玉碟": 1}, "relation_boost": 50},
        ],
        "relation_rewards": {100: {"item": "混沌精华", "message": "混沌老祖：这些混沌精华送你。"}, 200: {"technique": "混沌大道", "message": "混沌老祖传授你混沌级功法混沌大道！"}},
    },
}

# ============================================================
# 怪物系统
# ============================================================
MONSTER_DB = {
    "野狼": {"hp": 40, "attack": 8, "defense": 3, "element": Element.EARTH, "exp": 20,
             "drops": {"灵石": [10, 25], "灵芝": [0, 1]}},
    "灵蛇": {"hp": 60, "attack": 12, "defense": 5, "element": Element.WATER, "exp": 35,
             "drops": {"灵石": [15, 35], "灵芝": [0, 1]}},
    "石傀儡": {"hp": 100, "attack": 15, "defense": 20, "element": Element.EARTH, "exp": 50, "type": "humanoid",
              "drops": {"灵石": [20, 50], "天雷珠": [0, 1]}},
    "火焰妖": {"hp": 120, "attack": 30, "defense": 10, "element": Element.FIRE, "exp": 80, "type": "spirit",
              "skills": ["烈焰喷射", "火球术"],
              "drops": {"灵石": [40, 100], "聚气丹": [0, 2]}},
    "水鬼": {"hp": 90, "attack": 22, "defense": 12, "element": Element.WATER, "exp": 60, "type": "spirit",
             "drops": {"灵石": [25, 80], "回春丹": [0, 1]}},
    "树妖": {"hp": 150, "attack": 25, "defense": 18, "element": Element.WOOD, "exp": 100, "type": "spirit",
             "drops": {"灵石": [40, 120], "千年灵芝": [0, 1]}},
    "雷兽": {"hp": 200, "attack": 45, "defense": 25, "element": Element.FIRE, "exp": 150, "type": "beast",
             "skills": ["雷霆万钧", "电光火石"],
             "drops": {"灵石": [80, 200], "天雷珠": [0, 2]}},
    "玄冰蛟": {"hp": 300, "attack": 55, "defense": 30, "element": Element.WATER, "exp": 200, "type": "dragon",
               "skills": ["寒冰吐息", "冰封万里"],
               "drops": {"灵石": [100, 300], "天材地宝": [0, 1]}},
    "金甲虫": {"hp": 50, "attack": 10, "defense": 15, "element": Element.METAL, "exp": 25,
               "drops": {"灵石": [12, 30], "铁矿石": [0, 1]}},
    "毒蝎": {"hp": 70, "attack": 18, "defense": 8, "element": Element.WOOD, "exp": 40,
             "drops": {"灵石": [18, 40], "解毒丹": [0, 1]}},
    "岩魔": {"hp": 180, "attack": 35, "defense": 30, "element": Element.EARTH, "exp": 120,
             "drops": {"灵石": [60, 150], "玄铁矿": [0, 1]}},
    "冰霜巨狼": {"hp": 160, "attack": 38, "defense": 20, "element": Element.WATER, "exp": 110,
                "drops": {"灵石": [50, 130], "冰晶": [0, 1]}},
    "幽魂": {"hp": 100, "attack": 28, "defense": 5, "element": Element.WATER, "exp": 70, "type": "spirit",
             "drops": {"灵石": [30, 70], "魂晶": [0, 1]}},
    "天机傀儡": {"hp": 250, "attack": 40, "defense": 35, "element": Element.METAL, "exp": 180, "type": "humanoid",
                "skills": ["机关术", "铁壁"],
                "drops": {"灵石": [100, 250], "天机碎片": [0, 1]}},

    # ── 青云镇补充 ──
    "野猪": {"hp": 35, "attack": 7, "defense": 4, "element": Element.EARTH, "exp": 15,
             "drops": {"灵石": [8, 20], "灵芝": [0, 1]}},
    "山贼": {"hp": 50, "attack": 10, "defense": 6, "element": Element.METAL, "exp": 22,
             "drops": {"灵石": [12, 30], "铁矿石": [0, 1]}},

    # ── 翠竹林补充 ──
    "竹精": {"hp": 80, "attack": 20, "defense": 12, "element": Element.WOOD, "exp": 45,
             "drops": {"灵石": [20, 50], "灵芝": [0, 2]}},
    "蜂群": {"hp": 45, "attack": 25, "defense": 3, "element": Element.WOOD, "exp": 38,
             "drops": {"灵石": [15, 40], "回春丹": [0, 1]}},

    # ── 炎魔谷补充 ──
    "熔岩蜥蜴": {"hp": 130, "attack": 28, "defense": 18, "element": Element.FIRE, "exp": 85,
                "drops": {"灵石": [45, 110], "玄铁矿": [0, 1]}},
    "火鸦": {"hp": 90, "attack": 35, "defense": 8, "element": Element.FIRE, "exp": 75,
             "drops": {"灵石": [35, 90], "聚气丹": [0, 1]}},

    # ── 幽冥涧补充 ──
    "怨灵": {"hp": 110, "attack": 32, "defense": 6, "element": Element.WATER, "exp": 85,
             "drops": {"灵石": [40, 100], "魂晶": [0, 1]}},
    "蛟龙": {"hp": 280, "attack": 50, "defense": 28, "element": Element.WATER, "exp": 180,
             "drops": {"灵石": [90, 250], "天材地宝": [0, 1]}},

    # ── 天机城补充 ──
    "机关兽": {"hp": 220, "attack": 38, "defense": 32, "element": Element.METAL, "exp": 160,
              "drops": {"灵石": [80, 220], "天机碎片": [0, 1]}},
    "傀儡将军": {"hp": 350, "attack": 55, "defense": 40, "element": Element.METAL, "exp": 250,
               "drops": {"灵石": [150, 400], "天机碎片": [0, 2], "仙器碎片": [0, 1]}},

    # ── 稀有精英 ──
    "五行灵蝶": {"hp": 180, "attack": 42, "defense": 22, "element": Element.WOOD, "exp": 140,
               "drops": {"灵石": [60, 180], "千年灵芝": [0, 1], "聚气丹": [0, 2]}},
    "噬魂蝠王": {"hp": 200, "attack": 48, "defense": 15, "element": Element.WATER, "exp": 160,
               "drops": {"灵石": [80, 200], "魂晶": [0, 2]}},
    "九尾妖狐": {"hp": 320, "attack": 60, "defense": 25, "element": Element.FIRE, "exp": 220,
               "drops": {"灵石": [120, 350], "天材地宝": [0, 1], "聚气丹": [0, 3]}},
    "上古石魔": {"hp": 400, "attack": 50, "defense": 50, "element": Element.EARTH, "exp": 280,
               "drops": {"灵石": [200, 500], "玄铁矿": [0, 3], "天雷珠": [0, 2]}},
    # ── 探索链补充怪物 ──
    "噬人妖虎": {"hp": 280, "attack": 50, "defense": 25, "element": Element.FIRE, "exp": 200,
                "drops": {"灵石": [100, 300], "妖丹": [0, 1]}},
    "万妖之王": {"hp": 600, "attack": 80, "defense": 50, "element": Element.FIRE, "exp": 400,
                "drops": {"灵石": [250, 700], "妖丹": [1, 1], "天材地宝": [0, 1]}},
    "海蛟龙": {"hp": 450, "attack": 70, "defense": 40, "element": Element.WATER, "exp": 350, "type": "dragon",
              "drops": {"灵石": [200, 550], "龙珠": [0, 1], "冰晶": [0, 2]}},
    "天玄叛徒": {"hp": 350, "attack": 60, "defense": 35, "element": Element.METAL, "exp": 280, "type": "humanoid",
               "drops": {"灵石": [150, 400], "天机碎片": [0, 1]}},
    "灵兽之母": {"hp": 500, "attack": 65, "defense": 45, "element": Element.WOOD, "exp": 380, "type": "spirit",
               "drops": {"灵石": [200, 600], "千年灵芝": [0, 2], "仙灵草": [0, 1]}},
    # ── 万妖山 ──
    "妖王": {"hp": 500, "attack": 75, "defense": 45, "element": Element.FIRE, "exp": 350, "type": "humanoid",
             "drops": {"灵石": [200, 600], "天材地宝": [0, 2], "妖丹": [1, 1]}},
    "石魔将": {"hp": 450, "attack": 65, "defense": 55, "element": Element.EARTH, "exp": 300, "type": "humanoid",
              "drops": {"灵石": [180, 500], "玄铁矿": [0, 3]}},
    # ── 星落海 ──
    "海妖": {"hp": 350, "attack": 60, "defense": 35, "element": Element.WATER, "exp": 260, "type": "spirit",
             "drops": {"灵石": [150, 400], "冰晶": [0, 2]}},
    "深海巨鲸": {"hp": 600, "attack": 70, "defense": 50, "element": Element.WATER, "exp": 400, "type": "beast",
                "drops": {"灵石": [250, 700], "天材地宝": [0, 2]}},
    "珊瑚精": {"hp": 280, "attack": 45, "defense": 40, "element": Element.WOOD, "exp": 200, "type": "spirit",
               "drops": {"灵石": [120, 350], "千年灵芝": [0, 2]}},
    "海龙": {"hp": 550, "attack": 80, "defense": 45, "element": Element.WATER, "exp": 380, "type": "dragon",
             "drops": {"灵石": [200, 600], "龙珠": [0, 1]}},
    "水母精": {"hp": 200, "attack": 55, "defense": 20, "element": Element.WATER, "exp": 170, "type": "spirit",
               "drops": {"灵石": [80, 250], "魂晶": [0, 1]}},
    "鲛人": {"hp": 320, "attack": 58, "defense": 30, "element": Element.WATER, "exp": 240, "type": "humanoid",
             "drops": {"灵石": [140, 380], "鲛人泪": [0, 1]}},
    # ── 天玄域 ──
    "天玄弟子": {"hp": 300, "attack": 55, "defense": 35, "element": Element.METAL, "exp": 230, "type": "humanoid",
                "drops": {"灵石": [130, 370], "天机碎片": [0, 1]}},
    "护山神兽": {"hp": 500, "attack": 70, "defense": 50, "element": Element.EARTH, "exp": 350, "type": "beast",
                "drops": {"灵石": [200, 550], "天材地宝": [0, 1]}},
    "剑灵": {"hp": 250, "attack": 85, "defense": 20, "element": Element.METAL, "exp": 280, "type": "spirit",
             "drops": {"灵石": [150, 450], "仙器碎片": [0, 1]}},
    "阵法傀儡": {"hp": 400, "attack": 50, "defense": 60, "element": Element.EARTH, "exp": 300, "type": "humanoid",
                "drops": {"灵石": [180, 500], "天机碎片": [0, 2]}},
    "天玄长老": {"hp": 600, "attack": 90, "defense": 55, "element": Element.FIRE, "exp": 450, "type": "humanoid",
                "drops": {"灵石": [300, 800], "天材地宝": [0, 2], "仙器碎片": [0, 1]}},
    "道心魔": {"hp": 350, "attack": 75, "defense": 25, "element": Element.WATER, "exp": 320, "type": "spirit",
               "drops": {"灵石": [160, 480], "魂晶": [0, 2]}},
    # ── 九幽地府 ──
    "鬼将": {"hp": 450, "attack": 70, "defense": 40, "element": Element.WATER, "exp": 340, "type": "humanoid",
             "drops": {"灵石": [200, 550], "魂晶": [0, 3]}},
    "冥河摆渡人": {"hp": 400, "attack": 65, "defense": 45, "element": Element.WATER, "exp": 310, "type": "humanoid",
                  "drops": {"灵石": [180, 500], "天材地宝": [0, 1]}},
    "判官": {"hp": 550, "attack": 80, "defense": 50, "element": Element.METAL, "exp": 420, "type": "humanoid",
             "drops": {"灵石": [250, 700], "天道碎片": [0, 1]}},
    "阎罗": {"hp": 800, "attack": 100, "defense": 60, "element": Element.FIRE, "exp": 600, "type": "humanoid",
             "drops": {"灵石": [400, 1000], "天道碎片": [0, 2], "混沌精华": [0, 1]}},
    "幽冥龙": {"hp": 700, "attack": 95, "defense": 55, "element": Element.WATER, "exp": 550, "type": "dragon",
               "drops": {"灵石": [350, 900], "龙珠": [0, 1], "天道碎片": [0, 1]}},
    "忘川水鬼": {"hp": 300, "attack": 60, "defense": 30, "element": Element.WATER, "exp": 250, "type": "spirit",
                "drops": {"灵石": [140, 400], "魂晶": [0, 2]}},
    # ── 混沌深渊 ──
    "混沌兽": {"hp": 600, "attack": 85, "defense": 50, "element": Element.EARTH, "exp": 480, "type": "beast",
               "drops": {"灵石": [300, 800], "混沌精华": [0, 1]}},
    "时空裂隙": {"hp": 500, "attack": 90, "defense": 30, "element": Element.FIRE, "exp": 450, "type": "spirit",
                "drops": {"灵石": [250, 700], "天道碎片": [0, 1]}},
    "虚空行者": {"hp": 450, "attack": 95, "defense": 35, "element": Element.METAL, "exp": 420, "type": "spirit",
                "drops": {"灵石": [220, 650], "天道碎片": [0, 1]}},
    "混沌魔神": {"hp": 1000, "attack": 120, "defense": 70, "element": Element.FIRE, "exp": 800, "type": "humanoid",
                "drops": {"灵石": [500, 1500], "混沌精华": [0, 2], "造化玉碟": [0, 1]}},
    "灭世天魔": {"hp": 1200, "attack": 140, "defense": 80, "element": Element.FIRE, "exp": 1000, "type": "humanoid",
                "drops": {"灵石": [600, 2000], "混沌精华": [0, 3], "天道碎片": [0, 2]}},
    "混沌之眼": {"hp": 800, "attack": 110, "defense": 60, "element": Element.WATER, "exp": 700, "type": "spirit",
                "drops": {"灵石": [400, 1200], "天道碎片": [0, 2]}},
    # ── 仙灵岛 ──
    "仙鹤": {"hp": 400, "attack": 60, "defense": 40, "element": Element.WOOD, "exp": 350, "type": "beast",
             "drops": {"灵石": [200, 600], "千年灵芝": [0, 2]}},
    "灵芝仙": {"hp": 350, "attack": 50, "defense": 45, "element": Element.WOOD, "exp": 320, "type": "spirit",
               "drops": {"灵石": [180, 500], "千年灵芝": [0, 3]}},
    "仙童": {"hp": 500, "attack": 75, "defense": 50, "element": Element.METAL, "exp": 400, "type": "humanoid",
             "drops": {"灵石": [250, 700], "天材地宝": [0, 2]}},
    "守岛神兽": {"hp": 800, "attack": 100, "defense": 65, "element": Element.EARTH, "exp": 650, "type": "beast",
                "drops": {"灵石": [400, 1100], "天道碎片": [0, 1], "造化玉碟": [0, 1]}},
    "仙灵蝶": {"hp": 300, "attack": 70, "defense": 30, "element": Element.WOOD, "exp": 280, "type": "spirit",
               "drops": {"灵石": [150, 450], "千年灵芝": [0, 2]}},
    "蟠桃仙": {"hp": 600, "attack": 80, "defense": 55, "element": Element.WOOD, "exp": 500,
               "drops": {"灵石": [300, 800], "蟠桃": [0, 1]}},
    # ── 天劫荒原 ──
    "劫雷兽": {"hp": 700, "attack": 100, "defense": 55, "element": Element.FIRE, "exp": 600,
               "drops": {"灵石": [350, 900], "天道碎片": [0, 1]}},
    "天劫守卫": {"hp": 650, "attack": 90, "defense": 60, "element": Element.METAL, "exp": 550,
                "drops": {"灵石": [300, 800], "天道碎片": [0, 1]}},
    "雷龙": {"hp": 900, "attack": 120, "defense": 65, "element": Element.FIRE, "exp": 750,
             "drops": {"灵石": [450, 1200], "龙珠": [0, 1], "天道碎片": [0, 2]}},
    "劫火凤凰": {"hp": 850, "attack": 115, "defense": 60, "element": Element.FIRE, "exp": 700,
                "drops": {"灵石": [400, 1100], "混沌精华": [0, 1]}},
    "天道使者": {"hp": 1000, "attack": 130, "defense": 75, "element": Element.METAL, "exp": 900,
                "drops": {"灵石": [500, 1500], "天道碎片": [0, 3], "造化玉碟": [0, 1]}},
    "劫魔": {"hp": 750, "attack": 105, "defense": 50, "element": Element.FIRE, "exp": 650,
             "drops": {"灵石": [380, 1000], "混沌精华": [0, 1]}},
    # ── 飞升台 ──
    "飞升守卫": {"hp": 900, "attack": 120, "defense": 70, "element": Element.METAL, "exp": 800,
                "drops": {"灵石": [500, 1400], "天道碎片": [0, 2]}},
    "天门将": {"hp": 1100, "attack": 140, "defense": 80, "element": Element.FIRE, "exp": 1000,
              "drops": {"灵石": [600, 1800], "天道碎片": [0, 3], "造化玉碟": [0, 1]}},
    "仙界使者": {"hp": 1000, "attack": 135, "defense": 75, "element": Element.WOOD, "exp": 900,
                "drops": {"灵石": [550, 1600], "混沌精华": [0, 2]}},
    "飞升劫灵": {"hp": 1200, "attack": 150, "defense": 85, "element": Element.FIRE, "exp": 1200,
                "drops": {"灵石": [700, 2000], "天道碎片": [0, 4], "造化玉碟": [0, 2]}},
    "天道化身": {"hp": 1500, "attack": 180, "defense": 100, "element": Element.METAL, "exp": 1500,
                "drops": {"灵石": [1000, 3000], "天道碎片": [0, 5], "混沌精华": [0, 3]}},
    "混沌守卫": {"hp": 1300, "attack": 160, "defense": 90, "element": Element.EARTH, "exp": 1300,
                "drops": {"灵石": [800, 2500], "混沌精华": [0, 3], "造化玉碟": [0, 1]}},
}

# ============================================================
# 区域系统
# ============================================================
REGIONS = {
    "青云镇": {
        "level": 1,
        "desc": "一处宁静的小镇，初入修仙之路的起点",
        "monsters": ["野狼", "灵蛇", "金甲虫", "野猪", "山贼"],
        "events": ["捡到灵石", "遇到老者指路", "发现灵草", "顿悟天道", "发现山洞",
                   "遇到行商", "发现古井", "村民求助"],
        "npc": ["李老头", "张铁柱"],
    },
    "翠竹林": {
        "level": 2,
        "desc": "竹林深处灵气充沛，偶有妖兽出没",
        "monsters": ["灵蛇", "树妖", "毒蝎", "竹精", "蜂群", "五行灵蝶"],
        "events": ["发现秘境入口", "遇到受伤修士", "捡到残破功法", "竹林淬体", "竹林古洞",
                   "竹林迷阵", "灵泉沐浴", "遇到采药人"],
        "npc": ["赵灵儿"],
    },
    "炎魔谷": {
        "level": 3,
        "desc": "地火蔓延的山谷，火属性妖兽横行",
        "monsters": ["火焰妖", "石傀儡", "岩魔", "熔岩蜥蜴", "火鸦"],
        "events": ["地火喷发", "发现矿脉", "遇到魔修", "地火炼心", "古修士遗迹",
                   "熔岩洞穴", "遇到火灵", "火山爆发"],
        "npc": [],
    },
    "幽冥涧": {
        "level": 4,
        "desc": "阴气弥漫的深渊，水鬼和亡灵游荡",
        "monsters": ["水鬼", "雷兽", "幽魂", "冰霜巨狼", "怨灵", "蛟龙", "噬魂蝠王"],
        "events": ["阴气侵体", "发现古墓", "遇到鬼修", "阴气感悟", "上古洞府",
                   "幽冥试炼", "鬼市", "遇到幽灵"],
        "npc": ["白骨夫人"],
    },
    "天机城": {
        "level": 5,
        "desc": "中立交易区，各路修士汇聚之地",
        "monsters": ["天机傀儡", "机关兽", "傀儡将军", "九尾妖狐", "上古石魔"],
        "events": ["拍卖会", "比武招亲", "悬赏任务", "机缘巧合",
                   "天机阁", "遇到神秘人", "天降奇缘"],
        "npc": ["李老头", "赵灵儿", "白骨夫人", "天机老人"],
    },
    "万妖山": {
        "level": 6,
        "desc": "群山之中妖兽云集，高阶修士方敢涉足",
        "monsters": ["九尾妖狐", "上古石魔", "雷兽", "岩魔", "噬魂蝠王", "妖王"],
        "events": ["妖王降临", "发现妖族圣地", "万妖朝拜", "妖兽围攻", "上古妖阵", "妖丹炼体", "妖族秘宝", "遇到妖修"],
        "npc": ["妖皇"],
    },
    "星落海": {
        "level": 7,
        "desc": "浩瀚大海，星辰倒映，海底藏有上古遗迹",
        "monsters": ["海妖", "深海巨鲸", "珊瑚精", "海龙", "水母精", "鲛人"],
        "events": ["海底遗迹", "遇到海商", "星辰坠落", "海底火山", "鲛人泪", "海市蜃楼", "风暴来袭", "龙宫探秘"],
        "npc": ["海商龙三"],
    },
    "天玄域": {
        "level": 8,
        "desc": "天玄宗所在，灵气浓郁，修士如云",
        "monsters": ["天玄弟子", "护山神兽", "剑灵", "阵法傀儡", "天玄长老", "道心魔"],
        "events": ["天玄试炼", "道心考验", "天玄藏经阁", "论道大会", "天玄秘境", "宗门大比", "遇到道友", "天玄拍卖"],
        "npc": ["天玄宗主", "剑痴", "阵法大师"],
    },
    "九幽地府": {
        "level": 9,
        "desc": "阴曹地府，亡魂归处，阴气森森",
        "monsters": ["鬼将", "冥河摆渡人", "判官", "阎罗", "幽冥龙", "忘川水鬼"],
        "events": ["冥河泛舟", "判官问案", "轮回感悟", "忘川花海", "地府宝藏", "鬼门关", "孟婆汤", "阴间市集"],
        "npc": ["孟婆", "鬼医"],
    },
    "混沌深渊": {
        "level": 10,
        "desc": "混沌之力弥漫，时空扭曲，危机四伏",
        "monsters": ["混沌兽", "时空裂隙", "虚空行者", "混沌魔神", "灭世天魔", "混沌之眼"],
        "events": ["时空裂缝", "混沌感悟", "虚空风暴", "混沌宝藏", "灭世预言", "混沌炼体", "遇到远古存在", "混沌之心"],
        "npc": ["混沌老祖"],
    },
    "仙灵岛": {
        "level": 11,
        "desc": "传说中的仙岛，灵气如液，遍地仙草",
        "monsters": ["仙鹤", "灵芝仙", "仙童", "守岛神兽", "仙灵蝶", "蟠桃仙"],
        "events": ["仙泉沐浴", "蟠桃盛会", "仙人指路", "仙岛秘境", "悟道茶", "仙草园", "遇到仙人", "仙岛奇遇"],
        "npc": ["仙灵岛主"],
    },
    "天劫荒原": {
        "level": 12,
        "desc": "天劫频发之地，雷电交加，渡劫圣地",
        "monsters": ["劫雷兽", "天劫守卫", "雷龙", "劫火凤凰", "天道使者", "劫魔"],
        "events": ["天劫降临", "劫雷淬体", "天道感悟", "劫火炼心", "天劫试炼", "遇到渡劫者", "天劫宝藏", "劫后余生"],
        "npc": [],
    },
    "飞升台": {
        "level": 13,
        "desc": "传说中的飞升之地，通往仙界的门户",
        "monsters": ["飞升守卫", "天门将", "仙界使者", "飞升劫灵", "天道化身", "混沌守卫"],
        "events": ["飞升试炼", "天门开启", "仙界召唤", "飞升感悟", "天道洗礼", "遇到飞升者", "飞升宝藏", "仙界预兆"],
        "npc": ["飞升仙人"],
    },
}

# 通用事件（所有区域都可能发生）
UNIVERSAL_EVENTS = [
    "灵石矿脉", "天降陨石", "修士切磋", "灵药园", "古传送阵",
    "神秘商人", "天地异象", "灵气漩涡", "遗落宝箱", "仙鹤指路",
    "遗迹探秘", "灵兽相助", "天劫降临", "悟道石碑", "仙人遗府",
    "丹药奇遇", "法器残片", "灵脉觉醒", "心魔试炼", "天道酬勤",
    "遇到仙人", "天劫降临", "混沌秘境", "造化之力", "天道碎片", "凤凰涅槃", "龙宫探秘", "蟠桃盛会",
    "天道洗礼", "轮回感悟", "妖王降临", "海底遗迹", "星辰坠落", "天玄试炼", "论道大会", "冥河泛舟",
    # 新增事件
    "灵泉沐浴", "仙果成熟", "剑冢探秘", "灵田丰收", "天降祥瑞",
    "修士论剑", "丹炉爆炸", "灵兽产崽", "阵法破损", "天劫余波",
    "仙人指点", "魔修来袭", "灵脉枯竭", "天材地宝", "秘境入口",
    "上古遗迹", "仙鹤报恩", "灵石雨", "心魔入侵", "天道感应",
    "灵气潮汐", "仙人渡劫", "妖兽暴动", "灵脉喷涌", "天降异宝",
    "修士求助", "灵兽异变", "阵法激活", "丹药成灵", "法器通灵",
    "天地共鸣", "混沌裂缝", "时空紊乱", "因果纠缠", "命运转折",
    "轮回之力", "造化弄人", "天道无常", "万法归一", "大道至简",
    "仙魔之战", "上古封印", "神兽苏醒", "天界通道", "幽冥之门",
    "五行失衡", "阴阳逆转", "星辰移位", "日月同辉", "天地交泰",
    "灵根觉醒", "血脉返祖", "悟道顿悟", "心境突破", "机缘巧合",
]

# 探索链事件（多步骤任务）
EXPLORATION_CHAINS = {
    "寻找失落的功法": {
        "steps": [
            {"desc": "你听到传闻，有一本上古功法遗落在翠竹林深处...", "region": "翠竹林", "type": "explore"},
            {"desc": "你在竹林中发现了一块刻有符文的石碑，似乎指向炎魔谷...", "region": "炎魔谷", "type": "explore"},
            {"desc": "你在炎魔谷找到了功法的下落，但它被一只强大的妖兽守护着...", "region": "炎魔谷", "type": "combat", "enemy": "火焰妖"},
        ],
        "rewards": {"exp": 200, "item": "聚气丹", "stat": {"悟性": 2}},
    },
    "营救被困修士": {
        "steps": [
            {"desc": "你听到求救声，似乎有修士被困在幽冥涧...", "region": "幽冥涧", "type": "explore"},
            {"desc": "你找到了被困的修士，但他被一群怨灵包围...", "region": "幽冥涧", "type": "combat", "enemy": "怨灵"},
            {"desc": "修士获救，他告诉你一个秘密宝藏的位置...", "region": "天机城", "type": "explore"},
        ],
        "rewards": {"exp": 150, "stones": 300, "relation": {"张铁柱": 30}},
    },
    "探索天机阁": {
        "steps": [
            {"desc": "你听说天机城的天机阁中藏有无上功法...", "region": "天机城", "type": "explore"},
            {"desc": "天机阁的守卫考验你的实力...", "region": "天机城", "type": "combat", "enemy": "天机傀儡"},
            {"desc": "你通过了考验，进入了天机阁深处...", "region": "天机城", "type": "explore"},
        ],
        "rewards": {"exp": 300, "ability": True, "stat": {"悟性": 3}},
    },
    "天道之路": {
        "steps": [
            {"desc": "你感应到天道之力的召唤，需要收集天道碎片...", "region": "天劫荒原", "type": "explore"},
            {"desc": "天道碎片散发着神秘光芒，似乎在指引你前往更深处...", "region": "天劫荒原", "type": "explore"},
            {"desc": "天道使者出现了！只有战胜它才能获得天道的认可...", "region": "天劫荒原", "type": "combat", "enemy": "天道使者"},
        ],
        "rewards": {"exp": 500, "item": "天道碎片", "stat": {"悟性": 5}},
    },
    "混沌之路": {
        "steps": [
            {"desc": "混沌深渊传来低沉的呼唤，你需要找到混沌精华...", "region": "混沌深渊", "type": "explore"},
            {"desc": "混沌之力扭曲了时空，你必须小心前行...", "region": "混沌深渊", "type": "explore"},
            {"desc": "混沌魔神挡住了去路，这是你必须面对的挑战...", "region": "混沌深渊", "type": "combat", "enemy": "混沌魔神"},
        ],
        "rewards": {"exp": 800, "item": "混沌精华", "stat": {"悟性": 8}},
    },
    "飞升之路": {
        "steps": [
            {"desc": "飞升台的传说吸引了你，你需要做好充分准备...", "region": "飞升台", "type": "explore"},
            {"desc": "飞升试炼开始了，你必须证明自己的实力...", "region": "飞升台", "type": "explore"},
            {"desc": "飞升劫灵降临，这是飞升前的最后考验...", "region": "飞升台", "type": "combat", "enemy": "飞升劫灵"},
        ],
        "rewards": {"exp": 1500, "item": "造化玉碟", "stat": {"悟性": 10}},
    },
    "仙岛奇缘": {
        "steps": [
            {"desc": "你听到了仙灵岛的传说，据说那里有仙人居住...", "region": "星落海", "type": "explore"},
            {"desc": "你找到了通往仙灵岛的路，但守岛神兽拦住了去路...", "region": "仙灵岛", "type": "combat", "enemy": "守岛神兽"},
            {"desc": "仙灵岛的美景令你陶醉，你在这里获得了仙缘...", "region": "仙灵岛", "type": "explore"},
        ],
        "rewards": {"exp": 600, "item": "蟠桃", "stat": {"魅力": 5}},
    },
    "地府探秘": {
        "steps": [
            {"desc": "九幽地府的阴气弥漫，你决定一探究竟...", "region": "九幽地府", "type": "explore"},
            {"desc": "冥河摆渡人出现了，他似乎想阻止你前进...", "region": "九幽地府", "type": "combat", "enemy": "冥河摆渡人"},
            {"desc": "你在地府深处发现了轮回的秘密...", "region": "九幽地府", "type": "explore"},
        ],
        "rewards": {"exp": 400, "item": "魂晶", "stat": {"悟性": 4}},
    },
    "万妖山除魔": {
        "steps": [
            {"desc": "万妖山近来妖气冲天，村民苦不堪言...", "region": "万妖山", "type": "explore"},
            {"desc": "你发现了一只作恶的妖兽，准备为民除害...", "region": "万妖山", "type": "combat", "enemy": "噬人妖虎"},
            {"desc": "妖虎被击败，但山中似乎还有更强大的妖兽...", "region": "万妖山", "type": "combat", "enemy": "万妖之王"},
        ],
        "rewards": {"exp": 350, "item": "妖丹", "stat": {"根骨": 3}},
    },
    "星落海寻宝": {
        "steps": [
            {"desc": "传说星落海底沉睡着上古仙人的宝藏...", "region": "星落海", "type": "explore"},
            {"desc": "你在海底发现了一座古老的宫殿...", "region": "星落海", "type": "explore"},
            {"desc": "宫殿的守护者出现了！这是一条古老的蛟龙...", "region": "星落海", "type": "combat", "enemy": "海蛟龙"},
        ],
        "rewards": {"exp": 450, "item": "龙珠", "stones": 500, "stat": {"气运": 4}},
    },
    "天玄域历练": {
        "steps": [
            {"desc": "天玄域的灵气异常浓郁，适合修炼...", "region": "天玄域", "type": "explore"},
            {"desc": "你遇到了天玄宗的弟子，他们正在寻找帮手...", "region": "天玄域", "type": "explore"},
            {"desc": "天玄宗的敌人来袭，你必须帮助他们...", "region": "天玄域", "type": "combat", "enemy": "天玄叛徒"},
        ],
        "rewards": {"exp": 500, "item": "天玄令", "stat": {"悟性": 5}},
    },
    "仙灵岛求药": {
        "steps": [
            {"desc": "你听说仙灵岛上有一种能治百病的仙草...", "region": "仙灵岛", "type": "explore"},
            {"desc": "仙草被一群灵兽守护着，你需要证明自己的善意...", "region": "仙灵岛", "type": "explore"},
            {"desc": "灵兽之母出现了，它要考验你的心性...", "region": "仙灵岛", "type": "combat", "enemy": "灵兽之母"},
        ],
        "rewards": {"exp": 550, "item": "仙灵草", "stat": {"魅力": 5}},
    },
    "混沌深渊探秘": {
        "steps": [
            {"desc": "混沌深渊的气息令人窒息，但你感应到了强大的力量...", "region": "混沌深渊", "type": "explore"},
            {"desc": "深渊中的混沌之力不断侵蚀你的灵力...", "region": "混沌深渊", "type": "explore"},
            {"desc": "混沌魔神出现了！这是你面对的最强敌人...", "region": "混沌深渊", "type": "combat", "enemy": "混沌魔神"},
        ],
        "rewards": {"exp": 1000, "item": "混沌精华", "stat": {"根骨": 8, "悟性": 8}},
    },
    "天劫荒原试炼": {
        "steps": [
            {"desc": "天劫荒原上空电闪雷鸣，天劫之力弥漫...", "region": "天劫荒原", "type": "explore"},
            {"desc": "你发现了一块天劫残片，其中蕴含着强大的力量...", "region": "天劫荒原", "type": "explore"},
            {"desc": "天劫守卫出现了！它要阻止你获取天劫之力...", "region": "天劫荒原", "type": "combat", "enemy": "天劫守卫"},
        ],
        "rewards": {"exp": 700, "item": "天劫残片", "stat": {"根骨": 6}},
    },
    "飞升台问道": {
        "steps": [
            {"desc": "飞升台散发着神圣的光芒，你感受到了天道的气息...", "region": "飞升台", "type": "explore"},
            {"desc": "飞升引路人出现了，他要考验你的道心...", "region": "飞升台", "type": "explore"},
            {"desc": "飞升劫灵降临！只有通过考验才能飞升...", "region": "飞升台", "type": "combat", "enemy": "飞升劫灵"},
        ],
        "rewards": {"exp": 2000, "item": "飞升丹", "stat": {"根骨": 10, "悟性": 10, "气运": 10}},
    },
}

# ============================================================
# 角色创建
# ============================================================
def create_character(name: str, elements: list, stats: dict = None) -> dict:
    if stats is None:
        stats = _roll_stats()

    # 灵根被动加成
    elem_bonuses = compute_element_bonuses(elements)

    # 基础属性
    base_hp = 100
    base_mp = 50
    base_atk = 10 + stats["根骨"]
    base_def = 5 + stats["根骨"] // 2

    # 应用灵根加成
    max_hp = int(base_hp * (1 + elem_bonuses.get("hp_pct", 0) / 100))
    max_mp = int(base_mp * (1 + elem_bonuses.get("mp_pct", 0) / 100))
    attack = int(base_atk * (1 + elem_bonuses.get("atk_pct", 0) / 100))
    defense = int(base_def * (1 + elem_bonuses.get("def_pct", 0) / 100))

    # 初始技能：基础剑法 + 每灵根对应元素基础技能
    elem_skill_map = {"金": "金刃术", "木": "木刺术", "水": "水弹术", "火": "火球术", "土": "落石术"}
    starter_skills = ["基础剑法"]
    for elem in elements:
        skill = elem_skill_map.get(elem)
        if skill and skill not in starter_skills:
            starter_skills.append(skill)

    character = {
        "name": name,
        "element": elements,
        "realm": Realm.LIANQI.value,
        "stage": 0,
        "exp": 0,
        "exp_to_next": 100 * len(elements),
        "hp": max_hp,
        "max_hp": max_hp,
        "mp": max_mp,
        "max_mp": max_mp,
        "attack": attack,
        "defense": defense,
        "lifespan": REALM_DATA[Realm.LIANQI]["max_lifespan"],
        "age": 16,
        "stats": stats,
        "inventory": {"灵石": 100, "聚气丹": 3, "回春丹": 2, "铁剑": 1, "布甲": 1},
        "equipped": {"weapon": "铁剑", "armor": "布甲"},
        "skills": starter_skills,
        "techniques": [],
        "abilities": [],
        "location": "青云镇",
        "npc_relations": {},
        "events_log": [],
        "kills": 0,
        "sword_uses": 0,
        "sword_tier": 1,
    }
    return character

# ============================================================
# 修炼系统
# ============================================================
def cultivate(character: dict) -> dict:
    # 寿元检查
    if character.get("lifespan", 0) <= 0:
        return {"exp_gain": 0, "lifespan_cost": 0, "total_exp": character["exp"],
                "exp_needed": character["exp_to_next"], "can_breakthrough": False,
                "message": "寿元已尽，无法修炼。请休息恢复寿元。"}

    realm = Realm(character["realm"])
    realm_data = REALM_DATA[realm]

    # 基础修炼速度
    base_speed = realm_data["base_cultivation_speed"]
    # 悟性影响修炼倍率（悟性10 vs 悟性5: +30%）
    wuxing_mult = 1.0 + (character["stats"]["悟性"] - 5) * 0.06
    # 气运影响随机下限（气运10: 下限0.8，气运5: 下限0.75）
    qiyun_floor = 0.7 + character["stats"]["气运"] * 0.01
    # 根骨固定加成
    gengu_bonus = int(character["stats"]["根骨"] * 0.3)
    # 多灵根修炼速度倍增
    elem_count = len(character_elements(character))

    gain = int(base_speed * wuxing_mult * random.uniform(qiyun_floor, 1.2) * 12 * elem_count * 1.2) + gengu_bonus
    character["exp"] += gain
    character["last_cultivate_time"] = time.time()  # 更新挂机计时

    # 更新修炼次数统计
    character.setdefault("stats", {})["cultivate_count"] = character.get("stats", {}).get("cultivate_count", 0) + 1

    # 消耗寿元
    lifespan_cost = random.randint(1, 2)
    character["lifespan"] -= lifespan_cost
    character["age"] += lifespan_cost

    result = {
        "exp_gain": gain,
        "lifespan_cost": lifespan_cost,
        "total_exp": character["exp"],
        "exp_needed": character["exp_to_next"],
    }

    # 检查是否可以突破
    if character["exp"] >= character["exp_to_next"]:
        result["can_breakthrough"] = True
    else:
        result["can_breakthrough"] = False

    return result

def check_idle_cultivation(character: dict) -> dict:
    """检查挂机修炼收益（离线时自动积累修为）"""
    import time
    last_time = character.get("last_cultivate_time", 0)
    if last_time <= 0:
        character["last_cultivate_time"] = time.time()
        return {"idle_gain": 0, "idle_time": 0, "message": "开始挂机修炼。"}

    now = time.time()
    elapsed = now - last_time
    if elapsed < 60:  # 不到1分钟不计算
        return {"idle_gain": 0, "idle_time": 0}

    # 最多计算24小时
    max_seconds = 24 * 3600
    elapsed = min(elapsed, max_seconds)

    realm = Realm(character["realm"])
    realm_data = REALM_DATA[realm]
    base_speed = realm_data["base_cultivation_speed"]
    wuxing_mult = 1.0 + (character["stats"]["悟性"] - 5) * 0.06
    elem_count = len(character_elements(character))

    # 挂机效率为手动修炼的80%
    idle_efficiency = 0.8
    # 每分钟一次修炼
    minutes = elapsed / 60
    gain = int(base_speed * wuxing_mult * 10 * elem_count * idle_efficiency * minutes)
    gain = max(1, gain)

    # 消耗寿元（每小时1点）
    lifespan_cost = max(1, int(elapsed / 3600))
    lifespan_cost = min(lifespan_cost, character.get("lifespan", 0))
    character["lifespan"] = max(0, character.get("lifespan", 0) - lifespan_cost)

    character["exp"] += gain
    character["last_cultivate_time"] = now

    hours = int(elapsed // 3600)
    mins = int((elapsed % 3600) // 60)
    time_str = f"{hours}小时{mins}分钟" if hours > 0 else f"{mins}分钟"

    return {
        "idle_gain": gain,
        "idle_time": elapsed,
        "lifespan_cost": lifespan_cost,
        "time_str": time_str,
        "total_exp": character["exp"],
        "exp_needed": character["exp_to_next"],
        "can_breakthrough": character["exp"] >= character["exp_to_next"],
        "message": f"挂机修炼 {time_str}，获得 {gain} 修为，消耗 {lifespan_cost} 寿元。"
    }

# ============================================================
# 突破系统
# ============================================================
def attempt_breakthrough(character: dict, use_items: list = None) -> dict:
    realm = Realm(character["realm"])
    realm_data = REALM_DATA[realm]

    # 计算突破成功率
    base_rate = realm_data["breakthrough_base_rate"]
    # 境内小境界突破有额外加成（初期→中期更容易）
    stage_bonus = character["stage"] * 0.03
    wuxing_bonus = character["stats"]["悟性"] * 0.025
    gengu_bonus = character["stats"]["根骨"] * 0.015
    qiyun_bonus = character["stats"]["气运"] * 0.02

    # 使用丹药加成
    item_bonus = 0
    if use_items:
        for item_name in use_items:
            if item_name in character["inventory"] and character["inventory"][item_name] > 0:
                item_data = ITEM_DB.get(item_name, {})
                if item_data.get("effect") == "breakthrough":
                    item_bonus += item_data["value"] / 100
                    character["inventory"][item_name] -= 1
                    if character["inventory"][item_name] <= 0:
                        del character["inventory"][item_name]

    # 临时增益加成（来自预服丹药等）
    temp_bonus = character.get("temp_buffs", {}).get("breakthrough_rate", 0) / 100
    if temp_bonus > 0:
        character.setdefault("temp_buffs", {})["breakthrough_rate"] = 0  # 使用后清零

    total_rate = min(base_rate + stage_bonus + wuxing_bonus + gengu_bonus + qiyun_bonus + item_bonus + temp_bonus, 0.95)

    roll = random.random()
    success = roll < total_rate

    result = {
        "success": success,
        "rate": round(total_rate * 100, 1),
        "roll": round(roll * 100, 1),
    }

    if success:
        # 突破成功
        current_stage = character["stage"]
        stages = realm_data["stages"]

        if current_stage < len(stages) - 1:
            # 境内提升
            character["stage"] += 1
            result["new_realm"] = get_realm_full_name(realm, character["stage"])
            result["message"] = f"突破成功！你现在是{result['new_realm']}"
        else:
            # 进入下一个大境界
            realm_index = REALM_ORDER.index(realm)
            if realm_index < len(REALM_ORDER) - 1:
                new_realm = REALM_ORDER[realm_index + 1]
                character["realm"] = new_realm.value
                character["stage"] = 0
                new_realm_data = REALM_DATA[new_realm]
                result["new_realm"] = get_realm_full_name(new_realm, 0)
                result["message"] = f"大道突破！你已踏入{result['new_realm']}！"

                # 境界提升奖励（根骨越高，攻防加成越多）
                gengu = character["stats"]["根骨"]
                hp_gain = 60 + realm_index * 15
                mp_gain = 35 + realm_index * 10
                character["max_hp"] += hp_gain
                character["hp"] = character["max_hp"]
                character["max_mp"] += mp_gain
                character["mp"] = character["max_mp"]
                character["attack"] += int(18 * (0.5 + gengu * 0.12))
                character["defense"] += int(12 * (0.5 + gengu * 0.12))
                character["lifespan"] = new_realm_data["max_lifespan"]
            else:
                result["message"] = "已达化神圆满，可尝试飞升！"

        # 重置修为
        character["exp"] = 0
        # 二次增长曲线：基于境界进度计算，避免指数爆炸
        new_realm_idx = REALM_ORDER.index(Realm(character["realm"]))
        total_level = new_realm_idx * 4 + character["stage"]
        character["exp_to_next"] = int(100 * (total_level + 1) ** 1.5)

        # 突破奖励（大境界突破给更多属性）
        is_major = character["stage"] == 0 and "new_realm" in result
        stat_gain = 2 if is_major else 1
        character["stats"]["根骨"] += stat_gain
        character["stats"]["悟性"] += stat_gain

        # 8%概率领悟随机神通
        if random.random() < 0.08:
            char_elems = character_elements(character)
            available = [name for name, a in ABILITY_DB.items()
                        if a["element"].value in char_elems
                        and name not in character.get("abilities", [])]
            if available:
                chosen = random.choice(available)
                character.setdefault("abilities", []).append(chosen)
                ability = ABILITY_DB[chosen]
                result["ability_learned"] = chosen
                result["message"] += f"\n\n突破之际，你顿悟了{ability['tier']}神通【{chosen}】！"
    else:
        result["message"] = f"突破失败！成功率 {result['rate']}%，你的修为倒退了一些..."
        character["exp"] = max(0, character["exp"] - int(character["exp_to_next"] * 0.3))
        # 失败惩罚
        character["hp"] = max(1, character["hp"] - int(character["max_hp"] * 0.2))

    return result

# ============================================================
# 飞升系统
# ============================================================
def attempt_ascension(character: dict) -> dict:
    """飞升仙界 — 游戏终极目标"""
    realm = Realm(character["realm"])
    stage = character["stage"]
    realm_data = REALM_DATA[realm]

    # 条件1：必须是渡劫圆满
    if realm != Realm.DUJIE or stage < len(realm_data["stages"]) - 1:
        return {"success": False, "message": "需要达到渡劫圆满才能尝试飞升。"}

    # 条件2：必须持有渡劫丹
    dujie_pills = character.get("inventory", {}).get("渡劫丹", 0)
    if dujie_pills < 1:
        return {"success": False, "message": "飞升需要消耗一枚「渡劫丹」。"}

    # 条件3：修为必须满
    if character["exp"] < character["exp_to_next"]:
        return {"success": False, "message": "修为不足，无法引动天劫。"}

    # 消耗渡劫丹
    character["inventory"]["渡劫丹"] -= 1
    if character["inventory"]["渡劫丹"] <= 0:
        del character["inventory"]["渡劫丹"]

    # 飞升成功率：基础30% + 悟性/根骨/气运加成
    base_rate = 0.30
    wuxing_bonus = character["stats"]["悟性"] * 0.02
    gengu_bonus = character["stats"]["根骨"] * 0.02
    qiyun_bonus = character["stats"]["气运"] * 0.03
    total_rate = min(base_rate + wuxing_bonus + gengu_bonus + qiyun_bonus, 0.85)

    roll = random.random()
    success = roll < total_rate

    if success:
        # 飞升成功！
        new_realm = Realm.FEISHENG
        new_realm_data = REALM_DATA[new_realm]
        character["realm"] = new_realm.value
        character["stage"] = 0
        character["exp"] = 0
        character["exp_to_next"] = 100000

        # 大幅属性提升
        character["max_hp"] += 2000
        character["hp"] = character["max_hp"]
        character["max_mp"] += 1000
        character["mp"] = character["max_mp"]
        character["attack"] += 500
        character["defense"] += 300
        character["lifespan"] = -1  # 长生不老

        # 属性大幅提升
        character["stats"]["根骨"] += 10
        character["stats"]["悟性"] += 10
        character["stats"]["气运"] += 10

        # 解锁飞升奖励
        character.setdefault("achievements", []).append("飞升仙界")

        return {
            "success": True,
            "message": "天劫渡过，你成功飞升仙界！从此长生不老，逍遥天地间！",
            "new_realm": get_realm_full_name(new_realm, 0),
            "rate": round(total_rate * 100, 1),
        }
    else:
        # 飞升失败，但不死亡（给予保底）
        character["hp"] = max(1, character["hp"] - int(character["max_hp"] * 0.5))
        character["exp"] = max(0, character["exp"] - int(character["exp_to_next"] * 0.2))

        return {
            "success": False,
            "message": f"天劫未过！成功率 {round(total_rate*100,1)}%，你重伤而退，修为倒退...",
            "rate": round(total_rate * 100, 1),
        }

# ============================================================
# 战斗系统
# ============================================================
def create_combat(character: dict, enemy_name: str) -> dict:
    if enemy_name in MONSTER_DB:
        m = MONSTER_DB[enemy_name]
        enemy = {
            "name": enemy_name,
            "hp": m["hp"],
            "max_hp": m["hp"],
            "attack": m["attack"],
            "defense": m["defense"],
            "element": m["element"].value if isinstance(m["element"], Element) else m["element"],
            "exp": m["exp"],
            "drops": m["drops"],
            "type": "monster",
            "skills": m.get("skills", []),
        }
    elif enemy_name in NPC_DB:
        npc = NPC_DB[enemy_name]
        enemy = {
            "name": enemy_name,
            "hp": npc["hp"],
            "max_hp": npc["hp"],
            "attack": npc["attack"],
            "defense": npc["defense"],
            "element": npc["element"].value if isinstance(npc["element"], Element) else npc["element"],
            "type": "npc",
        }
    else:
        return None

    # 计算功法加成
    tech_hp_bonus = 0
    tech_mp_bonus = 0
    tech_atk_bonus = 0
    tech_def_bonus = 0
    for tech_name in character.get("techniques", []):
        if tech_name in TECHNIQUE_DB:
            t = TECHNIQUE_DB[tech_name]
            tech_hp_bonus += t["hp_pct"]
            tech_mp_bonus += t["mp_pct"]
            tech_atk_bonus += t["atk_pct"]
            tech_def_bonus += t["def_pct"]

    # 灵根被动加成
    elem_bonuses = compute_element_bonuses(character_elements(character))

    effective_attack = int(character["attack"] * (1 + (tech_atk_bonus + elem_bonuses.get("atk_pct", 0)) / 100))
    effective_defense = int(character["defense"] * (1 + (tech_def_bonus + elem_bonuses.get("def_pct", 0)) / 100))
    effective_max_hp = int(character["max_hp"] * (1 + (tech_hp_bonus + elem_bonuses.get("hp_pct", 0)) / 100))
    effective_max_mp = int(character["max_mp"] * (1 + (tech_mp_bonus + elem_bonuses.get("mp_pct", 0)) / 100))

    combat = {
        "player": {
            "name": character["name"],
            "hp": character["hp"],
            "max_hp": effective_max_hp,
            "mp": character["mp"],
            "max_mp": effective_max_mp,
            "attack": effective_attack,
            "defense": effective_defense,
            "element": character_elements(character),
            "skills": character["skills"],
            "abilities": character.get("abilities", []),
        },
        "enemy": enemy,
        "turn": 0,
        "log": [f"遭遇 {enemy_name}！"],
        "finished": False,
        "victory": None,
        "_base_defense": effective_defense,
    }

    # 记录遭遇的怪物（图鉴系统）
    if enemy_name in MONSTER_DB:
        encountered = character.setdefault("stats", {}).setdefault("monsters_encountered", [])
        if enemy_name not in encountered:
            encountered.append(enemy_name)

    return combat

# ── 状态效果系统 ──
STATUS_EFFECTS = {
    "中毒": {"type": "dot", "hp_pct": 0.05, "desc": "每回合损失5%最大生命", "color": "#9b59b6"},
    "灼烧": {"type": "dot_def", "hp_pct": 0.03, "def_mult": 0.8, "desc": "每回合损失3%生命，防御降低20%", "color": "#e74c3c"},
    "冰冻": {"type": "skip", "chance": 0.5, "desc": "50%概率跳过回合", "color": "#3498db"},
    "眩晕": {"type": "skip", "chance": 1.0, "desc": "跳过回合", "color": "#f39c12"},
    "治愈": {"type": "hot", "hp_pct": 0.05, "desc": "每回合恢复5%最大生命", "color": "#2ecc71"},
    "护盾": {"type": "shield", "absorb": 0.2, "desc": "吸收20%伤害", "color": "#95a5a6"},
}

# 技能附带状态效果
SKILL_STATUS_CHANCE = {
    "中毒": 0.3, "灼烧": 0.25, "冰冻": 0.15, "眩晕": 0.1, "治愈": 0.35, "护盾": 0.2,
}

def _apply_status_effects(combat: dict, target: str) -> list:
    """处理目标身上持续效果，返回日志列表"""
    logs = []
    entity = combat[target]
    effects = entity.get("status_effects", {})
    to_remove = []

    for effect_name, duration in list(effects.items()):
        if duration <= 0:
            to_remove.append(effect_name)
            continue
        effect = STATUS_EFFECTS.get(effect_name)
        if not effect:
            continue

        if effect["type"] in ("dot", "dot_def"):
            dmg = max(1, int(entity["max_hp"] * effect["hp_pct"]))
            entity["hp"] = max(0, entity["hp"] - dmg)
            who = "你" if target == "player" else entity["name"]
            logs.append(f"{who}受到{effect_name}影响，损失 {dmg} 点生命！")
            if effect["type"] == "dot_def":
                entity["_status_def_mult"] = effect.get("def_mult", 1.0)
        elif effect["type"] == "hot":
            heal = max(1, int(entity["max_hp"] * effect["hp_pct"]))
            entity["hp"] = min(entity["max_hp"], entity["hp"] + heal)
            who = "你" if target == "player" else entity["name"]
            logs.append(f"{who}受到{effect_name}效果，恢复 {heal} 点生命！")
        elif effect["type"] == "skip":
            if random.random() < effect.get("chance", 1.0):
                who = "你" if target == "player" else entity["name"]
                logs.append(f"{who}被{effect_name}控制，无法行动！")
                entity["_skip_turn"] = True

        effects[effect_name] = duration - 1

    for name in to_remove:
        del effects[name]

    return logs

def _try_inflict_status(combat: dict, target: str, skill_element) -> list:
    """尝试对目标施加状态效果"""
    logs = []
    if not hasattr(skill_element, 'value'):
        return logs
    elem_val = skill_element.value if hasattr(skill_element, 'value') else str(skill_element)
    status_map = {"火": "灼烧", "水": "冰冻", "木": "中毒", "金": "眩晕", "土": "护盾"}
    effect_name = status_map.get(elem_val)
    if not effect_name:
        return logs
    chance = SKILL_STATUS_CHANCE.get(effect_name, 0.2)
    if random.random() < chance:
        entity = combat[target]
        entity.setdefault("status_effects", {})
        if effect_name not in entity["status_effects"]:
            entity["status_effects"][effect_name] = 3  # 持续3回合
            who = "你" if target == "player" else entity["name"]
            logs.append(f"{who}被施加了【{effect_name}】效果！")
    return logs

def combat_action(combat: dict, action: str, skill_name: str = None) -> dict:
    if combat["finished"]:
        return combat

    player = combat["player"]
    enemy = combat["enemy"]
    combat["turn"] += 1

    # ── 回合开始：处理双方状态效果 ──
    player_status_logs = _apply_status_effects(combat, "player")
    enemy_status_logs = _apply_status_effects(combat, "enemy")
    for log in player_status_logs + enemy_status_logs:
        combat["log"].append(log)

    # 检查是否因状态效果死亡
    if enemy["hp"] <= 0:
        combat["log"].append(f"{enemy['name']}被状态效果击败！")
        combat["finished"] = True
        combat["victory"] = True
        return combat
    if player["hp"] <= 0:
        combat["log"].append("你被状态效果击败了...")
        combat["finished"] = True
        combat["victory"] = False
        return combat

    # 检查玩家是否被控制（跳过回合）
    player_skip = player.pop("_skip_turn", False)
    enemy_skip = enemy.pop("_skip_turn", False)
    def_mult = player.pop("_status_def_mult", 1.0)

    # 玩家行动（如果被控制则跳过）
    player_elems = player["element"] if isinstance(player["element"], list) else [player["element"]]
    if player_skip:
        combat["log"].append("你被控制，无法行动！")
    elif action == "attack":
        elem_mult = _best_element_multiplier(player_elems, enemy["element"])
        base_damage = (player["attack"] - enemy["defense"] * 0.5) * elem_mult * random.uniform(0.8, 1.2)
        # 暴击判定（气运影响暴击率）
        crit_chance = min(0.3, player.get("stats", {}).get("气运", 5) * 0.02)
        is_crit = random.random() < crit_chance
        if is_crit:
            base_damage *= 1.8
        damage = max(1, int(base_damage))
        enemy["hp"] = max(0, enemy["hp"] - damage)
        if is_crit:
            combat["log"].append(f"【暴击！】你发起攻击，造成 {damage} 点伤害！")
            combat["_max_crit"] = max(combat.get("_max_crit", 0), damage)
        else:
            combat["log"].append(f"你发起攻击，造成 {damage} 点伤害！")
    elif action == "skill" and skill_name and skill_name in SKILL_DB:
        skill = SKILL_DB[skill_name]
        is_sword = skill.get("is_sword", False)
        cost = 0 if is_sword else skill["cost"]
        if player["mp"] >= cost:
            player["mp"] -= cost
            if is_sword:
                # 剑法使用次数追踪
                combat.setdefault("_sword_uses_delta", 0)
                combat["_sword_uses_delta"] += 1
            if skill["damage"] > 0:
                elem_mult = _best_element_multiplier([skill["element"].value], enemy["element"])
                atk_mult = skill.get("atk_mult", 0.3)
                raw_damage = skill["damage"] + player["attack"] * atk_mult
                # 暴击判定
                crit_chance = min(0.3, player.get("stats", {}).get("气运", 5) * 0.02)
                is_crit = random.random() < crit_chance
                if is_crit:
                    raw_damage *= 1.8
                damage = max(1, int(raw_damage * elem_mult * random.uniform(0.9, 1.1)))
                enemy["hp"] = max(0, enemy["hp"] - damage)
                if is_crit:
                    combat["log"].append(f"【暴击！】你使出{skill_name}，造成 {damage} 点伤害！")
                    combat["_max_crit"] = max(combat.get("_max_crit", 0), damage)
                else:
                    combat["log"].append(f"你使出{skill_name}，造成 {damage} 点伤害！")
                # 技能尝试施加状态效果
                status_logs = _try_inflict_status(combat, "enemy", skill["element"])
                for log in status_logs:
                    combat["log"].append(log)
            elif skill["damage"] < 0:
                heal = abs(skill["damage"])
                player["hp"] = min(player["max_hp"], player["hp"] + heal)
                combat["log"].append(f"你使出{skill_name}，恢复 {heal} 点生命！")
                combat["_max_heal"] = max(combat.get("_max_heal", 0), heal)
            else:
                # 防御技能：使用基础防御的2倍，防止叠加
                base_def = combat.get("_base_defense", player["defense"])
                player["defense"] = base_def * 2
                combat["log"].append(f"你使出{skill_name}，防御大幅提升！")
        else:
            combat["log"].append(f"灵力不足，无法使用{skill_name}！")
    elif action == "ability" and skill_name and skill_name in ABILITY_DB:
        ability = ABILITY_DB[skill_name]
        if ability["element"].value not in player_elems:
            combat["log"].append(f"灵根不符！{skill_name}需要{ability['element'].value}灵根！")
        elif player["mp"] >= ability["cost"]:
            player["mp"] -= ability["cost"]
            if ability["base_damage"] > 0:
                # 攻击型神通：base_damage + attack * atk_mult，五行克制1.5倍
                elem_mult = get_element_multiplier(ability["element"], Element(enemy["element"]))
                raw_damage = ability["base_damage"] + player["attack"] * ability["atk_mult"]
                # 暴击判定（神通暴击率更高）
                crit_chance = min(0.4, player.get("stats", {}).get("气运", 5) * 0.025)
                is_crit = random.random() < crit_chance
                if is_crit:
                    raw_damage *= 2.0
                damage = max(1, int(raw_damage * elem_mult * random.uniform(0.9, 1.1)))
                enemy["hp"] = max(0, enemy["hp"] - damage)
                if is_crit:
                    combat["_max_crit"] = max(combat.get("_max_crit", 0), damage)
                crit_text = "【暴击！】" if is_crit else ""
                if elem_mult > 1:
                    combat["log"].append(f"{crit_text}你使出{skill_name}，五行克制！造成 {damage} 点伤害！")
                elif elem_mult < 1:
                    combat["log"].append(f"{crit_text}你使出{skill_name}，五行被克...造成 {damage} 点伤害。")
                else:
                    combat["log"].append(f"{crit_text}你使出{skill_name}，造成 {damage} 点伤害！")
                # 神通尝试施加状态效果（概率更高）
                status_logs = _try_inflict_status(combat, "enemy", ability["element"])
                for log in status_logs:
                    combat["log"].append(log)
            else:
                # 恢复型神通
                heal = abs(ability["base_damage"])
                player["hp"] = min(player["max_hp"], player["hp"] + heal)
                combat["log"].append(f"你使出{skill_name}，恢复 {heal} 点生命！")
                combat["_max_heal"] = max(combat.get("_max_heal", 0), heal)
        else:
            combat["log"].append(f"灵力不足，无法使用{skill_name}！（需要{ability['cost']}灵力）")
    elif action == "defend":
        player["defense"] = int(player["defense"] * 1.5)
        combat["log"].append("你摆出防御姿态，防御提升！")
    elif action == "flee":
        if random.random() < 0.5:
            combat["log"].append("你成功逃跑了！")
            combat["finished"] = True
            combat["victory"] = None
            return combat
        else:
            combat["log"].append("逃跑失败！")

    # 检查敌人是否死亡
    if enemy["hp"] <= 0:
        combat["log"].append(f"你击败了 {enemy['name']}！")
        combat["finished"] = True
        combat["victory"] = True
        return combat

    # 敌人行动
    if not enemy_skip:
        enemy_elem = Element(enemy["element"])
        # 敌人攻击玩家：取最不利的灵根倍率
        worst_mult = 1.0
        for pe in player_elems:
            m = get_element_multiplier(enemy_elem, Element(pe))
            worst_mult = max(worst_mult, m)
        elem_mult = worst_mult

        # 敌人暴怒机制：HP < 30% 时攻击 +50%
        enrage_mult = 1.0
        if enemy["hp"] < enemy["max_hp"] * 0.3:
            enrage_mult = 1.5
            if not combat.get("_enraged"):
                combat["_enraged"] = True
                combat["log"].append(f"【暴怒！】{enemy['name']}进入暴怒状态，攻击力大增！")

        # 敌人技能系统：30% 概率使用技能
        enemy_skills = enemy.get("skills", [])
        use_skill = enemy_skills and random.random() < 0.3
        if use_skill:
            skill_name_e = random.choice(enemy_skills)
            skill_dmg_mult = random.uniform(1.3, 1.8)
            damage = max(1, int((enemy["attack"] * skill_dmg_mult - player["defense"] * def_mult * 0.3) * elem_mult * random.uniform(0.85, 1.15) * enrage_mult))
            player["hp"] = max(0, player["hp"] - damage)
            combat["log"].append(f"{enemy['name']}使出【{skill_name_e}】，造成 {damage} 点伤害！")
            # 敌人技能尝试施加状态
            status_logs = _try_inflict_status(combat, "player", enemy_elem)
            for log in status_logs:
                combat["log"].append(log)
        else:
            damage = max(1, int((enemy["attack"] - player["defense"] * def_mult * 0.35) * elem_mult * random.uniform(0.75, 1.15) * enrage_mult))
            player["hp"] = max(0, player["hp"] - damage)
            combat["log"].append(f"{enemy['name']} 攻击你，造成 {damage} 点伤害！")
    else:
        combat["log"].append(f"{enemy['name']} 被控制，无法行动！")

    # 恢复防御（如果之前防御加成）
    # Use initial defense from combat creation as base
    if player["defense"] > combat.get("_base_defense", player["defense"]):
        player["defense"] = combat.get("_base_defense", player["defense"])

    # 检查玩家是否死亡
    if player["hp"] <= 0:
        combat["log"].append("你被击败了...")
        combat["finished"] = True
        combat["victory"] = False

    return combat

def _check_sword_progression(character: dict) -> str:
    """检查剑法是否应该升级，返回升级消息或None"""
    uses = character.get("sword_uses", 0)
    current_tier = character.get("sword_tier", 1)
    max_tier = len(SWORD_PROGRESSION)
    if current_tier >= max_tier:
        return None  # 已满级
    for i in range(max_tier - 1, -1, -1):
        name, threshold = SWORD_PROGRESSION[i]
        if uses >= threshold and i + 1 > current_tier:
            # 替换旧剑法
            old_idx = max(0, min(current_tier - 1, max_tier - 1))
            old_name = SWORD_PROGRESSION[old_idx][0]
            if old_name in character["skills"]:
                character["skills"].remove(old_name)
            if name not in character["skills"]:
                character["skills"].append(name)
            character["sword_tier"] = i + 1
            return f"剑法精进！{old_name} → {name}"
    return None

def apply_combat_result(character: dict, combat: dict) -> dict:
    result = {"exp": 0, "drops": {}, "messages": []}

    # 同步战斗统计
    max_crit = combat.get("_max_crit", 0)
    if max_crit > 0:
        character.setdefault("stats", {})["max_crit_damage"] = max(
            character.get("stats", {}).get("max_crit_damage", 0), max_crit)
    max_heal = combat.get("_max_heal", 0)
    if max_heal > 0:
        character.setdefault("stats", {})["max_heal_in_combat"] = max(
            character.get("stats", {}).get("max_heal_in_combat", 0), max_heal)

    # 同步剑法使用次数
    sword_delta = combat.get("_sword_uses_delta", 0)
    if sword_delta > 0:
        character["sword_uses"] = character.get("sword_uses", 0) + sword_delta
        prog_msg = _check_sword_progression(character)
        if prog_msg:
            result["messages"].append(prog_msg)
            result["sword_upgrade"] = prog_msg

    if combat["victory"] is True:
        enemy_name = combat["enemy"]["name"]
        if enemy_name in MONSTER_DB:
            monster = MONSTER_DB[enemy_name]
            exp = monster["exp"]
            character["exp"] += exp
            result["exp"] = exp
            result["messages"].append(f"获得 {exp} 修为")

            # 掉落物品（支持随机范围 [min, max]）
            for item, amount_range in monster["drops"].items():
                if isinstance(amount_range, list):
                    amount = random.randint(amount_range[0], amount_range[1])
                else:
                    amount = amount_range
                if amount > 0 and random.random() < 0.8:
                    character["inventory"][item] = character["inventory"].get(item, 0) + amount
                    result["drops"][item] = amount
                    result["messages"].append(f"获得 {item} x{amount}")

            character["kills"] += 1

            # 统计精英怪击杀
            ELITE_MONSTERS = ["五行灵蝶", "噬魂蝠王", "九尾妖狐", "上古石魔"]
            if combat.get("enemy", {}).get("name") in ELITE_MONSTERS:
                character.setdefault("stats", {})["elite_kills"] = character.get("stats", {}).get("elite_kills", 0) + 1

            # 恢复部分生命和灵力（仅怪物战斗）
            character["hp"] = min(character["max_hp"], character["hp"] + int(character["max_hp"] * 0.15))
            character["mp"] = min(character["max_mp"], character["mp"] + int(character["max_mp"] * 0.15))

    elif combat["victory"] is False:
        # 死亡惩罚
        character["hp"] = max(1, int(character["max_hp"] * 0.35))
        character["mp"] = max(0, int(character["max_mp"] * 0.25))
        loss = int(character["exp"] * 0.15)
        character["exp"] = max(0, character["exp"] - loss)
        result["messages"].append(f"修为损失 {loss}")

    return result

# ============================================================
# 探索系统
# ============================================================
def explore_region(character: dict) -> dict:
    region = REGIONS.get(character["location"])
    if not region:
        return {"type": "error", "message": "未知区域"}

    # 更新探索次数统计
    character.setdefault("stats", {})["explore_count"] = character.get("stats", {}).get("explore_count", 0) + 1

    # 记录到访区域
    visited = character.setdefault("stats", {}).setdefault("regions_visited", [])
    if character["location"] not in visited:
        visited.append(character["location"])

    # 探索链系统
    active_chain = character.get("active_chain")
    if active_chain and active_chain in EXPLORATION_CHAINS:
        chain = EXPLORATION_CHAINS[active_chain]
        chain_step = character.get("chain_step", 0)
        if chain_step < len(chain["steps"]):
            step = chain["steps"][chain_step]
            if step["region"] == character["location"]:
                # 在正确的区域，推进链
                character["chain_step"] = chain_step + 1
                if step["type"] == "combat":
                    return {"type": "combat", "enemy": step["enemy"], "message": step["desc"], "chain": active_chain}
                else:
                    result = {"type": "chain", "chain": active_chain, "step": chain_step + 1, "message": step["desc"]}
                    # 检查是否完成链
                    if chain_step + 1 >= len(chain["steps"]):
                        # 完成链，给予奖励
                        rewards = chain["rewards"]
                        character["exp"] += rewards.get("exp", 0)
                        if "item" in rewards:
                            character["inventory"][rewards["item"]] = character["inventory"].get(rewards["item"], 0) + 1
                            result["reward"] = {rewards["item"]: 1}
                        if "stones" in rewards:
                            character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + rewards["stones"]
                            result["reward"] = {"灵石": rewards["stones"]}
                        if "stat" in rewards:
                            for stat, val in rewards["stat"].items():
                                character["stats"][stat] = character["stats"].get(stat, 0) + val
                            result["stat_boost"] = rewards["stat"]
                        if "relation" in rewards:
                            for npc, val in rewards["relation"].items():
                                character["npc_relations"][npc] = character["npc_relations"].get(npc, 0) + val
                        if "ability" in rewards and rewards["ability"]:
                            char_elems = character_elements(character)
                            available = [name for name, a in ABILITY_DB.items()
                                        if a["element"].value in char_elems
                                        and name not in character.get("abilities", [])]
                            if available:
                                chosen = random.choice(available)
                                character.setdefault("abilities", []).append(chosen)
                                result["ability_found"] = chosen
                        result["message"] += f"\n\n【{active_chain}】任务完成！"
                        del character["active_chain"]
                        del character["chain_step"]
                    return result

    # 5%概率触发新探索链
    if random.random() < 0.05 and not active_chain and EXPLORATION_CHAINS:
        available_chains = [name for name, chain in EXPLORATION_CHAINS.items()
                          if chain["steps"][0]["region"] == character["location"]]
        if available_chains:
            chosen_chain = random.choice(available_chains)
            character["active_chain"] = chosen_chain
            character["chain_step"] = 0
            chain = EXPLORATION_CHAINS[chosen_chain]
            return {"type": "chain_start", "chain": chosen_chain, "message": f"【{chosen_chain}】{chain['steps'][0]['desc']}"}

    roll = random.random()

    # 稀有精英怪遭遇（5%概率，无视区域限制）
    ELITE_MONSTERS = ["五行灵蝶", "噬魂蝠王", "九尾妖狐", "上古石魔"]
    if roll < 0.05 and region["level"] >= 2:
        elite = random.choice(ELITE_MONSTERS)
        return {"type": "combat", "enemy": elite, "message": f"你遭遇了稀有精英 [{elite}]！",
                "is_elite": True}

    if roll < 0.35 and region["monsters"]:
        # 遭遇怪物
        monster = random.choice(region["monsters"])
        return {"type": "combat", "enemy": monster, "message": f"你遭遇了 {monster}！"}
    elif roll < 0.55 and region["events"]:
        # 触发事件
        event = random.choice(region["events"])
        result = {"type": "event", "event": event, "message": event}

        if event == "捡到灵石":
            amount = random.randint(10, 50)
            character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + amount
            result["reward"] = {"灵石": amount}
        elif event == "发现灵草":
            character["inventory"]["灵芝"] = character["inventory"].get("灵芝", 0) + 1
            result["reward"] = {"灵芝": 1}
        elif event == "遇到老者指路":
            gain = random.randint(20, 80)
            character["exp"] += gain
            result["reward"] = {"修为": gain}
        elif event == "发现秘境入口":
            result["message"] = "你发现了一处秘境入口，是否进入探索？"
            result["choice"] = True
        elif event == "遇到受伤修士":
            if random.random() < character["stats"]["魅力"] / 20:
                character["npc_relations"]["张铁柱"] = character["npc_relations"].get("张铁柱", 0) + 20
                result["message"] = "你救助了受伤的散修，他对你感激不已。"
            else:
                result["message"] = "受伤的修士对你充满戒备，匆匆离去。"
        elif event == "顿悟天道":
            character["stats"]["悟性"] += 1
            result["message"] = "你在青云镇静坐冥想，忽然顿悟天道，悟性提升！"
            result["stat_boost"] = {"悟性": 1}
        elif event == "竹林淬体":
            character["stats"]["根骨"] += 1
            result["message"] = "你在翠竹林中以竹为伴，日夜淬炼体魄，根骨提升！"
            result["stat_boost"] = {"根骨": 1}
        elif event == "地火炼心":
            character["stats"]["气运"] += 1
            result["message"] = "你在炎魔谷中承受地火灼烧，心志愈发坚定，气运提升！"
            result["stat_boost"] = {"气运": 1}
        elif event == "阴气感悟":
            if random.random() < 0.5:
                character["stats"]["悟性"] += 1
                result["message"] = "你在幽冥涧中感悟阴阳之道，悟性提升！"
                result["stat_boost"] = {"悟性": 1}
            else:
                character["stats"]["魅力"] += 1
                result["message"] = "你在幽冥涧中与亡灵交流，领悟了沟通之术，魅力提升！"
                result["stat_boost"] = {"魅力": 1}
        elif event == "机缘巧合":
            stat = random.choice(["根骨", "悟性", "气运", "魅力"])
            character["stats"][stat] += 1
            result["message"] = f"你在天机城中偶遇奇人，获得指点，{stat}提升！"
            result["stat_boost"] = {stat: 1}

        # ── 新增：青云镇事件 ──
        elif event == "遇到行商":
            items_for_sale = ["聚气丹", "回春丹", "铁剑", "布甲"]
            item = random.choice(items_for_sale)
            price = random.randint(5, 20)
            if character["inventory"].get("灵石", 0) >= price:
                character["inventory"]["灵石"] -= price
                character["inventory"][item] = character["inventory"].get(item, 0) + 1
                result["message"] = f"你遇到一位行商，花费 {price} 灵石购买了 {item}。"
                result["reward"] = {item: 1}
            else:
                gain = random.randint(5, 15)
                character["exp"] += gain
                result["message"] = f"你遇到一位行商，但灵石不足。行商见你有缘，指点了一番修炼心得，获得 {gain} 修为。"
        elif event == "发现古井":
            if random.random() < 0.6:
                heal = random.randint(20, 50)
                character["hp"] = min(character["max_hp"], character["hp"] + heal)
                character["mp"] = min(character["max_mp"], character["mp"] + heal // 2)
                result["message"] = f"你发现一口古井，井水甘甜清冽，饮后气血恢复 {heal}，灵力恢复 {heal // 2}。"
                result["reward"] = {"气血": heal, "灵力": heal // 2}
            else:
                character["stats"]["气运"] += 1
                result["message"] = "你发现一口古井，井底似乎藏着什么。你仔细查看，发现是一枚转运符，气运提升！"
                result["stat_boost"] = {"气运": 1}
        elif event == "村民求助":
            if random.random() < 0.7:
                reward_stones = random.randint(20, 60)
                character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + reward_stones
                character["npc_relations"]["李老头"] = character["npc_relations"].get("李老头", 0) + 15
                result["message"] = f"村民请你帮忙驱赶野兽，你顺利完成任务，获得 {reward_stones} 灵石，与李老头好感度提升。"
                result["reward"] = {"灵石": reward_stones}
            else:
                gain = random.randint(10, 30)
                character["exp"] += gain
                result["message"] = f"村民向你诉说修仙界的奇闻异事，你从中领悟了不少道理，获得 {gain} 修为。"

        # ── 新增：翠竹林事件 ──
        elif event == "竹林迷阵":
            if character["stats"]["悟性"] >= 8:
                gain = random.randint(30, 80)
                character["exp"] += gain
                character["stats"]["悟性"] += 1
                result["message"] = f"你误入竹林迷阵，凭借过人的悟性破阵而出，获得 {gain} 修为，悟性提升！"
                result["stat_boost"] = {"悟性": 1}
            else:
                loss = random.randint(5, 15)
                character["hp"] = max(1, character["hp"] - loss)
                result["message"] = f"你误入竹林迷阵，在阵中迷失方向，撞得遍体鳞伤，损失 {loss} 气血。"
        elif event == "灵泉沐浴":
            mp_gain = random.randint(10, 30)
            character["mp"] = min(character["max_mp"], character["mp"] + mp_gain)
            character["lifespan"] = character.get("lifespan", 0) + 5
            result["message"] = f"你发现一处灵泉，沐浴其中，灵力恢复 {mp_gain}，寿元增加 5 年。"
            result["reward"] = {"灵力": mp_gain, "寿元": 5}
        elif event == "遇到采药人":
            herbs = ["灵芝", "千年灵芝", "聚气丹"]
            herb = random.choice(herbs)
            character["inventory"][herb] = character["inventory"].get(herb, 0) + 1
            result["message"] = f"你遇到一位采药人，他赠予你一株 {herb}。"
            result["reward"] = {herb: 1}

        # ── 新增：炎魔谷事件 ──
        elif event == "熔岩洞穴":
            if character["stats"]["根骨"] >= 10:
                character["stats"]["根骨"] += 1
                stones = random.randint(80, 200)
                character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
                result["message"] = f"你深入熔岩洞穴，凭借强横的体魄抵御高温，发现 {stones} 灵石，根骨提升！"
                result["stat_boost"] = {"根骨": 1}
                result["reward"] = {"灵石": stones}
            else:
                damage = random.randint(20, 50)
                character["hp"] = max(1, character["hp"] - damage)
                result["message"] = f"你试图进入熔岩洞穴，但高温难耐，被灼伤损失 {damage} 气血。"
        elif event == "遇到火灵":
            if random.random() < 0.4:
                character["attack"] += 2
                result["message"] = "你遇到一只火灵，它感受到你的五行灵根，化为一道火焰融入你的攻击之中，攻击力 +2！"
                result["stat_boost"] = {"攻击": 2}
            else:
                damage = random.randint(15, 35)
                character["hp"] = max(1, character["hp"] - damage)
                result["message"] = f"你遇到一只暴躁的火灵，它向你喷出火焰，损失 {damage} 气血。"
        elif event == "火山爆发":
            damage = random.randint(30, 60)
            character["hp"] = max(1, character["hp"] - damage)
            gain = random.randint(50, 120)
            character["exp"] += gain
            result["message"] = f"炎魔谷火山爆发，你被波及损失 {damage} 气血，但在生死边缘领悟了天地法则，获得 {gain} 修为！"

        # ── 新增：幽冥涧事件 ──
        elif event == "幽冥试炼":
            if character["stats"]["气运"] >= 8:
                character["stats"]["魅力"] += 1
                stones = random.randint(100, 300)
                character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
                result["message"] = f"你通过了幽冥试炼的考验，获得 {stones} 灵石，魅力提升！"
                result["stat_boost"] = {"魅力": 1}
                result["reward"] = {"灵石": stones}
            else:
                mp_loss = random.randint(10, 30)
                character["mp"] = max(0, character["mp"] - mp_loss)
                result["message"] = f"幽冥试炼失败，你的灵力被吞噬 {mp_loss} 点。"
        elif event == "鬼市":
            items = ["回春丹", "千年灵芝", "天雷珠", "聚气丹"]
            item = random.choice(items)
            price = random.randint(30, 100)
            if character["inventory"].get("灵石", 0) >= price:
                character["inventory"]["灵石"] -= price
                character["inventory"][item] = character["inventory"].get(item, 0) + 1
                result["message"] = f"你在鬼市中花费 {price} 灵石购得 {item}。"
                result["reward"] = {item: 1}
            else:
                result["message"] = "你来到鬼市，但身上的灵石不足以购买任何东西，只能悻悻离去。"
        elif event == "遇到幽灵":
            if random.random() < 0.5:
                gain = random.randint(20, 60)
                character["exp"] += gain
                result["message"] = f"你遇到一只游荡的幽灵，它向你讲述了生前的修仙经验，获得 {gain} 修为。"
            else:
                character["lifespan"] = max(0, character.get("lifespan", 0) - 10)
                result["message"] = "幽灵向你扑来，你奋力抵挡，虽击退了它，但寿元被侵蚀了 10 年。"

        # ── 新增：天机城事件 ──
        elif event == "天机阁":
            gain = random.randint(50, 150)
            character["exp"] += gain
            character["stats"]["悟性"] += 1
            result["message"] = f"你进入天机阁，参悟天机秘卷，获得 {gain} 修为，悟性提升！"
            result["stat_boost"] = {"悟性": 1}
        elif event == "遇到神秘人":
            if random.random() < 0.3:
                char_elems = character_elements(character)
                available = [name for name, a in ABILITY_DB.items()
                            if a["element"].value in char_elems
                            and name not in character.get("abilities", [])]
                if available:
                    chosen = random.choice(available)
                    character.setdefault("abilities", []).append(chosen)
                    result["message"] = f"一位神秘人拦住你的去路，观察你片刻后，传授了你 {chosen} 神通！"
                    result["ability_found"] = chosen
                else:
                    stones = random.randint(100, 500)
                    character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
                    result["message"] = f"一位神秘人赠予你 {stones} 灵石，飘然而去。"
                    result["reward"] = {"灵石": stones}
            else:
                stones = random.randint(50, 200)
                character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
                result["message"] = f"一位神秘人与你论道片刻，临别赠予 {stones} 灵石。"
                result["reward"] = {"灵石": stones}
        elif event == "天降奇缘":
            stat = random.choice(["根骨", "悟性", "气运", "魅力"])
            boost = random.randint(1, 2)
            character["stats"][stat] += boost
            stones = random.randint(100, 400)
            character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
            result["message"] = f"天降奇缘！一道金光落入你手中，化为 {stones} 灵石，{stat} +{boost}！"
            result["stat_boost"] = {stat: boost}
            result["reward"] = {"灵石": stones}

        # ── 洞穴/遗迹事件：获得功法或技能 ──
        elif event in ("发现山洞", "竹林古洞", "古修士遗迹", "上古洞府"):
            tier_map = {"发现山洞": "黄级", "竹林古洞": "玄级", "古修士遗迹": "地级", "上古洞府": "天级"}
            target_tier = tier_map[event]
            char_elems = character_elements(character)

            # 从功法和技能中筛选匹配五行和等级的
            available_techs = [name for name, t in TECHNIQUE_DB.items()
                              if t["tier"] == target_tier and t["element"].value in char_elems
                              and name not in character.get("techniques", [])]
            available_skills = [name for name, s in SKILL_DB.items()
                               if not s.get("is_sword") and s.get("price", 0) > 0
                               and s["element"].value in char_elems
                               and name not in character.get("skills", [])]

            all_available = [(name, "technique") for name in available_techs] + [(name, "skill") for name in available_skills]

            if all_available:
                chosen_name, chosen_type = random.choice(all_available)
                if chosen_type == "technique":
                    character.setdefault("techniques", []).append(chosen_name)
                    tech = TECHNIQUE_DB[chosen_name]
                    result["message"] = f"你在{event}中发现了古修士留下的传承，领悟了{tech['tier']}功法【{chosen_name}】！"
                    result["technique_found"] = chosen_name
                else:
                    character.setdefault("skills", []).append(chosen_name)
                    skill = SKILL_DB[chosen_name]
                    result["message"] = f"你在{event}中发现了上古石碑，领悟了技能【{chosen_name}】！"
                    result["skill_found"] = chosen_name
            else:
                # 已全部学会，给灵石补偿
                amount = random.randint(50, 200) * region["level"]
                character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + amount
                result["message"] = f"你进入{event}，但里面的传承你已全部领悟，只发现了 {amount} 灵石。"
                result["reward"] = {"灵石": amount}

        return result
    elif roll < 0.7 and region["npc"]:
        # 遇到 NPC
        npc = random.choice(region["npc"])
        return {"type": "npc", "npc": npc, "message": f"你遇到了 {npc}（{NPC_DB[npc]['title']}）"}
    else:
        # 平静探索（含通用事件）
        gain = random.randint(5, 20)
        character["exp"] += gain

        # 20%概率触发通用事件
        if random.random() < 0.20 and UNIVERSAL_EVENTS:
            event = random.choice(UNIVERSAL_EVENTS)
            result = {"type": "event", "event": event, "message": event}

            if event == "灵石矿脉":
                amount = random.randint(30, 100) * region["level"]
                character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + amount
                result["message"] = f"你发现了一处灵石矿脉，挖掘获得 {amount} 灵石！"
                result["reward"] = {"灵石": amount}
            elif event == "天降陨石":
                damage = random.randint(10, 30)
                character["hp"] = max(1, character["hp"] - damage)
                gain_extra = random.randint(50, 150)
                character["exp"] += gain_extra
                result["message"] = f"天降陨石！你被波及损失 {damage} 气血，但陨石中蕴含灵气，获得 {gain_extra} 额外修为！"
            elif event == "修士切磋":
                gain_extra = random.randint(20, 60)
                character["exp"] += gain_extra
                character["stats"]["根骨"] = character["stats"].get("根骨", 0) + 1
                result["message"] = f"你遇到一位修士，切磋一番后获益良多，修为 +{gain_extra}，根骨 +1！"
                result["stat_boost"] = {"根骨": 1}
            elif event == "灵药园":
                herbs = random.sample(["灵芝", "千年灵芝", "聚气丹", "回春丹"], 2)
                for herb in herbs:
                    character["inventory"][herb] = character["inventory"].get(herb, 0) + 1
                result["message"] = f"你发现一处灵药园，采集到 {'、'.join(herbs)}！"
                result["reward"] = {h: 1 for h in herbs}
            elif event == "古传送阵":
                result["message"] = "你发现一座古传送阵，但似乎已经失效了..."
                gain_extra = random.randint(30, 80)
                character["exp"] += gain_extra
                result["message"] += f"你在传送阵旁感悟空间法则，获得 {gain_extra} 修为。"
            elif event == "神秘商人":
                items = ["聚气丹", "回春丹", "培元丹", "千年灵芝"]
                item = random.choice(items)
                character["inventory"][item] = character["inventory"].get(item, 0) + 1
                result["message"] = f"一位神秘商人出现，赠予你 {item} 后消失无踪。"
                result["reward"] = {item: 1}
            elif event == "天地异象":
                stat = random.choice(["根骨", "悟性", "气运", "魅力"])
                character["stats"][stat] = character["stats"].get(stat, 0) + 1
                result["message"] = f"天空出现异象，你静心感悟，{stat} +1！"
                result["stat_boost"] = {stat: 1}
            elif event == "灵气漩涡":
                mp_gain = random.randint(20, 50)
                character["mp"] = min(character["max_mp"], character["mp"] + mp_gain)
                result["message"] = f"你遇到一处灵气漩涡，吸收其中灵气，灵力恢复 {mp_gain}！"
                result["reward"] = {"灵力": mp_gain}
            elif event == "遗落宝箱":
                items = ["灵石", "灵芝", "铁矿石", "聚气丹"]
                item = random.choice(items)
                amount = random.randint(1, 3)
                character["inventory"][item] = character["inventory"].get(item, 0) + amount
                result["message"] = f"你发现一个遗落的宝箱，获得 {item} ×{amount}！"
                result["reward"] = {item: amount}
            elif event == "仙鹤指路":
                gain_extra = random.randint(40, 120)
                character["exp"] += gain_extra
                result["message"] = f"一只仙鹤飞来，引领你感悟天地大道，获得 {gain_extra} 修为！"
            elif event == "遗迹探秘":
                if character["stats"]["悟性"] >= 10:
                    gain_extra = random.randint(60, 180)
                    character["exp"] += gain_extra
                    character["stats"]["悟性"] += 1
                    result["message"] = f"你发现一处上古遗迹，凭借过人的悟性破解了禁制，获得 {gain_extra} 修为，悟性 +1！"
                    result["stat_boost"] = {"悟性": 1}
                else:
                    damage = random.randint(15, 40)
                    character["hp"] = max(1, character["hp"] - damage)
                    result["message"] = f"你发现一处上古遗迹，但禁制反噬，损失 {damage} 气血。"
            elif event == "灵兽相助":
                hp_gain = random.randint(30, 80)
                mp_gain = random.randint(20, 50)
                character["hp"] = min(character["max_hp"], character["hp"] + hp_gain)
                character["mp"] = min(character["max_mp"], character["mp"] + mp_gain)
                result["message"] = f"一只灵兽出现，为你疗伤，气血 +{hp_gain}，灵力 +{mp_gain}。"
                result["reward"] = {"气血": hp_gain, "灵力": mp_gain}
            elif event == "天劫降临":
                damage = random.randint(50, 100)
                character["hp"] = max(1, character["hp"] - damage)
                if random.random() < 0.4:
                    gain_extra = random.randint(100, 300)
                    character["exp"] += gain_extra
                    character["stats"]["根骨"] += 2
                    result["message"] = f"天劫降临！你被雷劫击中损失 {damage} 气血，但在生死边缘突破极限，获得 {gain_extra} 修为，根骨 +2！"
                    result["stat_boost"] = {"根骨": 2}
                else:
                    result["message"] = f"天劫降临！你被雷劫击中损失 {damage} 气血，勉强保住了性命。"
            elif event == "悟道石碑":
                stat = random.choice(["根骨", "悟性", "气运", "魅力"])
                boost = random.randint(1, 3)
                character["stats"][stat] += boost
                gain_extra = random.randint(30, 80)
                character["exp"] += gain_extra
                result["message"] = f"你发现一块悟道石碑，静坐感悟，{stat} +{boost}，修为 +{gain_extra}！"
                result["stat_boost"] = {stat: boost}
            elif event == "仙人遗府":
                if random.random() < 0.3:
                    items = ["千年灵芝", "破境丹", "天蚕宝衣"]
                    item = random.choice(items)
                    character["inventory"][item] = character["inventory"].get(item, 0) + 1
                    result["message"] = f"你发现一处仙人遗府，获得 {item}！"
                    result["reward"] = {item: 1}
                else:
                    stones = random.randint(200, 500)
                    character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
                    result["message"] = f"你发现一处仙人遗府，获得 {stones} 灵石！"
                    result["reward"] = {"灵石": stones}

            # ── 新增通用事件 ──
            elif event == "丹药奇遇":
                pills = ["聚气丹", "培元丹", "回春丹", "续命丹"]
                pill = random.choice(pills)
                amount = random.randint(1, 3)
                character["inventory"][pill] = character["inventory"].get(pill, 0) + amount
                result["message"] = f"你偶然发现一位炼丹师的遗物，获得 {pill}×{amount}！"
                result["reward"] = {pill: amount}
            elif event == "法器残片":
                gain_extra = random.randint(30, 80)
                character["exp"] += gain_extra
                character["attack"] += 1
                result["message"] = f"你捡到一块法器残片，从中领悟了攻击之道，修为 +{gain_extra}，攻击 +1！"
                result["stat_boost"] = {"攻击": 1}
            elif event == "灵脉觉醒":
                mp_gain = random.randint(20, 60)
                character["mp"] = min(character["max_mp"], character["mp"] + mp_gain)
                character["stats"]["悟性"] += 1
                result["message"] = f"你感应到地底灵脉的波动，灵力恢复 {mp_gain}，悟性 +1！"
                result["stat_boost"] = {"悟性": 1}
                result["reward"] = {"灵力": mp_gain}
            elif event == "心魔试炼":
                if random.random() < 0.5:
                    gain_extra = random.randint(50, 150)
                    character["exp"] += gain_extra
                    character["stats"]["根骨"] += 1
                    result["message"] = f"你陷入心魔幻境，凭借坚定意志破除心魔，修为 +{gain_extra}，根骨 +1！"
                    result["stat_boost"] = {"根骨": 1}
                else:
                    damage = random.randint(15, 40)
                    character["hp"] = max(1, character["hp"] - damage)
                    result["message"] = f"心魔侵袭，你勉力抵挡，损失 {damage} 气血，但心志更加坚定。"
            elif event == "天道酬勤":
                cultivate_count = character.get("stats", {}).get("cultivate_count", 0)
                if cultivate_count >= 50:
                    gain_extra = random.randint(100, 300)
                    character["exp"] += gain_extra
                    result["message"] = f"天道酬勤！你日复一日的修炼终于得到回报，获得 {gain_extra} 修为！"
                else:
                    gain_extra = random.randint(30, 80)
                    character["exp"] += gain_extra
                    result["message"] = f"天道酬勤，你的努力得到了些许回报，获得 {gain_extra} 修为。"

            # ── 灵泉沐浴 ──
            elif event == "灵泉沐浴":
                hp_gain = random.randint(30, 80)
                mp_gain = random.randint(20, 60)
                character["hp"] = min(character["max_hp"], character["hp"] + hp_gain)
                character["mp"] = min(character["max_mp"], character["mp"] + mp_gain)
                character["lifespan"] = character.get("lifespan", 100) + 5
                result["message"] = f"你发现一处灵泉，沐浴其中，气血 +{hp_gain}，灵力 +{mp_gain}，寿元 +5！"
                result["reward"] = {"气血": hp_gain, "灵力": mp_gain, "寿元": 5}

            # ── 仙果成熟 ──
            elif event == "仙果成熟":
                fruits = ["蟠桃", "人参果", "火枣", "仙杏"]
                fruit = random.choice(fruits)
                character["inventory"][fruit] = character["inventory"].get(fruit, 0) + 1
                gain_extra = random.randint(50, 150)
                character["exp"] += gain_extra
                result["message"] = f"你遇到一棵仙果树，上面结着一颗{fruit}，服用后获得 {gain_extra} 修为！"
                result["reward"] = {fruit: 1}

            # ── 剑冢探秘 ──
            elif event == "剑冢探秘":
                if random.random() < 0.4:
                    swords = ["青锋剑", "寒冰剑", "烈焰剑", "玄铁重剑"]
                    sword = random.choice(swords)
                    character["inventory"][sword] = character["inventory"].get(sword, 0) + 1
                    result["message"] = f"你进入剑冢，在万千残剑中发现了一柄{sword}！"
                    result["reward"] = {sword: 1}
                else:
                    gain_extra = random.randint(40, 100)
                    character["exp"] += gain_extra
                    character["attack"] = character.get("attack", 10) + 2
                    result["message"] = f"你在剑冢中感悟剑意，修为 +{gain_extra}，攻击 +2！"
                    result["stat_boost"] = {"攻击": 2}

            # ── 灵田丰收 ──
            elif event == "灵田丰收":
                herbs = random.sample(["灵芝", "千年灵芝", "何首乌", "雪莲", "龙涎草"], 3)
                for herb in herbs:
                    character["inventory"][herb] = character["inventory"].get(herb, 0) + 1
                result["message"] = f"你发现一片灵田大丰收，采集到 {'、'.join(herbs)}！"
                result["reward"] = {h: 1 for h in herbs}

            # ── 天降祥瑞 ──
            elif event == "天降祥瑞":
                stat = random.choice(["根骨", "悟性", "气运", "魅力"])
                boost = random.randint(2, 4)
                character["stats"][stat] += boost
                stones = random.randint(200, 600)
                character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
                result["message"] = f"天降祥瑞！五彩霞光笼罩你全身，{stat} +{boost}，获得 {stones} 灵石！"
                result["stat_boost"] = {stat: boost}
                result["reward"] = {"灵石": stones}

            # ── 修士论剑 ──
            elif event == "修士论剑":
                gain_extra = random.randint(30, 90)
                character["exp"] += gain_extra
                character["attack"] = character.get("attack", 10) + 1
                character["defense"] = character.get("defense", 5) + 1
                result["message"] = f"你参加了一场修士论剑大会，获益良多，修为 +{gain_extra}，攻击 +1，防御 +1！"
                result["stat_boost"] = {"攻击": 1, "防御": 1}

            # ── 丹炉爆炸 ──
            elif event == "丹炉爆炸":
                damage = random.randint(20, 50)
                character["hp"] = max(1, character["hp"] - damage)
                if random.random() < 0.3:
                    pills = ["破境丹", "金丹丹", "化神丹"]
                    pill = random.choice(pills)
                    character["inventory"][pill] = character["inventory"].get(pill, 0) + 1
                    result["message"] = f"丹炉爆炸！你被炸伤损失 {damage} 气血，但在废墟中发现了{pill}！"
                    result["reward"] = {pill: 1}
                else:
                    result["message"] = f"路过一处废弃丹炉时突然爆炸，你被炸伤损失 {damage} 气血。"

            # ── 灵兽产崽 ──
            elif event == "灵兽产崽":
                pets = ["灵狐幼崽", "仙鹤雏鸟", "迷你雷兽", "小火凤"]
                pet = random.choice(pets)
                gain_extra = random.randint(20, 60)
                character["exp"] += gain_extra
                character["stats"]["魅力"] += 1
                result["message"] = f"你目睹了一只灵兽产崽的神奇过程，感悟生命之道，修为 +{gain_extra}，魅力 +1！"
                result["stat_boost"] = {"魅力": 1}

            # ── 阵法破损 ──
            elif event == "阵法破损":
                if character["stats"]["悟性"] >= 15:
                    gain_extra = random.randint(60, 180)
                    character["exp"] += gain_extra
                    character["stats"]["悟性"] += 2
                    result["message"] = f"你发现一处破损的上古阵法，凭借高超悟性修复了它，修为 +{gain_extra}，悟性 +2！"
                    result["stat_boost"] = {"悟性": 2}
                else:
                    gain_extra = random.randint(20, 50)
                    character["exp"] += gain_extra
                    result["message"] = f"你发现一处破损的阵法，研究片刻后略有所悟，修为 +{gain_extra}。"

            # ── 天劫余波 ──
            elif event == "天劫余波":
                damage = random.randint(10, 30)
                character["hp"] = max(1, character["hp"] - damage)
                gain_extra = random.randint(40, 120)
                character["exp"] += gain_extra
                character["stats"]["根骨"] += 1
                result["message"] = f"天劫余波席卷而来，你被波及损失 {damage} 气血，但在劫力中感悟天道，修为 +{gain_extra}，根骨 +1！"
                result["stat_boost"] = {"根骨": 1}

            # ── 仙人指点 ──
            elif event == "仙人指点":
                gain_extra = random.randint(80, 200)
                character["exp"] += gain_extra
                stat = random.choice(["根骨", "悟性", "气运"])
                boost = random.randint(1, 3)
                character["stats"][stat] += boost
                result["message"] = f"一位仙人路过，指点你修炼迷津，修为 +{gain_extra}，{stat} +{boost}！"
                result["stat_boost"] = {stat: boost}

            # ── 魔修来袭 ──
            elif event == "魔修来袭":
                damage = random.randint(30, 70)
                character["hp"] = max(1, character["hp"] - damage)
                stones = random.randint(100, 300)
                character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
                result["message"] = f"一群魔修袭击了你！你奋力抵抗损失 {damage} 气血，但击退他们后获得 {stones} 灵石！"
                result["reward"] = {"灵石": stones}

            # ── 灵脉枯竭 ──
            elif event == "灵脉枯竭":
                mp_loss = random.randint(10, 30)
                character["mp"] = max(0, character["mp"] - mp_loss)
                gain_extra = random.randint(30, 80)
                character["exp"] += gain_extra
                result["message"] = f"你遇到一处枯竭的灵脉，灵力被吸收 {mp_loss}，但从中感悟灵力本质，修为 +{gain_extra}。"

            # ── 天材地宝 ──
            elif event == "天材地宝":
                treasures = ["天道碎片", "混沌精华", "凤凰羽毛", "龙鳞", "麒麟角"]
                treasure = random.choice(treasures)
                character["inventory"][treasure] = character["inventory"].get(treasure, 0) + 1
                result["message"] = f"你发现了天材地宝——{treasure}！这可是炼器的稀有材料！"
                result["reward"] = {treasure: 1}

            # ── 秘境入口 ──
            elif event == "秘境入口":
                if random.random() < 0.5:
                    gain_extra = random.randint(60, 150)
                    character["exp"] += gain_extra
                    items = ["千年灵芝", "破境丹", "聚灵珠"]
                    item = random.choice(items)
                    character["inventory"][item] = character["inventory"].get(item, 0) + 1
                    result["message"] = f"你进入了一处秘境，获得 {gain_extra} 修为和 {item}！"
                    result["reward"] = {item: 1}
                else:
                    damage = random.randint(20, 50)
                    character["hp"] = max(1, character["hp"] - damage)
                    result["message"] = f"秘境中危机四伏，你被守护兽击伤损失 {damage} 气血，仓皇逃出。"

            # ── 上古遗迹 ──
            elif event == "上古遗迹":
                gain_extra = random.randint(50, 150)
                character["exp"] += gain_extra
                stat = random.choice(["根骨", "悟性", "气运"])
                boost = random.randint(1, 2)
                character["stats"][stat] += boost
                result["message"] = f"你发现一处上古遗迹，从中领悟了远古大道，修为 +{gain_extra}，{stat} +{boost}！"
                result["stat_boost"] = {stat: boost}

            # ── 仙鹤报恩 ──
            elif event == "仙鹤报恩":
                items = ["仙鹤羽毛", "灵芝", "聚气丹"]
                item = random.choice(items)
                character["inventory"][item] = character["inventory"].get(item, 0) + 2
                character["stats"]["气运"] += 1
                result["message"] = f"一只仙鹤飞来报恩，赠予你 {item}×2，气运 +1！"
                result["reward"] = {item: 2}
                result["stat_boost"] = {"气运": 1}

            # ── 灵石雨 ──
            elif event == "灵石雨":
                stones = random.randint(200, 800)
                character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
                result["message"] = f"天降灵石雨！你疯狂收集，获得 {stones} 灵石！"
                result["reward"] = {"灵石": stones}

            # ── 心魔入侵 ──
            elif event == "心魔入侵":
                damage = random.randint(30, 60)
                character["hp"] = max(1, character["hp"] - damage)
                if character["stats"]["悟性"] >= 20:
                    gain_extra = random.randint(80, 200)
                    character["exp"] += gain_extra
                    character["stats"]["悟性"] += 2
                    result["message"] = f"心魔入侵！你凭借高深悟性化解危机，损失 {damage} 气血，但修为 +{gain_extra}，悟性 +2！"
                    result["stat_boost"] = {"悟性": 2}
                else:
                    result["message"] = f"心魔入侵！你勉力抵挡，损失 {damage} 气血，心神受损。"

            # ── 天道感应 ──
            elif event == "天道感应":
                gain_extra = random.randint(100, 300)
                character["exp"] += gain_extra
                character["stats"]["悟性"] += 3
                result["message"] = f"你感应到天道的意志，陷入顿悟状态，修为 +{gain_extra}，悟性 +3！"
                result["stat_boost"] = {"悟性": 3}

            # ── 灵气潮汐 ──
            elif event == "灵气潮汐":
                mp_gain = random.randint(50, 100)
                character["mp"] = min(character["max_mp"], character["mp"] + mp_gain)
                gain_extra = random.randint(30, 80)
                character["exp"] += gain_extra
                result["message"] = f"灵气潮汐涌来！你趁机修炼，灵力 +{mp_gain}，修为 +{gain_extra}！"
                result["reward"] = {"灵力": mp_gain}

            # ── 仙人渡劫 ──
            elif event == "仙人渡劫":
                gain_extra = random.randint(80, 200)
                character["exp"] += gain_extra
                character["stats"]["根骨"] += 2
                character["stats"]["悟性"] += 2
                result["message"] = f"你目睹了一位仙人渡劫飞升！感悟颇深，修为 +{gain_extra}，根骨 +2，悟性 +2！"
                result["stat_boost"] = {"根骨": 2, "悟性": 2}

            # ── 妖兽暴动 ──
            elif event == "妖兽暴动":
                damage = random.randint(40, 80)
                character["hp"] = max(1, character["hp"] - damage)
                if random.random() < 0.5:
                    items = ["妖丹", "兽皮", "兽骨"]
                    item = random.choice(items)
                    character["inventory"][item] = character["inventory"].get(item, 0) + 2
                    result["message"] = f"妖兽暴动！你被妖兽围攻损失 {damage} 气血，但斩杀妖兽获得 {item}×2！"
                    result["reward"] = {item: 2}
                else:
                    result["message"] = f"妖兽暴动！你被妖兽围攻损失 {damage} 气血，勉强逃脱。"

            # ── 灵脉喷涌 ──
            elif event == "灵脉喷涌":
                mp_gain = random.randint(40, 80)
                hp_gain = random.randint(30, 60)
                character["mp"] = min(character["max_mp"], character["mp"] + mp_gain)
                character["hp"] = min(character["max_hp"], character["hp"] + hp_gain)
                gain_extra = random.randint(20, 60)
                character["exp"] += gain_extra
                result["message"] = f"灵脉喷涌！灵气充沛，气血 +{hp_gain}，灵力 +{mp_gain}，修为 +{gain_extra}！"
                result["reward"] = {"气血": hp_gain, "灵力": mp_gain}

            # ── 天降异宝 ──
            elif event == "天降异宝":
                items = ["造化玉碟", "天道碎片", "混沌精华", "凤凰涅槃丹"]
                item = random.choice(items)
                character["inventory"][item] = character["inventory"].get(item, 0) + 1
                result["message"] = f"天降异宝！一件{item}从天而降，落入你手中！"
                result["reward"] = {item: 1}

            # ── 修士求助 ──
            elif event == "修士求助":
                if random.random() < 0.6:
                    stones = random.randint(50, 150)
                    character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
                    character["stats"]["魅力"] += 1
                    result["message"] = f"你帮助了一位受伤的修士，他赠予你 {stones} 灵石，魅力 +1！"
                    result["reward"] = {"灵石": stones}
                    result["stat_boost"] = {"魅力": 1}
                else:
                    gain_extra = random.randint(20, 50)
                    character["exp"] += gain_extra
                    result["message"] = f"你帮助了一位修士，他与你分享修炼心得，修为 +{gain_extra}。"

            # ── 灵兽异变 ──
            elif event == "灵兽异变":
                damage = random.randint(25, 55)
                character["hp"] = max(1, character["hp"] - damage)
                gain_extra = random.randint(50, 150)
                character["exp"] += gain_extra
                character["stats"]["根骨"] += 1
                result["message"] = f"一只灵兽突然异变攻击你！你击退它损失 {damage} 气血，但获得 {gain_extra} 修为，根骨 +1！"
                result["stat_boost"] = {"根骨": 1}

            # ── 阵法激活 ──
            elif event == "阵法激活":
                if character["stats"]["悟性"] >= 12:
                    gain_extra = random.randint(60, 180)
                    character["exp"] += gain_extra
                    character["stats"]["悟性"] += 2
                    result["message"] = f"你激活了一座上古阵法，阵法之力灌入体内，修为 +{gain_extra}，悟性 +2！"
                    result["stat_boost"] = {"悟性": 2}
                else:
                    damage = random.randint(15, 35)
                    character["hp"] = max(1, character["hp"] - damage)
                    result["message"] = f"你试图激活阵法但被反噬，损失 {damage} 气血。"

            # ── 丹药成灵 ──
            elif event == "丹药成灵":
                pills = ["聚气丹", "培元丹", "回春丹", "破境丹"]
                pill = random.choice(pills)
                amount = random.randint(2, 5)
                character["inventory"][pill] = character["inventory"].get(pill, 0) + amount
                result["message"] = f"你遇到一颗成精的丹药，将它收服后获得 {pill}×{amount}！"
                result["reward"] = {pill: amount}

            # ── 法器通灵 ──
            elif event == "法器通灵":
                character["attack"] = character.get("attack", 10) + 3
                character["defense"] = character.get("defense", 5) + 2
                gain_extra = random.randint(30, 80)
                character["exp"] += gain_extra
                result["message"] = f"你的法器突然通灵，威能大增！攻击 +3，防御 +2，修为 +{gain_extra}！"
                result["stat_boost"] = {"攻击": 3, "防御": 2}

            # ── 天地共鸣 ──
            elif event == "天地共鸣":
                gain_extra = random.randint(100, 250)
                character["exp"] += gain_extra
                for stat in ["根骨", "悟性", "气运", "魅力"]:
                    character["stats"][stat] += 1
                result["message"] = f"天地共鸣！你与天地合为一体，修为 +{gain_extra}，所有属性 +1！"
                result["stat_boost"] = {"根骨": 1, "悟性": 1, "气运": 1, "魅力": 1}

            # ── 混沌裂缝 ──
            elif event == "混沌裂缝":
                damage = random.randint(50, 100)
                character["hp"] = max(1, character["hp"] - damage)
                if random.random() < 0.3:
                    item = "混沌精华"
                    character["inventory"][item] = character["inventory"].get(item, 0) + 1
                    gain_extra = random.randint(100, 300)
                    character["exp"] += gain_extra
                    result["message"] = f"混沌裂缝吞噬了你！损失 {damage} 气血，但你在混沌中获得 {item} 和 {gain_extra} 修为！"
                    result["reward"] = {item: 1}
                else:
                    result["message"] = f"混沌裂缝出现！你被混沌之力侵蚀，损失 {damage} 气血。"

            # ── 时空紊乱 ──
            elif event == "时空紊乱":
                gain_extra = random.randint(50, 150)
                character["exp"] += gain_extra
                character["lifespan"] = character.get("lifespan", 100) - random.randint(5, 15)
                result["message"] = f"时空紊乱！你被卷入时空裂缝，获得 {gain_extra} 修为，但寿元减少了。"

            # ── 因果纠缠 ──
            elif event == "因果纠缠":
                stat = random.choice(["根骨", "悟性", "气运", "魅力"])
                boost = random.randint(1, 3)
                penalty_stat = random.choice(["根骨", "悟性", "气运", "魅力"])
                while penalty_stat == stat:
                    penalty_stat = random.choice(["根骨", "悟性", "气运", "魅力"])
                penalty = random.randint(1, 2)
                character["stats"][stat] += boost
                character["stats"][penalty_stat] = max(1, character["stats"][penalty_stat] - penalty)
                result["message"] = f"因果纠缠！{stat} +{boost}，但{penalty_stat} -{penalty}。"

            # ── 命运转折 ──
            elif event == "命运转折":
                if random.random() < 0.5:
                    gain_extra = random.randint(100, 300)
                    character["exp"] += gain_extra
                    stones = random.randint(200, 500)
                    character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
                    result["message"] = f"命运转折！你遇到了大机缘，修为 +{gain_extra}，灵石 +{stones}！"
                    result["reward"] = {"灵石": stones}
                else:
                    damage = random.randint(30, 70)
                    character["hp"] = max(1, character["hp"] - damage)
                    result["message"] = f"命运转折！你遭遇了劫难，损失 {damage} 气血。"

            # ── 灵根觉醒 ──
            elif event == "灵根觉醒":
                gain_extra = random.randint(60, 180)
                character["exp"] += gain_extra
                character["stats"]["根骨"] += 2
                character["stats"]["悟性"] += 2
                result["message"] = f"灵根觉醒！你的灵根品质提升，修为 +{gain_extra}，根骨 +2，悟性 +2！"
                result["stat_boost"] = {"根骨": 2, "悟性": 2}

            # ── 血脉返祖 ──
            elif event == "血脉返祖":
                gain_extra = random.randint(80, 200)
                character["exp"] += gain_extra
                for stat in ["根骨", "悟性"]:
                    character["stats"][stat] += 2
                character["attack"] = character.get("attack", 10) + 5
                character["max_hp"] = character.get("max_hp", 100) + 20
                result["message"] = f"血脉返祖！远古血脉觉醒，修为 +{gain_extra}，根骨 +2，悟性 +2，攻击 +5，气血上限 +20！"
                result["stat_boost"] = {"根骨": 2, "悟性": 2, "攻击": 5}

            # ── 悟道顿悟 ──
            elif event == "悟道顿悟":
                gain_extra = random.randint(100, 300)
                character["exp"] += gain_extra
                character["stats"]["悟性"] += 5
                result["message"] = f"悟道顿悟！你突然领悟了大道真谛，修为 +{gain_extra}，悟性 +5！"
                result["stat_boost"] = {"悟性": 5}

            # ── 心境突破 ──
            elif event == "心境突破":
                gain_extra = random.randint(80, 200)
                character["exp"] += gain_extra
                character["stats"]["魅力"] += 3
                character["stats"]["气运"] += 2
                character["lifespan"] = character.get("lifespan", 100) + 20
                result["message"] = f"心境突破！你的心境达到新的层次，修为 +{gain_extra}，魅力 +3，气运 +2，寿元 +20！"
                result["stat_boost"] = {"魅力": 3, "气运": 2}

            # ── 机缘巧合 ──
            elif event == "机缘巧合":
                roll = random.random()
                if roll < 0.25:
                    item = "造化玉碟"
                    character["inventory"][item] = character["inventory"].get(item, 0) + 1
                    result["message"] = f"机缘巧合！你获得了至宝 {item}！"
                    result["reward"] = {item: 1}
                elif roll < 0.5:
                    gain_extra = random.randint(200, 500)
                    character["exp"] += gain_extra
                    result["message"] = f"机缘巧合！你获得大机缘，修为 +{gain_extra}！"
                elif roll < 0.75:
                    stones = random.randint(500, 1500)
                    character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
                    result["message"] = f"机缘巧合！你发现了一处灵石宝藏，获得 {stones} 灵石！"
                    result["reward"] = {"灵石": stones}
                else:
                    for stat in ["根骨", "悟性", "气运", "魅力"]:
                        character["stats"][stat] += 3
                    result["message"] = f"机缘巧合！天道眷顾，所有属性 +3！"
                    result["stat_boost"] = {"根骨": 3, "悟性": 3, "气运": 3, "魅力": 3}

            return result

        result = {"type": "peaceful", "message": f"你在{character['location']}四处探索，感悟天地之道，获得 {gain} 修为"}

        # 5%概率领悟随机神通
        if random.random() < 0.05:
            char_elems = character_elements(character)
            available = [name for name, a in ABILITY_DB.items()
                        if a["element"].value in char_elems
                        and name not in character.get("abilities", [])]
            if available:
                chosen = random.choice(available)
                character.setdefault("abilities", []).append(chosen)
                ability = ABILITY_DB[chosen]
                result["message"] += f"\n\n冥冥之中，你感应到天道指引，顿悟了{ability['tier']}神通【{chosen}】！"
                result["ability_found"] = chosen

        return result

def handle_exploration_choice(character: dict, choice: str) -> dict:
    """处理探索中的选择"""
    if choice == "enter_secret_realm":
        # 进入秘境
        damage = random.randint(20, 50)
        character["hp"] = max(1, character["hp"] - damage)
        gain = random.randint(80, 200)
        character["exp"] += gain
        items = ["千年灵芝", "聚气丹", "回春丹"]
        item = random.choice(items)
        character["inventory"][item] = character["inventory"].get(item, 0) + 1
        return {
            "success": True,
            "message": f"你进入秘境探索，遭遇危险损失 {damage} 气血，但获得 {gain} 修为和 {item}！",
            "reward": {item: 1},
        }
    elif choice == "avoid_secret_realm":
        # 避开秘境
        gain = random.randint(10, 30)
        character["exp"] += gain
        return {
            "success": True,
            "message": f"你选择避开秘境，继续在周围探索，获得 {gain} 修为。",
        }
    elif choice == "help_wounded":
        # 帮助受伤修士
        if random.random() < 0.7:
            character["npc_relations"]["张铁柱"] = character["npc_relations"].get("张铁柱", 0) + 25
            stones = random.randint(30, 80)
            character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + stones
            return {
                "success": True,
                "message": f"你救助了受伤的修士，他赠予你 {stones} 灵石表示感谢，好感度大幅提升！",
                "reward": {"灵石": stones},
            }
        else:
            character["npc_relations"]["张铁柱"] = character["npc_relations"].get("张铁柱", 0) + 10
            return {
                "success": True,
                "message": "你救助了受伤的修士，他对你表示感谢，好感度提升。",
            }
    elif choice == "ignore_wounded":
        # 忽略受伤修士
        return {
            "success": True,
            "message": "你选择不理会受伤的修士，继续前行。",
        }
    return {"success": False, "message": "未知选择"}

# ============================================================
# NPC 交互
# ============================================================
def talk_to_npc(character: dict, npc_name: str) -> dict:
    if npc_name not in NPC_DB:
        return {"success": False, "message": "找不到此人"}

    npc = NPC_DB[npc_name]
    relation = character["npc_relations"].get(npc_name, 0)

    # 根据好感度选择对话
    dialogue_key = 0
    for key in sorted(npc["dialogue"].keys()):
        if relation >= key:
            dialogue_key = key

    dialogue = npc["dialogue"][dialogue_key]

    return {
        "success": True,
        "npc": npc_name,
        "title": npc["title"],
        "dialogue": dialogue,
        "relation": relation,
        "shop": npc["shop"],
        "technique_shop": npc.get("technique_shop", []),
        "skill_shop": npc.get("skill_shop", []),
    }

def buy_from_npc(character: dict, npc_name: str, item_name: str) -> dict:
    if npc_name not in NPC_DB:
        return {"success": False, "message": "找不到此人"}

    npc = NPC_DB[npc_name]
    if item_name not in npc["shop"]:
        return {"success": False, "message": f"{npc_name}不卖这个东西"}

    item_data = ITEM_DB.get(item_name, {})
    price = item_data.get("price", 10)

    if character["inventory"].get("灵石", 0) < price:
        return {"success": False, "message": f"灵石不足，需要 {price} 灵石"}

    character["inventory"]["灵石"] -= price
    character["inventory"][item_name] = character["inventory"].get(item_name, 0) + 1

    return {"success": True, "message": f"购买了 {item_name}，花费 {price} 灵石"}

# ============================================================
# 任务系统
# ============================================================
def get_npc_quests(character: dict, npc_name: str) -> list:
    """获取NPC的可用任务列表"""
    if npc_name not in NPC_DB:
        return []

    npc = NPC_DB[npc_name]
    quests = npc.get("quests", [])
    completed_quests = character.get("completed_quests", [])
    active_quests = character.get("active_quests", [])

    available = []
    for quest in quests:
        quest_id = f"{npc_name}_{quest['name']}"
        if quest_id not in completed_quests and quest_id not in [q.get("id") for q in active_quests]:
            available.append({
                "id": quest_id,
                "name": quest["name"],
                "desc": quest["desc"],
                "reward": quest["reward"],
            })
    return available

def accept_quest(character: dict, quest_id: str) -> dict:
    """接受任务"""
    # 解析quest_id获取NPC和任务名
    parts = quest_id.split("_", 1)
    if len(parts) != 2:
        return {"success": False, "message": "无效的任务ID"}

    npc_name, quest_name = parts
    if npc_name not in NPC_DB:
        return {"success": False, "message": "找不到NPC"}

    npc = NPC_DB[npc_name]
    quest = None
    for q in npc.get("quests", []):
        if q["name"] == quest_name:
            quest = q
            break

    if not quest:
        return {"success": False, "message": "找不到任务"}

    # 检查是否已完成
    if quest_id in character.get("completed_quests", []):
        return {"success": False, "message": "任务已完成"}

    # 检查是否已接受
    for q in character.get("active_quests", []):
        if q.get("id") == quest_id:
            return {"success": False, "message": "任务已接受"}

    # 添加到活跃任务
    active_quest = {
        "id": quest_id,
        "name": quest["name"],
        "desc": quest["desc"],
        "npc": npc_name,
        "progress": 0,
        "count": quest["count"],
        "reward": quest["reward"],
        "relation_boost": quest.get("relation_boost", 0),
    }

    # 设置任务目标类型
    if "target" in quest:
        active_quest["type"] = "collect"
        active_quest["target"] = quest["target"]
    elif "target_kill" in quest:
        active_quest["type"] = "kill"
        active_quest["target"] = quest["target_kill"]
    elif "target_explore" in quest:
        active_quest["type"] = "explore"
        active_quest["target"] = quest["target_explore"]
    elif "target_skill_use" in quest:
        active_quest["type"] = "skill_use"
        active_quest["target"] = quest["target_skill_use"]

    character.setdefault("active_quests", []).append(active_quest)
    return {"success": True, "message": f"接受了任务：{quest['name']}", "quest": active_quest}

def check_quest_progress(character: dict, event_type: str, target: str = None) -> list:
    """检查任务进度，返回完成的任务列表"""
    completed = []
    active_quests = character.get("active_quests", [])

    for quest in active_quests:
        if quest.get("type") == event_type:
            if event_type == "collect" and quest.get("target") == target:
                # 检查背包中的物品数量
                count = character.get("inventory", {}).get(target, 0)
                quest["progress"] = min(count, quest["count"])
            elif event_type == "kill" and quest.get("target") == target:
                quest["progress"] += 1
            elif event_type == "explore" and quest.get("target") == target:
                quest["progress"] += 1
            elif event_type == "skill_use":
                quest["progress"] += 1
            elif event_type == "cultivate":
                quest["progress"] += 1
            elif event_type == "breakthrough":
                quest["progress"] += 1

            # 检查是否完成
            if quest["progress"] >= quest["count"]:
                completed.append(quest)

    return completed

def complete_quest(character: dict, quest_id: str) -> dict:
    """完成任务并领取奖励"""
    active_quests = character.get("active_quests", [])
    quest = None
    quest_index = -1

    for i, q in enumerate(active_quests):
        if q.get("id") == quest_id:
            quest = q
            quest_index = i
            break

    if not quest:
        return {"success": False, "message": "找不到此任务"}

    if quest["progress"] < quest["count"]:
        return {"success": False, "message": f"任务未完成 ({quest['progress']}/{quest['count']})"}

    # 发放奖励
    for item, count in quest.get("reward", {}).items():
        if item == "灵石":
            character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + count
        elif item in ITEM_DB:
            character["inventory"][item] = character["inventory"].get(item, 0) + count
        elif item in SKILL_DB:
            character.setdefault("skills", []).append(item)
        elif item in TECHNIQUE_DB:
            character.setdefault("techniques", []).append(item)

    # 提升好感度
    npc_name = quest.get("npc")
    relation_boost = quest.get("relation_boost", 0)
    if npc_name and relation_boost:
        character["npc_relations"][npc_name] = character["npc_relations"].get(npc_name, 0) + relation_boost

    # 移动到已完成列表
    active_quests.pop(quest_index)
    character.setdefault("completed_quests", []).append(quest_id)

    # 检查NPC关系奖励
    reward_msg = ""
    if npc_name and npc_name in NPC_DB:
        npc = NPC_DB[npc_name]
        current_relation = character["npc_relations"].get(npc_name, 0)
        for threshold, reward in npc.get("relation_rewards", {}).items():
            if current_relation >= threshold:
                reward_key = f"{npc_name}_relation_{threshold}"
                if reward_key not in character.get("completed_quests", []):
                    if "item" in reward:
                        item = reward["item"]
                        character["inventory"][item] = character["inventory"].get(item, 0) + 1
                        reward_msg += f"\n{reward.get('message', '')}"
                    elif "skill" in reward:
                        skill = reward["skill"]
                        if skill not in character.get("skills", []):
                            character.setdefault("skills", []).append(skill)
                            reward_msg += f"\n{reward.get('message', '')}"
                    elif "technique" in reward:
                        tech = reward["technique"]
                        if tech not in character.get("techniques", []):
                            character.setdefault("techniques", []).append(tech)
                            reward_msg += f"\n{reward.get('message', '')}"
                    character.setdefault("completed_quests", []).append(reward_key)

    return {
        "success": True,
        "message": f"完成任务：{quest['name']}！获得奖励。{reward_msg}",
        "reward": quest.get("reward", {}),
    }

# ============================================================
# 成就系统
# ============================================================
ACHIEVEMENT_DB = {
    "初入修仙": {"desc": "创建角色", "condition": "create", "reward": {"灵石": 50}},
    "修炼入门": {"desc": "修炼10次", "condition": "cultivate_10", "reward": {"聚气丹": 3}},
    "修炼达人": {"desc": "修炼100次", "condition": "cultivate_100", "reward": {"灵石": 500}},
    "小有成就": {"desc": "突破到筑基期", "condition": "realm_2", "reward": {"灵石": 200}},
    "金丹大道": {"desc": "突破到结丹期", "condition": "realm_3", "reward": {"灵石": 800}},
    "元婴老怪": {"desc": "突破到元婴期", "condition": "realm_4", "reward": {"灵石": 2000}},
    "化神之尊": {"desc": "突破到化神期", "condition": "realm_5", "reward": {"灵石": 5000}},
    "五行大师": {"desc": "拥有3种灵根", "condition": "elements_3", "reward": {"灵石": 300}},
    "五行齐聚": {"desc": "拥有全部5种灵根", "condition": "elements_5", "reward": {"灵石": 1000}},
    "战斗新手": {"desc": "赢得第一场战斗", "condition": "kill_1", "reward": {"回春丹": 2}},
    "十战十胜": {"desc": "赢得10场战斗", "condition": "kill_10", "reward": {"灵石": 150}},
    "百战老手": {"desc": "赢得100场战斗", "condition": "kill_100", "reward": {"灵石": 1000}},
    "千人斩": {"desc": "赢得500场战斗", "condition": "kill_500", "reward": {"化神丹": 2}},
    "探索先锋": {"desc": "探索50次", "condition": "explore_50", "reward": {"千年灵芝": 2}},
    "探索大师": {"desc": "探索200次", "condition": "explore_200", "reward": {"灵石": 1500}},
    "社交达人": {"desc": "与所有NPC好感度达到60", "condition": "all_npc_60", "reward": {"元婴丹": 1}},
    "至交好友": {"desc": "与任意NPC好感度达到100", "condition": "npc_100", "reward": {"灵石": 600}},
    "收藏家": {"desc": "学会10个技能", "condition": "skills_10", "reward": {"灵石": 500}},
    "功法大师": {"desc": "学会5个功法", "condition": "techniques_5", "reward": {"灵石": 800}},
    "神通广大": {"desc": "学会3个神通", "condition": "abilities_3", "reward": {"灵石": 1200}},
    "富甲一方": {"desc": "拥有10000灵石", "condition": "stones_10000", "reward": {"化神丹": 1}},
    "长生不老": {"desc": "寿元超过500年", "condition": "lifespan_500", "reward": {"千年灵芝": 5}},
    "博学者": {"desc": "图鉴收录10种怪物", "condition": "bestiary_10", "reward": {"灵石": 400}},
    "遍历山河": {"desc": "到访所有区域", "condition": "all_regions", "reward": {"天材地宝": 2}},
    "暴击之王": {"desc": "单次暴击造成200以上伤害", "condition": "crit_200", "reward": {"灵石": 300}},
    "不死之身": {"desc": "单场战斗中回复超过100生命", "condition": "heal_100", "reward": {"回春丹": 5}},
    "精英猎手": {"desc": "击败稀有精英怪物", "condition": "elite_kill", "reward": {"灵石": 800, "天材地宝": 1}},
    "炼丹大师": {"desc": "合成10次", "condition": "craft_10", "reward": {"灵石": 500, "千年灵芝": 3}},
    "装备收藏": {"desc": "拥有3件仙品装备", "condition": "legendary_3", "reward": {"灵石": 1500}},
    "转世重修": {"desc": "完成一次转世重生", "condition": "rebirth_1", "reward": {"灵石": 2000, "天材地宝": 3}},
    "天机城主": {"desc": "与天机老人好感度达到100", "condition": "tianji_100", "reward": {"灵石": 1000, "化神丹": 1}},
    "全图鉴": {"desc": "收录所有怪物", "condition": "bestiary_all", "reward": {"灵石": 3000, "天材地宝": 5}},
    "五行炼器": {"desc": "合成5件法器", "condition": "craft_weapon_5", "reward": {"灵石": 800, "玄铁矿": 5}},

    # ── 高阶境界成就 ──
    "炼虚修士": {"desc": "突破到炼虚期", "condition": "realm_6", "reward": {"灵石": 20000}},
    "合体大能": {"desc": "突破到合体期", "condition": "realm_7", "reward": {"灵石": 50000}},
    "大乘圣者": {"desc": "突破到大乘期", "condition": "realm_8", "reward": {"灵石": 100000}},
    "渡劫仙人": {"desc": "突破到渡劫期", "condition": "realm_9", "reward": {"灵石": 200000}},
    "飞升成仙": {"desc": "突破到飞升期", "condition": "realm_10", "reward": {"灵石": 500000}},
    # ── 战斗成就 ──
    "万人敌": {"desc": "赢得1000场战斗", "condition": "kill_1000", "reward": {"灵石": 50000}},
    "不败传说": {"desc": "赢得5000场战斗", "condition": "kill_5000", "reward": {"灵石": 200000}},
    # ── 探索成就 ──
    "秘境猎人": {"desc": "探索500次", "condition": "explore_500", "reward": {"灵石": 8000}},
    "遍历仙界": {"desc": "到访所有12个区域", "condition": "all_regions_12", "reward": {"灵石": 10000, "天道碎片": 2}},
    # ── 炼丹成就 ──
    "炼丹宗师": {"desc": "合成50次", "condition": "craft_50", "reward": {"灵石": 8000, "天材地宝": 3}},
    "法器宗师": {"desc": "合成10件法器", "condition": "craft_weapon_10", "reward": {"灵石": 15000, "仙器碎片": 2}},
    # ── 社交成就 ──
    "万人迷": {"desc": "与所有NPC好感度达到100", "condition": "all_npc_100", "reward": {"灵石": 20000, "天材地宝": 5}},
    # ── 特殊成就 ──
    "剑道通神": {"desc": "剑法达到出神入化", "condition": "sword_5", "reward": {"灵石": 10000, "仙器碎片": 3}},
    "万法归一": {"desc": "学会30个技能", "condition": "skills_30", "reward": {"灵石": 50000, "天道碎片": 3}},
    "功法大全": {"desc": "学会15个功法", "condition": "techniques_15", "reward": {"灵石": 50000, "天道碎片": 3}},
    "神通广大": {"desc": "学会15个神通", "condition": "abilities_15", "reward": {"灵石": 50000, "天道碎片": 3}},
    "百万富翁": {"desc": "拥有100万灵石", "condition": "stones_1000000", "reward": {"灵石": 100000, "混沌精华": 1}},
    "寿与天齐": {"desc": "寿元超过10000年", "condition": "lifespan_10000", "reward": {"灵石": 50000, "天道碎片": 5}},
    "万寿无疆": {"desc": "寿元超过100000年", "condition": "lifespan_100000", "reward": {"灵石": 500000, "造化玉碟": 1}},
    "混沌之主": {"desc": "击败混沌魔神", "condition": "kill_chaos", "reward": {"灵石": 100000, "混沌精华": 3}},
    "天道之子": {"desc": "击败天道化身", "condition": "kill_tiandao", "reward": {"灵石": 200000, "造化玉碟": 2}},
}

def check_achievements(character: dict) -> list:
    """检查并解锁成就"""
    new_achievements = []
    completed = character.get("achievements", [])

    for ach_id, ach in ACHIEVEMENT_DB.items():
        if ach_id in completed:
            continue

        unlocked = False
        condition = ach["condition"]

        if condition == "create":
            unlocked = True
        elif condition == "cultivate_10":
            unlocked = character.get("stats", {}).get("cultivate_count", 0) >= 10
        elif condition == "cultivate_100":
            unlocked = character.get("stats", {}).get("cultivate_count", 0) >= 100
        elif condition == "realm_2":
            realm = character.get("realm", "")
            unlocked = realm in ["筑基", "ZHUJI"] or character.get("realm_level", 0) >= 2
        elif condition == "realm_3":
            realm = character.get("realm", "")
            unlocked = realm in ["结丹", "JIEDAN"] or character.get("realm_level", 0) >= 3
        elif condition == "realm_4":
            realm = character.get("realm", "")
            unlocked = realm in ["元婴", "YUANYING"] or character.get("realm_level", 0) >= 4
        elif condition == "realm_5":
            realm = character.get("realm", "")
            unlocked = realm in ["化神", "HUASHEN"] or character.get("realm_level", 0) >= 5
        elif condition == "elements_3":
            unlocked = len(character.get("element", [])) >= 3
        elif condition == "elements_5":
            unlocked = len(character.get("element", [])) >= 5
        elif condition == "kill_1":
            unlocked = character.get("kills", 0) >= 1
        elif condition == "kill_10":
            unlocked = character.get("kills", 0) >= 10
        elif condition == "kill_100":
            unlocked = character.get("kills", 0) >= 100
        elif condition == "kill_500":
            unlocked = character.get("kills", 0) >= 500
        elif condition == "explore_50":
            unlocked = character.get("stats", {}).get("explore_count", 0) >= 50
        elif condition == "explore_200":
            unlocked = character.get("stats", {}).get("explore_count", 0) >= 200
        elif condition == "all_npc_60":
            all_npcs = ["李老头", "赵灵儿", "张铁柱", "白骨夫人", "天机老人"]
            unlocked = all(character.get("npc_relations", {}).get(npc, 0) >= 60 for npc in all_npcs)
        elif condition == "npc_100":
            unlocked = any(v >= 100 for v in character.get("npc_relations", {}).values())
        elif condition == "skills_10":
            unlocked = len(character.get("skills", [])) >= 10
        elif condition == "techniques_5":
            unlocked = len(character.get("techniques", [])) >= 5
        elif condition == "abilities_3":
            unlocked = len(character.get("abilities", [])) >= 3
        elif condition == "stones_10000":
            unlocked = character.get("inventory", {}).get("灵石", 0) >= 10000
        elif condition == "lifespan_500":
            unlocked = character.get("lifespan", 0) >= 500
        elif condition == "bestiary_10":
            unlocked = len(character.get("stats", {}).get("monsters_encountered", [])) >= 10
        elif condition == "all_regions":
            visited = character.get("stats", {}).get("regions_visited", [])
            unlocked = len(visited) >= 5
        elif condition == "crit_200":
            unlocked = character.get("stats", {}).get("max_crit_damage", 0) >= 200
        elif condition == "heal_100":
            unlocked = character.get("stats", {}).get("max_heal_in_combat", 0) >= 100
        elif condition == "elite_kill":
            unlocked = character.get("stats", {}).get("elite_kills", 0) >= 1
        elif condition == "craft_10":
            unlocked = character.get("stats", {}).get("craft_count", 0) >= 10
        elif condition == "legendary_3":
            legendary_count = 0
            for item_name in character.get("inventory", {}).keys():
                if ITEM_DB.get(item_name, {}).get("rarity") == "仙品" and ITEM_DB.get(item_name, {}).get("type") in ("weapon", "armor"):
                    legendary_count += 1
            equipped = character.get("equipped", {})
            for slot_item in equipped.values():
                if slot_item and ITEM_DB.get(slot_item, {}).get("rarity") == "仙品":
                    legendary_count += 1
            unlocked = legendary_count >= 3
        elif condition == "rebirth_1":
            unlocked = character.get("stats", {}).get("rebirth_count", 0) >= 1
        elif condition == "tianji_100":
            unlocked = character.get("npc_relations", {}).get("天机老人", 0) >= 100
        elif condition == "bestiary_all":
            unlocked = len(character.get("stats", {}).get("monsters_encountered", [])) >= len(MONSTER_DB)
        elif condition == "craft_weapon_5":
            unlocked = character.get("stats", {}).get("craft_weapon_count", 0) >= 5
        elif condition == "craft_20":
            unlocked = character.get("stats", {}).get("craft_count", 0) >= 20

        if unlocked:
            new_achievements.append(ach_id)
            character.setdefault("achievements", []).append(ach_id)

            # 发放奖励
            for item, count in ach.get("reward", {}).items():
                if item == "灵石":
                    character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + count
                elif item in ITEM_DB:
                    character["inventory"][item] = character["inventory"].get(item, 0) + count

    return new_achievements

def get_achievements(character: dict) -> list:
    """获取所有成就状态"""
    completed = character.get("achievements", [])
    result = []
    for ach_id, ach in ACHIEVEMENT_DB.items():
        result.append({
            "id": ach_id,
            "desc": ach["desc"],
            "completed": ach_id in completed,
            "reward": ach.get("reward", {}),
        })
    return result

# ============================================================
# 功法系统
# ============================================================
def learn_technique(character: dict, tech_name: str) -> dict:
    if tech_name not in TECHNIQUE_DB:
        return {"success": False, "message": "未知功法"}

    tech = TECHNIQUE_DB[tech_name]

    # 检查五行灵根
    if tech["element"].value not in character_elements(character):
        return {"success": False, "message": f"灵根不符！{tech_name}需要{tech['element'].value}灵根"}

    # 检查是否已学会
    if tech_name in character.get("techniques", []):
        return {"success": False, "message": f"你已经学会了{tech_name}"}

    character.setdefault("techniques", []).append(tech_name)
    return {"success": True, "message": f"领悟了{tech['tier']}功法【{tech_name}】！{tech['desc']}"}

def buy_technique(character: dict, npc_name: str, tech_name: str) -> dict:
    if npc_name not in NPC_DB:
        return {"success": False, "message": "找不到此人"}

    npc = NPC_DB[npc_name]
    if tech_name not in npc.get("technique_shop", []):
        return {"success": False, "message": f"{npc_name}不卖这个功法"}

    if tech_name not in TECHNIQUE_DB:
        return {"success": False, "message": "未知功法"}

    tech = TECHNIQUE_DB[tech_name]
    price = tech["price"]
    if price <= 0:
        return {"success": False, "message": "此功法不可购买"}

    # 检查五行灵根
    if tech["element"].value not in character_elements(character):
        return {"success": False, "message": f"灵根不符！{tech_name}需要{tech['element'].value}灵根"}

    # 检查是否已学会
    if tech_name in character.get("techniques", []):
        return {"success": False, "message": f"你已经学会了{tech_name}"}

    if character["inventory"].get("灵石", 0) < price:
        return {"success": False, "message": f"灵石不足，需要 {price} 灵石"}

    character["inventory"]["灵石"] -= price
    character.setdefault("techniques", []).append(tech_name)
    return {"success": True, "message": f"购买并领悟了{tech['tier']}功法【{tech_name}】，花费 {price} 灵石"}

# ============================================================
# 神通系统
# ============================================================
def learn_ability(character: dict, ability_name: str) -> dict:
    if ability_name not in ABILITY_DB:
        return {"success": False, "message": "未知神通"}

    ability = ABILITY_DB[ability_name]

    # 检查五行灵根
    if ability["element"].value not in character_elements(character):
        return {"success": False, "message": f"灵根不符！{ability_name}需要{ability['element'].value}灵根"}

    # 检查是否已学会
    if ability_name in character.get("abilities", []):
        return {"success": False, "message": f"你已经学会了{ability_name}"}

    character.setdefault("abilities", []).append(ability_name)
    return {"success": True, "message": f"领悟了{ability['tier']}神通【{ability_name}】！{ability['desc']}"}

def buy_skill(character: dict, npc_name: str, skill_name: str) -> dict:
    if npc_name not in NPC_DB:
        return {"success": False, "message": "找不到此人"}

    npc = NPC_DB[npc_name]
    if skill_name not in npc.get("skill_shop", []):
        return {"success": False, "message": f"{npc_name}不卖这个技能"}

    if skill_name not in SKILL_DB:
        return {"success": False, "message": "未知技能"}

    skill = SKILL_DB[skill_name]
    price = skill.get("price", 0)
    if price <= 0:
        return {"success": False, "message": "此技能不可购买"}

    # 检查五行灵根
    if skill["element"].value not in character_elements(character):
        return {"success": False, "message": f"灵根不符！{skill_name}需要{skill['element'].value}灵根"}

    # 检查是否已学会
    if skill_name in character.get("skills", []):
        return {"success": False, "message": f"你已经学会了{skill_name}"}

    if character["inventory"].get("灵石", 0) < price:
        return {"success": False, "message": f"灵石不足，需要 {price} 灵石"}

    character["inventory"]["灵石"] -= price
    character.setdefault("skills", []).append(skill_name)
    return {"success": True, "message": f"购买了技能【{skill_name}】，花费 {price} 灵石"}

# ============================================================
# 物品使用
# ============================================================
def use_item(character: dict, item_name: str) -> dict:
    if item_name not in character["inventory"] or character["inventory"][item_name] <= 0:
        return {"success": False, "message": f"你没有{item_name}"}

    item_data = ITEM_DB.get(item_name, {})
    if not item_data:
        return {"success": False, "message": "未知物品"}

    if item_data["type"] == "consumable":
        character["inventory"][item_name] -= 1
        if character["inventory"][item_name] <= 0:
            del character["inventory"][item_name]

        if item_data["effect"] == "cultivation":
            character["exp"] += item_data["value"]
            return {"success": True, "message": f"使用{item_name}，增加 {item_data['value']} 修为"}
        elif item_data["effect"] == "heal":
            heal = item_data["value"]
            old_hp = character["hp"]
            character["hp"] = min(character["max_hp"], character["hp"] + heal)
            actual = character["hp"] - old_hp
            return {"success": True, "message": f"使用{item_name}，恢复 {actual} 点生命"}
        elif item_data["effect"] == "lifespan":
            character["lifespan"] = character.get("lifespan", 0) + item_data["value"]
            return {"success": True, "message": f"使用{item_name}，寿元增加 {item_data['value']} 年"}
        elif item_data["effect"] == "breakthrough":
            character.setdefault("temp_buffs", {})["breakthrough_rate"] = \
                character.get("temp_buffs", {}).get("breakthrough_rate", 0) + item_data["value"]
            return {"success": True, "message": f"使用{item_name}，下次突破成功率 +{item_data['value']}%"}

    elif item_data["type"] in ("weapon", "armor"):
        slot = "weapon" if item_data["type"] == "weapon" else "armor"
        old_item = character["equipped"].get(slot)
        if old_item:
            old_value = ITEM_DB.get(old_item, {}).get("value", 0)
            if item_data["effect"] == "attack":
                character["attack"] -= old_value
                character["attack"] += item_data["value"]
            elif item_data["effect"] == "defense":
                character["defense"] -= old_value
                character["defense"] += item_data["value"]
        character["equipped"][slot] = item_name
        return {"success": True, "message": f"装备了{item_name}"}

    return {"success": False, "message": "无法使用该物品"}

# ============================================================
# 移动系统
# ============================================================
def move_to_region(character: dict, region_name: str) -> dict:
    if region_name not in REGIONS:
        return {"success": False, "message": "未知区域"}

    region = REGIONS[region_name]
    # 检查等级要求
    realm_index = REALM_ORDER.index(Realm(character["realm"]))
    if realm_index + 1 < region["level"]:
        return {"success": False, "message": f"修为不足，需要至少达到{REALM_ORDER[region['level']-1].value}才能前往"}

    character["location"] = region_name
    return {"success": True, "message": f"你来到了{region_name}", "region": region}

# ============================================================
# 休息系统
# ============================================================
def rest(character: dict) -> dict:
    heal_hp = int(character["max_hp"] * 0.3)
    heal_mp = int(character["max_mp"] * 0.5)
    old_hp = character["hp"]
    old_mp = character["mp"]
    character["hp"] = min(character["max_hp"], character["hp"] + heal_hp)
    character["mp"] = min(character["max_mp"], character["mp"] + heal_mp)
    character["age"] += 1
    character["lifespan"] -= 1

    return {
        "hp_restored": character["hp"] - old_hp,
        "mp_restored": character["mp"] - old_mp,
        "message": f"休息片刻，恢复了 {character['hp'] - old_hp} 生命和 {character['mp'] - old_mp} 灵力",
    }

# ============================================================
# 状态查询
# ============================================================
def get_character_summary(character: dict) -> dict:
    realm = Realm(character["realm"])

    # 计算功法加成
    tech_bonuses = {"hp_pct": 0, "mp_pct": 0, "atk_pct": 0, "def_pct": 0}
    for tech_name in character.get("techniques", []):
        if tech_name in TECHNIQUE_DB:
            t = TECHNIQUE_DB[tech_name]
            tech_bonuses["hp_pct"] += t["hp_pct"]
            tech_bonuses["mp_pct"] += t["mp_pct"]
            tech_bonuses["atk_pct"] += t["atk_pct"]
            tech_bonuses["def_pct"] += t["def_pct"]

    # 灵根被动加成
    elems = character_elements(character)
    elem_bonuses = compute_element_bonuses(elems)

    return {
        "name": character["name"],
        "element": elems,
        "realm_full": get_realm_full_name(realm, character["stage"]),
        "exp": character["exp"],
        "exp_to_next": character["exp_to_next"],
        "exp_percent": round(character["exp"] / max(1, character["exp_to_next"]) * 100, 1),
        "hp": character["hp"],
        "max_hp": character["max_hp"],
        "mp": character["mp"],
        "max_mp": character["max_mp"],
        "attack": character["attack"],
        "defense": character["defense"],
        "lifespan": character["lifespan"],
        "age": character["age"],
        "stats": character["stats"],
        "location": character["location"],
        "kills": character["kills"],
        "inventory_count": sum(v for v in character["inventory"].values() if isinstance(v, int)),
        "techniques": character.get("techniques", []),
        "abilities": character.get("abilities", []),
        "skills": character.get("skills", []),
        "tech_bonuses": tech_bonuses,
        "elem_bonuses": elem_bonuses,
        "sword_uses": character.get("sword_uses", 0),
        "sword_tier": character.get("sword_tier", 1),
    }

# ============================================================
# 转世重生系统
# ============================================================
def rebirth(character: dict) -> dict:
    """转世重生：保留部分加成，重新开始"""
    realm = character.get("realm", "练气")
    realm_level = character.get("realm_level", 1)

    # 最低要求：筑基期以上才能转世
    if realm_level < 2:
        return {"success": False, "message": "需达到筑基期以上方可转世重生！"}

    # 计算转世点数（基于境界、成就、击杀等）
    rebirth_points = 0
    rebirth_points += realm_level * 10  # 境界奖励
    rebirth_points += len(character.get("achievements", [])) * 3  # 成就奖励
    rebirth_points += character.get("kills", 0) // 10  # 战斗奖励
    rebirth_points += character.get("stats", {}).get("explore_count", 0) // 20  # 探索奖励

    # 保留的加成
    bonuses = {
        "rebirth_points": rebirth_points,
        "hp_bonus": rebirth_points * 2,
        "mp_bonus": rebirth_points,
        "atk_bonus": rebirth_points // 3,
        "def_bonus": rebirth_points // 4,
        "exp_bonus_pct": min(50, rebirth_points),  # 最高50%经验加成
        "lifespan_bonus": rebirth_points * 5,
    }

    # 保留成就
    achievements = character.get("achievements", [])
    # 保留图鉴
    monsters_encountered = character.get("stats", {}).get("monsters_encountered", [])
    # 保留NPC关系（减半）
    npc_relations = {k: v // 2 for k, v in character.get("npc_relations", {}).items()}

    # 获取灵根
    elements = character.get("element", ["金"])
    if isinstance(elements, str):
        elements = [elements]

    # 重置角色
    new_stats = _roll_stats()
    # 转世加成：每10点转世点数+1到随机属性
    bonus_stats = rebirth_points // 10
    for _ in range(bonus_stats):
        stat = random.choice(["根骨", "悟性", "气运", "魅力"])
        new_stats[stat] += 1

    elem_bonuses = compute_element_bonuses(elements)
    base_hp = 100 + bonuses["hp_bonus"]
    base_mp = 50 + bonuses["mp_bonus"]
    base_atk = 10 + new_stats["根骨"] + bonuses["atk_bonus"]
    base_def = 5 + new_stats["根骨"] // 2 + bonuses["def_bonus"]

    new_character = {
        "name": character["name"],
        "element": elements,
        "realm": "练气",
        "realm_level": 1,
        "stage": 0,
        "hp": int(base_hp * (1 + elem_bonuses.get("hp_pct", 0) / 100)),
        "max_hp": int(base_hp * (1 + elem_bonuses.get("hp_pct", 0) / 100)),
        "mp": int(base_mp * (1 + elem_bonuses.get("mp_pct", 0) / 100)),
        "max_mp": int(base_mp * (1 + elem_bonuses.get("mp_pct", 0) / 100)),
        "attack": int(base_atk * (1 + elem_bonuses.get("atk_pct", 0) / 100)),
        "defense": int(base_def * (1 + elem_bonuses.get("def_pct", 0) / 100)),
        "exp": 0,
        "exp_to_next": 100,
        "lifespan": 150 + bonuses["lifespan_bonus"],
        "spirit_stones": 0,
        "inventory": {"灵石": rebirth_points * 10},
        "skills": ["基础剑法"],
        "techniques": [],
        "abilities": [],
        "equipped": {"weapon": "无", "armor": "无"},
        "location": "青云镇",
        "relation": {},
        "npc_relations": npc_relations,
        "tutorial_step": 0,
        "tutorial_done": True,
        "base_hp": base_hp,
        "base_mp": base_mp,
        "base_attack": base_atk,
        "base_defense": base_def,
        "last_cultivate_time": time.time(),
        "sword_uses": 0,
        "sword_tier": 1,
        "kills": 0,
        "age": 16,
        "stats": {
            "根骨": new_stats["根骨"],
            "悟性": new_stats["悟性"],
            "气运": new_stats["气运"],
            "魅力": new_stats["魅力"],
            "cultivate_count": 0,
            "explore_count": 0,
            "monsters_encountered": monsters_encountered,
            "regions_visited": [],
            "rebirth_count": character.get("stats", {}).get("rebirth_count", 0) + 1,
            "total_rebirth_points": character.get("stats", {}).get("total_rebirth_points", 0) + rebirth_points,
            "exp_bonus_pct": bonuses["exp_bonus_pct"],
        },
        "active_quests": [],
        "completed_quests": [],
        "achievements": achievements,
    }

    return {
        "success": True,
        "character": new_character,
        "rebirth_points": rebirth_points,
        "bonuses": bonuses,
        "message": f"转世重生成功！获得 {rebirth_points} 转世点数，保留 {len(achievements)} 个成就。",
    }


# ============================================================
# 宗门系统
# ============================================================
SECT_DB = {
    "天剑宗": {
        "desc": "以剑道闻名天下的宗门",
        "element": Element.METAL,
        "bonus": {"atk_pct": 10, "crit_pct": 5},
        "skills": ["天剑诀", "万剑归宗"],
        "levels": [{"name": "外门弟子", "contribution": 0}, {"name": "内门弟子", "contribution": 500},
                   {"name": "核心弟子", "contribution": 2000}, {"name": "长老", "contribution": 10000}],
    },
    "青木门": {
        "desc": "精通木属性法术的宗门",
        "element": Element.WOOD,
        "bonus": {"hp_pct": 10, "mp_pct": 5},
        "skills": ["万木归春", "生命之树"],
        "levels": [{"name": "外门弟子", "contribution": 0}, {"name": "内门弟子", "contribution": 500},
                   {"name": "核心弟子", "contribution": 2000}, {"name": "长老", "contribution": 10000}],
    },
    "玄水宫": {
        "desc": "掌控水之力的神秘宗门",
        "element": Element.WATER,
        "bonus": {"mp_pct": 15, "def_pct": 5},
        "skills": ["北冥神功", "沧海桑田"],
        "levels": [{"name": "外门弟子", "contribution": 0}, {"name": "内门弟子", "contribution": 500},
                   {"name": "核心弟子", "contribution": 2000}, {"name": "长老", "contribution": 10000}],
    },
    "烈焰门": {
        "desc": "以火属性法术著称的宗门",
        "element": Element.FIRE,
        "bonus": {"atk_pct": 8, "hp_pct": 5},
        "skills": ["天火焚世", "焚天大道"],
        "levels": [{"name": "外门弟子", "contribution": 0}, {"name": "内门弟子", "contribution": 500},
                   {"name": "核心弟子", "contribution": 2000}, {"name": "长老", "contribution": 10000}],
    },
    "厚土宗": {
        "desc": "防御无敌的土属性宗门",
        "element": Element.EARTH,
        "bonus": {"def_pct": 15, "hp_pct": 5},
        "skills": ["山河社稷", "混沌之盾"],
        "levels": [{"name": "外门弟子", "contribution": 0}, {"name": "内门弟子", "contribution": 500},
                   {"name": "核心弟子", "contribution": 2000}, {"name": "长老", "contribution": 10000}],
    },
}

SECT_TASKS = [
    {"name": "宗门巡逻", "desc": "在宗门周围巡逻，击败入侵者", "type": "kill", "count": 3, "reward": {"contribution": 50, "灵石": 200}},
    {"name": "采集灵草", "desc": "为宗门采集灵草", "type": "collect", "target": "灵芝", "count": 5, "reward": {"contribution": 30, "灵石": 100}},
    {"name": "宗门试炼", "desc": "完成宗门试炼", "type": "explore", "count": 3, "reward": {"contribution": 80, "灵石": 300}},
    {"name": "宗门大比", "desc": "在宗门大比中获胜", "type": "kill", "count": 5, "reward": {"contribution": 150, "灵石": 500}},
    {"name": "宗门建设", "desc": "捐献灵石建设宗门", "type": "donate", "count": 1000, "reward": {"contribution": 100}},
]


def join_sect(character: dict, sect_name: str) -> dict:
    if sect_name not in SECT_DB:
        return {"success": False, "message": "未知宗门"}
    if character.get("sect"):
        return {"success": False, "message": f"你已是{character['sect']}弟子，需先退出当前宗门"}
    character["sect"] = sect_name
    character["sect_contribution"] = 0
    character["sect_rank"] = "外门弟子"
    return {"success": True, "message": f"成功加入{sect_name}！"}


def leave_sect(character: dict) -> dict:
    if not character.get("sect"):
        return {"success": False, "message": "你尚未加入任何宗门"}
    old_sect = character["sect"]
    character["sect"] = None
    character["sect_contribution"] = 0
    character["sect_rank"] = None
    return {"success": True, "message": f"已退出{old_sect}"}


def get_sect_info(character: dict) -> dict:
    sect = character.get("sect")
    if not sect or sect not in SECT_DB:
        return {"success": False, "message": "你尚未加入任何宗门"}
    data = SECT_DB[sect]
    contrib = character.get("sect_contribution", 0)
    rank = "外门弟子"
    for level in reversed(data["levels"]):
        if contrib >= level["contribution"]:
            rank = level["name"]
            break
    character["sect_rank"] = rank
    return {"success": True, "sect": sect, "data": data, "contribution": contrib, "rank": rank}


# ============================================================
# 灵宠系统
# ============================================================
PET_DB = {
    "小灵狐": {"element": Element.FIRE, "base_hp": 50, "base_atk": 15, "base_def": 8, "skill": "狐火",
               "desc": "可爱的灵狐，火属性", "catch_rate": 0.5},
    "灵龟": {"element": Element.WATER, "base_hp": 80, "base_atk": 8, "base_def": 20, "skill": "水盾",
             "desc": "防御型灵宠，水属性", "catch_rate": 0.4},
    "雷鹰": {"element": Element.FIRE, "base_hp": 40, "base_atk": 25, "base_def": 5, "skill": "雷击",
             "desc": "攻击型灵宠，雷属性", "catch_rate": 0.3},
    "木灵": {"element": Element.WOOD, "base_hp": 60, "base_atk": 12, "base_def": 12, "skill": "治愈",
             "desc": "辅助型灵宠，木属性", "catch_rate": 0.45},
    "土龙": {"element": Element.EARTH, "base_hp": 70, "base_atk": 18, "base_def": 15, "skill": "地裂",
             "desc": "均衡型灵宠，土属性", "catch_rate": 0.35},
    "金翅大鹏": {"element": Element.METAL, "base_hp": 45, "base_atk": 30, "base_def": 10, "skill": "金翅斩",
                "desc": "极速灵宠，金属性", "catch_rate": 0.2},
    "九尾妖狐": {"element": Element.FIRE, "base_hp": 100, "base_atk": 35, "base_def": 20, "skill": "妖火",
                 "desc": "传说灵宠，火属性", "catch_rate": 0.1},
    "玄武": {"element": Element.WATER, "base_hp": 150, "base_atk": 20, "base_def": 40, "skill": "玄武盾",
             "desc": "神兽灵宠，水属性", "catch_rate": 0.05},
}


def catch_pet(character: dict, pet_name: str) -> dict:
    if pet_name not in PET_DB:
        return {"success": False, "message": "未知灵宠"}
    if len(character.get("pets", [])) >= 3:
        return {"success": False, "message": "最多携带3只灵宠"}
    pet_data = PET_DB[pet_name]
    luck = character.get("stats", {}).get("气运", 5) / 100
    if random.random() < pet_data["catch_rate"] + luck:
        pet = {
            "name": pet_name, "level": 1, "exp": 0,
            "hp": pet_data["base_hp"], "attack": pet_data["base_atk"], "defense": pet_data["base_def"],
            "element": pet_data["element"].value if isinstance(pet_data["element"], Element) else pet_data["element"],
            "skill": pet_data["skill"], "loyalty": 50,
        }
        character.setdefault("pets", []).append(pet)
        return {"success": True, "message": f"成功捕获{pet_name}！", "pet": pet}
    return {"success": False, "message": f"{pet_name}逃脱了！"}


def feed_pet(character: dict, pet_index: int, item_name: str) -> dict:
    pets = character.get("pets", [])
    if pet_index >= len(pets):
        return {"success": False, "message": "灵宠不存在"}
    pet = pets[pet_index]
    if item_name not in character.get("inventory", {}):
        return {"success": False, "message": f"你没有{item_name}"}
    character["inventory"][item_name] -= 1
    if character["inventory"][item_name] <= 0:
        del character["inventory"][item_name]
    pet["loyalty"] = min(100, pet.get("loyalty", 50) + 10)
    pet["hp"] += 5
    pet["attack"] += 1
    pet["defense"] += 1
    return {"success": True, "message": f"喂食{pet['name']}成功！忠诚度+10"}


def evolve_pet(character: dict, pet_index: int) -> dict:
    pets = character.get("pets", [])
    if pet_index >= len(pets):
        return {"success": False, "message": "灵宠不存在"}
    pet = pets[pet_index]
    if pet.get("level", 1) < 20:
        return {"success": False, "message": "灵宠等级不足20级"}
    if pet.get("loyalty", 0) < 80:
        return {"success": False, "message": "灵宠忠诚度不足80"}
    pet["hp"] = int(pet["hp"] * 1.5)
    pet["attack"] = int(pet["attack"] * 1.5)
    pet["defense"] = int(pet["defense"] * 1.5)
    pet["level"] = 1
    pet["evolved"] = True
    return {"success": True, "message": f"{pet['name']}进化成功！属性大幅提升！"}


# ============================================================
# 秘境副本系统
# ============================================================
DUNGEON_DB = {
    "翠竹秘境": {"level": 2, "floors": 3, "enemies": ["竹精", "蜂群", "树妖"], "boss": "五行灵蝶",
                "rewards": {"灵石": [200, 500], "千年灵芝": [1, 3]}},
    "炎魔秘境": {"level": 3, "floors": 5, "enemies": ["火焰妖", "熔岩蜥蜴", "岩魔"], "boss": "九尾妖狐",
                "rewards": {"灵石": [500, 1500], "天雷珠": [1, 3]}},
    "幽冥秘境": {"level": 4, "floors": 5, "enemies": ["怨灵", "幽魂", "冰霜巨狼"], "boss": "蛟龙",
                "rewards": {"灵石": [800, 2500], "魂晶": [2, 5]}},
    "天机秘境": {"level": 5, "floors": 7, "enemies": ["天机傀儡", "机关兽", "傀儡将军"], "boss": "天机傀儡",
                "rewards": {"灵石": [1500, 5000], "天机碎片": [2, 5]}},
    "混沌秘境": {"level": 8, "floors": 10, "enemies": ["混沌兽", "虚空行者", "混沌魔神"], "boss": "灭世天魔",
                "rewards": {"灵石": [5000, 20000], "混沌精华": [1, 3]}},
}


def enter_dungeon(character: dict, dungeon_name: str) -> dict:
    if dungeon_name not in DUNGEON_DB:
        return {"success": False, "message": "未知秘境"}
    dungeon = DUNGEON_DB[dungeon_name]
    realm_idx = REALM_ORDER.index(Realm(character.get("realm", "练气"))) if character.get("realm") in [r.value for r in Realm] else 0
    if realm_idx + 1 < dungeon["level"]:
        return {"success": False, "message": f"修为不足，需要至少{dungeon['level']}级境界"}
    character["dungeon"] = {"name": dungeon_name, "floor": 1, "max_floors": dungeon["floors"]}
    return {"success": True, "message": f"进入{dungeon_name}第1层！", "dungeon": character["dungeon"]}


def dungeon_battle(character: dict) -> dict:
    if not character.get("dungeon"):
        return {"success": False, "message": "你不在任何秘境中"}
    dungeon_name = character["dungeon"]["name"]
    dungeon = DUNGEON_DB[dungeon_name]
    floor = character["dungeon"]["floor"]
    if floor > dungeon["floors"]:
        enemy = dungeon["boss"]
        msg = f"你来到了{dungeon_name}最深处，BOSS {enemy}出现了！"
    else:
        enemy = random.choice(dungeon["enemies"])
        msg = f"第{floor}层遭遇{enemy}！"
    return {"success": True, "message": msg, "enemy": enemy, "floor": floor, "is_boss": floor > dungeon["floors"]}


def dungeon_next_floor(character: dict) -> dict:
    if not character.get("dungeon"):
        return {"success": False, "message": "你不在任何秘境中"}
    character["dungeon"]["floor"] += 1
    dungeon_name = character["dungeon"]["name"]
    dungeon = DUNGEON_DB[dungeon_name]
    floor = character["dungeon"]["floor"]
    if floor > dungeon["floors"]:
        return {"success": True, "message": f"你来到了{dungeon_name}最深处！准备迎战BOSS！", "is_boss": True}
    return {"success": True, "message": f"进入第{floor}层", "is_boss": False}


def dungeon_reward(character: dict) -> dict:
    if not character.get("dungeon"):
        return {"success": False, "message": "你不在任何秘境中"}
    dungeon_name = character["dungeon"]["name"]
    dungeon = DUNGEON_DB[dungeon_name]
    rewards = {}
    for item, (lo, hi) in dungeon["rewards"].items():
        amount = random.randint(lo, hi)
        character.setdefault("inventory", {})[item] = character.get("inventory", {}).get(item, 0) + amount
        rewards[item] = amount
    character.pop("dungeon", None)
    return {"success": True, "message": f"通关{dungeon_name}！获得奖励！", "rewards": rewards}


# ============================================================
# 世界BOSS系统
# ============================================================
WORLD_BOSS_DB = {
    "天魔降世": {"hp": 50000, "attack": 200, "defense": 100, "element": Element.FIRE,
                "rewards": {"灵石": [5000, 20000], "天道碎片": [1, 3]}, "desc": "天魔降临人间，生灵涂炭"},
    "混沌之主": {"hp": 100000, "attack": 300, "defense": 150, "element": Element.EARTH,
                "rewards": {"灵石": [10000, 50000], "混沌精华": [1, 3]}, "desc": "混沌之主苏醒，天地变色"},
    "天道化身": {"hp": 200000, "attack": 500, "defense": 250, "element": Element.METAL,
                "rewards": {"灵石": [20000, 100000], "造化玉碟": [1, 2]}, "desc": "天道化身降临，考验众生"},
}


def get_world_boss() -> dict:
    boss_name = random.choice(list(WORLD_BOSS_DB.keys()))
    boss = WORLD_BOSS_DB[boss_name].copy()
    boss["name"] = boss_name
    boss["current_hp"] = boss["hp"]
    if hasattr(boss.get("element"), "value"):
        boss["element"] = boss["element"].value
    return boss


def attack_world_boss(character: dict, boss: dict) -> dict:
    char_atk = character.get("attack", 10)
    boss_def = boss.get("defense", 0)
    damage = max(1, char_atk - boss_def // 2 + random.randint(-5, 10))
    boss["current_hp"] = max(0, boss["current_hp"] - damage)
    if boss["current_hp"] <= 0:
        rewards = {}
        for item, (lo, hi) in boss["rewards"].items():
            amount = random.randint(lo, hi)
            character.setdefault("inventory", {})[item] = character.get("inventory", {}).get(item, 0) + amount
            rewards[item] = amount
        return {"success": True, "message": f"击败了{boss['name']}！", "damage": damage, "rewards": rewards, "defeated": True}
    return {"success": True, "message": f"对{boss['name']}造成{damage}点伤害！剩余HP: {boss['current_hp']}/{boss['hp']}",
            "damage": damage, "defeated": False}


# ============================================================
# 装备强化系统
# ============================================================
ENHANCE_DB = {
    "强化": {"success_rate": [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05],
             "bonus_per_level": 0.1, "cost": [100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 51200]},
    "附灵": {"success_rate": 0.5, "bonus": 0.2, "cost": 5000},
    "镶嵌": {"slots": 3, "cost": 2000},
}

GEM_DB = {
    "攻击宝石": {"effect": "attack", "value": 10, "desc": "攻击+10"},
    "防御宝石": {"effect": "defense", "value": 10, "desc": "防御+10"},
    "生命宝石": {"effect": "hp", "value": 50, "desc": "生命+50"},
    "灵力宝石": {"effect": "mp", "value": 30, "desc": "灵力+30"},
    "暴击宝石": {"effect": "crit", "value": 5, "desc": "暴击率+5%"},
}


def enhance_equipment(character: dict, item_name: str) -> dict:
    if item_name not in character.get("inventory", {}):
        return {"success": False, "message": f"你没有{item_name}"}
    item_data = ITEM_DB.get(item_name)
    if not item_data or item_data.get("type") not in ("weapon", "armor"):
        return {"success": False, "message": "只能强化武器和防具"}
    enhance_level = character.get("enhance", {}).get(item_name, 0)
    if enhance_level >= 10:
        return {"success": False, "message": "已达到最高强化等级"}
    cost = ENHANCE_DB["强化"]["cost"][enhance_level]
    if character.get("inventory", {}).get("灵石", 0) < cost:
        return {"success": False, "message": f"灵石不足，需要{cost}"}
    character["inventory"]["灵石"] -= cost
    rate = ENHANCE_DB["强化"]["success_rate"][enhance_level]
    if random.random() < rate:
        character.setdefault("enhance", {})[item_name] = enhance_level + 1
        bonus = ENHANCE_DB["强化"]["bonus_per_level"]
        return {"success": True, "message": f"{item_name}强化到+{enhance_level + 1}成功！属性提升{int(bonus * 100)}%",
                "level": enhance_level + 1}
    return {"success": False, "message": f"{item_name}强化失败..."}


def embed_gem(character: dict, item_name: str, gem_name: str) -> dict:
    if item_name not in character.get("inventory", {}):
        return {"success": False, "message": f"你没有{item_name}"}
    if gem_name not in character.get("inventory", {}):
        return {"success": False, "message": f"你没有{gem_name}"}
    if gem_name not in GEM_DB:
        return {"success": False, "message": "未知宝石"}
    gems_on_item = character.get("gems", {}).get(item_name, [])
    if len(gems_on_item) >= ENHANCE_DB["镶嵌"]["slots"]:
        return {"success": False, "message": "镶嵌孔已满"}
    character["inventory"][gem_name] -= 1
    if character["inventory"][gem_name] <= 0:
        del character["inventory"][gem_name]
    character.setdefault("gems", {}).setdefault(item_name, []).append(gem_name)
    gem_data = GEM_DB[gem_name]
    return {"success": True, "message": f"在{item_name}上镶嵌{gem_name}成功！{gem_data['desc']}"}


# ============================================================
# 丹道精通系统
# ============================================================
ALCHEMY_MASTERY = {
    "levels": [
        {"name": "炼丹新手", "exp_required": 0, "bonus": 0},
        {"name": "炼丹学徒", "exp_required": 50, "bonus": 0.05},
        {"name": "炼丹师", "exp_required": 200, "bonus": 0.10},
        {"name": "炼丹大师", "exp_required": 500, "bonus": 0.15},
        {"name": "炼丹宗师", "exp_required": 1000, "bonus": 0.20},
        {"name": "丹道圣手", "exp_required": 2000, "bonus": 0.30},
    ],
    "poison_threshold": 5,
    "poison_effects": {"轻度丹毒": {"atk_pct": -5, "desc": "攻击-5%"},
                       "中度丹毒": {"atk_pct": -10, "def_pct": -5, "desc": "攻击-10%，防御-5%"},
                       "重度丹毒": {"atk_pct": -20, "def_pct": -10, "hp_pct": -10, "desc": "全属性下降"}},
}


def get_alchemy_level(character: dict) -> dict:
    exp = character.get("alchemy_exp", 0)
    level = ALCHEMY_MASTERY["levels"][0]
    for lv in reversed(ALCHEMY_MASTERY["levels"]):
        if exp >= lv["exp_required"]:
            level = lv
            break
    return {"name": level["name"], "bonus": level["bonus"], "exp": exp}


def advanced_craft(character: dict, recipe_name: str) -> dict:
    result = craft_item(character, recipe_name)
    if result["success"]:
        character["alchemy_exp"] = character.get("alchemy_exp", 0) + 10
        alchemy = get_alchemy_level(character)
        if random.random() < alchemy["bonus"]:
            extra = result.get("count", 1)
            character["inventory"][result["item"]] = character["inventory"].get(result["item"], 0) + extra
            result["message"] += f" 炼丹精通触发！额外获得{extra}个！"
        pill_count = character.get("pill_count", 0) + 1
        character["pill_count"] = pill_count
        if pill_count % ALCHEMY_MASTERY["poison_threshold"] == 0:
            poison_level = min(3, pill_count // ALCHEMY_MASTERY["poison_threshold"])
            poison_names = list(ALCHEMY_MASTERY["poison_effects"].keys())
            if poison_level <= len(poison_names):
                character["poison"] = poison_names[poison_level - 1]
                result["message"] += f" 警告：丹毒积累！当前状态：{poison_names[poison_level - 1]}"
    return result


def detoxify(character: dict) -> dict:
    if not character.get("poison"):
        return {"success": False, "message": "你没有丹毒"}
    cost = 500
    if character.get("inventory", {}).get("灵石", 0) < cost:
        return {"success": False, "message": f"灵石不足，需要{cost}"}
    character["inventory"]["灵石"] -= cost
    character.pop("poison", None)
    character["pill_count"] = 0
    return {"success": True, "message": "丹毒清除成功！"}


# ============================================================
# 拍卖行系统
# ============================================================
AUCTION_HOUSE = {
    "refresh_items": [
        {"name": "聚气丹", "price": 35, "stock": 5},
        {"name": "回春丹", "price": 25, "stock": 5},
        {"name": "灵芝", "price": 18, "stock": 10},
        {"name": "铁矿石", "price": 12, "stock": 10},
        {"name": "千年灵芝", "price": 90, "stock": 3},
        {"name": "天雷珠", "price": 140, "stock": 2},
        {"name": "玄铁矿", "price": 70, "stock": 5},
        {"name": "冰晶", "price": 100, "stock": 3},
    ],
    "rare_items": [
        {"name": "天材地宝", "price": 600, "stock": 1},
        {"name": "仙器碎片", "price": 900, "stock": 1},
        {"name": "天机碎片", "price": 250, "stock": 2},
        {"name": "破境丹", "price": 3500, "stock": 1},
    ],
}


def refresh_auction() -> list:
    items = AUCTION_HOUSE["refresh_items"].copy()
    if random.random() < 0.3:
        rare = random.choice(AUCTION_HOUSE["rare_items"])
        items.append(rare)
    return items


def buy_auction(character: dict, item_name: str, price: int) -> dict:
    if character.get("inventory", {}).get("灵石", 0) < price:
        return {"success": False, "message": "灵石不足"}
    character["inventory"]["灵石"] -= price
    character["inventory"][item_name] = character["inventory"].get(item_name, 0) + 1
    return {"success": True, "message": f"成功购买{item_name}！"}


def sell_auction(character: dict, item_name: str, count: int = 1) -> dict:
    if character.get("inventory", {}).get(item_name, 0) < count:
        return {"success": False, "message": f"{item_name}数量不足"}
    item_data = ITEM_DB.get(item_name)
    if not item_data:
        return {"success": False, "message": "未知物品"}
    price = int(item_data.get("price", 1) * 0.6) * count
    character["inventory"][item_name] -= count
    if character["inventory"][item_name] <= 0:
        del character["inventory"][item_name]
    character["inventory"]["灵石"] = character["inventory"].get("灵石", 0) + price
    return {"success": True, "message": f"出售{item_name}×{count}，获得{price}灵石", "earned": price}
