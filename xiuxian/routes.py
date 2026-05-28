"""
修仙游戏路由注册模块
"""
from flask import send_from_directory, request, jsonify, session
from .xiuxian_db import save_character, load_character, delete_character, get_all_players
from .game_engine import (
    create_character, cultivate, attempt_breakthrough,
    create_combat, combat_action, apply_combat_result,
    explore_region, handle_exploration_choice, talk_to_npc, buy_from_npc,
    use_item, move_to_region, rest, get_character_summary,
    learn_technique, buy_technique, learn_ability, buy_skill,
    roll_dice, migrate_character, check_idle_cultivation, attempt_ascension,
    get_npc_quests, accept_quest, check_quest_progress, complete_quest,
    get_achievements, check_achievements, rebirth,
    craft_item, get_crafting_recipes,
    REGIONS, NPC_DB, ITEM_DB, SKILL_DB, MONSTER_DB, REALM_DATA, Realm,
    TECHNIQUE_DB, ABILITY_DB, CRAFTING_DB,
    get_realm_full_name,
    # 新系统
    SECT_DB, join_sect, leave_sect, get_sect_info, SECT_TASKS,
    PET_DB, catch_pet, feed_pet, evolve_pet,
    DUNGEON_DB, enter_dungeon, dungeon_battle, dungeon_next_floor, dungeon_reward,
    WORLD_BOSS_DB, get_world_boss, attack_world_boss,
    ENHANCE_DB, GEM_DB, enhance_equipment, embed_gem,
    ALCHEMY_MASTERY, get_alchemy_level, advanced_craft, detoxify,
    AUCTION_HOUSE, refresh_auction, buy_auction, sell_auction,
)

# ── 角色数据白名单（防止客户端注入） ──
_CHAR_ALLOWED_KEYS = {
    'name', 'element', 'elements', 'realm', 'realm_level', 'stage',
    'hp', 'max_hp', 'mp', 'max_mp', 'attack', 'defense',
    'exp', 'exp_to_next', 'max_exp', 'lifespan', 'spirit_stones',
    'inventory', 'skills', 'techniques', 'abilities', 'equipped',
    'location', 'relation', 'npc_relations',
    'tutorial_step', 'tutorial_done',
    'base_hp', 'base_mp', 'base_attack', 'base_defense',
    'last_cultivate_time', 'sword_uses', 'sword_tier', 'kills', 'age',
    'stats', 'active_quests', 'completed_quests', 'achievements',
}

def _sanitize_character(char_dict):
    """过滤角色数据，只保留白名单字段，防止客户端注入"""
    if not isinstance(char_dict, dict):
        return None
    result = {k: v for k, v in char_dict.items() if k in _CHAR_ALLOWED_KEYS}

    # 数值范围校验：防止修改器注入
    _int_fields_positive = ['hp', 'max_hp', 'mp', 'max_mp', 'attack', 'defense',
                            'exp', 'exp_to_next', 'lifespan', 'spirit_stones',
                            'base_hp', 'base_mp', 'base_attack', 'base_defense',
                            'kills', 'age', 'sword_uses', 'sword_tier']
    for key in _int_fields_positive:
        if key in result:
            try:
                result[key] = max(0, int(result[key]))
            except (ValueError, TypeError):
                result[key] = 0

    # hp 不能超过 max_hp
    if 'hp' in result and 'max_hp' in result:
        result['hp'] = min(result['hp'], result['max_hp'])
    # mp 不能超过 max_mp
    if 'mp' in result and 'max_mp' in result:
        result['mp'] = min(result['mp'], result['max_mp'])

    # 字符串字段长度限制
    for str_key in ['name', 'location']:
        if str_key in result and isinstance(result[str_key], str):
            result[str_key] = result[str_key][:20]

    # realm 必须是有效枚举值
    if 'realm' in result:
        try:
            from .game_engine import Realm
            Realm(result['realm'])  # 验证是否合法
        except (ValueError, KeyError):
            result['realm'] = 0

    return result

def _get_json():
    """安全获取 JSON 请求体"""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}

def _get_character_from_request():
    """从请求中获取并净化角色数据"""
    data = _get_json()
    char = data.get('character')
    if not isinstance(char, dict):
        return None, data
    return _sanitize_character(char), data

def register_routes(app, templates_dir, static_dir, prefix='/xiuxian'):
    def _route(path):
        return f"{prefix}{path}"

    # ── 页面路由 ──
    @app.route(_route('/'))
    def xiuxian_index():
        return send_from_directory(templates_dir, 'index.html')

    @app.route(_route('/static/<path:filename>'))
    def xiuxian_static(filename):
        return send_from_directory(static_dir, filename)

    # 战斗界面原型（独立页面）
    import os as _os
    _xiuxian_root = _os.path.dirname(_os.path.abspath(__file__))
    @app.route(_route('/battle.html'))
    def xiuxian_battle():
        return send_from_directory(_xiuxian_root, 'battle.html')

    # ── 游戏数据 API ──
    @app.route(_route('/api/game_data'))
    def xiuxian_game_data():
        return jsonify(
            success=True,
            data={
                "regions": {k: {"level": v["level"], "desc": v["desc"], "npc": v["npc"]} for k, v in REGIONS.items()},
                "npcs": {k: {"title": v["title"], "realm": v["realm"].value, "personality": v["personality"], "skill_shop": v.get("skill_shop", [])} for k, v in NPC_DB.items()},
                "items": {k: {"type": v["type"], "desc": v["desc"], "rarity": v["rarity"], "price": v.get("price", 10)} for k, v in ITEM_DB.items()},
                "skills": {k: {"element": v["element"].value, "damage": v["damage"], "cost": v["cost"], "atk_mult": v.get("atk_mult", 0.3), "is_sword": v.get("is_sword", False), "sword_tier": v.get("sword_tier", 0), "price": v.get("price", 0), "desc": v["desc"]} for k, v in SKILL_DB.items()},
                "techniques": {k: {"tier": v["tier"], "element": v["element"].value, "hp_pct": v["hp_pct"], "mp_pct": v["mp_pct"], "atk_pct": v["atk_pct"], "def_pct": v["def_pct"], "desc": v["desc"], "price": v["price"]} for k, v in TECHNIQUE_DB.items()},
                "abilities": {k: {"tier": v["tier"], "element": v["element"].value, "base_damage": v["base_damage"], "atk_mult": v["atk_mult"], "cost": v["cost"], "desc": v["desc"], "obtain": v.get("obtain", "explore")} for k, v in ABILITY_DB.items()},
                "monsters": {k: {"hp": v["hp"], "damage": v["attack"], "defense": v["defense"], "element": v["element"].value if hasattr(v["element"], 'value') else v["element"], "exp": v["exp"]} for k, v in MONSTER_DB.items()},
                "crafting": {k: {"materials": v["materials"], "result": v["result"], "result_count": v.get("result_count", 1), "desc": v["desc"]} for k, v in CRAFTING_DB.items()},
                "realms": {k.value: {"name": v["name"], "stages": v["stages"], "max_lifespan": v["max_lifespan"], "base_cultivation_speed": v["base_cultivation_speed"], "breakthrough_base_rate": v["breakthrough_base_rate"], "description": v["description"]} for k, v in REALM_DATA.items()},
            }
        )

    # ── 骰子 API ──
    @app.route(_route('/api/roll_dice'))
    def xiuxian_roll_dice():
        result = roll_dice()
        return jsonify(success=True, result=result)

    # ── 角色 API ──
    @app.route(_route('/api/create_character'), methods=['POST'])
    def xiuxian_create_character():
        data = _get_json()
        name = data.get('name', '').strip()
        elements = data.get('elements', ['金'])
        stats = data.get('stats')

        if not name or len(name) > 10:
            return jsonify(success=False, message="名字需要1-10个字符")
        valid_elems = ('金', '木', '水', '火', '土')
        if not isinstance(elements, list) or not all(e in valid_elems for e in elements):
            return jsonify(success=False, message="无效的五行属性")
        if not elements:
            return jsonify(success=False, message="至少选择一个灵根")

        character = create_character(name, elements, stats)
        username = session.get('xiuxian_user', f'guest_{name}')
        session['xiuxian_user'] = username
        save_character(username, character)

        return jsonify(success=True, character=character, summary=get_character_summary(character))

    @app.route(_route('/api/load_character'), methods=['GET', 'POST'])
    def xiuxian_load_character():
        username = session.get('xiuxian_user', '')
        if not username:
            return jsonify(success=False, message="未登录")

        character = load_character(username)
        if not character:
            return jsonify(success=False, message="没有存档")

        character = migrate_character(character)
        return jsonify(success=True, character=character, summary=get_character_summary(character))

    @app.route(_route('/api/save_character'), methods=['POST'])
    def xiuxian_save_character():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")

        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)
        return jsonify(success=True, message="存档成功")

    @app.route(_route('/api/delete_character'), methods=['POST'])
    def xiuxian_delete_character():
        username = session.get('xiuxian_user', '')
        if not username:
            return jsonify(success=False, message="未登录，无法删除")
        delete_character(username)
        return jsonify(success=True, message="删除成功")

    # ── 游戏操作 API ──
    @app.route(_route('/api/cultivate'), methods=['POST'])
    def xiuxian_cultivate():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")

        result = cultivate(character)
        # 任务进度：修炼
        check_quest_progress(character, "cultivate")
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/check_idle'), methods=['POST'])
    def xiuxian_check_idle():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")

        result = check_idle_cultivation(character)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/breakthrough'), methods=['POST'])
    def xiuxian_breakthrough():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        use_items = data.get('use_items', [])
        if not character:
            return jsonify(success=False, message="无效数据")

        result = attempt_breakthrough(character, use_items)
        # 任务进度：突破
        if result.get("success"):
            check_quest_progress(character, "breakthrough")
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/ascend'), methods=['POST'])
    def xiuxian_ascend():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")

        result = attempt_ascension(character)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/explore'), methods=['POST'])
    def xiuxian_explore():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")

        result = explore_region(character)
        # 任务进度：探索区域
        region = character.get("location", "")
        check_quest_progress(character, "explore", region)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/explore_choice'), methods=['POST'])
    def xiuxian_explore_choice():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        choice = data.get('choice', '')
        if isinstance(choice, str):
            choice = choice[:50]

        if not character:
            return jsonify(success=False, message="无效数据")

        result = handle_exploration_choice(character, choice)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/combat'), methods=['POST'])
    def xiuxian_combat():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        action = data.get('action', 'attack')
        if action not in ('attack', 'defend', 'skill', 'ability', 'flee'):
            action = 'attack'
        skill = data.get('skill')
        if isinstance(skill, str):
            skill = skill[:50]  # 限制长度
        enemy_name = data.get('enemy')
        if isinstance(enemy_name, str):
            enemy_name = enemy_name[:50]

        if not character:
            return jsonify(success=False, message="无效数据")

        # 创建战斗（如果需要）
        if enemy_name:
            combat = create_combat(character, enemy_name)
            if not combat:
                return jsonify(success=False, message="未知敌人")
            return jsonify(success=True, combat=combat)

        # 继续战斗
        combat = data.get('combat')
        if not combat:
            return jsonify(success=False, message="没有战斗数据")

        combat = combat_action(combat, action, skill)

        # 战斗结束处理
        if combat["finished"]:
            result = apply_combat_result(character, combat)
            # 任务进度：击杀怪物
            if combat.get("victory"):
                enemy_name = combat.get("enemy", {}).get("name", "")
                check_quest_progress(character, "kill", enemy_name)
            username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
            save_character(username, character)
            return jsonify(success=True, combat=combat, result=result, summary=get_character_summary(character))

        return jsonify(success=True, combat=combat)

    @app.route(_route('/api/npc'), methods=['POST'])
    def xiuxian_npc():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        npc_name = data.get('npc')

        if not character or not npc_name:
            return jsonify(success=False, message="无效数据")

        result = talk_to_npc(character, npc_name)
        return jsonify(success=True, result=result)

    @app.route(_route('/api/buy'), methods=['POST'])
    def xiuxian_buy():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        npc_name = data.get('npc')
        item_name = data.get('item')

        if not character or not npc_name or not item_name:
            return jsonify(success=False, message="无效数据")

        result = buy_from_npc(character, npc_name, item_name)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/use_item'), methods=['POST'])
    def xiuxian_use_item():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        item_name = data.get('item')

        if not character or not item_name:
            return jsonify(success=False, message="无效数据")

        result = use_item(character, item_name)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/move'), methods=['POST'])
    def xiuxian_move():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        region = data.get('region')

        if not character or not region:
            return jsonify(success=False, message="无效数据")

        result = move_to_region(character, region)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/rest'), methods=['POST'])
    def xiuxian_rest():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")

        result = rest(character)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    # ── 功法/神通 API ──
    @app.route(_route('/api/buy_technique'), methods=['POST'])
    def xiuxian_buy_technique():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        npc_name = data.get('npc')
        tech_name = data.get('technique')

        if not character or not npc_name or not tech_name:
            return jsonify(success=False, message="无效数据")

        result = buy_technique(character, npc_name, tech_name)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/buy_skill'), methods=['POST'])
    def xiuxian_buy_skill():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        npc_name = data.get('npc')
        skill_name = data.get('skill')

        if not character or not npc_name or not skill_name:
            return jsonify(success=False, message="无效数据")

        result = buy_skill(character, npc_name, skill_name)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/learn_technique'), methods=['POST'])
    def xiuxian_learn_technique():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        tech_name = data.get('technique')

        if not character or not tech_name:
            return jsonify(success=False, message="无效数据")

        result = learn_technique(character, tech_name)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/learn_ability'), methods=['POST'])
    def xiuxian_learn_ability():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        ability_name = data.get('ability')

        if not character or not ability_name:
            return jsonify(success=False, message="无效数据")

        result = learn_ability(character, ability_name)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    # ── 任务 API ──
    @app.route(_route('/api/get_quests'), methods=['POST'])
    def xiuxian_get_quests():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        npc_name = data.get('npc')

        if not character or not npc_name:
            return jsonify(success=False, message="无效数据")

        quests = get_npc_quests(character, npc_name)
        return jsonify(success=True, quests=quests)

    @app.route(_route('/api/accept_quest'), methods=['POST'])
    def xiuxian_accept_quest():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        quest_id = data.get('quest_id')

        if not character or not quest_id:
            return jsonify(success=False, message="无效数据")

        result = accept_quest(character, quest_id)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/complete_quest'), methods=['POST'])
    def xiuxian_complete_quest():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        quest_id = data.get('quest_id')

        if not character or not quest_id:
            return jsonify(success=False, message="无效数据")

        result = complete_quest(character, quest_id)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    # ── 成就 API ──
    @app.route(_route('/api/get_achievements'), methods=['POST'])
    def xiuxian_get_achievements():
        data = _get_json()
        character = _sanitize_character(data.get('character'))

        if not character:
            return jsonify(success=False, message="无效数据")

        achievements = get_achievements(character)
        return jsonify(success=True, achievements=achievements)

    @app.route(_route('/api/check_achievements'), methods=['POST'])
    def xiuxian_check_achievements():
        data = _get_json()
        character = _sanitize_character(data.get('character'))

        if not character:
            return jsonify(success=False, message="无效数据")

        new_achievements = check_achievements(character)
        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, new_achievements=new_achievements, summary=get_character_summary(character))

    # ── 转世重生 API ──
    @app.route(_route('/api/rebirth'), methods=['POST'])
    def xiuxian_rebirth():
        data = _get_json()
        character = _sanitize_character(data.get('character'))

        if not character:
            return jsonify(success=False, message="无效数据")

        result = rebirth(character)
        if not result["success"]:
            return jsonify(success=False, message=result["message"])

        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, result["character"])

        return jsonify(success=True, result=result, character=result["character"],
                       summary=get_character_summary(result["character"]))

    # ── 炼丹/合成 API ──
    @app.route(_route('/api/craft'), methods=['POST'])
    def xiuxian_craft():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        recipe_name = data.get('recipe')

        if not character or not recipe_name:
            return jsonify(success=False, message="无效数据")

        result = craft_item(character, recipe_name)
        if not result["success"]:
            return jsonify(success=False, message=result["message"])

        username = session.get('xiuxian_user', f'guest_{character.get("name", "")}')
        save_character(username, character)

        return jsonify(success=True, result=result, summary=get_character_summary(character))

    @app.route(_route('/api/get_recipes'), methods=['POST'])
    def xiuxian_get_recipes():
        data = _get_json()
        character = _sanitize_character(data.get('character'))

        if not character:
            return jsonify(success=False, message="无效数据")

        recipes = get_crafting_recipes(character)
        return jsonify(success=True, recipes=recipes)

    # ── 排行榜 API ──
    @app.route(_route('/api/leaderboard'))
    def xiuxian_leaderboard():
        try:
            players = get_all_players()
            leaderboard = []
            for username, char in players.items():
                if not isinstance(char, dict):
                    continue
                realm = char.get('realm', '练气')
                stage = char.get('stage', 0)
                realm_name = get_realm_full_name(Realm(realm), stage) if realm in [r.value for r in Realm] else realm
                leaderboard.append({
                    'name': char.get('name', '未知'),
                    'realm': realm_name,
                    'kills': char.get('kills', 0),
                    'exp': char.get('exp', 0),
                    'age': char.get('age', 16),
                })
            # 按修为排序
            leaderboard.sort(key=lambda x: x['exp'], reverse=True)
            return jsonify(success=True, leaderboard=leaderboard[:20])
        except Exception as e:
            return jsonify(success=False, message=str(e))

    # ── 游戏统计 API ──
    @app.route(_route('/api/game_stats'), methods=['POST'])
    def xiuxian_game_stats():
        data = _get_json()
        character = _sanitize_character(data.get('character'))

        if not character:
            return jsonify(success=False, message="无效数据")

        stats = character.get('stats', {})
        game_stats = {
            'kills': character.get('kills', 0),
            'explore_count': stats.get('explore_count', 0),
            'cultivate_count': stats.get('cultivate_count', 0),
            'craft_count': stats.get('craft_count', 0),
            'max_crit_damage': stats.get('max_crit_damage', 0),
            'elite_kills': stats.get('elite_kills', 0),
            'monsters_encountered': len(stats.get('monsters_encountered', [])),
            'regions_visited': len(stats.get('regions_visited', [])),
            'achievements': len(character.get('achievements', [])),
        }
        return jsonify(success=True, stats=game_stats)

    # ── 宗门系统 API ──
    @app.route(_route('/api/sect/join'), methods=['POST'])
    def xiuxian_sect_join():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = join_sect(character, data.get('sect_name', ''))
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/sect/leave'), methods=['POST'])
    def xiuxian_sect_leave():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = leave_sect(character)
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/sect/info'), methods=['POST'])
    def xiuxian_sect_info():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = get_sect_info(character)
        return jsonify(**result)

    @app.route(_route('/api/sect/list'), methods=['POST'])
    def xiuxian_sect_list():
        return jsonify(success=True, sects={k: {"desc": v["desc"], "element": v["element"].value, "bonus": v["bonus"]} for k, v in SECT_DB.items()})

    # ── 灵宠系统 API ──
    @app.route(_route('/api/pet/catch'), methods=['POST'])
    def xiuxian_pet_catch():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = catch_pet(character, data.get('pet_name', ''))
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/pet/feed'), methods=['POST'])
    def xiuxian_pet_feed():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = feed_pet(character, data.get('pet_index', 0), data.get('item_name', ''))
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/pet/evolve'), methods=['POST'])
    def xiuxian_pet_evolve():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = evolve_pet(character, data.get('pet_index', 0))
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/pet/list'), methods=['POST'])
    def xiuxian_pet_list():
        return jsonify(success=True, pets={k: {"element": v["element"].value, "desc": v["desc"], "catch_rate": v["catch_rate"]} for k, v in PET_DB.items()})

    # ── 秘境副本 API ──
    @app.route(_route('/api/dungeon/enter'), methods=['POST'])
    def xiuxian_dungeon_enter():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = enter_dungeon(character, data.get('dungeon_name', ''))
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/dungeon/battle'), methods=['POST'])
    def xiuxian_dungeon_battle():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = dungeon_battle(character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/dungeon/next'), methods=['POST'])
    def xiuxian_dungeon_next():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = dungeon_next_floor(character)
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/dungeon/reward'), methods=['POST'])
    def xiuxian_dungeon_reward():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = dungeon_reward(character)
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/dungeon/list'), methods=['POST'])
    def xiuxian_dungeon_list():
        return jsonify(success=True, dungeons={k: {"level": v["level"], "floors": v["floors"], "desc": v.get("desc", "")} for k, v in DUNGEON_DB.items()})

    # ── 世界BOSS API ──
    @app.route(_route('/api/world_boss/info'), methods=['POST'])
    def xiuxian_world_boss_info():
        boss = get_world_boss()
        return jsonify(success=True, boss=boss)

    @app.route(_route('/api/world_boss/attack'), methods=['POST'])
    def xiuxian_world_boss_attack():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        boss = data.get('boss')
        if not character or not boss:
            return jsonify(success=False, message="无效数据")
        result = attack_world_boss(character, boss)
        if result.get('defeated'):
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character, boss=boss)

    # ── 装备强化 API ──
    @app.route(_route('/api/enhance/equip'), methods=['POST'])
    def xiuxian_enhance_equip():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = enhance_equipment(character, data.get('item_name', ''))
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/enhance/gem'), methods=['POST'])
    def xiuxian_enhance_gem():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = embed_gem(character, data.get('item_name', ''), data.get('gem_name', ''))
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/enhance/gems'))
    def xiuxian_enhance_gems():
        return jsonify(success=True, gems={k: {"effect": v["effect"], "value": v["value"], "desc": v["desc"]} for k, v in GEM_DB.items()})

    # ── 丹道精通 API ──
    @app.route(_route('/api/alchemy/craft'), methods=['POST'])
    def xiuxian_alchemy_craft():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = advanced_craft(character, data.get('recipe_name', ''))
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/alchemy/detox'), methods=['POST'])
    def xiuxian_alchemy_detox():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = detoxify(character)
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/alchemy/info'), methods=['POST'])
    def xiuxian_alchemy_info():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = get_alchemy_level(character)
        return jsonify(success=True, alchemy=result)

    # ── 拍卖行 API ──
    @app.route(_route('/api/auction/list'), methods=['POST'])
    def xiuxian_auction_list():
        items = refresh_auction()
        return jsonify(success=True, items=items)

    @app.route(_route('/api/auction/buy'), methods=['POST'])
    def xiuxian_auction_buy():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = buy_auction(character, data.get('item_name', ''), data.get('price', 0))
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)

    @app.route(_route('/api/auction/sell'), methods=['POST'])
    def xiuxian_auction_sell():
        data = _get_json()
        character = _sanitize_character(data.get('character'))
        if not character:
            return jsonify(success=False, message="无效数据")
        result = sell_auction(character, data.get('item_name', ''), data.get('count', 1))
        if result['success']:
            save_character(session.get('xiuxian_user', ''), character)
        return jsonify(**result, character=character)
