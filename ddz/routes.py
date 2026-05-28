"""
斗地主路由模块
供 server.py 和 app.py 共用
"""

import os
from flask import send_from_directory, redirect, request, jsonify, session
from functools import wraps

from doudizhu_db import (
    init_db, create_user, verify_user, ensure_user_data, get_user_data,
    update_game_result, update_coins, set_coins, get_leaderboard,
    check_admin, get_all_users, delete_user, add_user_by_admin
)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect('/ddz/')
        return f(*args, **kwargs)
    return decorated


def register_routes(app, templates_dir, static_dir, prefix='/ddz'):
    """注册斗地主路由

    Args:
        app: Flask应用实例
        templates_dir: 模板目录绝对路径
        static_dir: 静态文件目录绝对路径
        prefix: URL前缀，默认'/ddz'（独立运行时用'/'）
    """

    def _route(path):
        return f'{prefix}{path}' if prefix != '/' else path

    # ---- 页面路由 ----

    @app.route(_route(''))
    @app.route(_route('/'))
    def ddz_index():
        return send_from_directory(templates_dir, 'index.html')

    @app.route(_route('/static/<path:filename>'))
    def ddz_static(filename):
        return send_from_directory(static_dir, filename)

    @app.route(_route('/register_page'))
    def ddz_register():
        return send_from_directory(templates_dir, 'register.html')

    @app.route(_route('/nav'))
    @login_required
    def ddz_nav():
        return send_from_directory(templates_dir, 'nav.html')

    @app.route(_route('/lobby'))
    @login_required
    def ddz_lobby():
        return send_from_directory(templates_dir, 'lobby.html')

    @app.route(_route('/profile'))
    @login_required
    def ddz_profile():
        return send_from_directory(templates_dir, 'profile.html')

    @app.route(_route('/doudizhu'))
    @login_required
    def ddz_game():
        return send_from_directory(templates_dir, 'doudizhu.html')

    @app.route(_route('/doudizhu_online'))
    @login_required
    def ddz_online():
        return send_from_directory(templates_dir, 'doudizhu_online.html')

    @app.route(_route('/admin_login'))
    def ddz_admin_login():
        return send_from_directory(templates_dir, 'admin_login.html')

    @app.route(_route('/admin'))
    def ddz_admin():
        if not session.get('is_admin'):
            return redirect(_route('/admin_login'))
        return send_from_directory(templates_dir, 'admin.html')

    @app.route(_route('/logout'))
    def ddz_logout():
        session.clear()
        return redirect(_route('/'))

    @app.route(_route('/switch_account'))
    def ddz_switch_account():
        session.clear()
        return redirect(_route('/'))

    # ---- 认证 API ----

    @app.route(_route('/login'), methods=['POST'])
    def ddz_api_login():
        data = request.json
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''

        if not username or not password:
            return jsonify(success=False, message='用户名和密码不能为空')

        if verify_user(username, password):
            session['username'] = username
            ensure_user_data(username)
            return jsonify(success=True, message='登录成功！')

        return jsonify(success=False, message='用户名或密码错误！')

    @app.route(_route('/register'), methods=['POST'])
    def ddz_api_register():
        data = request.json
        if not data:
            return jsonify(success=False, message='请求数据无效')
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''

        if not username or not password:
            return jsonify(success=False, message='用户名和密码不能为空！')
        if len(username) < 2:
            return jsonify(success=False, message='用户名至少2个字符！')
        if len(password) < 6:
            return jsonify(success=False, message='密码长度至少6位！')
        if len(username) > 20:
            return jsonify(success=False, message='用户名不能超过20个字符！')

        ok, msg = create_user(username, password)
        return jsonify(success=ok, message=msg)

    # ---- 数据 API ----

    @app.route(_route('/api/get_user_data'))
    def ddz_api_user_data():
        if 'username' not in session:
            return jsonify(success=False, message='未登录')
        data = get_user_data(session['username'])
        return jsonify(success=bool(data), data=data)

    @app.route(_route('/api/update_result'), methods=['POST'])
    def ddz_api_update_result():
        if 'username' not in session:
            return jsonify(success=False, message='未登录')
        result = request.json.get('result')
        if result not in ('win', 'loss', 'draw'):
            return jsonify(success=False, message='无效的结果')
        update_game_result(session['username'], result)
        return jsonify(success=True, data=get_user_data(session['username']))

    @app.route(_route('/api/leaderboard'))
    def ddz_api_leaderboard():
        return jsonify(success=True, leaderboard=get_leaderboard(10))

    # ---- 管理员 API ----

    @app.route(_route('/api/admin_login'), methods=['POST'])
    def ddz_api_admin_login():
        data = request.json
        if not data:
            return jsonify(success=False, message='请求数据无效')
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''
        if not username or not password:
            return jsonify(success=False, message='请输入账号和密码')
        if check_admin(username, password):
            session['is_admin'] = True
            session['admin_username'] = username
            return jsonify(success=True, message='管理员登录成功！')
        return jsonify(success=False, message='管理员账号或密码错误！')

    @app.route(_route('/api/admin/users'))
    def ddz_api_admin_users():
        if not session.get('is_admin'):
            return jsonify(success=False, message='请先登录')
        return jsonify(success=True, users=get_all_users())

    @app.route(_route('/api/admin/set_coins'), methods=['POST'])
    def ddz_api_admin_set_coins():
        if not session.get('is_admin'):
            return jsonify(success=False, message='请先登录')
        data = request.json
        if not data or not data.get('username'):
            return jsonify(success=False, message='参数错误')
        coins = data.get('coins', 1000)
        if not isinstance(coins, (int, float)) or coins < 0:
            return jsonify(success=False, message='金币不能为负数')
        try:
            set_coins(data['username'], int(coins))
            return jsonify(success=True, message=f"金币已设置为 {int(coins)}")
        except Exception as e:
            return jsonify(success=False, message=str(e))

    @app.route(_route('/api/admin/delete_user'), methods=['POST'])
    def ddz_api_admin_delete_user():
        if not session.get('is_admin'):
            return jsonify(success=False, message='请先登录')
        data = request.json
        if not data or not data.get('username'):
            return jsonify(success=False, message='参数错误')
        username = data['username']
        try:
            delete_user(username)
            return jsonify(success=True, message=f'用户 {username} 已删除')
        except Exception as e:
            return jsonify(success=False, message=str(e))

    @app.route(_route('/api/admin/add_user'), methods=['POST'])
    def ddz_api_admin_add_user():
        if not session.get('is_admin'):
            return jsonify(success=False, message='请先登录')
        data = request.json
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''
        if not username or not password:
            return jsonify(success=False, message='用户名和密码不能为空')
        ok, msg = add_user_by_admin(username, password, data.get('coins', 1000))
        return jsonify(success=ok, message=msg)
