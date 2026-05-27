"""
统一服务器 - 托管所有项目
- / -> my word (作品集)
- /ddz -> 斗地主游戏
- /hand-particles -> 手势粒子
"""

from flask import Flask, send_from_directory, redirect
from flask_socketio import SocketIO
import os
import sys

# 添加 ddz 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ddz'))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================
# 作品集路由
# ============================================

@app.route('/')
def home():
    """作品集主页"""
    return send_from_directory(os.path.join(BASE_DIR, 'my word'), 'index.html')


@app.route('/assets/<path:filename>')
def home_assets(filename):
    """作品集资源文件"""
    return send_from_directory(os.path.join(BASE_DIR, 'my word', 'assets'), filename)


@app.route('/style.css')
def home_css():
    """作品集样式"""
    return send_from_directory(os.path.join(BASE_DIR, 'my word'), 'style.css')


@app.route('/script.js')
def home_js():
    """作品集脚本"""
    return send_from_directory(os.path.join(BASE_DIR, 'my word'), 'script.js')


# ============================================
# 手势粒子路由
# ============================================

@app.route('/hand-particles')
def hand_redirect():
    """手势粒子入口"""
    return redirect('/hand-particles/')


@app.route('/hand-particles/')
def hand_index():
    """手势粒子主页"""
    return send_from_directory(os.path.join(BASE_DIR, 'hand-particles'), 'index.html')


@app.route('/hand-particles/<path:filename>')
def hand_static(filename):
    """手势粒子静态文件"""
    return send_from_directory(os.path.join(BASE_DIR, 'hand-particles'), filename)


# ============================================
# 斗地主路由（需要导入游戏模块）
# ============================================

@app.route('/ddz')
def ddz_redirect():
    """斗地主页入口"""
    return redirect('/ddz/')


@app.route('/ddz/')
def ddz_index():
    """斗地主主页"""
    return send_from_directory(os.path.join(BASE_DIR, 'ddz', 'templates'), 'index.html')


@app.route('/ddz/templates/<path:filename>')
def ddz_templates(filename):
    """斗地主模板文件"""
    return send_from_directory(os.path.join(BASE_DIR, 'ddz', 'templates'), filename)


@app.route('/ddz/static/<path:filename>')
def ddz_static(filename):
    """斗地主静态文件"""
    return send_from_directory(os.path.join(BASE_DIR, 'ddz', 'static'), filename)


# ============================================
# 斗地主登录和注册页面路由
# ============================================

@app.route('/ddz/register_page')
def ddz_register():
    """斗地主注册页面"""
    return send_from_directory(os.path.join(BASE_DIR, 'ddz', 'templates'), 'register.html')


@app.route('/ddz/nav')
def ddz_nav():
    """斗地主导航页面"""
    return send_from_directory(os.path.join(BASE_DIR, 'ddz', 'templates'), 'nav.html')


@app.route('/ddz/lobby')
def ddz_lobby():
    """斗地主大厅"""
    return send_from_directory(os.path.join(BASE_DIR, 'ddz', 'templates'), 'lobby.html')


@app.route('/ddz/profile')
def ddz_profile():
    """斗地主个人资料"""
    return send_from_directory(os.path.join(BASE_DIR, 'ddz', 'templates'), 'profile.html')


@app.route('/ddz/doudizhu')
def ddz_game():
    """斗地主单机游戏"""
    return send_from_directory(os.path.join(BASE_DIR, 'ddz', 'templates'), 'doudizhu.html')


@app.route('/ddz/doudizhu_online')
def ddz_online():
    """斗地主联机游戏"""
    return send_from_directory(os.path.join(BASE_DIR, 'ddz', 'templates'), 'doudizhu_online.html')


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  项目统一服务器")
    print("=" * 50)
    print("  作品集:     http://127.0.0.1:8080/")
    print("  斗地主:     http://127.0.0.1:8080/ddz/")
    print("  手势粒子:   http://127.0.0.1:8080/hand-particles/")
    print("=" * 50 + "\n")

    socketio.run(app, debug=True, host='0.0.0.0', port=8080)
