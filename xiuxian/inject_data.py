"""
直接注入扩展数据到 game_engine.py
"""
import re

# 读取原文件
with open("game_engine.py", "r", encoding="utf-8") as f:
    content = f.read()

print(f"原始文件大小: {len(content)} 字节, {content.count(chr(10))} 行")

# ============================================================
# 1. 扩展 Realm 枚举
# ============================================================
old_realm_enum = '''class Realm(Enum):
    LIANQI = "练气"
    ZHUJI = "筑基"
    JIEDAN = "结丹"
    YUANYING = "元婴"
    HUASHEN = "化神"'''

new_realm_enum = '''class Realm(Enum):
    LIANQI = "练气"
    ZHUJI = "筑基"
    JIEDAN = "结丹"
    YUANYING = "元婴"
    HUASHEN = "化神"
    LIANXU = "炼虚"
    HETI = "合体"
    DACHENG = "大乘"
    DUJIE = "渡劫"
    FEISHENG = "飞升"'''

content = content.replace(old_realm_enum, new_realm_enum)

# 2. 扩展 REALM_ORDER
old_order = "REALM_ORDER = [Realm.LIANQI, Realm.ZHUJI, Realm.JIEDAN, Realm.YUANYING, Realm.HUASHEN]"
new_order = "REALM_ORDER = [Realm.LIANQI, Realm.ZHUJI, Realm.JIEDAN, Realm.YUANYING, Realm.HUASHEN, Realm.LIANXU, Realm.HETI, Realm.DACHENG, Realm.DUJIE, Realm.FEISHENG]"
content = content.replace(old_order, new_order)

# 3. 在 REALM_DATA 的化神条目后添加新境界
old_huashen_end = '''        "description": "元婴化神，掌控天地",
    },
}'''

new_huashen_end = '''        "description": "元婴化神，掌控天地",
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
}'''

content = content.replace(old_huashen_end, new_huashen_end)

# 4. 在 ITEM_DB 末尾添加新物品
old_item_end = '    "破境丹": {"type": "consumable", "effect": "breakthrough", "value": 30, "desc": "突破成功率+30%", "rarity": "仙品", "price": 3000},\n}'

new_items = '''
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
'''

new_item_end = '    "破境丹": {"type": "consumable", "effect": "breakthrough", "value": 30, "desc": "突破成功率+30%", "rarity": "仙品", "price": 3000},' + new_items + '}'
content = content.replace(old_item_end, new_item_end)

# 5. 在 CRAFTING_DB 末尾添加新配方
old_craft_end = '    "破境丹": {"materials": {"灵石": 2000, "天材地宝": 2, "天机碎片": 2, "千年灵芝": 3}, "result": "破境丹", "result_count": 1, "desc": "天材地宝×2 + 天机碎片×2 + 千年灵芝×3 + 灵石×2000"},\n}'

new_recipes = '''
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
'''

new_craft_end = '    "破境丹": {"materials": {"灵石": 2000, "天材地宝": 2, "天机碎片": 2, "千年灵芝": 3}, "result": "破境丹", "result_count": 1, "desc": "天材地宝×2 + 天机碎片×2 + 千年灵芝×3 + 灵石×2000"},' + new_recipes + '}'
content = content.replace(old_craft_end, new_craft_end)

# 6. 在 SKILL_DB 末尾添加新技能
old_skill_end = '    "山崩地裂": {"element": Element.EARTH, "damage": 80, "cost": 58, "atk_mult": 0.7, "desc": "土属性高级法术", "price": 1200},\n}'

new_skills = '''
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
'''

new_skill_end = '    "山崩地裂": {"element": Element.EARTH, "damage": 80, "cost": 58, "atk_mult": 0.7, "desc": "土属性高级法术", "price": 1200},' + new_skills + '}'
content = content.replace(old_skill_end, new_skill_end)

# 7. 在 TECHNIQUE_DB 末尾添加新功法
old_tech_end = '    "混元大道": {"tier": "仙级", "element": Element.EARTH, "hp_pct": 38, "mp_pct": 28, "atk_pct": 18, "def_pct": 25, "desc": "土属性仙级功法", "price": 0},\n}'

new_techniques = '''
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
'''

new_tech_end = '    "混元大道": {"tier": "仙级", "element": Element.EARTH, "hp_pct": 38, "mp_pct": 28, "atk_pct": 18, "def_pct": 25, "desc": "土属性仙级功法", "price": 0},' + new_techniques + '}'
content = content.replace(old_tech_end, new_tech_end)

# 8. 在 ABILITY_DB 末尾添加新神通
old_abi_end = '    "焚天大道": {"tier": "仙级", "element": Element.FIRE,  "base_damage": 130, "atk_mult": 1.0, "cost": 85, "desc": "火属性仙级神通", "obtain": "breakthrough"},\n}'

new_abilities = '''
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
'''

new_abi_end = '    "焚天大道": {"tier": "仙级", "element": Element.FIRE,  "base_damage": 130, "atk_mult": 1.0, "cost": 85, "desc": "火属性仙级神通", "obtain": "breakthrough"},' + new_abilities + '}'
content = content.replace(old_abi_end, new_abi_end)

# 9. 在 MONSTER_DB 末尾添加新怪物
old_monster_end = '    "上古石魔": {"hp": 400, "attack": 50, "defense": 50, "element": Element.EARTH, "exp": 280,\n               "drops": {"灵石": [200, 500], "玄铁矿": [0, 3], "天雷珠": [0, 2]}},\n}'

new_monsters = '''
    # ── 万妖山 ──
    "妖王": {"hp": 500, "attack": 75, "defense": 45, "element": Element.FIRE, "exp": 350,
             "drops": {"灵石": [200, 600], "天材地宝": [0, 2], "妖丹": [1, 1]}},
    "石魔将": {"hp": 450, "attack": 65, "defense": 55, "element": Element.EARTH, "exp": 300,
              "drops": {"灵石": [180, 500], "玄铁矿": [0, 3]}},
    # ── 星落海 ──
    "海妖": {"hp": 350, "attack": 60, "defense": 35, "element": Element.WATER, "exp": 260,
             "drops": {"灵石": [150, 400], "冰晶": [0, 2]}},
    "深海巨鲸": {"hp": 600, "attack": 70, "defense": 50, "element": Element.WATER, "exp": 400,
                "drops": {"灵石": [250, 700], "天材地宝": [0, 2]}},
    "珊瑚精": {"hp": 280, "attack": 45, "defense": 40, "element": Element.WOOD, "exp": 200,
               "drops": {"灵石": [120, 350], "千年灵芝": [0, 2]}},
    "海龙": {"hp": 550, "attack": 80, "defense": 45, "element": Element.WATER, "exp": 380,
             "drops": {"灵石": [200, 600], "龙珠": [0, 1]}},
    "水母精": {"hp": 200, "attack": 55, "defense": 20, "element": Element.WATER, "exp": 170,
               "drops": {"灵石": [80, 250], "魂晶": [0, 1]}},
    "鲛人": {"hp": 320, "attack": 58, "defense": 30, "element": Element.WATER, "exp": 240,
             "drops": {"灵石": [140, 380], "鲛人泪": [0, 1]}},
    # ── 天玄域 ──
    "天玄弟子": {"hp": 300, "attack": 55, "defense": 35, "element": Element.METAL, "exp": 230,
                "drops": {"灵石": [130, 370], "天机碎片": [0, 1]}},
    "护山神兽": {"hp": 500, "attack": 70, "defense": 50, "element": Element.EARTH, "exp": 350,
                "drops": {"灵石": [200, 550], "天材地宝": [0, 1]}},
    "剑灵": {"hp": 250, "attack": 85, "defense": 20, "element": Element.METAL, "exp": 280,
             "drops": {"灵石": [150, 450], "仙器碎片": [0, 1]}},
    "阵法傀儡": {"hp": 400, "attack": 50, "defense": 60, "element": Element.EARTH, "exp": 300,
                "drops": {"灵石": [180, 500], "天机碎片": [0, 2]}},
    "天玄长老": {"hp": 600, "attack": 90, "defense": 55, "element": Element.FIRE, "exp": 450,
                "drops": {"灵石": [300, 800], "天材地宝": [0, 2], "仙器碎片": [0, 1]}},
    "道心魔": {"hp": 350, "attack": 75, "defense": 25, "element": Element.WATER, "exp": 320,
               "drops": {"灵石": [160, 480], "魂晶": [0, 2]}},
    # ── 九幽地府 ──
    "鬼将": {"hp": 450, "attack": 70, "defense": 40, "element": Element.WATER, "exp": 340,
             "drops": {"灵石": [200, 550], "魂晶": [0, 3]}},
    "冥河摆渡人": {"hp": 400, "attack": 65, "defense": 45, "element": Element.WATER, "exp": 310,
                  "drops": {"灵石": [180, 500], "天材地宝": [0, 1]}},
    "判官": {"hp": 550, "attack": 80, "defense": 50, "element": Element.METAL, "exp": 420,
             "drops": {"灵石": [250, 700], "天道碎片": [0, 1]}},
    "阎罗": {"hp": 800, "attack": 100, "defense": 60, "element": Element.FIRE, "exp": 600,
             "drops": {"灵石": [400, 1000], "天道碎片": [0, 2], "混沌精华": [0, 1]}},
    "幽冥龙": {"hp": 700, "attack": 95, "defense": 55, "element": Element.WATER, "exp": 550,
               "drops": {"灵石": [350, 900], "龙珠": [0, 1], "天道碎片": [0, 1]}},
    "忘川水鬼": {"hp": 300, "attack": 60, "defense": 30, "element": Element.WATER, "exp": 250,
                "drops": {"灵石": [140, 400], "魂晶": [0, 2]}},
    # ── 混沌深渊 ──
    "混沌兽": {"hp": 600, "attack": 85, "defense": 50, "element": Element.EARTH, "exp": 480,
               "drops": {"灵石": [300, 800], "混沌精华": [0, 1]}},
    "时空裂隙": {"hp": 500, "attack": 90, "defense": 30, "element": Element.FIRE, "exp": 450,
                "drops": {"灵石": [250, 700], "天道碎片": [0, 1]}},
    "虚空行者": {"hp": 450, "attack": 95, "defense": 35, "element": Element.METAL, "exp": 420,
                "drops": {"灵石": [220, 650], "天道碎片": [0, 1]}},
    "混沌魔神": {"hp": 1000, "attack": 120, "defense": 70, "element": Element.FIRE, "exp": 800,
                "drops": {"灵石": [500, 1500], "混沌精华": [0, 2], "造化玉碟": [0, 1]}},
    "灭世天魔": {"hp": 1200, "attack": 140, "defense": 80, "element": Element.FIRE, "exp": 1000,
                "drops": {"灵石": [600, 2000], "混沌精华": [0, 3], "天道碎片": [0, 2]}},
    "混沌之眼": {"hp": 800, "attack": 110, "defense": 60, "element": Element.WATER, "exp": 700,
                "drops": {"灵石": [400, 1200], "天道碎片": [0, 2]}},
    # ── 仙灵岛 ──
    "仙鹤": {"hp": 400, "attack": 60, "defense": 40, "element": Element.WOOD, "exp": 350,
             "drops": {"灵石": [200, 600], "千年灵芝": [0, 2]}},
    "灵芝仙": {"hp": 350, "attack": 50, "defense": 45, "element": Element.WOOD, "exp": 320,
               "drops": {"灵石": [180, 500], "千年灵芝": [0, 3]}},
    "仙童": {"hp": 500, "attack": 75, "defense": 50, "element": Element.METAL, "exp": 400,
             "drops": {"灵石": [250, 700], "天材地宝": [0, 2]}},
    "守岛神兽": {"hp": 800, "attack": 100, "defense": 65, "element": Element.EARTH, "exp": 650,
                "drops": {"灵石": [400, 1100], "天道碎片": [0, 1], "造化玉碟": [0, 1]}},
    "仙灵蝶": {"hp": 300, "attack": 70, "defense": 30, "element": Element.WOOD, "exp": 280,
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
'''

new_monster_end = '    "上古石魔": {"hp": 400, "attack": 50, "defense": 50, "element": Element.EARTH, "exp": 280,\n               "drops": {"灵石": [200, 500], "玄铁矿": [0, 3], "天雷珠": [0, 2]}},' + new_monsters + '}'
content = content.replace(old_monster_end, new_monster_end)

# 10. 在 REGIONS 末尾添加新区域
old_region_end = '''        "npc": ["天机老人"],
    },
}'''

new_regions = '''
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
}'''

content = content.replace(old_region_end, new_regions)

# 11. 在 UNIVERSAL_EVENTS 末尾添加新事件名
old_events_end = '    "丹药奇遇", "法器残片", "灵脉觉醒", "心魔试炼", "天道酬勤",\n]'

new_events = '''    "丹药奇遇", "法器残片", "灵脉觉醒", "心魔试炼", "天道酬勤",
    "遇到仙人", "天劫降临", "混沌秘境", "造化之力", "天道碎片", "凤凰涅槃", "龙宫探秘", "蟠桃盛会",
    "天道洗礼", "轮回感悟", "妖王降临", "海底遗迹", "星辰坠落", "天玄试炼", "论道大会", "冥河泛舟",
]'''

content = content.replace(old_events_end, new_events)

# 12. 在 EXPLORATION_CHAINS 末尾添加新任务链
old_chain_end = '''        "rewards": {"exp": 300, "ability": True, "stat": {"悟性": 3}},
    },
}'''

new_chains = '''
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
}'''

content = content.replace(old_chain_end, new_chains)

# 13. 在 ACHIEVEMENT_DB 末尾添加新成就（使用字符串条件）
old_achieve_end = '    "丹道宗师": {"desc": "合成20次", "condition": "craft_20", "reward": {"灵石": 1500, "千年灵芝": 5}},\n}'

new_achievements = '''
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
}'''

content = content.replace(old_achieve_end, new_achievements)

# 14. 在 NPC_DB 末尾添加新NPC（在天机老人之后）
old_npc_end = '''        "relation_rewards": {
            80: {"item": "化神丹", "message": "天机老人：这枚化神丹，助你一臂之力。"},
            150: {"technique": "雷霆万钧", "message": "天机老人传授你天级功法雷霆万钧！"},
        },
    },
}'''

new_npcs = '''
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
}'''

content = content.replace(old_npc_end, new_npcs)

# 写入文件
with open("game_engine.py", "w", encoding="utf-8") as f:
    f.write(content)

print(f"扩展数据注入完成！")
print(f"文件大小: {len(content)} 字节, {content.count(chr(10))} 行")
